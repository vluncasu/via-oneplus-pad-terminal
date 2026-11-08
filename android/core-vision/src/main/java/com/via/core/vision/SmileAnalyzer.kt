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

/**
 * VIA smile pipeline.
 *
 * The smile is a voluntary confirmation gesture for an already-created VIA session.
 * It is NOT treated as standalone banking authentication or 1:N identity recognition.
 */
class SmileAnalyzer(
    private val config: Config = Config(),
    private val onFrame: (Frame) -> Unit,
    private val onConfirmed: () -> Unit,
) : ImageAnalysis.Analyzer {

    data class Config(
        val smileThreshold: Float = 0.85f,
        val neutralThreshold: Float = 0.35f,
        val requiredSmileFrames: Int = 4,
        val requiredNeutralFrames: Int = 3,
        val maxAbsHeadEulerY: Float = 24f,
        val maxAbsHeadEulerZ: Float = 18f,
        val minFaceWidthFraction: Float = 0.18f,
        val requirePassiveLiveness: Boolean = true,
    )

    data class Frame(
        val facePresent: Boolean,
        val faceQualityOk: Boolean,
        val smileProbability: Float,
        val neutralObserved: Boolean,
        val livenessObserved: Boolean,
        val confirmed: Boolean,
    )

    private val options = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
        .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
        .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_NONE)
        .setContourMode(FaceDetectorOptions.CONTOUR_MODE_NONE)
        .setMinFaceSize(0.16f)
        .enableTracking()
        .build()

    private val detector = FaceDetection.getClient(options)
    private val busy = AtomicBoolean(false)
    private var neutralFrames = 0
    private var smileFrames = 0
    private var lastEulerY: Float? = null
    private var lastEulerZ: Float? = null
    private var livenessMotion = 0f
    private var fired = false

    fun reset() {
        neutralFrames = 0
        smileFrames = 0
        lastEulerY = null
        lastEulerZ = null
        livenessMotion = 0f
        fired = false
    }

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
        detector.process(image)
            .addOnSuccessListener { faces -> process(faces.maxByOrNull { it.boundingBox.width() }, imageProxy.width) }
            .addOnFailureListener {
                onFrame(Frame(false, false, 0f, neutralFrames >= config.requiredNeutralFrames, false, false))
            }
            .addOnCompleteListener {
                busy.set(false)
                imageProxy.close()
            }
    }

    private fun process(face: Face?, frameWidth: Int) {
        if (face == null) {
            smileFrames = 0
            onFrame(Frame(false, false, 0f, neutralFrames >= config.requiredNeutralFrames, false, false))
            return
        }

        val smile = face.smilingProbability ?: 0f
        val widthFraction = face.boundingBox.width().toFloat() / frameWidth.coerceAtLeast(1)
        val quality = widthFraction >= config.minFaceWidthFraction &&
            abs(face.headEulerAngleY) <= config.maxAbsHeadEulerY &&
            abs(face.headEulerAngleZ) <= config.maxAbsHeadEulerZ

        if (quality && smile <= config.neutralThreshold) neutralFrames++ else if (smile > config.neutralThreshold) neutralFrames = (neutralFrames - 1).coerceAtLeast(0)

        val prevY = lastEulerY
        val prevZ = lastEulerZ
        if (prevY != null && prevZ != null) {
            livenessMotion += abs(face.headEulerAngleY - prevY) + abs(face.headEulerAngleZ - prevZ)
            livenessMotion = livenessMotion.coerceAtMost(30f)
        }
        lastEulerY = face.headEulerAngleY
        lastEulerZ = face.headEulerAngleZ

        val neutralObserved = neutralFrames >= config.requiredNeutralFrames
        val livenessObserved = !config.requirePassiveLiveness || livenessMotion >= 1.5f
        val eligible = quality && neutralObserved && livenessObserved

        if (eligible && smile >= config.smileThreshold) smileFrames++ else smileFrames = 0
        val confirmed = smileFrames >= config.requiredSmileFrames

        onFrame(Frame(true, quality, smile, neutralObserved, livenessObserved, confirmed))
        if (confirmed && !fired) {
            fired = true
            onConfirmed()
        }
    }

    fun close() = detector.close()
}
