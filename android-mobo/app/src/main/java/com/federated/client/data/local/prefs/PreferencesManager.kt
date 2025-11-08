package com.federated.client.data.local.prefs

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "federated_ai_prefs")

/**
 * Manager for app preferences using DataStore.
 */
@Singleton
class PreferencesManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.dataStore

    companion object {
        val AUTH_TOKEN = stringPreferencesKey("auth_token")
        val USER_ID = stringPreferencesKey("user_id")
        val DEVICE_ID = stringPreferencesKey("device_id")
        val MODEL_VERSION = stringPreferencesKey("model_version")
        val IS_ONBOARDED = booleanPreferencesKey("is_onboarded")
        val LAST_SYNC_TIMESTAMP = longPreferencesKey("last_sync_timestamp")
        val TRAINING_WIFI_ONLY = booleanPreferencesKey("training_wifi_only")
        val TRAINING_BATTERY_THRESHOLD = longPreferencesKey("training_battery_threshold")
        val THEME_MODE = stringPreferencesKey("theme_mode")
    }

    val authToken: Flow<String?> = dataStore.data.map { it[AUTH_TOKEN] }
    val userId: Flow<String?> = dataStore.data.map { it[USER_ID] }
    val deviceId: Flow<String?> = dataStore.data.map { it[DEVICE_ID] }
    val modelVersion: Flow<String?> = dataStore.data.map { it[MODEL_VERSION] }
    val isOnboarded: Flow<Boolean> = dataStore.data.map { it[IS_ONBOARDED] ?: false }
    val lastSyncTimestamp: Flow<Long> = dataStore.data.map { it[LAST_SYNC_TIMESTAMP] ?: 0L }
    val trainingWifiOnly: Flow<Boolean> = dataStore.data.map { it[TRAINING_WIFI_ONLY] ?: true }
    val trainingBatteryThreshold: Flow<Long> = dataStore.data.map { it[TRAINING_BATTERY_THRESHOLD] ?: 30L }
    val themeMode: Flow<String> = dataStore.data.map { it[THEME_MODE] ?: "system" }

    suspend fun saveAuthToken(token: String) {
        dataStore.edit { it[AUTH_TOKEN] = token }
    }

    suspend fun saveUserId(userId: String) {
        dataStore.edit { it[USER_ID] = userId }
    }

    suspend fun saveDeviceId(deviceId: String) {
        dataStore.edit { it[DEVICE_ID] = deviceId }
    }

    suspend fun setModelVersion(version: String) {
        dataStore.edit { it[MODEL_VERSION] = version }
    }

    suspend fun setOnboarded(onboarded: Boolean) {
        dataStore.edit { it[IS_ONBOARDED] = onboarded }
    }

    suspend fun updateLastSyncTimestamp(timestamp: Long) {
        dataStore.edit { it[LAST_SYNC_TIMESTAMP] = timestamp }
    }

    suspend fun setTrainingWifiOnly(wifiOnly: Boolean) {
        dataStore.edit { it[TRAINING_WIFI_ONLY] = wifiOnly }
    }

    suspend fun setTrainingBatteryThreshold(threshold: Long) {
        dataStore.edit { it[TRAINING_BATTERY_THRESHOLD] = threshold }
    }

    suspend fun setThemeMode(mode: String) {
        dataStore.edit { it[THEME_MODE] = mode }
    }

    suspend fun clearAuthData() {
        dataStore.edit {
            it.remove(AUTH_TOKEN)
            it.remove(USER_ID)
        }
    }

    suspend fun clearAll() {
        dataStore.edit { it.clear() }
    }

    /**
     * Get auth token synchronously (for interceptors).
     */
    suspend fun getAuthToken(): String? {
        var token: String? = null
        authToken.collect { token = it }
        return token
    }

    /**
     * Get device ID synchronously.
     */
    suspend fun getDeviceId(): String? {
        var id: String? = null
        deviceId.collect { id = it }
        return id
    }

    /**
     * Get model version synchronously.
     */
    suspend fun getModelVersion(): String? {
        var version: String? = null
        modelVersion.collect { version = it }
        return version
    }
}
