package com.federated.client.data.local.db.entities

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Entity representing training metrics for each round.
 *
 * @property id Unique identifier for the metric
 * @property sessionId Foreign key to training session
 * @property roundNumber Training round number
 * @property loss Loss value for this round
 * @property accuracy Accuracy value for this round
 * @property valLoss Validation loss (if available)
 * @property valAccuracy Validation accuracy (if available)
 * @property timestamp Timestamp when metrics were recorded
 * @property duration Duration of round in milliseconds
 */
@Entity(
    tableName = "metrics",
    foreignKeys = [
        ForeignKey(
            entity = TrainingSessionEntity::class,
            parentColumns = ["id"],
            childColumns = ["session_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["session_id"])]
)
data class MetricsEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "session_id")
    val sessionId: Long,
    
    @ColumnInfo(name = "round_number")
    val roundNumber: Int,
    
    @ColumnInfo(name = "loss")
    val loss: Float,
    
    @ColumnInfo(name = "accuracy")
    val accuracy: Float,
    
    @ColumnInfo(name = "val_loss")
    val valLoss: Float? = null,
    
    @ColumnInfo(name = "val_accuracy")
    val valAccuracy: Float? = null,
    
    @ColumnInfo(name = "timestamp")
    val timestamp: Long = System.currentTimeMillis(),
    
    @ColumnInfo(name = "duration")
    val duration: Long? = null
)
