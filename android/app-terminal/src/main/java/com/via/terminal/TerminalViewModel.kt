package com.via.terminal

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.via.core.crypto.DeviceIdentity
import com.via.core.crypto.MasterSecret
import com.via.core.crypto.ViaCanonical
import com.via.core.hardware.ViaBleController
import com.via.core.model.*
import com.via.core.network.ViaApiClient
import com.via.core.storage.ViaStorage
import com.via.core.vision.FaceDescriptor
import com.via.core.vision.FramingState
import com.via.core.vision.TrackedFace
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.util.UUID

class TerminalViewModel(app: Application) : AndroidViewModel(app) {
    enum class Screen {
        HOME, PAY, VALIDATE, DOWNLOAD,
        SMILE, PALM, PHONE, TAP,
        ENROLL, PALM_ENROLL, PRESENTATION, ENGINEERING
    }

    enum class ResultKind { SUCCESS, ERROR }
    enum class SetupStep { FACE, SMILE, PALM, DONE }

    data class UiState(
        val screen: Screen = Screen.HOME,
        val merchant: String = "VIA Demo Store",
        val amountMinor: Long = 2490,
        val currency: String = "RON",
        val validationDomain: ViaDomain = ViaDomain.TRANSPORT,
        val currentSession: ViaSession? = null,
        val resultTitle: String? = null,
        val resultSubtitle: String? = null,
        val resultKind: ResultKind = ResultKind.SUCCESS,
        val qrRequest: String? = null,
        val qrScanning: Boolean = false,
        val qrError: String? = null,
        val qrConnecting: Boolean = false,
        val profiles: List<FaceProfile> = emptyList(),
        val enteringProfileName: Boolean = false,
        val backendAvailable: Boolean = false,
        val downloadUrl: String = "http://10.0.2.2:8787/download",
        // Smart Camera
        val faceCount: Int = 0,
        val activeFaceName: String? = null,
        val recognizedProfile: FaceProfile? = null,
        val targetZoom: Float = 1f,
        val groupMode: Boolean = false,
        // Smile
        val smileProgress: Float = 0f,
        val smileReady: Boolean = false,
        // Palm
        val palmSimilarity: Float = 0f,
        val palmProgress: Float = 0f,
        // Engineering (hidden)
        val engineeringMode: Boolean = false,
        val cameraFps: Int = 0,
        val inferenceLatencyMs: Long = 0,
        val engSmileRaw: Float = 0f,
        val engNeutralBaseline: Float = 0f,
        val engZoom: Float = 1f,
        val engFaceCount: Int = 0,
        val engRecognitionScore: Float = 0f,
        // Enrollment / Setup
        val enrollProgress: Float = 0f,
        val enrollName: String = "",
        val setupStep: SetupStep = SetupStep.FACE,
    ) {
        val profileCount: Int get() = profiles.size
        val amountDisplay: String get() = "%.2f".format(amountMinor / 100.0).replace('.', ',')
    }

    private val storage = ViaStorage(app)
    private var config = TerminalConfig()
    private val api = ViaApiClient(config.backendBaseUrl)
    val ble = ViaBleController(app)
    private val identity = DeviceIdentity("via_terminal_identity_v1")
    private val master = MasterSecret("via_terminal_master_v1")
    private val _ui = MutableStateFlow(UiState())
    val ui: StateFlow<UiState> = _ui
    private var idleJob: Job? = null
    private var logoTapCount = 0
    private var lastLogoTap = 0L

    private var faceProfiles = listOf<FaceProfile>()
    private var lastRecognitionCheck = 0L
    private var enrolledDescriptors = mutableListOf<List<Float>>()
    private var palmAccumulator = com.via.core.vision.PalmEnrollmentAccumulator()
    private val enrollmentOnce = EnrollmentOnce()
    private var enrollmentGeneration = 0L
    private var pendingEnrollmentName = ""
    private var setupSaving = false
    private var operationJob: Job? = null
    private var resultJob: Job? = null
    private var exchangeGeneration = 0L
    private val localReceiver = com.via.core.hardware.LocalConfirmationReceiver(app)
    private var acceptedResponseHash: String? = null
    private var offlineGate: OfflineSessionGate? = null
    private val consumedSessions = mutableSetOf<String>()
    private var enrollingProfileId: String? = null
    private var storedPalmTemplate: List<Float>? = null
    private val eventJson = Json { ignoreUnknownKeys = true }
    private var wsJob: Job? = null
    private var lastPalmUploadMs = 0L

