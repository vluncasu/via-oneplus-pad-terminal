package com.via.core.vision

import kotlin.math.abs
import kotlin.math.hypot
import kotlin.math.max

data class TrackedFace(
    val id: Int,
    val centerX: Float,
    val centerY: Float,
    val width: Float,
    val height: Float,
    val smileProbability: Float,
    val eulerY: Float,
    val eulerZ: Float,
    val confidence: Float,
    val stableFrames: Int,
    val lastSeenFrame: Long,
)

data class FramingState(
    val faces: List<TrackedFace>,
    val activeFace: TrackedFace?,
    val targetCenterX: Float,
    val targetCenterY: Float,
    val targetZoom: Float,
    val groupMode: Boolean,
)

class FaceTracker {

    private val tracked = mutableMapOf<Int, TrackedFace>()
    private var activeFaceId: Int? = null
    private var frameCount = 0L
    private var switchCooldown = 0

    private var smoothCenterX = 0.5f
    private var smoothCenterY = 0.5f
    private var smoothZoom = 1.0f
    private var velX = 0f
    private var velY = 0f
    private var velZoom = 0f
    private var lastUpdateNanos = 0L

    companion object {
        private const val LOST_THRESHOLD = 15
        private const val SWITCH_COOLDOWN_FRAMES = 20
        private const val MIN_ZOOM = 1.0f
        private const val MAX_ZOOM = 2.8f
        private const val IDEAL_FACE_FRACTION = 0.28f
        private const val GROUP_DISTANCE_THRESHOLD = 0.4f
        private const val SPRING_STIFFNESS = 120f
        private const val SPRING_DAMPING = 22f
        private const val ZOOM_STIFFNESS = 60f
        private const val ZOOM_DAMPING = 16f
    }

    fun update(rawFaces: List<RawFace>): FramingState {
        frameCount++
        if (switchCooldown > 0) switchCooldown--

        for (raw in rawFaces) {
            val existing = tracked[raw.trackingId]
            if (existing != null) {
                tracked[raw.trackingId] = existing.copy(
                    centerX = raw.centerX,
                    centerY = raw.centerY,
                    width = raw.width,
                    height = raw.height,
                    smileProbability = raw.smileProbability,
                    eulerY = raw.eulerY,
                    eulerZ = raw.eulerZ,
                    confidence = raw.confidence,
                    stableFrames = existing.stableFrames + 1,
                    lastSeenFrame = frameCount,
                )
            } else {
                tracked[raw.trackingId] = TrackedFace(
                    id = raw.trackingId,
                    centerX = raw.centerX,
                    centerY = raw.centerY,
                    width = raw.width,
                    height = raw.height,
                    smileProbability = raw.smileProbability,
                    eulerY = raw.eulerY,
                    eulerZ = raw.eulerZ,
                    confidence = raw.confidence,
                    stableFrames = 1,
                    lastSeenFrame = frameCount,
                )
            }
        }

        tracked.entries.removeAll { (frameCount - it.value.lastSeenFrame) > LOST_THRESHOLD }

        val faces = tracked.values.toList()
        val groupMode = isGroupMode(faces)
        val active = selectActiveFace(faces)
        activeFaceId = active?.id

        val (targetX, targetY, targetZoom) = computeFraming(faces, active, groupMode)

        val now = System.nanoTime()
        val dt = if (lastUpdateNanos == 0L) 0.033f else ((now - lastUpdateNanos) / 1_000_000_000f).coerceIn(0.001f, 0.1f)
        lastUpdateNanos = now

        val (newX, newVelX) = springStep(smoothCenterX, velX, targetX, SPRING_STIFFNESS, SPRING_DAMPING, dt)
        val (newY, newVelY) = springStep(smoothCenterY, velY, targetY, SPRING_STIFFNESS, SPRING_DAMPING, dt)
        val (newZ, newVelZ) = springStep(smoothZoom, velZoom, targetZoom, ZOOM_STIFFNESS, ZOOM_DAMPING, dt)
        smoothCenterX = newX; velX = newVelX
        smoothCenterY = newY; velY = newVelY
        val clampedZoom = newZ.coerceIn(MIN_ZOOM, MAX_ZOOM)
        if (clampedZoom != newZ) velZoom = 0f else velZoom = newVelZ
        smoothZoom = clampedZoom

        return FramingState(
            faces = faces,
            activeFace = active,
            targetCenterX = smoothCenterX,
            targetCenterY = smoothCenterY,
            targetZoom = smoothZoom,
            groupMode = groupMode,
        )
    }

