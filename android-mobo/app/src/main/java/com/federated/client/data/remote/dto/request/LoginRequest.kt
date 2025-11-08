package com.federated.client.data.remote.dto.request

import com.google.gson.annotations.SerializedName

/**
 * Request DTO for user login.
 */
data class LoginRequest(
    @SerializedName("username")
    val username: String,
    
    @SerializedName("password")
    val password: String
)
