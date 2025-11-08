package com.federated.client.data.remote.dto.response

import com.google.gson.annotations.SerializedName

/**
 * Response DTO for authentication endpoints.
 */
data class AuthResponse(
    @SerializedName("token")
    val token: String,
    
    @SerializedName("user_id")
    val userId: String,
    
    @SerializedName("username")
    val username: String,
    
    @SerializedName("email")
    val email: String
)
