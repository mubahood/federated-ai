package com.federated.client.data.local.db.dao

import androidx.room.*
import com.federated.client.data.local.db.entities.UserProfileEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for UserProfileEntity.
 * Provides methods to interact with the user_profile table.
 */
@Dao
interface UserProfileDao {
    
    /**
     * Insert or update user profile.
     * @return The row ID of the inserted/updated profile
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(profile: UserProfileEntity): Long
    
    /**
     * Update user profile.
     */
    @Update
    suspend fun update(profile: UserProfileEntity)
    
    /**
     * Delete user profile.
     */
    @Delete
    suspend fun delete(profile: UserProfileEntity)
    
    /**
     * Get user profile.
     */
    @Query("SELECT * FROM user_profile WHERE id = 1")
    suspend fun getProfile(): UserProfileEntity?
    
    /**
     * Get user profile as Flow for reactive updates.
     */
    @Query("SELECT * FROM user_profile WHERE id = 1")
    fun getProfileFlow(): Flow<UserProfileEntity?>
    
    /**
     * Update username.
     */
    @Query("UPDATE user_profile SET username = :username WHERE id = 1")
    suspend fun updateUsername(username: String)
    
    /**
     * Update email.
     */
    @Query("UPDATE user_profile SET email = :email WHERE id = 1")
    suspend fun updateEmail(email: String)
    
    /**
     * Update user ID.
     */
    @Query("UPDATE user_profile SET user_id = :userId WHERE id = 1")
    suspend fun updateUserId(userId: String)
    
    /**
     * Update last sync timestamp.
     */
    @Query("UPDATE user_profile SET last_sync_at = :timestamp WHERE id = 1")
    suspend fun updateLastSyncAt(timestamp: Long)
    
    /**
     * Increment total images contributed.
     */
    @Query("UPDATE user_profile SET total_images_contributed = total_images_contributed + :count WHERE id = 1")
    suspend fun incrementImagesContributed(count: Int = 1)
    
    /**
     * Increment total training rounds.
     */
    @Query("UPDATE user_profile SET total_training_rounds = total_training_rounds + :count WHERE id = 1")
    suspend fun incrementTrainingRounds(count: Int = 1)
    
    /**
     * Update contribution score.
     */
    @Query("UPDATE user_profile SET contribution_score = :score WHERE id = 1")
    suspend fun updateContributionScore(score: Int)
    
    /**
     * Increment contribution score.
     */
    @Query("UPDATE user_profile SET contribution_score = contribution_score + :points WHERE id = 1")
    suspend fun incrementContributionScore(points: Int)
    
    /**
     * Update training streak.
     */
    @Query("UPDATE user_profile SET current_streak = :streak, longest_streak = :longestStreak, last_training_date = :date WHERE id = 1")
    suspend fun updateStreak(streak: Int, longestStreak: Int, date: Long)
    
    /**
     * Reset current streak.
     */
    @Query("UPDATE user_profile SET current_streak = 0 WHERE id = 1")
    suspend fun resetCurrentStreak()
    
    /**
     * Delete user profile.
     */
    @Query("DELETE FROM user_profile WHERE id = 1")
    suspend fun deleteProfile()
    
    /**
     * Check if profile exists.
     */
    @Query("SELECT COUNT(*) FROM user_profile WHERE id = 1")
    suspend fun profileExists(): Int
}