    init {
        viewModelScope.launch {
            storage.faceProfiles.collect { saved ->
                faceProfiles = saved
                _ui.value = _ui.value.copy(profiles = saved)
            }
        }
        viewModelScope.launch {
            config = storage.terminalConfig.first()


            storedPalmTemplate = storage.palmTemplate.first()
            _ui.value = _ui.value.copy(
                merchant = config.operatorName,
                amountMinor = config.demoAmountMinor,
                backendAvailable = false,
                downloadUrl = "${config.backendBaseUrl}/download",
            )

        }
    }

    // --- Smart Camera callbacks ---

    fun onFramingUpdate(state: FramingState) {
        val now = System.currentTimeMillis()
        val activeName = state.activeFace?.let { recognizeFace(it, now) }
        val profile = activeName?.let { name -> faceProfiles.find { it.displayName == name } }

        _ui.value = _ui.value.copy(
            faceCount = state.faces.size,
            activeFaceName = activeName,
            recognizedProfile = profile,
            targetZoom = state.targetZoom,
            groupMode = state.groupMode,
            engZoom = state.targetZoom,
            engFaceCount = state.faces.size,
        )

        if (_ui.value.screen == Screen.ENROLL && !_ui.value.enteringProfileName && _ui.value.setupStep == SetupStep.FACE) {
            val stable = state.activeFace?.stableFrames ?: 0
            if (state.faces.size == 1 && stable > 25 && enrolledDescriptors.size >= 5) {
                _ui.value = _ui.value.copy(setupStep = SetupStep.SMILE)
            }
        }
    }

    private fun recognizeFace(face: TrackedFace, now: Long): String? {
        if (faceProfiles.isEmpty()) return null
        if (now - lastRecognitionCheck < 500) return _ui.value.activeFaceName
        lastRecognitionCheck = now
        return _ui.value.activeFaceName
    }

    fun onFaceRecognized(descriptor: List<Float>) {
        if (faceProfiles.isEmpty()) return
        var bestScore = 0f
        var bestProfile: FaceProfile? = null
        for (p in faceProfiles) {
            val score = FaceDescriptor.similarity(descriptor, p.embedding)
            if (score > bestScore) {
                bestScore = score
                bestProfile = p
            }
        }
        val threshold = 0.72f
        if (bestScore >= threshold && bestProfile != null) {
            _ui.value = _ui.value.copy(
                activeFaceName = bestProfile.displayName,
                recognizedProfile = bestProfile,
                engRecognitionScore = bestScore,
            )
        } else {
            _ui.value = _ui.value.copy(
                engRecognitionScore = bestScore,
            )
        }
    }

    // --- Smile ---

    fun onSmileProgress(progress: Float, rawSmile: Float) {
        _ui.value = _ui.value.copy(
            smileProgress = progress,
            smileReady = progress >= 1f,
            engSmileRaw = rawSmile,
        )
    }

    fun onSmileConfirmed() {
        if (_ui.value.faceCount != 1) return
        if (_ui.value.screen == Screen.ENROLL && _ui.value.setupStep == SetupStep.SMILE) {
            _ui.value = _ui.value.copy(setupStep = SetupStep.PALM, smileProgress = 0f)
            return
        }
        if (_ui.value.screen == Screen.SMILE) confirmPayment(ConfirmationMethod.SMILE)
    }

    // --- Enrollment ---

    fun startEnrollment() {
        navigate(Screen.ENROLL)
        pendingEnrollmentName = ""
        setupSaving = false
        enrollmentOnce.reset()
        enrollmentGeneration++
        enrolledDescriptors.clear()
        palmAccumulator = com.via.core.vision.PalmEnrollmentAccumulator()
        _ui.value = _ui.value.copy(
            screen = Screen.ENROLL,
            setupStep = SetupStep.FACE,
            enrollProgress = 0f,
            enrollName = "",
            enteringProfileName = true,
            smileProgress = 0f,
            smileReady = false,
            palmProgress = 0f,
        )
        armIdle()
    }

    fun setEnrollName(name: String) {
        if (_ui.value.enteringProfileName) _ui.value = _ui.value.copy(enrollName = name.filterNot { it.isISOControl() }.take(40))
    }
    fun beginNamedEnrollment() {
        if (!_ui.value.enteringProfileName) return
        val name = _ui.value.enrollName.trim().replace(Regex("\\s+"), " ")
        if (name.isBlank()) return
        pendingEnrollmentName = name
        _ui.value = _ui.value.copy(enrollName = name, enteringProfileName = false)
        armIdle()
    }

