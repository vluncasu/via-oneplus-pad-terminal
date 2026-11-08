package com.via.core.vision

import android.content.Context
import android.graphics.Bitmap
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarkerResult
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicBoolean

class PalmLandmarkerEngine(
    context: Context,
    private val modelAssetPath: String = "hand_landmarker.task",
    private val onDescriptor: (descriptor: List<Float>, handedness: String?, confidence: Float) -> Unit,
    private val onError: (Throwable) -> Unit = {},
) : ImageAnalysis.Analyzer, AutoCloseable {

    private val busy = AtomicBoolean(false)
    private val landmarker: HandLandmarker

    private var lastDescriptor: List<Float>? = null
    private var stableCount = 0

    init {
        val base = BaseOptions.builder().setModelAssetPath(modelAssetPath).build()
        val options = HandLandmarker.HandLandmarkerOptions.builder()
            .setBaseOptions(base)
            .setRunningMode(RunningMode.IMAGE)
            .setNumHands(1)
            .setMinHandDetectionConfidence(0.40f)
            .setMinHandPresenceConfidence(0.40f)
            .setMinTrackingConfidence(0.45f)
            .build()
        landmarker = HandLandmarker.createFromOptions(context, options)
    }

    override fun analyze(image: ImageProxy) {
        if (!busy.compareAndSet(false, true)) { image.close(); return }
        try {
            val bitmap = rgbaImageProxyToBitmap(image)
            val mpImage = BitmapImageBuilder(bitmap).build()
            val result = landmarker.detect(mpImage)
            process(result)
        } catch (t: Throwable) {
            onError(t)
        } finally {
            busy.set(false)
            image.close()
        }
    }

    private fun process(result: HandLandmarkerResult) {
        val hand = result.landmarks().firstOrNull() ?: run {
            stableCount = 0
            lastDescriptor = null
            return
        }
        val descriptor = PalmDescriptor.fromLandmarks(hand)
        val category = result.handedness().firstOrNull()?.firstOrNull()
        val confidence = category?.score() ?: 0f

        val prev = lastDescriptor
        val smoothed = if (prev != null && prev.size == descriptor.size) {
            val sim = PalmDescriptor.cosine(prev, descriptor)
            if (sim > 0.85f) {
                stableCount++
                descriptor.indices.map { i -> prev[i] * 0.3f + descriptor[i] * 0.7f }
            } else {
                stableCount = 0
                descriptor
            }
        } else {
            stableCount = 0
            descriptor
        }
        lastDescriptor = smoothed
        onDescriptor(smoothed, category?.categoryName(), confidence)
    }

    override fun close() = landmarker.close()

    private fun rgbaImageProxyToBitmap(image: ImageProxy): Bitmap {
        require(image.format == android.graphics.PixelFormat.RGBA_8888 || image.planes.size == 1) {
            "Configure ImageAnalysis OUTPUT_IMAGE_FORMAT_RGBA_8888 for palm analysis"
        }
        val plane = image.planes[0]
        val buffer = plane.buffer
        buffer.rewind()
        val rowStride = plane.rowStride
        val pixelStride = plane.pixelStride
        val rowPadding = rowStride - pixelStride * image.width
        val paddedWidth = image.width + rowPadding / pixelStride
        val temp = Bitmap.createBitmap(paddedWidth, image.height, Bitmap.Config.ARGB_8888)
        temp.copyPixelsFromBuffer(buffer)
        val cropped = Bitmap.createBitmap(temp, 0, 0, image.width, image.height)
        if (cropped !== temp) temp.recycle()
        return rotate(cropped, image.imageInfo.rotationDegrees.toFloat())
    }

    private fun rotate(source: Bitmap, degrees: Float): Bitmap {
        if (degrees == 0f) return source
        val matrix = android.graphics.Matrix().apply { postRotate(degrees) }
        val out = Bitmap.createBitmap(source, 0, 0, source.width, source.height, matrix, true)
        if (out !== source) source.recycle()
        return out
    }
}
