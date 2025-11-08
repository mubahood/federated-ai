package com.federated.client.data.remote.interceptors

import com.federated.client.data.local.prefs.PreferencesManager
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * OkHttp interceptor that adds authentication token to requests.
 */
@Singleton
class AuthInterceptor @Inject constructor(
    private val preferencesManager: PreferencesManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Get auth token from preferences
        val token = runBlocking {
            preferencesManager.authToken.first()
        }

        // If no token, proceed without auth header
        if (token.isNullOrEmpty()) {
            return chain.proceed(originalRequest)
        }

        // Add auth header
        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()

        return chain.proceed(authenticatedRequest)
    }
}
