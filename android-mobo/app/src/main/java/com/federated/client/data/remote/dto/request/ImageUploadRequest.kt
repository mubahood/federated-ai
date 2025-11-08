package com.federated.client.data.remote.dto.request

/**
 * DTO for image upload request to /api/training/images/upload_from_mobile/
 * 
 * This is a marker class for documentation.
 * Actual upload uses multipart/form-data with the following fields:
 * 
 * - images: MultipartBody.Part[] - Array of image files
 * - labels: String (JSON array) - Labels for each image ["Cat", "Dog", "Person"]
 * - batch_id: String (optional) - Batch identifier for grouping
 * - client_id: String - Device/client identifier
 * - auto_validate: Boolean (optional) - Whether to auto-validate images
 * 
 * Example usage in TrainingApi:
 * ```kotlin
 * val images = listOf(
 *     MultipartBody.Part.createFormData("images", "img1.jpg", imageFile1.asRequestBody()),
 *     MultipartBody.Part.createFormData("images", "img2.jpg", imageFile2.asRequestBody())
 * )
 * val labels = """["Cat", "Dog"]""".toRequestBody("application/json".toMediaTypeOrNull())
 * val clientId = "device-123".toRequestBody("text/plain".toMediaTypeOrNull())
 * 
 * trainingApi.uploadImages(images, labels, null, clientId, null)
 * ```
 */
data class ImageUploadRequest(
    val batchId: String? = null,
    val clientId: String,
    val autoValidate: Boolean = false
)
