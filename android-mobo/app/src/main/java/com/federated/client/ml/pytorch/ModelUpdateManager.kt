package com.federated.client.ml.pytorch

import android.content.Context
import com.federated.client.data.local.prefs.PreferencesManager
import com.federated.client.data.remote.api.ModelApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.ResponseBody
import timber.log.Timber
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for checking, downloading, and hot-swapping ML models.
 * 
 * Features:
 * - Check for model updates from server
 * - Download new model versions with progress tracking
 * - Verify file integrity with SHA256 checksums
 * - Hot-swap models at runtime without app restart
 * - Rollback to previous version on failure
 * 
 * Usage:
 * ```kotlin
 * val updateAvailable = modelUpdateManager.checkForUpdates()
 * if (updateAvailable) {
 *     modelUpdateManager.downloadAndInstall { progress ->
 *         updateProgressBar(progress)
 *     }
 * }
 * ```
 */
@Singleton
class ModelUpdateManager @Inject constructor(
    private val context: Context,
    private val modelApi: ModelApi,
    private val preferencesManager: PreferencesManager,
    private val modelManager: PyTorchModelManager
) {

    private val modelDirectory = File(context.filesDir, "models")
    private val currentModelFile = File(modelDirectory, "current_model.ptl")
    private val backupModelFile = File(modelDirectory, "backup_model.ptl")

    init {
        if (!modelDirectory.exists()) {
            modelDirectory.mkdirs()
            Timber.d("Created models directory: ${modelDirectory.absolutePath}")
        }
    }

    /**
     * Check if a model update is available.
     * 
     * Compares current version with server's latest version.
     * 
     * @return ModelUpdateInfo if update available, null otherwise
     */
    suspend fun checkForUpdates(): ModelUpdateInfo? = withContext(Dispatchers.IO) {
        try {
            val currentVersion = preferencesManager.getModelVersion()
            Timber.d("Checking for updates. Current version: $currentVersion")

            val response = modelApi.getLatestModel(currentVersion)
            
            if (!response.isSuccessful) {
                Timber.e("Failed to check for updates: ${response.code()}")
                return@withContext null
            }

            val metadata = response.body() ?: run {
                Timber.e("Empty response body when checking updates")
                return@withContext null
            }

            if (metadata.requiresUpdate) {
                Timber.i("Update available: ${metadata.version} (current: $currentVersion)")
                ModelUpdateInfo(
                    version = metadata.version,
                    downloadUrl = metadata.downloadUrl,
                    fileSize = metadata.fileSize,
                    checksum = metadata.checksum,
                    description = metadata.description
                )
            } else {
                Timber.d("No update needed. Latest version already installed.")
                null
            }
        } catch (e: Exception) {
            Timber.e(e, "Error checking for updates")
            null
        }
    }

    /**
     * Download and install a new model version.
     * 
     * Steps:
     * 1. Download model file from server
     * 2. Verify checksum
     * 3. Backup current model
     * 4. Install new model
     * 5. Hot-swap in PyTorchModelManager
     * 6. Update version in preferences
     * 
     * @param updateInfo Update information from checkForUpdates()
     * @param onProgress Progress callback (0.0 to 1.0)
     * @return UpdateResult indicating success or failure
     */
    suspend fun downloadAndInstall(
        updateInfo: ModelUpdateInfo,
        onProgress: ((Float) -> Unit)? = null
    ): UpdateResult = withContext(Dispatchers.IO) {
        try {
            Timber.i("Starting download of model version ${updateInfo.version}")
            
            // Step 1: Download model
            val tempFile = File(modelDirectory, "download_temp.ptl")
            val downloadResult = downloadModel(updateInfo.version, tempFile, onProgress)
            
            if (!downloadResult) {
                tempFile.delete()
                return@withContext UpdateResult.Error("Download failed")
            }

            // Step 2: Verify checksum
            Timber.d("Verifying checksum...")
            val fileChecksum = calculateSHA256(tempFile)
            if (fileChecksum != updateInfo.checksum) {
                Timber.e("Checksum mismatch! Expected: ${updateInfo.checksum}, Got: $fileChecksum")
                tempFile.delete()
                return@withContext UpdateResult.Error("Checksum verification failed")
            }
            Timber.i("Checksum verified successfully")

            // Step 3: Backup current model
            if (currentModelFile.exists()) {
                Timber.d("Backing up current model...")
                currentModelFile.copyTo(backupModelFile, overwrite = true)
            }

            // Step 4: Install new model
            Timber.d("Installing new model...")
            tempFile.copyTo(currentModelFile, overwrite = true)
            tempFile.delete()

            // Step 5: Hot-swap model
            Timber.d("Hot-swapping model in PyTorchModelManager...")
            val loadSuccess = modelManager.loadModel(currentModelFile)
            
            if (!loadSuccess) {
                Timber.e("Failed to load new model! Rolling back...")
                // Rollback to backup
                if (backupModelFile.exists()) {
                    backupModelFile.copyTo(currentModelFile, overwrite = true)
                    modelManager.loadModel(currentModelFile)
                }
                return@withContext UpdateResult.Error("Failed to load model")
            }

            // Step 6: Update version in preferences
            preferencesManager.setModelVersion(updateInfo.version)
            Timber.i("✅ Model successfully updated to version ${updateInfo.version}")

            UpdateResult.Success(updateInfo.version)
        } catch (e: Exception) {
            Timber.e(e, "Error during model update")
            UpdateResult.Error(e.message ?: "Unknown error")
        }
    }

    /**
     * Download model file from server.
     */
    private suspend fun downloadModel(
        version: String,
        destination: File,
        onProgress: ((Float) -> Unit)?
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val response = modelApi.downloadModel(version)
            
            if (!response.isSuccessful) {
                Timber.e("Download failed with code: ${response.code()}")
                return@withContext false
            }

            val body = response.body() ?: run {
                Timber.e("Empty response body")
                return@withContext false
            }

            val contentLength = body.contentLength()
            Timber.d("Downloading model: ${contentLength / 1024 / 1024}MB")

            body.byteStream().use { input ->
                FileOutputStream(destination).use { output ->
                    val buffer = ByteArray(8192)
                    var bytesRead: Int
                    var totalBytesRead = 0L

                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        output.write(buffer, 0, bytesRead)
                        totalBytesRead += bytesRead

                        if (contentLength > 0) {
                            val progress = totalBytesRead.toFloat() / contentLength
                            onProgress?.invoke(progress)
                        }
                    }
                }
            }

            Timber.i("Download complete: ${destination.length() / 1024 / 1024}MB")
            true
        } catch (e: Exception) {
            Timber.e(e, "Download error")
            false
        }
    }

    /**
     * Calculate SHA256 checksum of a file.
     */
    private fun calculateSHA256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(8192)
            var bytesRead: Int
            while (input.read(buffer).also { bytesRead = it } != -1) {
                digest.update(buffer, 0, bytesRead)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    /**
     * Rollback to previous model version.
     */
    suspend fun rollback(): Boolean = withContext(Dispatchers.IO) {
        try {
            if (!backupModelFile.exists()) {
                Timber.w("No backup model available for rollback")
                return@withContext false
            }

            Timber.i("Rolling back to previous model...")
            backupModelFile.copyTo(currentModelFile, overwrite = true)
            
            val loadSuccess = modelManager.loadModel(currentModelFile)
            if (loadSuccess) {
                Timber.i("✅ Rollback successful")
            } else {
                Timber.e("❌ Rollback failed")
            }
            
            loadSuccess
        } catch (e: Exception) {
            Timber.e(e, "Rollback error")
            false
        }
    }

    /**
     * Get current model version from preferences.
     */
    suspend fun getCurrentVersion(): String? {
        return preferencesManager.getModelVersion()
    }
}

/**
 * Model update information.
 */
data class ModelUpdateInfo(
    val version: String,
    val downloadUrl: String,
    val fileSize: Long,
    val checksum: String,
    val description: String?
)

/**
 * Update result sealed class.
 */
sealed class UpdateResult {
    data class Success(val version: String) : UpdateResult()
    data class Error(val message: String) : UpdateResult()
}
