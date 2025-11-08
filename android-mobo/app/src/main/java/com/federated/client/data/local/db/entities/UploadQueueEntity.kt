package com.federated.client.data.local.db.entities

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.Date

/**
 * Database entity for tracking pending image uploads.
 * 
 * Stores images that need to be uploaded to the server,
 * along with retry logic and upload status tracking.
 * 
 * This enables:
 * - Offline image capture with later sync
 * - Batch upload optimization
 * - Retry mechanism for failed uploads
 * - Upload progress tracking
 */
@Entity(
    tableName = "upload_queue",
    foreignKeys = [
        ForeignKey(
            entity = ImageEntity::class,
            parentColumns = ["id"],
            childColumns = ["image_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["image_id"]),
        Index(value = ["status"]),
        Index(value = ["batch_id"]),
        Index(value = ["created_at"])
    ]
)
data class UploadQueueEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    /**
     * Reference to ImageEntity that needs to be uploaded
     */
    @ColumnInfo(name = "image_id")
    val imageId: Long,
    
    /**
     * Upload status: PENDING, UPLOADING, SUCCESS, FAILED
     */
    @ColumnInfo(name = "status")
    val status: UploadStatus,
    
    /**
     * Batch identifier for grouping uploads
     * Images with same batch_id are uploaded together
     */
    @ColumnInfo(name = "batch_id")
    val batchId: String? = null,
    
    /**
     * Number of upload attempts
     */
    @ColumnInfo(name = "retry_count")
    val retryCount: Int = 0,
    
    /**
     * Maximum number of retries before giving up
     */
    @ColumnInfo(name = "max_retries")
    val maxRetries: Int = 3,
    
    /**
     * Error message from last failed attempt
     */
    @ColumnInfo(name = "error_message")
    val errorMessage: String? = null,
    
    /**
     * Server-assigned TrainingImage ID after successful upload
     */
    @ColumnInfo(name = "server_image_id")
    val serverImageId: Int? = null,
    
    /**
     * When the upload was queued
     */
    @ColumnInfo(name = "created_at")
    val createdAt: Date = Date(),
    
    /**
     * Last upload attempt timestamp
     */
    @ColumnInfo(name = "last_attempt_at")
    val lastAttemptAt: Date? = null,
    
    /**
     * When the upload successfully completed
     */
    @ColumnInfo(name = "completed_at")
    val completedAt: Date? = null,
    
    /**
     * Priority for upload (higher = more important)
     */
    @ColumnInfo(name = "priority")
    val priority: Int = 0
)

/**
 * Upload status enum
 */
enum class UploadStatus {
    /**
     * Waiting to be uploaded
     */
    PENDING,
    
    /**
     * Currently uploading
     */
    UPLOADING,
    
    /**
     * Successfully uploaded to server
     */
    SUCCESS,
    
    /**
     * Upload failed (will retry if retryCount < maxRetries)
     */
    FAILED,
    
    /**
     * Cancelled by user
     */
    CANCELLED
}
