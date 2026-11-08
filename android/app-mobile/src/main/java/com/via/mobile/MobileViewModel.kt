package com.via.mobile

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.via.core.crypto.DeviceIdentity
import com.via.core.crypto.MasterSecret
import com.via.core.crypto.ViaCanonical
import com.via.core.model.*
import com.via.core.network.ViaApiClient
import com.via.core.storage.ViaStorage
import com.via.core.vision.PalmDescriptor
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

class MobileViewModel(app: Application) : AndroidViewModel(app) {
    enum class Screen { HOME, WALLET, SCAN, SETTINGS, SESSION, PALM_ENROLL }

    data class UiState(
        val screen: Screen = Screen.HOME,
        val credentials: List<RightCredential> = emptyList(),
        val session: ViaSession? = null,
        val message: String? = null,
        val responseQr: String? = null,
        val delivered: Boolean = false,
        val busy: Boolean = false,
        val palmEnabled: Boolean = false,
        val smileEnabled: Boolean = true,
        val viaLightEnabled: Boolean = true,
        val palmEnrollProgress: Float = 0f,
        val palmTemplate: List<Float>? = null,
        val backendUrl: String = "http://10.0.2.2:8787",
    )

    private val storage = ViaStorage(app)
    private val identity = DeviceIdentity("via_mobile_identity_v1")
    private val master = MasterSecret("via_mobile_master_v1")
    private val localSender = com.via.core.hardware.LocalConfirmationSender(app)
    private var confirmationJob: kotlinx.coroutines.Job? = null
    private var operationGeneration = 0L
    private var requestQr: String? = null
    private var issuedResponses: Map<String, String> = emptyMap()
    private var ready = false
    private val _ui = MutableStateFlow(UiState())
    val ui: StateFlow<UiState> = _ui

    init {
        viewModelScope.launch {
            val existing = storage.credentials.first()
            val credentials = if (existing.isEmpty()) seedDemoCredentials() else {
                val now = System.currentTimeMillis()
                val withBenefits = if (existing.none { it.id == "demo-benefit" }) existing + RightCredential("demo-benefit", "VIA Demo Issuer", ViaDomain.BENEFIT, "", "benefit", mapOf("label" to "Voucher demo"), now - 60000, now + 7L * 86400000, 100) else existing
                storage.saveCredentials(withBenefits)
                withBenefits
            }
            issuedResponses = storage.offlineResponses.first()
            val palm = storage.palmTemplate.first()
            _ui.value = _ui.value.copy(
                credentials = credentials,
                palmTemplate = palm,
                palmEnabled = storage.palmEnabled.first(),
                smileEnabled = storage.smileEnabled.first(),
                viaLightEnabled = storage.viaLightEnabled.first(),
            )
            ready = true
        }
    }

    fun goBack() {
        confirmationJob?.cancel()
        confirmationJob = null
        operationGeneration++
        requestQr = null
        val target = backDestination(_ui.value.screen)
        _ui.value = _ui.value.copy(screen = target, busy = false, session = null, responseQr = null, delivered = false, message = null)
    }
    fun navigate(screen: Screen) { if (_ui.value.busy) return; _ui.value = _ui.value.copy(screen = screen, message = null) }
    companion object {
        internal fun backDestination(screen: Screen) = if (screen == Screen.PALM_ENROLL) Screen.SETTINGS else Screen.HOME
    }

    fun handleUri(uri: Uri?) { if (uri != null) _ui.value = _ui.value.copy(message = "Folosește codul VIA local al tabletei") }

    fun handleScannedPayload(payload: String) {
        if (!ready || _ui.value.busy) return
        try {
            val session = OfflineQr.readRequest(payload, System.currentTimeMillis())
            requestQr = payload
            _ui.value = _ui.value.copy(screen = Screen.SESSION, session = session, responseQr = issuedResponses[session.id], delivered = false, message = null)
            confirmPhone()
        } catch (_: Exception) { _ui.value = _ui.value.copy(message = "Cod invalid sau expirat") }
    }

