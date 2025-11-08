package com.federated.client.data.local.storage

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for cache operations.
 * Handles cache size limits and cleanup.
 */
@Singleton
class CacheManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    companion object {
        private const val MAX_CACHE_SIZE_BYTES = 500L * 1024 * 1024 // 500 MB
        private const val CACHE_CLEANUP_THRESHOLD = 0.9f // Cleanup when 90% full
        private const val TARGET_CACHE_SIZE = 0.7f // Clean down to 70% of max
    }
    
    /**
     * Get current cache size in bytes.
     */
    suspend fun getCacheSize(): Long = withContext(Dispatchers.IO) {
        calculateDirectorySize(context.cacheDir)
    }
    
    /**
     * Get cache statistics.
     */
    suspend fun getCacheStats(): CacheStats = withContext(Dispatchers.IO) {
        val currentSize = getCacheSize()
        val maxSize = MAX_CACHE_SIZE_BYTES
        val usagePercentage = (currentSize.toFloat() / maxSize * 100).toInt()
        val fileCount = countFiles(context.cacheDir)
        
        CacheStats(
            currentSize = currentSize,
            maxSize = maxSize,
            usagePercentage = usagePercentage,
            fileCount = fileCount,
            needsCleanup = currentSize > (maxSize * CACHE_CLEANUP_THRESHOLD)
        )
    }
    
    /**
     * Check if cache needs cleanup.
     */
    suspend fun needsCleanup(): Boolean = withContext(Dispatchers.IO) {
        val currentSize = getCacheSize()
        currentSize > (MAX_CACHE_SIZE_BYTES * CACHE_CLEANUP_THRESHOLD)
    }
    
    /**
     * Perform cache cleanup.
     * Removes oldest files first until target size is reached.
     * 
     * @return Number of files deleted
     */
    suspend fun cleanup(): Int = withContext(Dispatchers.IO) {
        val targetSize = (MAX_CACHE_SIZE_BYTES * TARGET_CACHE_SIZE).toLong()
        var currentSize = getCacheSize()
        
        if (currentSize <= targetSize) {
            return@withContext 0
        }
        
        // Get all files sorted by last modified (oldest first)
        val files = getAllFiles(context.cacheDir)
            .sortedBy { it.lastModified() }
        
        var deletedCount = 0
        for (file in files) {
            if (currentSize <= targetSize) {
                break
            }
            
            val fileSize = file.length()
            if (file.delete()) {
                currentSize -= fileSize
                deletedCount++
            }
        }
        
        deletedCount
    }
    
    /**
     * Auto cleanup if threshold is exceeded.
     * Call this periodically or after significant cache writes.
     * 
     * @return true if cleanup was performed
     */
    suspend fun autoCleanup(): Boolean = withContext(Dispatchers.IO) {
        if (needsCleanup()) {
            cleanup()
            true
        } else {
            false
        }
    }
    
    /**
     * Clear all cache.
     * 
     * @return true if successful
     */
    suspend fun clearAll(): Boolean = withContext(Dispatchers.IO) {
        try {
            context.cacheDir.deleteRecursively()
            context.cacheDir.mkdirs()
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Clear cache for specific subdirectory.
     * 
     * @param subdirName Name of subdirectory to clear
     * @return true if successful
     */
    suspend fun clearSubdir(subdirName: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val subdir = File(context.cacheDir, subdirName)
            if (subdir.exists()) {
                subdir.deleteRecursively()
                subdir.mkdirs()
            }
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Delete files older than specified age.
     * 
     * @param maxAgeMillis Maximum age in milliseconds
     * @return Number of files deleted
     */
    suspend fun deleteOlderThan(maxAgeMillis: Long): Int = withContext(Dispatchers.IO) {
        val cutoffTime = System.currentTimeMillis() - maxAgeMillis
        val files = getAllFiles(context.cacheDir)
        
        var deletedCount = 0
        for (file in files) {
            if (file.lastModified() < cutoffTime) {
                if (file.delete()) {
                    deletedCount++
                }
            }
        }
        
        deletedCount
    }
    
    /**
     * Calculate total size of directory recursively.
     */
    private fun calculateDirectorySize(directory: File): Long {
        var size = 0L
        
        directory.walkTopDown().forEach { file ->
            if (file.isFile) {
                size += file.length()
            }
        }
        
        return size
    }
    
    /**
     * Count total files in directory recursively.
     */
    private fun countFiles(directory: File): Int {
        return directory.walkTopDown().count { it.isFile }
    }
    
    /**
     * Get all files in directory recursively.
     */
    private fun getAllFiles(directory: File): List<File> {
        return directory.walkTopDown()
            .filter { it.isFile }
            .toList()
    }
}

/**
 * Cache statistics data class.
 */
data class CacheStats(
    val currentSize: Long,
    val maxSize: Long,
    val usagePercentage: Int,
    val fileCount: Int,
    val needsCleanup: Boolean
) {
    /**
     * Get current size formatted as human-readable string.
     */
    fun getCurrentSizeFormatted(): String = formatBytes(currentSize)
    
    /**
     * Get max size formatted as human-readable string.
     */
    fun getMaxSizeFormatted(): String = formatBytes(maxSize)
    
    /**
     * Get available space.
     */
    fun getAvailableSpace(): Long = maxSize - currentSize
    
    /**
     * Get available space formatted.
     */
    fun getAvailableSpaceFormatted(): String = formatBytes(getAvailableSpace())
    
    private fun formatBytes(bytes: Long): String {
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> "${bytes / 1024} KB"
            bytes < 1024 * 1024 * 1024 -> "${bytes / (1024 * 1024)} MB"
            else -> String.format("%.2f GB", bytes / (1024.0 * 1024.0 * 1024.0))
        }
    }
}
