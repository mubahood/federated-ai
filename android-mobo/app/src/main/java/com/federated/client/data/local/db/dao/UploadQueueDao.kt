package com.federated.client.data.local.db.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import androidx.room.Update
import com.federated.client.data.local.db.entities.UploadQueueEntity
import com.federated.client.data.local.db.entities.UploadStatus
import kotlinx.coroutines.flow.Flow
import java.util.Date

/**
 * DAO for UploadQueue database operations.
 * 
 * Provides methods for:
 * - Queuing images for upload
 * - Retrieving pending uploads
 * - Updating upload status
 * - Retrying failed uploads
 * - Batch operations
 */
@Dao
interface UploadQueueDao {

    /**
     * Insert a new upload queue entry.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(uploadQueue: UploadQueueEntity): Long

    /**
     * Insert multiple upload queue entries.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(uploadQueues: List<UploadQueueEntity>): List<Long>

    /**
     * Update an existing upload queue entry.
     */
    @Update
    suspend fun update(uploadQueue: UploadQueueEntity)

    /**
     * Get all pending uploads ordered by priority (highest first) and creation time.
     */
    @Query("""
        SELECT * FROM upload_queue 
        WHERE status = 'PENDING' 
        ORDER BY priority DESC, created_at ASC
    """)
    suspend fun getPendingUploads(): List<UploadQueueEntity>

    /**
     * Get pending uploads with a specific batch ID.
     */
    @Query("""
        SELECT * FROM upload_queue 
        WHERE status = 'PENDING' AND batch_id = :batchId
        ORDER BY created_at ASC
    """)
    suspend fun getPendingUploadsByBatch(batchId: String): List<UploadQueueEntity>

    /**
     * Get all failed uploads that can be retried.
     */
    @Query("""
        SELECT * FROM upload_queue 
        WHERE status = 'FAILED' AND retry_count < max_retries
        ORDER BY last_attempt_at ASC
    """)
    suspend fun getRetriableUploads(): List<UploadQueueEntity>

    /**
     * Observe upload queue status (for UI updates).
     */
    @Query("""
        SELECT * FROM upload_queue 
        WHERE status IN ('PENDING', 'UPLOADING', 'FAILED')
        ORDER BY created_at DESC
    """)
    fun observeActiveUploads(): Flow<List<UploadQueueEntity>>

    /**
     * Get upload queue entry by ID.
     */
    @Query("SELECT * FROM upload_queue WHERE id = :id")
    suspend fun getById(id: Long): UploadQueueEntity?

    /**
     * Get upload queue entry by image ID.
     */
    @Query("SELECT * FROM upload_queue WHERE image_id = :imageId LIMIT 1")
    suspend fun getByImageId(imageId: Long): UploadQueueEntity?

    /**
     * Update upload status.
     */
    @Query("""
        UPDATE upload_queue 
        SET status = :status, 
            last_attempt_at = :timestamp
        WHERE id = :id
    """)
    suspend fun updateStatus(id: Long, status: UploadStatus, timestamp: Date = Date())

    /**
     * Mark upload as success and store server image ID.
     */
    @Query("""
        UPDATE upload_queue 
        SET status = 'SUCCESS', 
            server_image_id = :serverImageId,
            completed_at = :timestamp
        WHERE id = :id
    """)
    suspend fun markAsSuccess(id: Long, serverImageId: Int, timestamp: Date = Date())

    /**
     * Mark upload as failed and increment retry count.
     */
    @Query("""
        UPDATE upload_queue 
        SET status = 'FAILED', 
            retry_count = retry_count + 1,
            error_message = :errorMessage,
            last_attempt_at = :timestamp
        WHERE id = :id
    """)
    suspend fun markAsFailed(id: Long, errorMessage: String, timestamp: Date = Date())

    /**
     * Reset failed upload to pending (for manual retry).
     */
    @Query("""
        UPDATE upload_queue 
        SET status = 'PENDING', 
            error_message = NULL
        WHERE id = :id
    """)
    suspend fun retryUpload(id: Long)

    /**
     * Delete upload queue entry.
     */
    @Query("DELETE FROM upload_queue WHERE id = :id")
    suspend fun delete(id: Long)

    /**
     * Delete all successful uploads older than specified date.
     */
    @Query("""
        DELETE FROM upload_queue 
        WHERE status = 'SUCCESS' AND completed_at < :beforeDate
    """)
    suspend fun deleteOldSuccessfulUploads(beforeDate: Date)

    /**
     * Get count of pending uploads.
     */
    @Query("SELECT COUNT(*) FROM upload_queue WHERE status = 'PENDING'")
    suspend fun getPendingCount(): Int

    /**
     * Get count of failed uploads.
     */
    @Query("SELECT COUNT(*) FROM upload_queue WHERE status = 'FAILED' AND retry_count < max_retries")
    suspend fun getFailedCount(): Int

    /**
     * Get upload statistics (for UI display).
     */
    @Query("""
        SELECT 
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'UPLOADING' THEN 1 ELSE 0 END) as uploading,
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
        FROM upload_queue
    """)
    suspend fun getStats(): UploadStats

    /**
     * Delete all cancelled uploads.
     */
    @Query("DELETE FROM upload_queue WHERE status = 'CANCELLED'")
    suspend fun deleteCancelled()
}

/**
 * Upload statistics data class.
 */
data class UploadStats(
    val pending: Int,
    val uploading: Int,
    val success: Int,
    val failed: Int
)