    fun onSetupDescriptor(descriptor: List<Float>) {
        if (_ui.value.screen != Screen.ENROLL || _ui.value.enteringProfileName || _ui.value.faceCount != 1) return
        val step = _ui.value.setupStep
        if (step == SetupStep.FACE || step == SetupStep.SMILE) {
            enrolledDescriptors.add(descriptor)
        }
    }

    fun onSetupPalmDescriptor(descriptor: List<Float>) {
        if (_ui.value.screen != Screen.ENROLL || _ui.value.enteringProfileName || _ui.value.setupStep != SetupStep.PALM || setupSaving) return
        palmAccumulator.offer(descriptor)
        _ui.value = _ui.value.copy(palmProgress = palmAccumulator.progress)
        if (palmAccumulator.ready) {
            completePersonSetup()
        }
    }

    private fun completePersonSetup() {
        if (!enrollmentOnce.beginSave()) return
        setupSaving = true
        val averaged = averageDescriptors(enrolledDescriptors)
        val palmTemplate = palmAccumulator.template()
        val name = pendingEnrollmentName.ifBlank { "Utilizator ${faceProfiles.size + 1}" }
        val profile = FaceProfile(
            id = UUID.randomUUID().toString(),
            displayName = name,
            embedding = averaged,
            palmEmbedding = palmTemplate,
            createdAtEpochMs = System.currentTimeMillis(),
        )
        val generation = enrollmentGeneration
        viewModelScope.launch {
            try {
                storage.savePerson(profile, palmTemplate)
                faceProfiles = (faceProfiles.filterNot { it.id == profile.id } + profile)
                storedPalmTemplate = palmTemplate
                if (generation != enrollmentGeneration || _ui.value.screen != Screen.ENROLL) return@launch
                _ui.value = _ui.value.copy(setupStep = SetupStep.DONE)
                ble.setLedState(ViaBleController.LedState.SUCCESS)
                delay(2000)
                if (generation == enrollmentGeneration && _ui.value.screen == Screen.ENROLL) navigate(Screen.HOME)
            } catch (e: kotlinx.coroutines.CancellationException) { throw e
            } catch (_: Exception) { if (generation == enrollmentGeneration) showResult("Salvare nereușită", "Reîncearcă înregistrarea", false) }
        }
    }

    fun onEnrollDescriptor(descriptor: List<Float>) {
        enrolledDescriptors.add(descriptor)
        val progress = (enrolledDescriptors.size / 5f).coerceAtMost(1f)
        _ui.value = _ui.value.copy(enrollProgress = progress)

        if (enrolledDescriptors.size >= 5) {
            finalizeEnrollment()
        }
    }

    private fun finalizeEnrollment() {
        val averaged = averageDescriptors(enrolledDescriptors)
        val name = _ui.value.enrollName.ifBlank { "Utilizator ${faceProfiles.size + 1}" }
        val profile = FaceProfile(
            id = UUID.randomUUID().toString(),
            displayName = name,
            embedding = averaged,
            createdAtEpochMs = System.currentTimeMillis(),
        )
        faceProfiles = faceProfiles + profile
        viewModelScope.launch { storage.addFaceProfile(profile) }
        showResult(name, "Profil creat", true)
    }

    // --- Palm Enrollment ---

    fun startPalmEnrollment(profileId: String? = null) {
        palmAccumulator = com.via.core.vision.PalmEnrollmentAccumulator()
        enrollingProfileId = profileId
        _ui.value = _ui.value.copy(screen = Screen.PALM_ENROLL, palmProgress = 0f)
        armIdle()
    }

    fun onPalmEnrollDescriptor(descriptor: List<Float>) {
        palmAccumulator.offer(descriptor)
        _ui.value = _ui.value.copy(palmProgress = palmAccumulator.progress)
        if (palmAccumulator.ready) {
            finalizePalmEnrollment()
        }
    }

    private fun finalizePalmEnrollment() {
        val template = palmAccumulator.template()
        val targetProfileId = enrollingProfileId
        viewModelScope.launch {
            if (targetProfileId != null) {
                val profile = faceProfiles.find { it.id == targetProfileId }
                if (profile != null) {
                    val updated = profile.copy(palmEmbedding = template)
                    faceProfiles = faceProfiles.map { if (it.id == targetProfileId) updated else it }
                    storage.saveFaceProfiles(faceProfiles)
                }
            }
            storage.savePalmTemplate(template)
            storedPalmTemplate = template
            showResult("Palmă înregistrată", null, true)
        }
    }

