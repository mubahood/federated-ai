package com.federated.client.data.remote.api

import com.federated.client.data.remote.dto.request.LoginRequest
import com.federated.client.data.remote.dto.request.RegisterRequest
import com.federated.client.data.remote.dto.response.AuthResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

/**
 * Retrofit API interface for authentication endpoints.
 */
interface AuthApi {

    @POST("auth/register/")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<AuthResponse>

    @POST("auth/login/")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<AuthResponse>

    @POST("auth/logout/")
    suspend fun logout(): Response<Unit>
}
