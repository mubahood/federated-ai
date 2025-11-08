package com.federated.client.di

import android.content.Context
import androidx.room.Room
import com.federated.client.data.local.db.AppDatabase
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.dao.MetricsDao
import com.federated.client.data.local.db.dao.TrainingSessionDao
import com.federated.client.data.local.db.dao.UserProfileDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt module for database-related dependencies.
 */
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideAppDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            AppDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration() // TODO: Replace with proper migrations in production
            .build()
    }

    @Provides
    @Singleton
    fun provideImageDao(database: AppDatabase): ImageDao {
        return database.imageDao()
    }

    @Provides
    @Singleton
    fun provideTrainingSessionDao(database: AppDatabase): TrainingSessionDao {
        return database.trainingSessionDao()
    }

    @Provides
    @Singleton
    fun provideMetricsDao(database: AppDatabase): MetricsDao {
        return database.metricsDao()
    }

    @Provides
    @Singleton
    fun provideUserProfileDao(database: AppDatabase): UserProfileDao {
        return database.userProfileDao()
    }
}
