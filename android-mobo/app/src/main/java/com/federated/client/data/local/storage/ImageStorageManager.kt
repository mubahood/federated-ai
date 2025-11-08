package com.federated.client.data.local.storage

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for image storage operations.
 * Handles saving, loading, and deleting images from local storage.
 */
@Singleton
class ImageStorageManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    companion object {
        private const val IMAGES_DIR = "images"
        private const val THUMBNAILS_DIR = "thumbnails"
        private const val COMPRESSION_QUALITY = 90
        private const val THUMBNAIL_SIZE = 200
        private const val MAX_IMAGE_SIZE = 1920 // Max width/height for stored images
    }
    
    private val imagesDir: File by lazy {
        File(context.filesDir, IMAGES_DIR).apply {
            if (!exists()) mkdirs()
        }
    }
    
    private val thumbnailsDir: File by lazy {
        File(context.filesDir, THUMBNAILS_DIR).apply {
            if (!exists()) mkdirs()
        }
    }
    
    /**
     * Save image to internal storage with compression.
     * 
     * @param bitmap The bitmap to save
     * @param filename Optional filename (generates UUID if null)
     * @return URI of the saved image, or null if failed
     */
    suspend fun saveImage(
        bitmap: Bitmap,
        filename: String? = null
    ): Result<ImageSaveResult> = withContext(Dispatchers.IO) {
        try {
            val fileName = filename ?: "${UUID.randomUUID()}.jpg"
            val imageFile = File(imagesDir, fileName)
            val thumbnailFile = File(thumbnailsDir, "thumb_$fileName")
            
            // Scale down if image is too large
            val scaledBitmap = scaleDownBitmap(bitmap, MAX_IMAGE_SIZE)
            
            // Save full image
            FileOutputStream(imageFile).use { out ->
                scaledBitmap.compress(Bitmap.CompressFormat.JPEG, COMPRESSION_QUALITY, out)
            }
            
            // Generate and save thumbnail
            val thumbnail = createThumbnail(scaledBitmap, THUMBNAIL_SIZE)
            FileOutputStream(thumbnailFile).use { out ->
                thumbnail.compress(Bitmap.CompressFormat.JPEG, COMPRESSION_QUALITY, out)
            }
            
            // Clean up bitmaps if we created new ones
            if (scaledBitmap != bitmap) {
                scaledBitmap.recycle()
            }
            thumbnail.recycle()
            
            Result.success(
                ImageSaveResult(
                    uri = Uri.fromFile(imageFile).toString(),
                    thumbnailUri = Uri.fromFile(thumbnailFile).toString(),
                    width = scaledBitmap.width,
                    height = scaledBitmap.height,
                    fileSize = imageFile.length()
                )
            )
        } catch (e: IOException) {
            Result.failure(e)
        }
    }
    
    /**
     * Load image from storage.
     * 
     * @param uri URI of the image to load
     * @return Bitmap or null if not found
     */
    suspend fun loadImage(uri: String): Bitmap? = withContext(Dispatchers.IO) {
        try {
            val file = File(Uri.parse(uri).path ?: return@withContext null)
            if (!file.exists()) return@withContext null
            
            BitmapFactory.decodeFile(file.absolutePath)
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Load thumbnail image.
     * 
     * @param thumbnailUri URI of the thumbnail
     * @return Bitmap or null if not found
     */
    suspend fun loadThumbnail(thumbnailUri: String): Bitmap? = withContext(Dispatchers.IO) {
        try {
            val file = File(Uri.parse(thumbnailUri).path ?: return@withContext null)
            if (!file.exists()) return@withContext null
            
            BitmapFactory.decodeFile(file.absolutePath)
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Delete image and its thumbnail.
     * 
     * @param uri URI of the image to delete
     * @return true if deleted successfully
     */
    suspend fun deleteImage(uri: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val imageFile = File(Uri.parse(uri).path ?: return@withContext false)
            val thumbnailFile = File(thumbnailsDir, "thumb_${imageFile.name}")
            
            var success = true
            if (imageFile.exists()) {
                success = imageFile.delete()
            }
            if (thumbnailFile.exists()) {
                success = thumbnailFile.delete() && success
            }
            success
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Delete multiple images.
     * 
     * @param uris List of URIs to delete
     * @return Number of successfully deleted images
     */
    suspend fun deleteImages(uris: List<String>): Int = withContext(Dispatchers.IO) {
        var deletedCount = 0
        uris.forEach { uri ->
            if (deleteImage(uri)) {
                deletedCount++
            }
        }
        deletedCount
    }
    
    /**
     * Get total storage size used by images.
     * 
     * @return Size in bytes
     */
    suspend fun getStorageSize(): Long = withContext(Dispatchers.IO) {
        val imagesSize = imagesDir.walkTopDown().filter { it.isFile }.map { it.length() }.sum()
        val thumbnailsSize = thumbnailsDir.walkTopDown().filter { it.isFile }.map { it.length() }.sum()
        imagesSize + thumbnailsSize
    }
    
    /**
     * Get number of stored images.
     * 
     * @return Count of image files
     */
    suspend fun getImageCount(): Int = withContext(Dispatchers.IO) {
        imagesDir.listFiles()?.size ?: 0
    }
    
    /**
     * Check if image exists.
     * 
     * @param uri URI to check
     * @return true if image exists
     */
    suspend fun imageExists(uri: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val file = File(Uri.parse(uri).path ?: return@withContext false)
            file.exists()
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Delete all images.
     */
    suspend fun clearAll(): Boolean = withContext(Dispatchers.IO) {
        try {
            imagesDir.deleteRecursively()
            thumbnailsDir.deleteRecursively()
            imagesDir.mkdirs()
            thumbnailsDir.mkdirs()
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Scale down bitmap if it exceeds max size.
     */
    private fun scaleDownBitmap(bitmap: Bitmap, maxSize: Int): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        
        if (width <= maxSize && height <= maxSize) {
            return bitmap
        }
        
        val scale = if (width > height) {
            maxSize.toFloat() / width
        } else {
            maxSize.toFloat() / height
        }
        
        val newWidth = (width * scale).toInt()
        val newHeight = (height * scale).toInt()
        
        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }
    
    /**
     * Create thumbnail from bitmap.
     */
    private fun createThumbnail(bitmap: Bitmap, size: Int): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        
        val scale = if (width > height) {
            size.toFloat() / width
        } else {
            size.toFloat() / height
        }
        
        val newWidth = (width * scale).toInt()
        val newHeight = (height * scale).toInt()
        
        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }
}

/**
 * Result of saving an image.
 */
data class ImageSaveResult(
    val uri: String,
    val thumbnailUri: String,
    val width: Int,
    val height: Int,
    val fileSize: Long
)
