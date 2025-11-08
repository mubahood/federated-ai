package com.federated.client.data.local.db.dao

import androidx.room.*
import com.federated.client.data.local.db.entities.ImageEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for ImageEntity.
 * Provides methods to interact with the images table.
 */
@Dao
interface ImageDao {
    
    /**
     * Insert a new image.
     * @return The row ID of the inserted image
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(image: ImageEntity): Long
    
    /**
     * Insert multiple images.
     * @return List of row IDs
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(images: List<ImageEntity>): List<Long>
    
    /**
     * Update an existing image.
     */
    @Update
    suspend fun update(image: ImageEntity)
    
    /**
     * Delete an image.
     */
    @Delete
    suspend fun delete(image: ImageEntity)
    
    /**
     * Delete an image by ID.
     */
    @Query("DELETE FROM images WHERE id = :imageId")
    suspend fun deleteById(imageId: Long)
    
    /**
     * Get an image by ID.
     */
    @Query("SELECT * FROM images WHERE id = :imageId")
    suspend fun getById(imageId: Long): ImageEntity?
    
    /**
     * Get all images as Flow for reactive updates.
     */
    @Query("SELECT * FROM images ORDER BY captured_at DESC")
    fun getAllFlow(): Flow<List<ImageEntity>>
    
    /**
     * Get all images.
     */
    @Query("SELECT * FROM images ORDER BY captured_at DESC")
    suspend fun getAll(): List<ImageEntity>
    
    /**
     * Get labeled images.
     */
    @Query("SELECT * FROM images WHERE is_labeled = 1 ORDER BY captured_at DESC")
    fun getLabeledFlow(): Flow<List<ImageEntity>>
    
    /**
     * Get unlabeled images.
     */
    @Query("SELECT * FROM images WHERE is_labeled = 0 ORDER BY captured_at DESC")
    fun getUnlabeledFlow(): Flow<List<ImageEntity>>
    
    /**
     * Get images by category.
     */
    @Query("SELECT * FROM images WHERE category = :category ORDER BY captured_at DESC")
    fun getByCategory(category: String): Flow<List<ImageEntity>>
    
    /**
     * Get images that haven't been uploaded.
     */
    @Query("SELECT * FROM images WHERE is_uploaded = 0 AND is_labeled = 1")
    suspend fun getNotUploaded(): List<ImageEntity>
    
    /**
     * Get total image count.
     */
    @Query("SELECT COUNT(*) FROM images")
    suspend fun getCount(): Int
    
    /**
     * Get labeled image count.
     */
    @Query("SELECT COUNT(*) FROM images WHERE is_labeled = 1")
    suspend fun getLabeledCount(): Int
    
    /**
     * Get count by category.
     */
    @Query("SELECT COUNT(*) FROM images WHERE category = :category")
    suspend fun getCountByCategory(category: String): Int
    
    /**
     * Get all unique categories.
     */
    @Query("SELECT DISTINCT category FROM images WHERE category IS NOT NULL ORDER BY category")
    suspend fun getAllCategories(): List<String>
    
    /**
     * Delete all images.
     */
    @Query("DELETE FROM images")
    suspend fun deleteAll()
    
    /**
     * Delete old images (older than timestamp).
     */
    @Query("DELETE FROM images WHERE captured_at < :timestamp")
    suspend fun deleteOlderThan(timestamp: Long)
}
