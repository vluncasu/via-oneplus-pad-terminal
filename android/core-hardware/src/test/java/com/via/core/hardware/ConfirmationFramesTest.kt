package com.via.core.hardware

import org.junit.Assert.*
import org.junit.Test

class ConfirmationFramesTest {
    @Test fun responseSurvivesAnyBleFragmentSize() {
        val payload = "VIA2:" + "signedResponse123_-".repeat(200)
        listOf(1, 20, 182, 244, 512).forEach { size ->
            val frames = ConfirmationFrames()
            val parts = (payload + "\n").chunked(size)
            parts.forEachIndexed { index, value ->
                val result = frames.append(value.toByteArray())
                if (index == parts.lastIndex) assertEquals(payload, result) else assertNull(result)
            }
        }
    }
    @Test fun rejectsOversizedAndMalformedBoundaries() {
        assertTrue(runCatching { ConfirmationFrames().append("a".repeat(10002).toByteArray()) }.isFailure)
        assertTrue(runCatching { ConfirmationFrames().append("one\ntwo\n".toByteArray()) }.isFailure)
        assertTrue(runCatching { ConfirmationFrames().append(byteArrayOf(0)) }.isFailure)
    }
    @Test fun phonesHaveIndependentFrames() {
        val a = ConfirmationFrames(); val b = ConfirmationFrames()
        assertNull(a.append("A".toByteArray())); assertNull(b.append("B".toByteArray()))
        assertEquals("A1",a.append("1\n".toByteArray()))
        assertEquals("B2",b.append("2\n".toByteArray()))
    }
}
