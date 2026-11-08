package com.via.core.vision

import com.google.mediapipe.tasks.components.containers.NormalizedLandmark
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sqrt
import kotlin.math.sin

/** Versioned geometric palm/hand descriptor. It is used only for 1:1 verification. */
object PalmDescriptor {
    const val VERSION = 1
    const val SIZE = 84

    fun fromLandmarks(points: List<NormalizedLandmark>): List<Float> {
        require(points.size >= 21) { "21 hand landmarks required" }
        val wrist = points[0]
        val middleMcp = points[9]
        val dx = middleMcp.x() - wrist.x()
        val dy = middleMcp.y() - wrist.y()
        val angle = atan2(dy, dx) - (-Math.PI / 2.0).toFloat()
        val c = cos(-angle)
        val s = sin(-angle)

        val palmScale = distance(points[0], points[9]).coerceAtLeast(0.02f)
        val xyz = ArrayList<Float>(63)
        val radial = ArrayList<Float>(21)

        points.take(21).forEach { p ->
            val tx = (p.x() - wrist.x()) / palmScale
            val ty = (p.y() - wrist.y()) / palmScale
            val rx = tx * c - ty * s
            val ry = tx * s + ty * c
            val rz = (p.z() - wrist.z()) / palmScale
            xyz += rx
            xyz += ry
            xyz += rz
            radial += sqrt(rx * rx + ry * ry + rz * rz)
        }
        return l2Normalize(xyz + radial)
    }

    fun cosine(a: List<Float>, b: List<Float>): Float {
        require(a.size == b.size && a.isNotEmpty())
        var dot = 0f
        var aa = 0f
        var bb = 0f
        for (i in a.indices) {
            dot += a[i] * b[i]
            aa += a[i] * a[i]
            bb += b[i] * b[i]
        }
        return dot / (sqrt(aa) * sqrt(bb)).coerceAtLeast(1e-8f)
    }

    private fun distance(a: NormalizedLandmark, b: NormalizedLandmark): Float {
        val dx = a.x() - b.x(); val dy = a.y() - b.y(); val dz = a.z() - b.z()
        return sqrt(dx * dx + dy * dy + dz * dz)
    }

    private fun l2Normalize(input: List<Float>): List<Float> {
        val n = sqrt(input.sumOf { (it * it).toDouble() }).toFloat().coerceAtLeast(1e-8f)
        return input.map { it / n }
    }
}

class PalmEnrollmentAccumulator(
    private val targetFrames: Int = 8,
    private val maxAdjacentDistance: Float = 0.20f,
) {
    private val frames = mutableListOf<List<Float>>()

    fun reset() = frames.clear()
    val progress: Float get() = (frames.size.toFloat() / targetFrames).coerceIn(0f, 1f)
    val ready: Boolean get() = frames.size >= targetFrames

    fun offer(descriptor: List<Float>): Boolean {
        if (descriptor.size != PalmDescriptor.SIZE) return false
        val previous = frames.lastOrNull()
        if (previous != null && PalmDescriptor.cosine(previous, descriptor) < (1f - maxAdjacentDistance)) return false
        frames += descriptor
        return true
    }

    fun template(): List<Float> {
        require(ready)
        val mean = MutableList(PalmDescriptor.SIZE) { 0f }
        frames.take(targetFrames).forEach { f -> for (i in mean.indices) mean[i] += f[i] }
        for (i in mean.indices) mean[i] /= targetFrames
        val norm = sqrt(mean.sumOf { (it * it).toDouble() }).toFloat().coerceAtLeast(1e-8f)
        return mean.map { it / norm }
    }
}
