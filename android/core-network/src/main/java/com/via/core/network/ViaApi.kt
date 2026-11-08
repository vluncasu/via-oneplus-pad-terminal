package com.via.core.network

import com.via.core.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.io.IOException
import java.util.concurrent.TimeUnit

class ViaApiClient(
    private var baseUrl: String,
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(8, TimeUnit.SECONDS)
        .writeTimeout(8, TimeUnit.SECONDS)
        .pingInterval(15, TimeUnit.SECONDS)
        .build(),
) {
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    private val mediaType = "application/json; charset=utf-8".toMediaType()

    fun setBaseUrl(value: String) { baseUrl = value.trimEnd('/') }

    suspend fun health(): Boolean = runCatching { get<ApiMessage>("/health").ok }.getOrDefault(false)

    suspend fun createSession(request: SessionCreateRequest): ViaSession = post("/api/v1/session", request)
    suspend fun getSession(id: String): ViaSession = get("/api/v1/session/$id")
    suspend fun confirmSession(confirmation: SessionConfirmation): ViaSession = post("/api/v1/session/${confirmation.sessionId}/confirm", confirmation)
    suspend fun presentCredential(presentation: CredentialPresentation): PresentationResult = post("/api/v1/session/${presentation.sessionId}/present", presentation)
    suspend fun uploadPalmProbe(probe: PalmProbe): ApiMessage = post("/api/v1/palm/${probe.sessionId}/probe", probe)
    suspend fun fetchPalmProbe(sessionId: String): PalmProbe = get("/api/v1/palm/$sessionId/probe")
    suspend fun postPalmDecision(decision: PalmDecision): ApiMessage = post("/api/v1/palm/${decision.sessionId}/decision", decision)
    suspend fun getPalmDecision(sessionId: String): PalmDecision = get("/api/v1/palm/$sessionId/decision")
    suspend fun issueCredential(credential: RightCredential): RightCredential = post("/api/v1/credential/issue", credential)
    suspend fun revokeCredential(credentialId: String): ApiMessage = postRaw("/api/v1/credential/$credentialId/revoke", "{}")
    suspend fun resetDemo(): ApiMessage = postRaw("/api/v1/demo/reset", "{}")

    fun terminalEvents(terminalId: String): Flow<String> = callbackFlow {
        val wsUrl = baseUrl.replaceFirst("http://", "ws://").replaceFirst("https://", "wss://") + "/ws/terminal/$terminalId"
        val socket = client.newWebSocket(Request.Builder().url(wsUrl).build(), object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) { trySend(text) }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) { close(t) }
            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) { close() }
        })
        awaitClose { socket.close(1000, "bye") }
    }

    private suspend inline fun <reified T> get(path: String): T = withContext(Dispatchers.IO) {
        val response = client.newCall(Request.Builder().url(baseUrl + path).get().build()).execute()
        response.use { decodeResponse<T>(it) }
    }

    private suspend inline fun <reified Req, reified Res> post(path: String, request: Req): Res = withContext(Dispatchers.IO) {
        val body = json.encodeToString(request).toRequestBody(mediaType)
        val response = client.newCall(Request.Builder().url(baseUrl + path).post(body).build()).execute()
        response.use { decodeResponse<Res>(it) }
    }

    private suspend inline fun <reified Res> postRaw(path: String, raw: String): Res = withContext(Dispatchers.IO) {
        val response = client.newCall(Request.Builder().url(baseUrl + path).post(raw.toRequestBody(mediaType)).build()).execute()
        response.use { decodeResponse<Res>(it) }
    }

    private inline fun <reified T> decodeResponse(response: Response): T {
        val body = response.body?.string().orEmpty()
        if (!response.isSuccessful) throw IOException("HTTP ${response.code}: $body")
        return json.decodeFromString(body)
    }
}
