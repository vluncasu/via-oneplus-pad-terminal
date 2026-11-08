package com.via.core.hardware

import org.junit.Assert.*
import org.junit.Test

class LocalConfirmationAddressTest {
    @Test fun sameSessionHasSameAdvertisementAcrossRetry() {
        assertArrayEquals(LocalConfirmationAddress.tag("session-A"), LocalConfirmationAddress.tag("session-A"))
    }
    @Test fun differentSessionChangesFilterWithoutChangingGattDatabase() {
        val service = LocalConfirmationAddress.SERVICE
        assertFalse(LocalConfirmationAddress.tag("session-A").contentEquals(LocalConfirmationAddress.tag("session-B")))
        assertEquals(4,LocalConfirmationAddress.tag("session-B").size)
        assertEquals(service,LocalConfirmationAddress.SERVICE)
    }
}
