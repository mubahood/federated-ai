package com.federated.client.di

import android.content.Context
import com.federated.client.data.local.storage.CacheManager
import com.federated.client.data.local.storage.ImageStorageManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt module for storage-related dependencies.
 */
@Module
@InstallIn(SingletonComponent::class)
object StorageModule {

    @Provides
    @Singleton
    fun provideImageStorageManager(
        @ApplicationContext context: Context
    ): ImageStorageManager {
        return ImageStorageManager(context)
    }

    @Provides
    @Singleton
    fun provideCacheManager(
        @ApplicationContext context: Context
    ): CacheManager {
        return CacheManager(context)
    }
}
