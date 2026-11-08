package com.via.core.hardware

import java.util.UUID
import java.security.MessageDigest

/** Keep the GATT database stable for Android caching; choose the session in the advertisement. */
internal object LocalConfirmationAddress {
    val SERVICE: UUID = UUID.fromString("f8911568-6f70-4f20-8c72-1c98bf1be780")
    const val MANUFACTURER = 0xffff // Bluetooth testing identifier, used by this demo only.
    fun tag(sessionId: String): ByteArray = MessageDigest.getInstance("SHA-256").digest(sessionId.toByteArray(Charsets.UTF_8)).copyOf(4)
}