    fun onPalmVerify(descriptor: List<Float>) {
        val profiles = faceProfiles.filter { it.palmEmbedding.isNotEmpty() }
        val globalTemplate = storedPalmTemplate

        var bestSim = 0f
        var matched = false

        for (p in profiles) {
            val sim = com.via.core.vision.PalmDescriptor.cosine(descriptor, p.palmEmbedding)
            if (sim > bestSim) bestSim = sim
            if (sim > 0.82f) {
                matched = true
                _ui.value = _ui.value.copy(
                    activeFaceName = p.displayName,
                    recognizedProfile = p,
                )
                break
            }
        }

        if (!matched && globalTemplate != null) {
            val sim = com.via.core.vision.PalmDescriptor.cosine(descriptor, globalTemplate)
            if (sim > bestSim) bestSim = sim
            if (sim > 0.82f) matched = true
        }

        _ui.value = _ui.value.copy(palmSimilarity = bestSim)

    }

    private fun averageDescriptors(descriptors: List<List<Float>>): List<Float> {
        if (descriptors.isEmpty()) return emptyList()
        val size = descriptors[0].size
        val sum = FloatArray(size)
        for (d in descriptors) for (i in d.indices) sum[i] += d[i]
        val n = descriptors.size.toFloat()
        val avg = sum.map { it / n }
        var norm = 0f
        for (v in avg) norm += v * v
        norm = kotlin.math.sqrt(norm).coerceAtLeast(1e-6f)
        return avg.map { it / norm }
    }

    // --- Navigation ---

    fun onLogoTap() {
        val now = System.currentTimeMillis()
        if (now - lastLogoTap > 2000) logoTapCount = 0
        lastLogoTap = now
        logoTapCount++
        if (logoTapCount >= 5) {
            logoTapCount = 0
            navigate(Screen.PRESENTATION)
        }
    }

    fun navigate(screen: Screen) {
        resultJob?.cancel()
        if (screen !in listOf(Screen.PAY, Screen.PHONE, Screen.SMILE, Screen.PALM, Screen.TAP)) {
            exchangeGeneration++
            localReceiver.close()
            operationJob?.cancel()
            _ui.value = _ui.value.copy(currentSession = null, qrRequest = null, qrScanning = false, qrError = null)
        }
        _ui.value = _ui.value.copy(screen = screen, resultTitle = null, resultSubtitle = null)
        ledFor(screen)
        armIdle()
    }

    fun setDemo(merchant: String, amountMinor: Long) {
        _ui.value = _ui.value.copy(merchant = merchant, amountMinor = amountMinor)
        viewModelScope.launch {
            config = config.copy(operatorName = merchant, demoAmountMinor = amountMinor)
            storage.saveTerminalConfig(config)
        }
    }

    // --- Payment ---

    private fun newSession(domain: ViaDomain): ViaSession {
        val now = System.currentTimeMillis()
        return ViaSession(UUID.randomUUID().toString(), UUID.randomUUID().toString(), domain,
            config.operatorId, _ui.value.merchant, if (domain == ViaDomain.PAYMENT) Money(_ui.value.amountMinor, _ui.value.currency) else null,
            when(domain) { ViaDomain.TRANSPORT -> "transport_pass"; ViaDomain.PARKING -> "parking_right"; ViaDomain.ACCESS -> "access_pass"; ViaDomain.BENEFIT -> "benefit"; else -> null }, now, now + 180000)
    }
    fun beginPayment() { beginLocalSession(ViaDomain.PAYMENT, Screen.PAY) }
    fun beginValidation(domain: ViaDomain) { beginLocalSession(domain, Screen.TAP) }
    private fun beginLocalSession(domain: ViaDomain, screen: Screen) {
        operationJob?.cancel()
        exchangeGeneration++
        val session = newSession(domain)
        val request = OfflineQr.encode("request", OfflineQr.requestBody(session), identity.publicKeySpkiBase64(), identity::sign)
        navigate(screen)
        offlineGate = OfflineSessionGate(request)
        _ui.value = _ui.value.copy(currentSession = session, validationDomain = domain, qrRequest = request, qrScanning = false, qrError = null)
        acceptedResponseHash = null
        startLocalReceiver()
    }
    fun openQrExchange() {
        if (_ui.value.currentSession == null || (_ui.value.currentSession?.expiresAtEpochMs ?: 0) <= System.currentTimeMillis()) beginPayment()
        navigate(Screen.PHONE)
    }
    fun scanQrResponse() { _ui.value = _ui.value.copy(qrScanning = true, qrError = null) }
    fun stopQrScanner() { _ui.value = _ui.value.copy(qrScanning = false, qrError = null) }
    fun startLocalReceiver() {
        val session = _ui.value.currentSession ?: return
        if (session.expiresAtEpochMs <= System.currentTimeMillis()) { renewQrSession(); return }
        if (session.id in consumedSessions) return
        _ui.value = _ui.value.copy(qrError = null, qrConnecting = true)
        localReceiver.start(session.id, ::acceptLocalResponse, error = { error ->
            if (_ui.value.currentSession?.id == session.id) _ui.value = _ui.value.copy(qrError = error, qrConnecting = false)
        }, ready = {
            if (_ui.value.currentSession?.id == session.id) _ui.value = _ui.value.copy(qrError = null, qrConnecting = false)
        })
    }
    fun acceptQrResponse(payload: String) { acceptLocalResponse(payload) }
    private fun acceptLocalResponse(payload: String): Boolean {
        val session = _ui.value.currentSession ?: return false
        val digest = OfflineQr.hash(payload)
        if (session.id in consumedSessions) return acceptedResponseHash == digest
        if (_ui.value.resultTitle != null) return false
        return try {
            val response = requireNotNull(offlineGate).accept(payload, System.currentTimeMillis())
            consumedSessions.add(session.id)
            acceptedResponseHash = digest
            _ui.value = _ui.value.copy(currentSession = session.copy(status = if (response.approved) SessionStatus.CONFIRMED else SessionStatus.DENIED), qrScanning = false)
            showResult(if (!response.approved) "Refuzat" else if (session.domain == ViaDomain.PAYMENT) "Confirmat · demo" else "Valid · demo", null, response.approved)
            true
        } catch (_: Exception) { false }
    }
    fun renewQrSession() {
        val session = _ui.value.currentSession
        if (session?.domain == ViaDomain.PAYMENT) { beginPayment(); openQrExchange() }
        else beginValidation(session?.domain ?: _ui.value.validationDomain)
    }

