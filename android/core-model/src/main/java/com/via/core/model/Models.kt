package com.via.core.model

import kotlinx.serialization.Serializable

@Serializable
enum class ViaDomain { PAYMENT, TRANSPORT, PARKING, ACCESS, BENEFIT }

@Serializable
enum class ConfirmationMethod { SMILE, PALM, PHONE, NFC, QR, PIN }

@Serializable
enum class SessionStatus { CREATED, PAIRED, PRESENTED, CONFIRMED, DENIED, EXPIRED, CONSUMED }

@Serializable
data class Money(val amountMinor: Long, val currency: String = "RON") {
    val display: String get() = "%.2f %s".format(amountMinor / 100.0, currency)
}

@Serializable
data class PaymentRequest(
    val requestId: String,
    val merchantId: String,
    val merchantName: String,
    val total: Money,
    val createdAtEpochMs: Long,
    val expiresAtEpochMs: Long,
)

@Serializable
data class ValidationRequest(
    val requestId: String,
    val domain: ViaDomain,
    val operatorId: String,
    val operatorName: String,
    val requestedRightType: String,
    val createdAtEpochMs: Long,
    val expiresAtEpochMs: Long,
)

@Serializable
data class ViaSession(
    val id: String,
    val challenge: String,
    val domain: ViaDomain,
    val operatorId: String,
    val operatorName: String,
    val amount: Money? = null,
    val requestedRightType: String? = null,
    val createdAtEpochMs: Long,
    val expiresAtEpochMs: Long,
    val status: SessionStatus = SessionStatus.CREATED,
    val presentationRequired: Boolean = domain != ViaDomain.PAYMENT,
)

@Serializable
data class SessionCreateRequest(
    val domain: ViaDomain,
    val operatorId: String,
    val operatorName: String,
    val amount: Money? = null,
    val requestedRightType: String? = null,
    val ttlSeconds: Int = 90,
)

@Serializable
data class SessionConfirmation(
    val sessionId: String,
    val challenge: String,
    val approved: Boolean,
    val method: ConfirmationMethod,
    val scopedSubject: String,
    val publicKeySpkiBase64: String,
    val signatureDerBase64: String,
)

@Serializable
data class RightCredential(
    val id: String,
    val issuer: String,
    val domain: ViaDomain,
    val scopedSubject: String,
    val type: String,
    val claims: Map<String, String> = emptyMap(),
    val validFromEpochMs: Long,
    val validUntilEpochMs: Long,
    val remainingUses: Int? = null,
    val revoked: Boolean = false,
    val signature: String? = null,
)

@Serializable
data class CredentialPresentation(
    val sessionId: String,
    val challenge: String,
    val credential: RightCredential,
    val scopedSubject: String,
    val publicKeySpkiBase64: String,
    val signatureDerBase64: String,
)

@Serializable
data class PresentationResult(
    val accepted: Boolean,
    val reason: String? = null,
    val remainingUses: Int? = null,
)

@Serializable
data class PalmProbe(
    val sessionId: String,
    val descriptorVersion: Int = 1,
    val descriptor: List<Float>,
    val createdAtEpochMs: Long,
)

@Serializable
data class PalmDecision(
    val sessionId: String,
    val accepted: Boolean,
    val similarity: Float,
    val threshold: Float,
)

@Serializable
data class ApiMessage(val ok: Boolean, val message: String? = null)

@Serializable
data class TerminalConfig(
    val backendBaseUrl: String = "http://10.0.2.2:8787",
    val terminalId: String = "VIA-01",
    val operatorId: String = "demo.operator",
    val operatorName: String = "VIA Demo Store",
    val demoAmountMinor: Long = 2490,
    val ledEnabled: Boolean = true,
)

@Serializable
data class WalletState(
    val credentials: List<RightCredential> = emptyList(),
    val biometricPalmEnabled: Boolean = false,
    val biometricSmileEnabled: Boolean = true,
    val viaLightEnabled: Boolean = true,
)

@Serializable
data class FaceProfile(
    val id: String,
    val displayName: String,
    val embedding: List<Float>,
    val palmEmbedding: List<Float> = emptyList(),
    val createdAtEpochMs: Long,
    val preferredAction: String = "pay",
)

@Serializable
data class TerminalEvent(
    val type: String,
    val sessionId: String? = null,
    val status: SessionStatus? = null,
    val method: ConfirmationMethod? = null,
    val domain: ViaDomain? = null,
    val accepted: Boolean? = null,
    val similarity: Float? = null,
    val message: String? = null,
)
