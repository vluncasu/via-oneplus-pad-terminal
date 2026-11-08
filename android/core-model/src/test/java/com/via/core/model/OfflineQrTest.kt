package com.via.core.model

import java.security.KeyPairGenerator
import java.security.Signature
import java.util.Base64
import java.util.concurrent.Executors
import java.util.concurrent.Callable
import org.junit.Assert.*
import org.junit.Test

class OfflineQrTest {
    private val now = 1000000L
    private val pair = KeyPairGenerator.getInstance("EC").apply { initialize(256) }.generateKeyPair()
    private val key = Base64.getEncoder().encodeToString(pair.public.encoded)
    private fun sign(bytes: ByteArray) = Base64.getEncoder().encodeToString(Signature.getInstance("SHA256withECDSA").run { initSign(pair.private); update(bytes); sign() })
    private fun session(domain: ViaDomain = ViaDomain.PAYMENT) = ViaSession("id", "a".repeat(36), domain, "demo", "VIA", if (domain == ViaDomain.PAYMENT) Money(2490) else null, when(domain) { ViaDomain.TRANSPORT -> "transport_pass"; ViaDomain.ACCESS -> "access_pass"; ViaDomain.PARKING -> "parking_right"; ViaDomain.BENEFIT -> "benefit"; else -> null }, now, now + 180000)
    private fun request(s: ViaSession) = OfflineQr.encode("request", OfflineQr.requestBody(s), key, ::sign)
    private fun reply(s: ViaSession, request: String, credential: RightCredential? = null, approved: Boolean = true) = OfflineQr.encode("response", OfflineQr.responseBody(OfflineResponse(s.id, s.challenge, OfflineQr.hash(request), approved, now + 100, credential)), key, ::sign)
    private fun rejected(block: () -> Unit) { assertTrue(runCatching(block).isFailure) }
    @Test fun paymentNeedsValidResponseAndCanOnlyFinishOnce() {
        val s = session(); val qr = request(s); val gate = OfflineSessionGate(qr)
        rejected { gate.accept(qr, now + 100) } // Scanning the request cannot confirm itself.
        val response = reply(s, qr)
        assertTrue(gate.accept(response, now + 100).approved)
        rejected { gate.accept(response, now + 101) }
    }
    @Test fun signedResponseWorksForEachService() {
        ViaDomain.entries.filter { it != ViaDomain.PAYMENT }.forEach { domain ->
            val s = session(domain); val qr = request(s)
            val credential = RightCredential("demo-${domain.name}", "VIA Demo Issuer", domain, "", s.requestedRightType!!, emptyMap(), now - 1000, now + 86400000, 1)
            assertTrue(OfflineSessionGate(qr).accept(reply(s, qr, credential), now + 100).approved)
            rejected { OfflineSessionGate(qr).accept(reply(s, qr, credential.copy(remainingUses = 0)), now + 100) }
            rejected { OfflineSessionGate(qr).accept(reply(s, qr, credential.copy(revoked = true)), now + 100) }
            rejected { OfflineSessionGate(qr).accept(reply(s, qr, credential.copy(type = "wrong")), now + 100) }
            rejected { OfflineSessionGate(qr).accept(reply(s, qr, credential.copy(validUntilEpochMs = now)), now + 100) }
        }
    }
    @Test fun rejectsOldCodesWrongChallengeWrongSessionAndMalformed() {
        val s = session(); val qr = request(s)
        rejected { OfflineQr.readRequest(qr, s.expiresAtEpochMs) }
        rejected { OfflineSessionGate(qr).accept(reply(s.copy(id = "other"), qr), now + 100) }
        rejected { OfflineSessionGate(qr).accept(reply(s.copy(challenge = "b".repeat(36)), qr), now + 100) }
        rejected { OfflineSessionGate(qr).accept(reply(s, request(s.copy(id = "other"))), now + 100) }
        rejected { OfflineSessionGate(qr).accept("not VIA", now + 100) }
        rejected { OfflineSessionGate(qr).accept(reply(s, qr).dropLast(15), now + 100) }
        rejected { OfflineQr.readRequest("VIA2:" + "a".repeat(10000), now) }
    }
    @Test fun rejectsModifiedSignedBody() {
        val s = session(); val body = OfflineQr.requestBody(s)
        val signature = sign(OfflineQr.message("request",body))
        val invalid = OfflineQr.encode("request", OfflineQr.requestBody(s.copy(amount = Money(9999))), key) { signature }
        rejected { OfflineQr.readRequest(invalid, now) }
    }
    @Test fun refusalIsNotSuccessAndCannotBeReplayed() {
        val s = session(); val qr = request(s); val gate = OfflineSessionGate(qr)
        assertFalse(gate.accept(reply(s, qr, approved = false), now + 100).approved)
        rejected { gate.accept(reply(s, qr), now + 101) }
    }
    @Test fun bothDirectionsFitRealQrAndDecode() {
        val s = session(ViaDomain.BENEFIT); val request = request(s)
        val credential = RightCredential("demo-benefit", "VIA Demo Issuer", ViaDomain.BENEFIT, "", "benefit", mapOf("label" to "Voucher demo"), now - 1000, now + 86400000, 100)
        val response = reply(s, request, credential)
        listOf(request, response).forEach { value ->
            val matrix = com.google.zxing.qrcode.QRCodeWriter().encode(value, com.google.zxing.BarcodeFormat.QR_CODE, 300, 300, mapOf(com.google.zxing.EncodeHintType.MARGIN to 4))
            val pixels = IntArray(matrix.width * matrix.height) { i -> if (matrix[i % matrix.width, i / matrix.width]) 0xff000000.toInt() else 0xffffffff.toInt() }
            val bitmap = com.google.zxing.BinaryBitmap(com.google.zxing.common.HybridBinarizer(com.google.zxing.RGBLuminanceSource(matrix.width,matrix.height,pixels)))
            assertEquals(value, com.google.zxing.qrcode.QRCodeReader().decode(bitmap).text)
        }
    }
    @Test fun manyPalmFramesClaimOnlyOneProfileSave() {
        val gate = EnrollmentOnce(); val pool = Executors.newFixedThreadPool(8)
        try { assertEquals(1, pool.invokeAll((1..100).map { Callable { gate.beginSave() } }).count { it.get() }) }
        finally { pool.shutdownNow() }
        gate.reset(); assertTrue(gate.beginSave()); assertFalse(gate.beginSave())
    }
}