    fun onPalmProgress(value: Float, similarity: Float = _ui.value.palmSimilarity) {
        _ui.value = _ui.value.copy(palmProgress = value, palmSimilarity = similarity)
    }

    fun confirmPayment(method: ConfirmationMethod) {
        if (method in listOf(ConfirmationMethod.QR, ConfirmationMethod.PHONE, ConfirmationMethod.NFC)) { openQrExchange(); return }
        if (_ui.value.recognizedProfile == null) { showResult("Profil nerecunoscut", null, false); return }
        val session = _ui.value.currentSession ?: return
        if (session.expiresAtEpochMs <= System.currentTimeMillis() || !consumedSessions.add(session.id)) return
        showResult("Gest confirmat · demo", _ui.value.activeFaceName, true)
    }
    fun validateDemo() { scanQrResponse() }
    fun showResult(title: String, subtitle: String?, success: Boolean) {
        resultJob?.cancel()
        _ui.value = _ui.value.copy(resultTitle = title, resultSubtitle = subtitle, resultKind = if (success) ResultKind.SUCCESS else ResultKind.ERROR)
        ble.setLedState(if (success) ViaBleController.LedState.SUCCESS else ViaBleController.LedState.ERROR)
        resultJob = viewModelScope.launch {
            delay(3000)
            navigate(Screen.HOME)
            ble.setLedState(ViaBleController.LedState.IDLE)
        }
    }

    // --- Presentation Mode ---

    fun triggerPayment(merchant: String, amountMinor: Long) {
        setDemo(merchant, amountMinor)
        beginPayment()
    }

    fun triggerValidation(domain: ViaDomain) = beginValidation(domain)
    fun fallbackSuccess() = showResult("Simulare reușită", "Fără operațiune reală", true)
    fun fallbackDeny() = showResult("Refuzat", null, false)

    fun resetDemo() {
        viewModelScope.launch {

            navigate(Screen.HOME)
        }
    }

    // --- Idle & LED ---

    fun userInteraction() = armIdle()

    private fun armIdle() {
        idleJob?.cancel()
        idleJob = viewModelScope.launch {
            delay(45_000)
            if (_ui.value.resultTitle == null) navigate(Screen.HOME)
        }
    }

    private fun ledFor(screen: Screen) {
        val state = when (screen) {
            Screen.HOME -> ViaBleController.LedState.IDLE
            Screen.SMILE, Screen.PALM, Screen.ENROLL, Screen.PALM_ENROLL -> ViaBleController.LedState.SCAN
            else -> ViaBleController.LedState.ACTIVE
        }
        ble.setLedState(state)
    }

    override fun onCleared() {
        localReceiver.close()
        ble.disconnect()
        super.onCleared()
    }
}