    fun confirmPhone() {
        val session = _ui.value.session ?: return
        val request = requestQr ?: return
        if (_ui.value.busy || _ui.value.delivered) return
        val generation = ++operationGeneration
        _ui.value = _ui.value.copy(busy = true)
        confirmationJob = viewModelScope.launch {
            try {
                OfflineQr.readRequest(request, System.currentTimeMillis())
                issuedResponses = storage.offlineResponses.first()
                if (generation != operationGeneration) return@launch
                val existingResponse = issuedResponses[session.id]
                if (existingResponse != null) {
                    _ui.value = _ui.value.copy(message = "Se conectează la tabletă…")
                    localSender.send(session.id, existingResponse)
                    if (generation == operationGeneration) _ui.value = _ui.value.copy(delivered = true, message = "Confirmat pe tabletă")
                    return@launch
                }
                val credential = if (session.domain == ViaDomain.PAYMENT) null else bestCredentialFor(session) ?: error("Nu există un drept compatibil")
                val response = OfflineResponse(session.id, session.challenge, OfflineQr.hash(request), true, System.currentTimeMillis(), credential)
                val qr = OfflineQr.encode("response", OfflineQr.responseBody(response), identity.publicKeySpkiBase64(), identity::sign)
                val updated = _ui.value.credentials.map { if (it.id == credential?.id && it.remainingUses != null) it.copy(remainingUses = (it.remainingUses ?: 1) - 1) else it }
                // Commit the signed answer and the use counter together, before showing a scannable response.
                storage.saveOfflineApproval(updated, session.id, qr)
                if (generation != operationGeneration) return@launch
                issuedResponses = issuedResponses + (session.id to qr)
                _ui.value = _ui.value.copy(credentials = updated, responseQr = qr, message = "Se conectează la tabletă…")
                localSender.send(session.id, qr)
                if (generation == operationGeneration) _ui.value = _ui.value.copy(delivered = true, message = "Confirmat pe tabletă")
            } catch (_: kotlinx.coroutines.TimeoutCancellationException) { if (generation == operationGeneration) _ui.value = _ui.value.copy(message = "Conectarea a durat prea mult. Activează Bluetooth pe tabletă și reîncearcă.")
            } catch (e: kotlinx.coroutines.CancellationException) { throw e
            } catch (_: Exception) { if (generation == operationGeneration) _ui.value = _ui.value.copy(message = "Nu s-a confirmat. Activează Bluetooth pe ambele dispozitive, permite Dispozitive din apropiere și reîncearcă.")
            } finally { if (generation == operationGeneration) _ui.value = _ui.value.copy(busy = false) }
        }
    }

    fun verifyPalmForSession() { _ui.value = _ui.value.copy(message = "Confirmă cererea și arată codul tabletei") }

    fun savePalmTemplate(template: List<Float>) {
        viewModelScope.launch {
            storage.savePalmTemplate(template)
            _ui.value = _ui.value.copy(palmTemplate = template, palmEnabled = true, palmEnrollProgress = 1f, message = "Palmă adăugată")
        }
    }

    fun setPalmProgress(progress: Float) { _ui.value = _ui.value.copy(palmEnrollProgress = progress) }
    fun clearPalm() { viewModelScope.launch { storage.savePalmTemplate(null); _ui.value = _ui.value.copy(palmTemplate = null, palmEnabled = false, message = "Palma a fost ștearsă") } }
    fun setViaLight(value: Boolean) { viewModelScope.launch { storage.setViaLightEnabled(value); _ui.value = _ui.value.copy(viaLightEnabled = value) } }
    fun setSmile(value: Boolean) { viewModelScope.launch { storage.setSmileEnabled(value); _ui.value = _ui.value.copy(smileEnabled = value) } }

    private fun bestCredentialFor(session: ViaSession): RightCredential? {
        val now = System.currentTimeMillis()
        return _ui.value.credentials.firstOrNull {
            val uses = it.remainingUses
            it.domain == session.domain && (session.requestedRightType == null || it.type == session.requestedRightType) && !it.revoked && it.validFromEpochMs <= now && it.validUntilEpochMs >= now && (uses == null || uses > 0)
        }
    }

    private suspend fun seedDemoCredentials(): List<RightCredential> {
        val now = System.currentTimeMillis()
        val list = listOf(
            RightCredential("demo-transport", "VIA Demo Issuer", ViaDomain.TRANSPORT, "", "transport_pass", mapOf("label" to "Abonament 30 zile"), now - 60_000, now + 30L * 24 * 3600 * 1000, null),
            RightCredential("demo-parking", "VIA Demo Issuer", ViaDomain.PARKING, "", "parking_right", mapOf("label" to "2 ore parcare"), now - 60_000, now + 7L * 24 * 3600 * 1000, 20),
            RightCredential("demo-access", "VIA Demo Issuer", ViaDomain.ACCESS, "", "access_pass", mapOf("label" to "TECHALLENGE"), now - 60_000, now + 7L * 24 * 3600 * 1000, 100),
        )
        val complete = list + RightCredential("demo-benefit", "VIA Demo Issuer", ViaDomain.BENEFIT, "", "benefit", mapOf("label" to "Voucher demo"), now - 60000, now + 7L * 24 * 3600 * 1000, 100)
        storage.saveCredentials(complete)
        return complete
    }
}
