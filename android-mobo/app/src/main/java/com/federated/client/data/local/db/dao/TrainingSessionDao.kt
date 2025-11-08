package com.federated.client.data.local.db.dao

import androidx.room.*
import com.federated.client.data.local.db.entities.TrainingSessionEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for TrainingSessionEntity.
 * Provides methods to interact with the training_sessions table.
 */
@Dao
interface TrainingSessionDao {
    
    /**
     * Insert a new training session.
     * @return The row ID of the inserted session
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(session: TrainingSessionEntity): Long
    
    /**
     * Update an existing training session.
     */
    @Update
    suspend fun update(session: TrainingSessionEntity)
    
    /**
     * Delete a training session.
     */
    @Delete
    suspend fun delete(session: TrainingSessionEntity)
    
    /**
     * Delete a training session by ID.
     */
    @Query("DELETE FROM training_sessions WHERE id = :sessionId")
    suspend fun deleteById(sessionId: Long)
    
    /**
     * Get a training session by ID.
     */
    @Query("SELECT * FROM training_sessions WHERE id = :sessionId")
    suspend fun getById(sessionId: Long): TrainingSessionEntity?
    
    /**
     * Get a training session by ID as Flow.
     */
    @Query("SELECT * FROM training_sessions WHERE id = :sessionId")
    fun getByIdFlow(sessionId: Long): Flow<TrainingSessionEntity?>
    
    /**
     * Get all training sessions.
     */
    @Query("SELECT * FROM training_sessions ORDER BY start_time DESC")
    fun getAllFlow(): Flow<List<TrainingSessionEntity>>
    
    /**
     * Get all training sessions.
     */
    @Query("SELECT * FROM training_sessions ORDER BY start_time DESC")
    suspend fun getAll(): List<TrainingSessionEntity>
    
    /**
     * Get training sessions by status.
     */
    @Query("SELECT * FROM training_sessions WHERE status = :status ORDER BY start_time DESC")
    fun getByStatus(status: String): Flow<List<TrainingSessionEntity>>
    
    /**
     * Get the most recent training session.
     */
    @Query("SELECT * FROM training_sessions ORDER BY start_time DESC LIMIT 1")
    suspend fun getLatest(): TrainingSessionEntity?
    
    /**
     * Get the most recent training session as Flow.
     */
    @Query("SELECT * FROM training_sessions ORDER BY start_time DESC LIMIT 1")
    fun getLatestFlow(): Flow<TrainingSessionEntity?>
    
    /**
     * Get active/running training session.
     */
    @Query("SELECT * FROM training_sessions WHERE status = 'running' LIMIT 1")
    suspend fun getActiveSession(): TrainingSessionEntity?
    
    /**
     * Get active/running training session as Flow.
     */
    @Query("SELECT * FROM training_sessions WHERE status = 'running' LIMIT 1")
    fun getActiveSessionFlow(): Flow<TrainingSessionEntity?>
    
    /**
     * Get completed training sessions.
     */
    @Query("SELECT * FROM training_sessions WHERE status = 'completed' ORDER BY start_time DESC")
    fun getCompletedFlow(): Flow<List<TrainingSessionEntity>>
    
    /**
     * Get total completed rounds count.
     */
    @Query("SELECT SUM(total_rounds) FROM training_sessions WHERE status = 'completed'")
    suspend fun getTotalCompletedRounds(): Int?
    
    /**
     * Get total training sessions count.
     */
    @Query("SELECT COUNT(*) FROM training_sessions")
    suspend fun getCount(): Int
    
    /**
     * Get count by status.
     */
    @Query("SELECT COUNT(*) FROM training_sessions WHERE status = :status")
    suspend fun getCountByStatus(status: String): Int
    
    /**
     * Delete all training sessions.
     */
    @Query("DELETE FROM training_sessions")
    suspend fun deleteAll()
    
    /**
     * Delete old sessions (older than timestamp).
     */
    @Query("DELETE FROM training_sessions WHERE start_time < :timestamp")
    suspend fun deleteOlderThan(timestamp: Long)
}
