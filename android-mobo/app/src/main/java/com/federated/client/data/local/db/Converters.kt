package com.federated.client.data.local.db

import androidx.room.TypeConverter
import com.federated.client.data.local.db.entities.UploadStatus
import java.util.Date

/**
 * Type converters for Room database.
 * 
 * Converts complex types to/from primitives that SQLite can store.
 */
class Converters {
    
    /**
     * Convert Long timestamp to Date.
     */
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }
    
    /**
     * Convert Date to Long timestamp.
     */
    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }
    
    /**
     * Convert String to UploadStatus enum.
     */
    @TypeConverter
    fun toUploadStatus(value: String): UploadStatus {
        return UploadStatus.valueOf(value)
    }
    
    /**
     * Convert UploadStatus enum to String.
     */
    @TypeConverter
    fun fromUploadStatus(status: UploadStatus): String {
        return status.name
    }
}
