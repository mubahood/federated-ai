package com.federated.client.ui.screens.label

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.entities.ImageEntity
import com.federated.client.ml.pytorch.PyTorchModelManager
import com.federated.client.data.repository.UploadQueueManager
import com.federated.client.data.local.db.dao.UploadStats
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * ViewModel for Image Labeling Screen
 * Manages state for labeling unlabeled images with categories
 */
@HiltViewModel
class ImageLabelViewModel @Inject constructor(
    private val imageDao: ImageDao,
    private val modelManager: PyTorchModelManager,
    private val uploadQueueManager: UploadQueueManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(LabelUiState())
    val uiState: StateFlow<LabelUiState> = _uiState.asStateFlow()

    init {
        loadUnlabeledImages()
        observeUploadQueue()
        loadUploadStats()
    }
    
    /**
     * Observe active uploads for UI updates.
     */
    private fun observeUploadQueue() {
        viewModelScope.launch {
            uploadQueueManager.observeActiveUploads()
                .collect { activeUploads ->
                    _uiState.update { 
                        it.copy(
                            activeUploads = activeUploads.size,
                            isUploading = activeUploads.isNotEmpty()
                        ) 
                    }
                }
        }
    }
    
    /**
     * Load upload statistics.
     */
    private fun loadUploadStats() {
        viewModelScope.launch {
            try {
                val stats = uploadQueueManager.getStats()
                _uiState.update {
                    it.copy(uploadStats = stats)
                }
            } catch (e: Exception) {
                Timber.e(e, "Error loading upload stats")
            }
        }
    }

    /**
     * Load all unlabeled images from database
     */
    private fun loadUnlabeledImages() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            imageDao.getUnlabeledFlow()
                .catch { exception ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = "Failed to load images: ${exception.message}"
                        )
                    }
                }
                .collect { images ->
                    _uiState.update {
                        it.copy(
                            unlabeledImages = images,
                            currentIndex = if (images.isNotEmpty()) 0 else -1,
                            totalCount = images.size,
                            isLoading = false,
                            error = null
                        )
                    }
                }
        }
    }

    /**
     * Assign selected category to current image
     */
    fun assignLabel(category: String) {
        val currentImage = getCurrentImage() ?: return
        
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(isLoading = true) }
                
                // Update image with category and mark as labeled
                val updatedImage = currentImage.copy(
                    category = category,
                    isLabeled = true
                )
                
                imageDao.update(updatedImage)
                
                // Move to next image
                moveToNext()
                
                _uiState.update { it.copy(isLoading = false, error = null) }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "Failed to assign label: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Skip current image without labeling
     */
    fun skip() {
        moveToNext()
    }

    /**
     * Move to previous image
     */
    fun previous() {
        val state = _uiState.value
        if (state.currentIndex > 0) {
            _uiState.update {
                it.copy(
                    currentIndex = state.currentIndex - 1,
                    selectedCategory = null
                )
            }
        }
    }

    /**
     * Move to next image
     */
    private fun moveToNext() {
        val state = _uiState.value
        val nextIndex = state.currentIndex + 1
        
        if (nextIndex < state.totalCount) {
            _uiState.update {
                it.copy(
                    currentIndex = nextIndex,
                    selectedCategory = null
                )
            }
        } else {
            // No more images to label
            _uiState.update {
                it.copy(
                    currentIndex = -1,
                    selectedCategory = null
                )
            }
        }
    }

    /**
     * Select a category
     */
    fun selectCategory(category: String) {
        _uiState.update { it.copy(selectedCategory = category) }
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    /**
     * Get current image being labeled
     */
    private fun getCurrentImage(): ImageEntity? {
        val state = _uiState.value
        return if (state.currentIndex >= 0 && state.currentIndex < state.unlabeledImages.size) {
            state.unlabeledImages[state.currentIndex]
        } else {
            null
        }
    }

    /**
     * Get progress percentage
     */
    fun getProgress(): Float {
        val state = _uiState.value
        return if (state.totalCount > 0) {
            (state.currentIndex.toFloat() / state.totalCount.toFloat())
        } else {
            0f
        }
    }

    /**
     * Get progress text (e.g., "3 of 15")
     */
    fun getProgressText(): String {
        val state = _uiState.value
        return if (state.totalCount > 0 && state.currentIndex >= 0) {
            "${state.currentIndex + 1} of ${state.totalCount}"
        } else {
            "0 of 0"
        }
    }

    /**
     * Get available categories from the model
     */
    fun getCategories(): List<String> {
        return modelManager.classLabels.toList()
    }
    
    /**
     * Upload all labeled images to server.
     */
    fun uploadLabeledImages() {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(isUploading = true, error = null) }
                
                // Get all labeled images that haven't been uploaded
                val labeledImages = imageDao.getNotUploaded()
                
                if (labeledImages.isEmpty()) {
                    _uiState.update {
                        it.copy(
                            isUploading = false,
                            error = "No labeled images to upload"
                        )
                    }
                    return@launch
                }
                
                // Queue images for upload in batch
                val batchId = System.currentTimeMillis().toString()
                val imageIds = labeledImages.map { it.id }
                uploadQueueManager.queueBatch(imageIds, batchId)
                
                // Process pending uploads with progress tracking
                uploadQueueManager.processPendingUploads { current, total ->
                    val progress = current.toFloat() / total
                    _uiState.update { it.copy(uploadProgress = progress) }
                }
                
                // Refresh stats after upload
                loadUploadStats()
                
                _uiState.update {
                    it.copy(
                        isUploading = false,
                        uploadProgress = 0f,
                        successMessage = "Successfully uploaded ${labeledImages.size} images"
                    )
                }
                
                Timber.i("Successfully uploaded ${labeledImages.size} images")
            } catch (e: Exception) {
                Timber.e(e, "Error uploading images")
                _uiState.update {
                    it.copy(
                        isUploading = false,
                        uploadProgress = 0f,
                        error = "Upload failed: ${e.message}"
                    )
                }
            }
        }
    }
    
    /**
     * Retry failed uploads.
     */
    fun retryFailedUploads() {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(isUploading = true, error = null) }
                
                val result = uploadQueueManager.retryFailed()
                
                // Refresh stats
                loadUploadStats()
                
                _uiState.update {
                    it.copy(
                        isUploading = false,
                        uploadProgress = 0f,
                        successMessage = "Retry completed: ${result.successCount} succeeded, ${result.failedCount} failed"
                    )
                }
                
                Timber.i("Retry completed")
            } catch (e: Exception) {
                Timber.e(e, "Error retrying uploads")
                _uiState.update {
                    it.copy(
                        isUploading = false,
                        uploadProgress = 0f,
                        error = "Retry failed: ${e.message}"
                    )
                }
            }
        }
    }
    
    /**
     * Dismiss success message.
     */
    fun dismissSuccess() {
        _uiState.update { it.copy(successMessage = null) }
    }

    companion object {
        // Removed static CATEGORIES - now using model's classes dynamically
    }
}

/**
 * UI State for Image Labeling Screen
 */
data class LabelUiState(
    val unlabeledImages: List<ImageEntity> = emptyList(),
    val currentIndex: Int = -1,
    val totalCount: Int = 0,
    val selectedCategory: String? = null,
    val isLoading: Boolean = false,
    val isUploading: Boolean = false,
    val uploadProgress: Float = 0f,
    val activeUploads: Int = 0,
    val uploadStats: UploadStats? = null,
    val successMessage: String? = null,
    val error: String? = null
) {
    /**
     * Get current image being labeled
     */
    val currentImage: ImageEntity?
        get() = if (currentIndex >= 0 && currentIndex < unlabeledImages.size) {
            unlabeledImages[currentIndex]
        } else {
            null
        }

    /**
     * Check if there are any unlabeled images
     */
    val hasImages: Boolean
        get() = totalCount > 0

    /**
     * Check if all images have been labeled
     */
    val allLabeled: Boolean
        get() = !hasImages && !isLoading
        
    /**
     * Check if there are failed uploads to retry
     */
    val hasFailedUploads: Boolean
        get() = uploadStats?.failed ?: 0 > 0
}
