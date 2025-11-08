package com.federated.client.data.remote.api

import com.federated.client.data.remote.dto.response.ModelMetadataDto
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Path
import retrofit2.http.Streaming

/**
 * Retrofit API interface for model management endpoints.
 * 
 * Endpoints:
 * - GET /api/models/latest/ - Check for model updates
 * - GET /api/models/download/{version}/ - Download specific model version
 */
interface ModelApi {

    /**
     * Get latest model information.
     * 
     * Headers:
     * - X-Model-Version: Current version installed on device (for update check)
     * 
     * Response includes:
     * - version: Latest model version (e.g., "1.2.0")
     * - checksum: SHA256 hash for verification
     * - download_url: URL to download the model
     * - requires_update: Boolean flag if update needed
     * - file_size: Model file size in bytes
     * - released_at: Release timestamp
     * 
     * @param currentVersion Current model version on device (optional)
     * @return ModelMetadataDto with update information
     */
    @GET("models/latest/")
    suspend fun getLatestModel(
        @Header("X-Model-Version") currentVersion: String? = null
    ): Response<ModelMetadataDto>

    /**
     * Download a specific model version.
     * 
     * Streams binary .ptl file from server.
     * Use @Streaming to prevent loading entire file into memory.
     * 
     * @param version Model version to download (e.g., "1.2.0")
     * @return ResponseBody containing the .ptl file binary data
     */
    @Streaming
    @GET("models/download/{version}/")
    suspend fun downloadModel(
        @Path("version") version: String
    ): Response<ResponseBody>
}
