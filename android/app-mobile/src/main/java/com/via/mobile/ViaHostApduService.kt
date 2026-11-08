package com.via.mobile

import android.nfc.cardemulation.HostApduService
import android.os.Bundle

class ViaHostApduService : HostApduService() {
    private val ok = byteArrayOf(0x90.toByte(), 0x00)
    override fun processCommandApdu(commandApdu: ByteArray?, extras: Bundle?): ByteArray {
        if (commandApdu == null) return byteArrayOf(0x6F, 0x00)
        val payload = HcePayload.current.encodeToByteArray()
        return payload + ok
    }
    override fun onDeactivated(reason: Int) = Unit
}
