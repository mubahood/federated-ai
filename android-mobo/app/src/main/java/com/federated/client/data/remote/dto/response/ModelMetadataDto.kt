package com.federated.client.data.remote.dto.response

import com.google.gson.annotations.SerializedName

/**
 * DTO for model metadata response from /api/models/latest/
 * 
 * Server returns information about the latest available model version,
 * including whether an update is required for the current device.
 */
data class ModelMetadataDto(
    /**
     * Latest model version (semantic versioning: "1.2.0")
     */
    @SerializedName("version")
    val version: String,
    
    /**
     * SHA256 checksum for file integrity verification
     */
    @SerializedName("checksum")
    val checksum: String,
    
    /**
     * Full URL to download the model file
     * Example: "http://localhost:8000/api/models/download/1.2.0/"
     */
    @SerializedName("download_url")
    val downloadUrl: String,
    
    /**
     * Whether the device needs to update its model
     * Calculated by comparing device version vs server version
     */
    @SerializedName("requires_update")
    val requiresUpdate: Boolean,
    
    /**
     * Model file size in bytes
     */
    @SerializedName("file_size")
    val fileSize: Long,
    
    /**
     * When the model was released (ISO 8601 format)
     * Example: "2025-11-07T10:30:00Z"
     */
    @SerializedName("released_at")
    val releasedAt: String,
    
    /**
     * Model accuracy percentage (0.0 to 100.0)
     * Optional field, may be null for new models
     */
    @SerializedName("accuracy")
    val accuracy: Double? = null,
    
    /**
     * User-friendly description of changes in this version
     * Optional field
     */
    @SerializedName("description")
    val description: String? = null
)
