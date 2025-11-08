package com.federated.client.di

import android.content.Context
import com.federated.client.BuildConfig
import com.federated.client.data.local.db.AppDatabase
import com.federated.client.data.local.prefs.PreferencesManager
import com.federated.client.data.remote.api.ModelApi
import com.federated.client.data.remote.api.TrainingApi
import com.federated.client.data.repository.UploadQueueManager
import com.federated.client.ml.pytorch.ModelDownloadManager
import com.federated.client.ml.pytorch.ModelUpdateManager
import com.federated.client.ml.pytorch.PyTorchModelManager
import com.google.gson.Gson
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Dependency injection module for ML components.
 * 
 * Provides singleton instances of:
 * - PyTorchModelManager: For on-device inference
 * - ModelDownloadManager: For downloading models from API (legacy)
 * - ModelUpdateManager: For checking updates and hot-swapping models
 * - UploadQueueManager: For queuing and uploading training images
 */
@Module
@InstallIn(SingletonComponent::class)
object MLModule {

    /**
     * Provides PyTorch model manager for inference.
     * Singleton to keep model loaded in memory.
     */
    @Provides
    @Singleton
    fun providePyTorchModelManager(
        @ApplicationContext context: Context
    ): PyTorchModelManager {
        return PyTorchModelManager(context)
    }

    /**
     * Provides model download manager (legacy).
     * Singleton to manage downloads and cache.
     * 
     * Note: Consider using ModelUpdateManager for new features.
     */
    @Provides
    @Singleton
    fun provideModelDownloadManager(
        @ApplicationContext context: Context,
        preferencesManager: PreferencesManager
    ): ModelDownloadManager {
        // Get base URL without /api/ suffix for model endpoint
        val baseUrl = BuildConfig.BASE_URL.removeSuffix("api/").removeSuffix("/")
        
        // Auth token will be null initially, ModelDownloadManager will handle it
        // Token is needed for authenticated downloads but model can work without it
        return ModelDownloadManager(
            context = context,
            baseUrl = baseUrl,
            authToken = null
        )
    }

    /**
     * Provides model update manager for checking updates and hot-swapping.
     * Singleton to manage model lifecycle.
     * 
     * Features:
     * - Check for updates from server
     * - Download new model versions
     * - Verify checksums
     * - Hot-swap models at runtime
     * - Rollback on failure
     */
    @Provides
    @Singleton
    fun provideModelUpdateManager(
        @ApplicationContext context: Context,
        modelApi: ModelApi,
        preferencesManager: PreferencesManager,
        modelManager: PyTorchModelManager
    ): ModelUpdateManager {
        return ModelUpdateManager(
            context = context,
            modelApi = modelApi,
            preferencesManager = preferencesManager,
            modelManager = modelManager
        )
    }

    /**
     * Provides upload queue manager for managing training image uploads.
     * Singleton to manage upload queue and batch operations.
     * 
     * Features:
     * - Queue images for batch upload
     * - Compress images
     * - Automatic retry on failure
     * - Offline support
     * - Progress tracking
     */
    @Provides
    @Singleton
    fun provideUploadQueueManager(
        @ApplicationContext context: Context,
        database: AppDatabase,
        trainingApi: TrainingApi,
        preferencesManager: PreferencesManager,
        gson: Gson
    ): UploadQueueManager {
        return UploadQueueManager(
            context = context,
            uploadQueueDao = database.uploadQueueDao(),
            imageDao = database.imageDao(),
            trainingApi = trainingApi,
            preferencesManager = preferencesManager,
            gson = gson
        )
    }
}
