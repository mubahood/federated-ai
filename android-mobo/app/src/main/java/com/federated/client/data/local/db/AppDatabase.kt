package com.federated.client.data.local.db

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.dao.MetricsDao
import com.federated.client.data.local.db.dao.TrainingSessionDao
import com.federated.client.data.local.db.dao.UploadQueueDao
import com.federated.client.data.local.db.dao.UserProfileDao
import com.federated.client.data.local.db.entities.ImageEntity
import com.federated.client.data.local.db.entities.MetricsEntity
import com.federated.client.data.local.db.entities.TrainingSessionEntity
import com.federated.client.data.local.db.entities.UploadQueueEntity
import com.federated.client.data.local.db.entities.UserProfileEntity

/**
 * Room database for FederatedAI app.
 * Contains all local data tables.
 *
 * Version: 2 (added UploadQueue table)
 */
@Database(
    entities = [
        ImageEntity::class,
        TrainingSessionEntity::class,
        MetricsEntity::class,
        UserProfileEntity::class,
        UploadQueueEntity::class
    ],
    version = 2,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    
    /**
     * Data Access Object for images.
     */
    abstract fun imageDao(): ImageDao
    
    /**
     * Data Access Object for training sessions.
     */
    abstract fun trainingSessionDao(): TrainingSessionDao
    
    /**
     * Data Access Object for metrics.
     */
    abstract fun metricsDao(): MetricsDao
    
    /**
     * Data Access Object for user profile.
     */
    abstract fun userProfileDao(): UserProfileDao
    
    /**
     * Data Access Object for upload queue.
     */
    abstract fun uploadQueueDao(): UploadQueueDao
    
    companion object {
        const val DATABASE_NAME = "federated_ai_database"
    }
}
