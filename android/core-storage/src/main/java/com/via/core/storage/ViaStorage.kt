package com.via.core.storage

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.via.core.crypto.AesGcmVault
import com.via.core.model.FaceProfile
import com.via.core.model.RightCredential
import com.via.core.model.TerminalConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

private val Context.viaDataStore by preferencesDataStore(name = "via_preferences_v1")

class ViaStorage(private val context: Context) {
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    private val vault by lazy { AesGcmVault() }

    private object Keys {
        val terminalConfig = stringPreferencesKey("terminal_config")
        val credentials = stringPreferencesKey("credentials_enc")
        val palmTemplate = stringPreferencesKey("palm_template_enc")
        val palmEnabled = booleanPreferencesKey("palm_enabled")
        val smileEnabled = booleanPreferencesKey("smile_enabled")
        val viaLightEnabled = booleanPreferencesKey("via_light_enabled")
        val offlineResponses = stringPreferencesKey("offline_responses")
        val faceProfiles = stringPreferencesKey("face_profiles")
    }

    val terminalConfig: Flow<TerminalConfig> = context.viaDataStore.data.map { prefs ->
        prefs[Keys.terminalConfig]?.let { runCatching { json.decodeFromString<TerminalConfig>(it) }.getOrNull() }
            ?: TerminalConfig()
    }

    suspend fun saveTerminalConfig(config: TerminalConfig) {
        context.viaDataStore.edit { it[Keys.terminalConfig] = json.encodeToString(config) }
    }

    val credentials: Flow<List<RightCredential>> = context.viaDataStore.data.map { prefs ->
        val encrypted = prefs[Keys.credentials] ?: return@map emptyList()
        runCatching {
            val plain = vault.decrypt(encrypted, "credentials-v1".toByteArray()).decodeToString()
            json.decodeFromString(ListSerializer(RightCredential.serializer()), plain)
        }.getOrElse { emptyList() }
    }

    suspend fun saveCredentials(credentials: List<RightCredential>) {
        val plain = json.encodeToString(ListSerializer(RightCredential.serializer()), credentials).toByteArray()
        val encrypted = vault.encrypt(plain, "credentials-v1".toByteArray())
        context.viaDataStore.edit { it[Keys.credentials] = encrypted }
    }

    suspend fun savePalmTemplate(descriptor: List<Float>?) {
        context.viaDataStore.edit { prefs ->
            if (descriptor == null) {
                prefs.remove(Keys.palmTemplate)
                prefs[Keys.palmEnabled] = false
            } else {
                val plain = descriptor.joinToString(",").toByteArray()
                prefs[Keys.palmTemplate] = vault.encrypt(plain, "palm-v1".toByteArray())
                prefs[Keys.palmEnabled] = true
            }
        }
    }

    val palmTemplate: Flow<List<Float>?> = context.viaDataStore.data.map { prefs ->
        val encrypted = prefs[Keys.palmTemplate] ?: return@map null
        runCatching {
            vault.decrypt(encrypted, "palm-v1".toByteArray())
                .decodeToString().split(',').map { it.toFloat() }
        }.getOrNull()
    }

    val palmEnabled: Flow<Boolean> = context.viaDataStore.data.map { it[Keys.palmEnabled] ?: false }
    val smileEnabled: Flow<Boolean> = context.viaDataStore.data.map { it[Keys.smileEnabled] ?: true }
    val viaLightEnabled: Flow<Boolean> = context.viaDataStore.data.map { it[Keys.viaLightEnabled] ?: true }

    suspend fun setPalmEnabled(value: Boolean) = context.viaDataStore.edit { it[Keys.palmEnabled] = value }
    suspend fun setSmileEnabled(value: Boolean) = context.viaDataStore.edit { it[Keys.smileEnabled] = value }
    suspend fun setViaLightEnabled(value: Boolean) = context.viaDataStore.edit { it[Keys.viaLightEnabled] = value }

    val faceProfiles: Flow<List<FaceProfile>> = context.viaDataStore.data.map { prefs ->
        val raw = prefs[Keys.faceProfiles] ?: return@map emptyList()
        runCatching {
            json.decodeFromString(ListSerializer(FaceProfile.serializer()), raw)
        }.getOrElse { emptyList() }
    }

    suspend fun saveFaceProfiles(profiles: List<FaceProfile>) {
        val encoded = json.encodeToString(ListSerializer(FaceProfile.serializer()), profiles)
        context.viaDataStore.edit { it[Keys.faceProfiles] = encoded }
    }

    val offlineResponses: Flow<Map<String, String>> = context.viaDataStore.data.map { prefs ->
        prefs[Keys.offlineResponses]?.let { json.decodeFromString<Map<String,String>>(it) } ?: emptyMap()
    }
    suspend fun saveOfflineApproval(credentials: List<RightCredential>, sessionId: String, response: String) {
        val encrypted = vault.encrypt(json.encodeToString(ListSerializer(RightCredential.serializer()), credentials).toByteArray(), "credentials-v1".toByteArray())
        context.viaDataStore.edit { prefs ->
            val existing = prefs[Keys.offlineResponses]?.let { json.decodeFromString<Map<String,String>>(it) } ?: emptyMap()
            require(sessionId !in existing) { "Already confirmed" }
            require(existing.size < 1000) { "Demo storage full" }
            prefs[Keys.credentials] = encrypted
            prefs[Keys.offlineResponses] = json.encodeToString(existing + (sessionId to response))
        }
    }

    suspend fun savePerson(profile: FaceProfile, palm: List<Float>) {
        val encrypted = vault.encrypt(palm.joinToString(",").toByteArray(), "palm-v1".toByteArray())
        context.viaDataStore.edit { prefs ->
            val existing = prefs[Keys.faceProfiles]?.let { json.decodeFromString(ListSerializer(FaceProfile.serializer()), it) } ?: emptyList()
            prefs[Keys.faceProfiles] = json.encodeToString(ListSerializer(FaceProfile.serializer()), existing.filterNot { it.id == profile.id } + profile)
            prefs[Keys.palmTemplate] = encrypted
            prefs[Keys.palmEnabled] = true
        }
    }

    suspend fun addFaceProfile(profile: FaceProfile) {
        context.viaDataStore.edit { prefs ->
            val existing = prefs[Keys.faceProfiles]?.let {
                runCatching { json.decodeFromString(ListSerializer(FaceProfile.serializer()), it) }.getOrElse { emptyList() }
            } ?: emptyList()
            val updated = existing.filter { it.id != profile.id } + profile
            prefs[Keys.faceProfiles] = json.encodeToString(ListSerializer(FaceProfile.serializer()), updated)
        }
    }

    suspend fun removeFaceProfile(id: String) {
        context.viaDataStore.edit { prefs ->
            val existing = prefs[Keys.faceProfiles]?.let {
                runCatching { json.decodeFromString(ListSerializer(FaceProfile.serializer()), it) }.getOrElse { emptyList() }
            } ?: emptyList()
            val updated = existing.filter { it.id != id }
            prefs[Keys.faceProfiles] = json.encodeToString(ListSerializer(FaceProfile.serializer()), updated)
        }
    }
}
