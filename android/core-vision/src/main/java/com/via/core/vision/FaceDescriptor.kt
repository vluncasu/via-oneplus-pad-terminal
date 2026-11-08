package com.via.core.vision

import com.google.mlkit.vision.face.Face
import com.google.mlkit.vision.face.FaceLandmark
import kotlin.math.hypot
import kotlin.math.sqrt

object FaceDescriptor {

    private const val DESCRIPTOR_SIZE = 64

    fun extract(face: Face): List<Float>? {
        val landmarks = listOf(
            FaceLandmark.LEFT_EYE,
            FaceLandmark.RIGHT_EYE,
            FaceLandmark.NOSE_BASE,
            FaceLandmark.MOUTH_LEFT,
            FaceLandmark.MOUTH_RIGHT,
            FaceLandmark.MOUTH_BOTTOM,
            FaceLandmark.LEFT_EAR,
            FaceLandmark.RIGHT_EAR,
            FaceLandmark.LEFT_CHEEK,
            FaceLandmark.RIGHT_CHEEK,
        ).mapNotNull { face.getLandmark(it)?.position }

        if (landmarks.size < 8) return null

        val box = face.boundingBox
        val bw = box.width().toFloat().coerceAtLeast(1f)
        val bh = box.height().toFloat().coerceAtLeast(1f)
        val bx = box.left.toFloat()
        val by = box.top.toFloat()

        val normalized = landmarks.map { p ->
            Pair((p.x - bx) / bw, (p.y - by) / bh)
        }

        val descriptor = mutableListOf<Float>()

        for (i in normalized.indices) {
            descriptor.add(normalized[i].first)
            descriptor.add(normalized[i].second)
        }

        for (i in normalized.indices) {
            for (j in i + 1 until normalized.size) {
                val dx = normalized[i].first - normalized[j].first
                val dy = normalized[i].second - normalized[j].second
                descriptor.add(hypot(dx, dy))
                if (descriptor.size >= DESCRIPTOR_SIZE) break
            }
            if (descriptor.size >= DESCRIPTOR_SIZE) break
        }

        while (descriptor.size < DESCRIPTOR_SIZE) descriptor.add(0f)
        val trimmed = descriptor.take(DESCRIPTOR_SIZE)

        return l2Normalize(trimmed)
    }

    fun similarity(a: List<Float>, b: List<Float>): Float {
        if (a.size != b.size) return 0f
        var dot = 0f
        for (i in a.indices) dot += a[i] * b[i]
        return dot.coerceIn(0f, 1f)
    }

    private fun l2Normalize(v: List<Float>): List<Float> {
        var sum = 0f
        for (x in v) sum += x * x
        val norm = sqrt(sum).coerceAtLeast(1e-6f)
        return v.map { it / norm }
    }
}
