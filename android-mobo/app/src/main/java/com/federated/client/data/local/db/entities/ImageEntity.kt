package com.federated.client.data.local.db.entities

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity representing a captured image in the local database.
 *
 * @property id Unique identifier for the image
 * @property uri Local file URI where image is stored
 * @property category Image category/label
 * @property isLabeled Whether the image has been labeled
 * @property capturedAt Timestamp when image was captured
 * @property width Image width in pixels
 * @property height Image height in pixels
 * @property fileSize File size in bytes
 * @property isUploaded Whether image metadata was uploaded to server
 * @property uploadedAt Timestamp when uploaded
 */
@Entity(tableName = "images")
data class ImageEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "uri")
    val uri: String,
    
    @ColumnInfo(name = "category")
    val category: String? = null,
    
    @ColumnInfo(name = "is_labeled")
    val isLabeled: Boolean = false,
    
    @ColumnInfo(name = "captured_at")
    val capturedAt: Long = System.currentTimeMillis(),
    
    @ColumnInfo(name = "width")
    val width: Int? = null,
    
    @ColumnInfo(name = "height")
    val height: Int? = null,
    
    @ColumnInfo(name = "file_size")
    val fileSize: Long? = null,
    
    @ColumnInfo(name = "is_uploaded")
    val isUploaded: Boolean = false,
    
    @ColumnInfo(name = "uploaded_at")
    val uploadedAt: Long? = null
)
