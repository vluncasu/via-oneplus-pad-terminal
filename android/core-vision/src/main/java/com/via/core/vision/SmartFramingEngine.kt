package com.via.core.vision

import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.Face
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.abs

class SmartFramingEngine(
    private val onFramingUpdate: (FramingState) -> Unit,
    private val onSmileConfirmed: (() -> Unit)? = null,
    private val onFaceDescriptor: ((List<Float>) -> Unit)? = null,
) : ImageAnalysis.Analyzer {

    private val faceTracker = FaceTracker()
    private val busy = AtomicBoolean(false)

    private var neutralBaseline = 0.15f
    private var neutralSamples = 0
    private var smileConsecutive = 0
    private var smileFired = false
    private var waitingForSmile = false
    private var lastDescriptorTimeMs = 0L

    companion object {
        private const val SMILE_DELTA_THRESHOLD = 0.45f
        private const val SMILE_CONSECUTIVE_REQUIRED = 4
        private const val NEUTRAL_SAMPLE_LIMIT = 20
        private const val DESCRIPTOR_INTERVAL_MS = 400L
    }

    fun startSmileDetection() {
        waitingForSmile = true
        smileConsecutive = 0
        smileFired = false
        neutralBaseline = 0.15f
        neutralSamples = 0
    }

    fun stopSmileDetection() {
        waitingForSmile = false
        smileConsecutive = 0
        smileFired = false
    }

    fun reset() {
        faceTracker.reset()
        stopSmileDetection()
    }

    private val options = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
        .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
        .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_ALL)
        .setContourMode(FaceDetectorOptions.CONTOUR_MODE_NONE)
        .setMinFaceSize(0.12f)
        .enableTracking()
        .build()

    private val detector = FaceDetection.getClient(options)

    @androidx.annotation.OptIn(ExperimentalGetImage::class)
    override fun analyze(imageProxy: ImageProxy) {
        if (!busy.compareAndSet(false, true)) {
            imageProxy.close()
            return
        }
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            busy.set(false)
            imageProxy.close()
            return
        }
        val image = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
        val frameW = imageProxy.width.toFloat()
        val frameH = imageProxy.height.toFloat()

        detector.process(image)
            .addOnSuccessListener { faces ->
                processDetection(faces, frameW, frameH)
            }
            .addOnFailureListener {
                onFramingUpdate(faceTracker.update(emptyList()))
            }
            .addOnCompleteListener {
                busy.set(false)
                imageProxy.close()
            }
    }

    private fun processDetection(faces: List<Face>, frameW: Float, frameH: Float) {
        val rawFaces = faces.mapNotNull { face ->
            val tid = face.trackingId ?: return@mapNotNull null
            val box = face.boundingBox
            RawFace(
                trackingId = tid,
                centerX = (box.centerX().toFloat()) / frameW,
                centerY = (box.centerY().toFloat()) / frameH,
                width = box.width().toFloat() / frameW,
                height = box.height().toFloat() / frameH,
                smileProbability = face.smilingProbability ?: 0f,
                eulerY = face.headEulerAngleY,
                eulerZ = face.headEulerAngleZ,
                confidence = 1f,
            )
        }

        val state = faceTracker.update(rawFaces)
        onFramingUpdate(state)

        if (waitingForSmile && !smileFired && state.activeFace != null) {
            processSmile(state.activeFace)
        }

        if (onFaceDescriptor != null && state.activeFace != null) {
            val now = System.currentTimeMillis()
            if (now - lastDescriptorTimeMs >= DESCRIPTOR_INTERVAL_MS) {
                lastDescriptorTimeMs = now
                val activeTid = state.activeFace.id
                val activeMlFace = faces.find { it.trackingId == activeTid }
                if (activeMlFace != null && abs(state.activeFace.eulerY) < 20f) {
                    val descriptor = FaceDescriptor.extract(activeMlFace)
                    if (descriptor != null) onFaceDescriptor.invoke(descriptor)
                }
            }
        }
    }

    private fun processSmile(face: TrackedFace) {
        val smile = face.smileProbability

        if (neutralSamples < NEUTRAL_SAMPLE_LIMIT && smile < 0.4f) {
            neutralBaseline = (neutralBaseline * neutralSamples + smile) / (neutralSamples + 1)
            neutralSamples++
        }

        val delta = smile - neutralBaseline
        val headOk = abs(face.eulerY) < 25f && abs(face.eulerZ) < 20f

        if (delta >= SMILE_DELTA_THRESHOLD && headOk && face.stableFrames > 5) {
            smileConsecutive++
        } else {
            smileConsecutive = (smileConsecutive - 1).coerceAtLeast(0)
        }

        if (smileConsecutive >= SMILE_CONSECUTIVE_REQUIRED) {
            smileFired = true
            onSmileConfirmed?.invoke()
        }
    }

    fun close() {
        detector.close()
    }
}
