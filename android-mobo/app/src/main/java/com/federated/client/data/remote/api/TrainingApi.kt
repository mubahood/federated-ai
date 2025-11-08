package com.federated.client.data.remote.api

import com.federated.client.data.remote.dto.request.ImageUploadRequest
import com.federated.client.data.remote.dto.response.ImageUploadResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.PartMap

/**
 * Retrofit API interface for training data endpoints.
 * 
 * Endpoints:
 * - POST /api/training/images/upload_from_mobile/ - Upload labeled images
 */
interface TrainingApi {

    /**
     * Upload multiple images with labels from mobile device.
     * 
     * Supports batch upload with the following fields:
     * - images: Array of image files (multipart)
     * - labels: JSON array of labels matching image order
     * - batch_id: Optional batch identifier
     * - client_id: Device identifier
     * - auto_validate: Whether to auto-validate images (default: false)
     * 
     * Response includes:
     * - success: Number of successfully uploaded images
     * - failed: Number of failed uploads
     * - errors: List of error messages for failed images
     * - image_ids: List of created TrainingImage IDs
     * 
     * @param images List of image files as MultipartBody.Part
     * @param labels JSON string array of labels (e.g., ["Cat", "Dog", "Person"])
     * @param batchId Optional batch identifier for grouping
     * @param clientId Device/client identifier
     * @param autoValidate Whether to auto-validate images
     * @return ImageUploadResponse with success/failure details
     */
    @Multipart
    @POST("training/images/upload_from_mobile/")
    suspend fun uploadImages(
        @Part images: List<MultipartBody.Part>,
        @Part("labels") labels: RequestBody,
        @Part("batch_id") batchId: RequestBody? = null,
        @Part("client_id") clientId: RequestBody,
        @Part("auto_validate") autoValidate: RequestBody? = null
    ): Response<ImageUploadResponse>
}
