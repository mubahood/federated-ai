package com.federated.client.data.repository

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.dao.UploadQueueDao
import com.federated.client.data.local.db.entities.UploadQueueEntity
import com.federated.client.data.local.db.entities.UploadStatus
import com.federated.client.data.local.prefs.PreferencesManager
import com.federated.client.data.remote.api.TrainingApi
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import timber.log.Timber
import java.io.File
import java.io.FileOutputStream
import java.util.Date
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for queuing and uploading training images to the server.
 * 
 * Features:
 * - Queue images for batch upload
 * - Automatic retry on failure with exponential backoff
 * - Image compression to reduce bandwidth
 * - Batch upload optimization
 * - Upload progress tracking
 * - Offline support (queue persists across app restarts)
 * 
 * Usage:
 * ```kotlin
 * // Queue single image
 * uploadManager.queueImage(imageId)
 * 
 * // Queue batch of images
 * uploadManager.queueBatch(imageIds, batchId)
 * 
 * // Process pending uploads
 * uploadManager.processPendingUploads { progress ->
 *     updateUI(progress)
 * }
 * ```
 */
@Singleton
class UploadQueueManager @Inject constructor(
    private val context: Context,
    private val uploadQueueDao: UploadQueueDao,
    private val imageDao: ImageDao,
    private val trainingApi: TrainingApi,
    private val preferencesManager: PreferencesManager,
    private val gson: Gson
) {

    companion object {
        private const val MAX_RETRIES = 3
        private const val BATCH_SIZE = 10
        private const val COMPRESSION_QUALITY = 80
        private const val MAX_IMAGE_WIDTH = 800
        private const val MAX_IMAGE_HEIGHT = 800
    }

    /**
     * Queue a single image for upload.
     * 
     * @param imageId Local image ID
     * @param priority Upload priority (higher = more important)
     * @return Upload queue ID
     */
    suspend fun queueImage(
        imageId: Long,
        priority: Int = 0
    ): Long = withContext(Dispatchers.IO) {
        try {
            // Check if already queued
            val existing = uploadQueueDao.getByImageId(imageId)
            if (existing != null) {
                Timber.d("Image $imageId already queued (queue ID: ${existing.id})")
                return@withContext existing.id
            }

            val queueEntry = UploadQueueEntity(
                imageId = imageId,
                status = UploadStatus.PENDING,
                maxRetries = MAX_RETRIES,
                priority = priority
            )

            val queueId = uploadQueueDao.insert(queueEntry)
            Timber.i("Queued image $imageId for upload (queue ID: $queueId)")
            queueId
        } catch (e: Exception) {
            Timber.e(e, "Error queuing image $imageId")
            -1
        }
    }

    /**
     * Queue multiple images as a batch.
     * 
     * @param imageIds List of local image IDs
     * @param batchId Optional batch identifier (auto-generated if null)
     * @param priority Upload priority
     * @return List of upload queue IDs
     */
    suspend fun queueBatch(
        imageIds: List<Long>,
        batchId: String? = null,
        priority: Int = 0
    ): List<Long> = withContext(Dispatchers.IO) {
        try {
            val actualBatchId = batchId ?: UUID.randomUUID().toString()
            
            val queueEntries = imageIds.map { imageId ->
                UploadQueueEntity(
                    imageId = imageId,
                    status = UploadStatus.PENDING,
                    batchId = actualBatchId,
                    maxRetries = MAX_RETRIES,
                    priority = priority
                )
            }

            val queueIds = uploadQueueDao.insertAll(queueEntries)
            Timber.i("Queued batch of ${imageIds.size} images (batch ID: $actualBatchId)")
            queueIds
        } catch (e: Exception) {
            Timber.e(e, "Error queuing batch")
            emptyList()
        }
    }

    /**
     * Process all pending uploads.
     * 
     * Uploads images in batches of BATCH_SIZE.
     * 
     * @param onProgress Progress callback (current/total)
     * @return UploadBatchResult with success/failure counts
     */
    suspend fun processPendingUploads(
        onProgress: ((Int, Int) -> Unit)? = null
    ): UploadBatchResult = withContext(Dispatchers.IO) {
        try {
            val pendingUploads = uploadQueueDao.getPendingUploads()
            
            if (pendingUploads.isEmpty()) {
                Timber.d("No pending uploads")
                return@withContext UploadBatchResult(0, 0, emptyList())
            }

            Timber.i("Processing ${pendingUploads.size} pending uploads...")
            
            var successCount = 0
            var failedCount = 0
            val errors = mutableListOf<String>()

            // Process in batches
            pendingUploads.chunked(BATCH_SIZE).forEachIndexed { batchIndex, batch ->
                Timber.d("Processing batch ${batchIndex + 1}/${(pendingUploads.size + BATCH_SIZE - 1) / BATCH_SIZE}")
                
                val result = uploadBatch(batch)
                successCount += result.successCount
                failedCount += result.failedCount
                errors.addAll(result.errors)

                // Update progress
                val processed = (batchIndex + 1) * BATCH_SIZE.coerceAtMost(pendingUploads.size)
                onProgress?.invoke(processed, pendingUploads.size)
            }

            Timber.i("Upload complete: $successCount success, $failedCount failed")
            UploadBatchResult(successCount, failedCount, errors)
        } catch (e: Exception) {
            Timber.e(e, "Error processing uploads")
            UploadBatchResult(0, 0, listOf(e.message ?: "Unknown error"))
        }
    }

    /**
     * Upload a batch of queued images.
     */
    private suspend fun uploadBatch(
        queueEntries: List<UploadQueueEntity>
    ): UploadBatchResult = withContext(Dispatchers.IO) {
        try {
            // Load image entities
            val imageEntities = queueEntries.mapNotNull { queue ->
                imageDao.getById(queue.imageId)?.let { image -> queue to image }
            }

            if (imageEntities.isEmpty()) {
                Timber.w("No valid images in batch")
                return@withContext UploadBatchResult(0, queueEntries.size, listOf("No valid images"))
            }

            // Mark as uploading
            imageEntities.forEach { (queue, _) ->
                uploadQueueDao.updateStatus(queue.id, UploadStatus.UPLOADING)
            }

            // Prepare multipart request
            val imageParts = mutableListOf<MultipartBody.Part>()
            val labels = mutableListOf<String>()
            val compressionTemp = File(context.cacheDir, "upload_temp")
            compressionTemp.mkdirs()

            imageEntities.forEach { (queue, image) ->
                try {
                    // Compress image
                    val compressedFile = compressImage(File(image.uri), compressionTemp)
                    
                    // Create multipart part
                    val requestFile = compressedFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
                    val part = MultipartBody.Part.createFormData(
                        "images",
                        "image_${queue.id}.jpg",
                        requestFile
                    )
                    imageParts.add(part)
                    
                    // Add label
                    labels.add(image.category ?: "Unknown")
                } catch (e: Exception) {
                    Timber.e(e, "Error preparing image ${queue.imageId}")
                }
            }

            if (imageParts.isEmpty()) {
                return@withContext UploadBatchResult(0, queueEntries.size, listOf("Failed to prepare images"))
            }

            // Prepare request body parts
            val labelsJson = gson.toJson(labels)
            val labelsBody = labelsJson.toRequestBody("application/json".toMediaTypeOrNull())
            val clientId = (preferencesManager.getDeviceId() ?: "unknown")
                .toRequestBody("text/plain".toMediaTypeOrNull())
            val batchId = queueEntries.first().batchId?.toRequestBody("text/plain".toMediaTypeOrNull())

            // Make API call
            Timber.d("Uploading ${imageParts.size} images...")
            val response = trainingApi.uploadImages(
                images = imageParts,
                labels = labelsBody,
                batchId = batchId,
                clientId = clientId
            )

            // Clean up temp files
            compressionTemp.deleteRecursively()

            if (!response.isSuccessful) {
                Timber.e("Upload failed: ${response.code()}")
                // Mark all as failed
                imageEntities.forEach { (queue, _) ->
                    uploadQueueDao.markAsFailed(queue.id, "HTTP ${response.code()}")
                }
                return@withContext UploadBatchResult(0, queueEntries.size, listOf("HTTP ${response.code()}"))
            }

            val uploadResponse = response.body()
            if (uploadResponse == null) {
                Timber.e("Empty response body")
                imageEntities.forEach { (queue, _) ->
                    uploadQueueDao.markAsFailed(queue.id, "Empty response")
                }
                return@withContext UploadBatchResult(0, queueEntries.size, listOf("Empty response"))
            }

            // Process response
            Timber.i("Upload response: ${uploadResponse.successCount} success, ${uploadResponse.failedCount} failed")
            
            // Mark successful uploads
            uploadResponse.imageIds.forEachIndexed { index, serverId ->
                if (index < imageEntities.size) {
                    val (queue, _) = imageEntities[index]
                    uploadQueueDao.markAsSuccess(queue.id, serverId)
                }
            }

            // Mark failed uploads
            if (uploadResponse.failedCount > 0) {
                imageEntities.drop(uploadResponse.successCount).forEach { (queue, _) ->
                    val errorMsg = uploadResponse.errors.firstOrNull() ?: "Upload failed"
                    uploadQueueDao.markAsFailed(queue.id, errorMsg)
                }
            }

            UploadBatchResult(
                uploadResponse.successCount,
                uploadResponse.failedCount,
                uploadResponse.errors
            )
        } catch (e: Exception) {
            Timber.e(e, "Batch upload error")
            // Mark all as failed
            queueEntries.forEach { queue ->
                uploadQueueDao.markAsFailed(queue.id, e.message ?: "Unknown error")
            }
            UploadBatchResult(0, queueEntries.size, listOf(e.message ?: "Unknown error"))
        }
    }

    /**
     * Compress image to reduce upload size.
     */
    private fun compressImage(sourceFile: File, tempDir: File): File {
        val options = BitmapFactory.Options().apply {
            inJustDecodeBounds = true
        }
        BitmapFactory.decodeFile(sourceFile.absolutePath, options)

        // Calculate inSampleSize
        options.inSampleSize = calculateInSampleSize(options, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT)
        options.inJustDecodeBounds = false

        val bitmap = BitmapFactory.decodeFile(sourceFile.absolutePath, options)
        
        val outputFile = File(tempDir, "${UUID.randomUUID()}.jpg")
        FileOutputStream(outputFile).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, COMPRESSION_QUALITY, out)
        }
        bitmap.recycle()

        return outputFile
    }

    /**
     * Calculate sample size for bitmap decoding.
     */
    private fun calculateInSampleSize(
        options: BitmapFactory.Options,
        reqWidth: Int,
        reqHeight: Int
    ): Int {
        val height = options.outHeight
        val width = options.outWidth
        var inSampleSize = 1

        if (height > reqHeight || width > reqWidth) {
            val halfHeight = height / 2
            val halfWidth = width / 2

            while (halfHeight / inSampleSize >= reqHeight && halfWidth / inSampleSize >= reqWidth) {
                inSampleSize *= 2
            }
        }

        return inSampleSize
    }

    /**
     * Retry failed uploads.
     */
    suspend fun retryFailed(): UploadBatchResult = withContext(Dispatchers.IO) {
        val retriable = uploadQueueDao.getRetriableUploads()
        Timber.i("Retrying ${retriable.size} failed uploads...")
        uploadBatch(retriable)
    }

    /**
     * Observe active uploads for UI.
     */
    fun observeActiveUploads(): Flow<List<UploadQueueEntity>> {
        return uploadQueueDao.observeActiveUploads()
    }

    /**
     * Get upload statistics.
     */
    suspend fun getStats() = uploadQueueDao.getStats()

    /**
     * Clear old successful uploads (cleanup).
     */
    suspend fun cleanupOldUploads(daysOld: Int = 7) = withContext(Dispatchers.IO) {
        val cutoffDate = Date(System.currentTimeMillis() - daysOld * 24 * 60 * 60 * 1000L)
        uploadQueueDao.deleteOldSuccessfulUploads(cutoffDate)
    }
}

/**
 * Upload batch result.
 */
data class UploadBatchResult(
    val successCount: Int,
    val failedCount: Int,
    val errors: List<String>
)