    fun reset() {
        tracked.clear()
        activeFaceId = null
        frameCount = 0
        switchCooldown = 0
        smoothCenterX = 0.5f
        smoothCenterY = 0.5f
        smoothZoom = 1.0f
        velX = 0f; velY = 0f; velZoom = 0f
        lastUpdateNanos = 0L
    }

    private fun springStep(pos: Float, vel: Float, target: Float, stiffness: Float, damping: Float, dt: Float): Pair<Float, Float> {
        val displacement = pos - target
        val springForce = -stiffness * displacement
        val dampForce = -damping * vel
        val accel = springForce + dampForce
        val newVel = vel + accel * dt
        val newPos = pos + newVel * dt
        return newPos to newVel
    }

    private fun selectActiveFace(faces: List<TrackedFace>): TrackedFace? {
        if (faces.isEmpty()) return null
        if (faces.size == 1) return faces[0]

        val current = activeFaceId?.let { id -> faces.find { it.id == id } }
        if (current != null && switchCooldown > 0) return current

        val scored = faces.map { face ->
            val sizeScore = face.width * 2.0f
            val centerScore = 1.0f - abs(face.centerX - 0.5f) * 2.0f
            val stabilityScore = (face.stableFrames / 30f).coerceAtMost(1f)
            val currentBonus = if (face.id == activeFaceId) 0.3f else 0f
            face to (sizeScore + centerScore + stabilityScore + currentBonus)
        }

        val best = scored.maxByOrNull { it.second }?.first
        if (best != null && best.id != activeFaceId) {
            switchCooldown = SWITCH_COOLDOWN_FRAMES
        }
        return best
    }

    private fun isGroupMode(faces: List<TrackedFace>): Boolean {
        if (faces.size < 2) return false
        for (i in faces.indices) {
            for (j in i + 1 until faces.size) {
                val dist = hypot(
                    faces[i].centerX - faces[j].centerX,
                    faces[i].centerY - faces[j].centerY
                )
                if (dist < GROUP_DISTANCE_THRESHOLD) return true
            }
        }
        return false
    }

    private fun computeFraming(
        faces: List<TrackedFace>,
        active: TrackedFace?,
        groupMode: Boolean,
    ): Triple<Float, Float, Float> {
        if (faces.isEmpty() || active == null) {
            return Triple(0.5f, 0.5f, MIN_ZOOM)
        }

        if (groupMode && faces.size > 1) {
            var minX = 1f; var maxX = 0f; var minY = 1f; var maxY = 0f
            for (f in faces) {
                minX = minOf(minX, f.centerX - f.width / 2)
                maxX = maxOf(maxX, f.centerX + f.width / 2)
                minY = minOf(minY, f.centerY - f.height / 2)
                maxY = maxOf(maxY, f.centerY + f.height / 2)
            }
            val cx = (minX + maxX) / 2
            val cy = (minY + maxY) / 2
            val span = max(maxX - minX, maxY - minY)
            val zoom = (IDEAL_FACE_FRACTION / span.coerceAtLeast(0.1f)).coerceIn(MIN_ZOOM, 1.8f)
            return Triple(cx, cy, zoom)
        }

        val zoom = (IDEAL_FACE_FRACTION / active.width.coerceAtLeast(0.05f))
            .coerceIn(MIN_ZOOM, MAX_ZOOM)
        return Triple(active.centerX, active.centerY, zoom)
    }
}

data class RawFace(
    val trackingId: Int,
    val centerX: Float,
    val centerY: Float,
    val width: Float,
    val height: Float,
    val smileProbability: Float,
    val eulerY: Float,
    val eulerZ: Float,
    val confidence: Float,
)
