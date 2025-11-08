package com.federated.client.data.remote.dto.response

import com.google.gson.annotations.SerializedName

/**
 * DTO for image upload response from /api/training/images/upload_from_mobile/
 * 
 * Server returns detailed information about the success/failure of batch uploads.
 */
data class ImageUploadResponse(
    /**
     * Number of images successfully uploaded
     */
    @SerializedName("success")
    val successCount: Int,
    
    /**
     * Number of images that failed to upload
     */
    @SerializedName("failed")
    val failedCount: Int,
    
    /**
     * Total number of images in the batch
     */
    @SerializedName("total")
    val totalCount: Int,
    
    /**
     * List of database IDs for successfully created TrainingImage records
     */
    @SerializedName("image_ids")
    val imageIds: List<Int>,
    
    /**
     * List of error messages for failed uploads
     * Each error includes the image index and reason
     * Example: ["Image 0: Invalid format", "Image 2: Category not found"]
     */
    @SerializedName("errors")
    val errors: List<String>,
    
    /**
     * Batch ID assigned by server (if batch_id was provided in request)
     */
    @SerializedName("batch_id")
    val batchId: String? = null,
    
    /**
     * Overall success message
     */
    @SerializedName("message")
    val message: String? = null
)
