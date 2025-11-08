package com.federated.client.data.local.db.entities

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity representing a federated learning training session.
 *
 * @property id Unique identifier for the training session
 * @property sessionId Server-side session ID
 * @property status Training status (pending, running, completed, failed)
 * @property startTime Timestamp when training started
 * @property endTime Timestamp when training ended
 * @property currentRound Current training round
 * @property totalRounds Total number of rounds
 * @property initialLoss Initial loss value
 * @property finalLoss Final loss value
 * @property initialAccuracy Initial accuracy value
 * @property finalAccuracy Final accuracy value
 * @property numLocalEpochs Number of local epochs per round
 * @property batchSize Batch size used for training
 * @property learningRate Learning rate
 * @property totalImages Total images used in training
 * @property errorMessage Error message if training failed
 */
@Entity(tableName = "training_sessions")
data class TrainingSessionEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "session_id")
    val sessionId: String? = null,
    
    @ColumnInfo(name = "status")
    val status: String = "pending", // pending, running, completed, failed
    
    @ColumnInfo(name = "start_time")
    val startTime: Long = System.currentTimeMillis(),
    
    @ColumnInfo(name = "end_time")
    val endTime: Long? = null,
    
    @ColumnInfo(name = "current_round")
    val currentRound: Int = 0,
    
    @ColumnInfo(name = "total_rounds")
    val totalRounds: Int = 0,
    
    @ColumnInfo(name = "initial_loss")
    val initialLoss: Float? = null,
    
    @ColumnInfo(name = "final_loss")
    val finalLoss: Float? = null,
    
    @ColumnInfo(name = "initial_accuracy")
    val initialAccuracy: Float? = null,
    
    @ColumnInfo(name = "final_accuracy")
    val finalAccuracy: Float? = null,
    
    @ColumnInfo(name = "num_local_epochs")
    val numLocalEpochs: Int = 1,
    
    @ColumnInfo(name = "batch_size")
    val batchSize: Int = 32,
    
    @ColumnInfo(name = "learning_rate")
    val learningRate: Float = 0.001f,
    
    @ColumnInfo(name = "total_images")
    val totalImages: Int = 0,
    
    @ColumnInfo(name = "error_message")
    val errorMessage: String? = null
)
