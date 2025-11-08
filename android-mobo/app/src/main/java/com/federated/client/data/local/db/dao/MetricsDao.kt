package com.federated.client.data.local.db.dao

import androidx.room.*
import com.federated.client.data.local.db.entities.MetricsEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for MetricsEntity.
 * Provides methods to interact with the metrics table.
 */
@Dao
interface MetricsDao {
    
    /**
     * Insert a new metric.
     * @return The row ID of the inserted metric
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(metric: MetricsEntity): Long
    
    /**
     * Insert multiple metrics.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(metrics: List<MetricsEntity>): List<Long>
    
    /**
     * Update an existing metric.
     */
    @Update
    suspend fun update(metric: MetricsEntity)
    
    /**
     * Delete a metric.
     */
    @Delete
    suspend fun delete(metric: MetricsEntity)
    
    /**
     * Delete a metric by ID.
     */
    @Query("DELETE FROM metrics WHERE id = :metricId")
    suspend fun deleteById(metricId: Long)
    
    /**
     * Get a metric by ID.
     */
    @Query("SELECT * FROM metrics WHERE id = :metricId")
    suspend fun getById(metricId: Long): MetricsEntity?
    
    /**
     * Get all metrics for a training session.
     */
    @Query("SELECT * FROM metrics WHERE session_id = :sessionId ORDER BY round_number ASC")
    fun getBySessionId(sessionId: Long): Flow<List<MetricsEntity>>
    
    /**
     * Get all metrics for a training session (non-Flow).
     */
    @Query("SELECT * FROM metrics WHERE session_id = :sessionId ORDER BY round_number ASC")
    suspend fun getBySessionIdSync(sessionId: Long): List<MetricsEntity>
    
    /**
     * Get metric for a specific round.
     */
    @Query("SELECT * FROM metrics WHERE session_id = :sessionId AND round_number = :roundNumber")
    suspend fun getByRound(sessionId: Long, roundNumber: Int): MetricsEntity?
    
    /**
     * Get latest metric for a training session.
     */
    @Query("SELECT * FROM metrics WHERE session_id = :sessionId ORDER BY round_number DESC LIMIT 1")
    suspend fun getLatestForSession(sessionId: Long): MetricsEntity?
    
    /**
     * Get latest metric for a training session as Flow.
     */
    @Query("SELECT * FROM metrics WHERE session_id = :sessionId ORDER BY round_number DESC LIMIT 1")
    fun getLatestForSessionFlow(sessionId: Long): Flow<MetricsEntity?>
    
    /**
     * Get all metrics.
     */
    @Query("SELECT * FROM metrics ORDER BY timestamp DESC")
    fun getAllFlow(): Flow<List<MetricsEntity>>
    
    /**
     * Get metrics count for a session.
     */
    @Query("SELECT COUNT(*) FROM metrics WHERE session_id = :sessionId")
    suspend fun getCountForSession(sessionId: Long): Int
    
    /**
     * Delete all metrics for a training session.
     */
    @Query("DELETE FROM metrics WHERE session_id = :sessionId")
    suspend fun deleteBySessionId(sessionId: Long)
    
    /**
     * Delete all metrics.
     */
    @Query("DELETE FROM metrics")
    suspend fun deleteAll()
    
    /**
     * Get average loss for a session.
     */
    @Query("SELECT AVG(loss) FROM metrics WHERE session_id = :sessionId")
    suspend fun getAverageLoss(sessionId: Long): Float?
    
    /**
     * Get average accuracy for a session.
     */
    @Query("SELECT AVG(accuracy) FROM metrics WHERE session_id = :sessionId")
    suspend fun getAverageAccuracy(sessionId: Long): Float?
}
