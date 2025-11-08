package com.federated.client.data.remote.dto.request

import com.google.gson.annotations.SerializedName

/**
 * Request DTO for user registration.
 */
data class RegisterRequest(
    @SerializedName("username")
    val username: String,
    
    @SerializedName("email")
    val email: String,
    
    @SerializedName("password")
    val password: String,
    
    @SerializedName("device_id")
    val deviceId: String
)
