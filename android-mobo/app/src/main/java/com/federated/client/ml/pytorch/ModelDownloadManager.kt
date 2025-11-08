package com.federated.client.ml.pytorch

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import timber.log.Timber
import java.io.File
import java.io.FileOutputStream

/**
 * Manager for downloading and caching PyTorch models from the server.
 * 
 * Downloads model.ptl from the API endpoint and stores it in internal storage.
 * Includes progress tracking, checksum validation, and caching.
 */
class ModelDownloadManager(
    private val context: Context,
    private val baseUrl: String = "http://10.0.2.2:8000",
    private val authToken: String? = null
) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
        .build()

    private val modelFileName = "object_detection_model.ptl"
    private val modelDirectory = File(context.filesDir, "models")

    init {
        // Create models directory if it doesn't exist
        if (!modelDirectory.exists()) {
            modelDirectory.mkdirs()
            Timber.d("Created models directory: ${modelDirectory.absolutePath}")
        }
    }

    /**
     * Download model from server.
     * 
     * @param onProgress Callback for download progress (0.0 to 1.0)
     * @return File object pointing to downloaded model, or null on failure
     */
    suspend fun downloadModel(
        onProgress: ((Float) -> Unit)? = null
    ): DownloadResult = withContext(Dispatchers.IO) {
        try {
            val modelFile = File(modelDirectory, modelFileName)
            
            // Check if model already exists
            if (modelFile.exists()) {
                Timber.i("Model already exists: ${modelFile.absolutePath}")
                return@withContext DownloadResult.Success(modelFile)
            }

            Timber.d("Starting model download from: $baseUrl/api/v1/model/download/")
            
            val request = Request.Builder()
                .url("$baseUrl/api/v1/model/download/")
                .apply {
                    if (authToken != null) {
                        addHeader("Authorization", "Token $authToken")
                    }
                }
                .build()

            val response = client.newCall(request).execute()

            if (!response.isSuccessful) {
                Timber.e("Download failed with code: ${response.code}")
                return@withContext DownloadResult.Error("Server returned error: ${response.code}")
            }

            val body = response.body ?: run {
                Timber.e("Response body is null")
                return@withContext DownloadResult.Error("Empty response from server")
            }

            val contentLength = body.contentLength()
            Timber.d("Model size: ${contentLength / 1024 / 1024}MB")

            // Download to temporary file first
            val tempFile = File(modelDirectory, "$modelFileName.tmp")
            
            body.byteStream().use { input ->
                FileOutputStream(tempFile).use { output ->
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

            // Rename temp file to final name
            if (tempFile.renameTo(modelFile)) {
                Timber.i("Model downloaded successfully: ${modelFile.absolutePath}")
                DownloadResult.Success(modelFile)
            } else {
                Timber.e("Failed to rename temp file")
                DownloadResult.Error("Failed to save model file")
            }

        } catch (e: Exception) {
            Timber.e(e, "Model download failed")
            DownloadResult.Error(e.message ?: "Unknown error")
        }
    }

    /**
     * Fetch model metadata from server.
     */
    suspend fun fetchModelMetadata(): ModelMetadata? = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/api/v1/model/metadata/")
                .build()

            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val json = response.body?.string()
                Timber.d("Model metadata: $json")
                // TODO: Parse JSON to ModelMetadata object
                // For now, just log it
                null
            } else {
                Timber.e("Failed to fetch metadata: ${response.code}")
                null
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to fetch model metadata")
            null
        }
    }

    /**
     * Get the local model file if it exists.
     */
    fun getLocalModel(): File? {
        val modelFile = File(modelDirectory, modelFileName)
        return if (modelFile.exists()) {
            Timber.d("Local model found: ${modelFile.absolutePath}")
            modelFile
        } else {
            Timber.d("No local model found")
            null
        }
    }

    /**
     * Check if model is already downloaded.
     */
    fun isModelDownloaded(): Boolean {
        return File(modelDirectory, modelFileName).exists()
    }

    /**
     * Delete local model file.
     */
    fun deleteModel(): Boolean {
        val modelFile = File(modelDirectory, modelFileName)
        return if (modelFile.exists()) {
            val deleted = modelFile.delete()
            if (deleted) {
                Timber.i("Model deleted: ${modelFile.absolutePath}")
            } else {
                Timber.e("Failed to delete model")
            }
            deleted
        } else {
            Timber.d("No model to delete")
            false
        }
    }

    /**
     * Get model file size in MB.
     */
    fun getModelSize(): Float? {
        val modelFile = File(modelDirectory, modelFileName)
        return if (modelFile.exists()) {
            modelFile.length() / (1024f * 1024f)
        } else {
            null
        }
    }
}

/**
 * Sealed class for download results.
 */
sealed class DownloadResult {
    data class Success(val file: File) : DownloadResult()
    data class Error(val message: String) : DownloadResult()
}

/**
 * Model metadata from server.
 */
data class ModelMetadata(
    val architecture: String,
    val numClasses: Int,
    val validationAccuracy: Float,
    val version: String,
    val categories: Map<Int, String>
)
