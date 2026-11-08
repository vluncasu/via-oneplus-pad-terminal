package com.via.core.model

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.security.KeyFactory
import java.security.MessageDigest
import java.security.Signature
import java.security.interfaces.ECPublicKey
import java.security.spec.X509EncodedKeySpec
import java.util.Base64

@Serializable data class OfflineEnvelope(val kind: String, val body: String, val key: String, val signature: String)
@Serializable data class OfflineResponse(val sessionId: String, val challenge: String, val requestHash: String, val approved: Boolean, val createdAt: Long, val credential: RightCredential? = null)

/** Offline demo exchange. Keys prove possession, not bank or issuer identity. */
object OfflineQr {
    private val json = Json { encodeDefaults = true; ignoreUnknownKeys = false }
    fun message(kind: String, body: String) = "VIA2|$kind|$body".toByteArray(Charsets.UTF_8)
    fun hash(value: String) = MessageDigest.getInstance("SHA-256").digest(value.toByteArray()).joinToString("") { "%02x".format(it) }
    fun requestBody(session: ViaSession) = json.encodeToString(session)
    fun responseBody(response: OfflineResponse) = json.encodeToString(response)
    fun encode(kind: String, body: String, key: String, sign: (ByteArray) -> String): String {
        require(kind in setOf("request", "response"))
        return "VIA2:" + Base64.getUrlEncoder().withoutPadding().encodeToString(json.encodeToString(OfflineEnvelope(kind,body,key,sign(message(kind,body)))).toByteArray())
    }
    private fun envelope(raw: String, kind: String): OfflineEnvelope {
        require(raw.length in 6..10000 && raw.startsWith("VIA2:")) { "Cod VIA invalid" }
        val envelope = json.decodeFromString<OfflineEnvelope>(Base64.getUrlDecoder().decode(raw.substring(5)).toString(Charsets.UTF_8))
        require(envelope.kind == kind) { "Tip QR incorect" }
        val key = KeyFactory.getInstance("EC").generatePublic(X509EncodedKeySpec(Base64.getDecoder().decode(envelope.key))) as ECPublicKey
        require(key.params.curve.field.fieldSize == 256)
        val valid = Signature.getInstance("SHA256withECDSA").run { initVerify(key); update(message(kind,envelope.body)); verify(Base64.getDecoder().decode(envelope.signature)) }
        require(valid) { "Semnătură invalidă" }
        return envelope
    }
    fun readRequest(raw: String, now: Long): ViaSession {
        val session = json.decodeFromString<ViaSession>(envelope(raw,"request").body)
        require(session.id.isNotBlank() && session.challenge.length >= 32 && session.status == SessionStatus.CREATED)
        require(session.createdAtEpochMs <= now + 30000 && session.expiresAtEpochMs > now && session.expiresAtEpochMs - session.createdAtEpochMs in 1..180000) { "Cod expirat" }
        if (session.domain == ViaDomain.PAYMENT) require((session.amount?.amountMinor ?: 0) > 0)
        return session
    }
    fun readResponse(raw: String, request: String, now: Long): OfflineResponse {
        val session = readRequest(request, now)
        val response = json.decodeFromString<OfflineResponse>(envelope(raw,"response").body)
        require(response.sessionId == session.id && response.challenge == session.challenge && response.requestHash == hash(request)) { "Altă sesiune" }
        require(response.createdAt >= session.createdAtEpochMs - 30000 && response.createdAt <= now + 30000)
        if (response.approved && session.domain != ViaDomain.PAYMENT) {
            val credential = requireNotNull(response.credential) { "Drept lipsă" }
            require(credential.issuer == "VIA Demo Issuer" && credential.id.startsWith("demo-")) { "Doar drepturi demo" }
            require(credential.domain == session.domain && credential.type == session.requestedRightType && !credential.revoked) { "Drept incompatibil" }
            require(now in credential.validFromEpochMs until credential.validUntilEpochMs && (credential.remainingUses == null || credential.remainingUses > 0)) { "Drept expirat sau consumat" }
        }
        return response
    }
}

class EnrollmentOnce {
    private val started = java.util.concurrent.atomic.AtomicBoolean(false)
    fun beginSave() = started.compareAndSet(false, true)
    fun reset() { started.set(false) }
}

class OfflineSessionGate(private val request: String) {
    private var consumed = false
    @Synchronized fun accept(response: String, now: Long): OfflineResponse {
        check(!consumed) { "Sesiune deja consumată" }
        val verified = OfflineQr.readResponse(response, request, now)
        consumed = true
        return verified
    }
}
