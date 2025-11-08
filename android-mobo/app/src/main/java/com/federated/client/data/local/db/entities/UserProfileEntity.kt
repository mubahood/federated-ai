package com.federated.client.data.local.db.entities

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity representing the user profile.
 *
 * @property id Unique identifier (always 1 for single user)
 * @property userId Server-side user ID
 * @property username Username
 * @property email Email address
 * @property deviceId Unique device identifier
 * @property createdAt Account creation timestamp
 * @property lastSyncAt Last sync with server timestamp
 * @property totalImagesContributed Total images contributed
 * @property totalTrainingRounds Total training rounds completed
 * @property contributionScore User contribution score
 * @property currentStreak Current training streak in days
 * @property longestStreak Longest training streak in days
 * @property lastTrainingDate Last training date (for streak calculation)
 */
@Entity(tableName = "user_profile")
data class UserProfileEntity(
    @PrimaryKey
    val id: Long = 1, // Single user profile
    
    @ColumnInfo(name = "user_id")
    val userId: String? = null,
    
    @ColumnInfo(name = "username")
    val username: String? = null,
    
    @ColumnInfo(name = "email")
    val email: String? = null,
    
    @ColumnInfo(name = "device_id")
    val deviceId: String,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),
    
    @ColumnInfo(name = "last_sync_at")
    val lastSyncAt: Long? = null,
    
    @ColumnInfo(name = "total_images_contributed")
    val totalImagesContributed: Int = 0,
    
    @ColumnInfo(name = "total_training_rounds")
    val totalTrainingRounds: Int = 0,
    
    @ColumnInfo(name = "contribution_score")
    val contributionScore: Int = 0,
    
    @ColumnInfo(name = "current_streak")
    val currentStreak: Int = 0,
    
    @ColumnInfo(name = "longest_streak")
    val longestStreak: Int = 0,
    
    @ColumnInfo(name = "last_training_date")
    val lastTrainingDate: Long? = null
)
