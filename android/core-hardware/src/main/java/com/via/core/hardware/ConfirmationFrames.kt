package com.via.core.hardware

/** Bounded frame assembler for an ASCII signed response split across BLE writes. */
internal class ConfirmationFrames {
    private val data = StringBuilder()
    fun append(packet: ByteArray): String? {
        require(packet.isNotEmpty() && packet.all { it.toInt() in 10..126 && (it.toInt() >= 32 || it.toInt() == 10) })
        data.append(packet.toString(Charsets.US_ASCII))
        require(data.length <= 10001) { "Response too large" }
        val end = data.indexOf("\n")
        if (end < 0) return null
        require(end == data.lastIndex && end > 0) { "Invalid frame boundary" }
        return data.substring(0, end)
    }
}
