package com.via.core.hardware

import org.junit.Assert.*
import org.junit.Test

class ReceiverAttemptsTest {
    @Test fun bluetoothOffAndRetryInvalidateOldQueuedCallbacks() {
        val attempts = ReceiverAttempts()
        val beforeOff = attempts.current
        attempts.invalidate() // Bluetooth OFF closes the original GATT server.
        assertFalse(attempts.isCurrent(beforeOff))
        val whileOff = attempts.current
        attempts.invalidate() // Retry opens a new GATT server after Bluetooth ON.
        assertFalse(attempts.isCurrent(whileOff))
        assertTrue(attempts.isCurrent(attempts.current))
    }
    @Test fun closingOrSecondRetryCannotAcceptPreviousReadyEvent() {
        val attempts = ReceiverAttempts()
        val firstRetry = attempts.current
        repeat(3) { attempts.invalidate() }
        assertFalse(attempts.isCurrent(firstRetry))
        val active = attempts.current
        assertTrue(attempts.isCurrent(active))
        attempts.invalidate()
        assertFalse(attempts.isCurrent(active))
    }
}
