package com.federated.client.ui.screens.camera

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.entities.ImageEntity
import com.federated.client.data.local.storage.CacheManager
import com.federated.client.data.local.storage.ImageStorageManager
import com.federated.client.domain.usecase.ml.RunInferenceUseCase
import com.federated.client.ml.pytorch.PredictionResult
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import timber.log.Timber
import java.io.File
import java.util.concurrent.Executor
import javax.inject.Inject

/**
 * ViewModel for Camera screen.
 * Handles camera permissions, image capture, compression, storage, and ML inference.
 */
@HiltViewModel
class CameraViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val imageDao: ImageDao,
    private val imageStorageManager: ImageStorageManager,
    private val cacheManager: CacheManager,
    private val runInferenceUseCase: RunInferenceUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(CameraUiState())
    val uiState: StateFlow<CameraUiState> = _uiState.asStateFlow()

    /**
     * Capture image from camera.
     */
    fun captureImage(
        imageCapture: ImageCapture,
        executor: Executor,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        _uiState.update { it.copy(isCapturing = true, error = null) }

        // Create temporary file for capture
        val photoFile = File(
            context.cacheDir,
            "temp_capture_${System.currentTimeMillis()}.jpg"
        )

        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

        imageCapture.takePicture(
            outputOptions,
            executor,
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                    viewModelScope.launch {
                        try {
                            // In Train tab, we DON'T run inference
                            // User will manually label the image
                            Timber.d("Image captured for training - no auto-inference")
                            
                            // Process and save image WITHOUT prediction
                            processAndSaveImage(photoFile, predictionResult = null)
                            
                            withContext(Dispatchers.Main) {
                                _uiState.update {
                                    it.copy(
                                        isCapturing = false,
                                        captureSuccess = true,
                                        lastPrediction = null, // No prediction in Train mode
                                        error = null
                                    )
                                }
                                onSuccess()
                            }
                        } catch (e: Exception) {
                            withContext(Dispatchers.Main) {
                                _uiState.update {
                                    it.copy(
                                        isCapturing = false,
                                        error = "Failed to process image: ${e.message}"
                                    )
                                }
                                onError(e.message ?: "Unknown error")
                            }
                        } finally {
                            // Clean up temp file
                            photoFile.delete()
                        }
                    }
                }

                override fun onError(exception: ImageCaptureException) {
                    _uiState.update {
                        it.copy(
                            isCapturing = false,
                            error = "Capture failed: ${exception.message}"
                        )
                    }
                    onError(exception.message ?: "Capture failed")
                }
            }
        )
    }

    /**
     * Process captured image: compress, generate thumbnail, save to storage, and store prediction.
     */
    private suspend fun processAndSaveImage(
        sourceFile: File,
        predictionResult: PredictionResult? = null
    ) = withContext(Dispatchers.IO) {
        // Check storage before proceeding
        val cacheStats = cacheManager.getCacheStats()
        val maxSize = 500L * 1024 * 1024 // 500MB
        val availableSpace = maxSize - cacheStats.currentSize
        
        if (availableSpace < sourceFile.length()) {
            cacheManager.cleanup()
            
            // Check again after cleanup
            val newStats = cacheManager.getCacheStats()
            val newAvailableSpace = maxSize - newStats.currentSize
            if (newAvailableSpace < sourceFile.length()) {
                throw Exception("Storage full. Please delete some images.")
            }
        }

        // Load bitmap
        val originalBitmap = BitmapFactory.decodeFile(sourceFile.absolutePath)
            ?: throw Exception("Failed to decode image")

        try {
            // Save image (ImageStorageManager handles compression and thumbnails)
            val saveResult = imageStorageManager.saveImage(
                bitmap = originalBitmap,
                filename = "img_${System.currentTimeMillis()}.jpg"
            ).getOrThrow()

            // Save to database WITHOUT auto-labeling
            // In Train mode, user manually labels images
            val imageEntity = ImageEntity(
                uri = saveResult.uri,
                category = null, // User will label this manually
                isLabeled = false, // Not labeled yet - user's job!
                capturedAt = System.currentTimeMillis(),
                width = saveResult.width,
                height = saveResult.height,
                fileSize = saveResult.fileSize,
                isUploaded = false,
                uploadedAt = null
            )
            
            imageDao.insert(imageEntity)
            
            Timber.i("Image captured for training - waiting for user to label")

            // Clean up bitmap
            originalBitmap.recycle()

        } catch (e: Exception) {
            originalBitmap.recycle()
            throw e
        }
    }

    /**
     * Reset capture success state.
     */
    fun resetCaptureState() {
        _uiState.update { it.copy(captureSuccess = false, lastPrediction = null) }
    }

    /**
     * Clear error state.
     */
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    /**
     * Get total captured images count.
     */
    fun getTotalCapturedCount() {
        viewModelScope.launch {
            val count = imageDao.getCount()
            _uiState.update { it.copy(totalCaptured = count) }
        }
    }
    
    /**
     * Check if ML model is ready for inference.
     */
    fun isModelReady(): Boolean = runInferenceUseCase.isReady()
    
    /**
     * Process image from gallery picker.
     * Loads bitmap from URI, runs inference, and saves to database.
     */
    fun processGalleryImage(
        uri: Uri,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        _uiState.update { it.copy(isCapturing = true, error = null) }
        
        viewModelScope.launch {
            try {
                // Create temporary file for the gallery image
                val tempFile = File(
                    context.cacheDir,
                    "temp_gallery_${System.currentTimeMillis()}.jpg"
                )
                
                // Load bitmap from URI and save to temp file
                val bitmap = withContext(Dispatchers.IO) {
                    context.contentResolver.openInputStream(uri)?.use { inputStream ->
                        val bmp = BitmapFactory.decodeStream(inputStream)
                        if (bmp != null) {
                            // Save bitmap to temp file
                            tempFile.outputStream().use { outputStream ->
                                bmp.compress(Bitmap.CompressFormat.JPEG, 95, outputStream)
                            }
                        }
                        bmp
                    }
                }
                
                if (bitmap == null) {
                    _uiState.update { 
                        it.copy(
                            isCapturing = false, 
                            error = "Failed to load image from gallery"
                        ) 
                    }
                    onError("Failed to load image")
                    return@launch
                }
                
                // In Train mode, we DON'T run inference
                // User will manually label the image
                Timber.d("Gallery image loaded for training - no auto-inference")
                
                // Process and save WITHOUT prediction
                processAndSaveImage(tempFile, predictionResult = null)
                
                // Clean up temp file
                tempFile.delete()
                
                _uiState.update { 
                    it.copy(
                        isCapturing = false, 
                        captureSuccess = true,
                        lastPrediction = null // No prediction in Train mode
                    ) 
                }
                
                onSuccess()
                
            } catch (e: Exception) {
                Timber.e(e, "Error processing gallery image")
                _uiState.update { 
                    it.copy(
                        isCapturing = false, 
                        error = "Failed to process gallery image: ${e.message}"
                    ) 
                }
                onError(e.message ?: "Unknown error")
            }
        }
    }
}

/**
 * UI state for Camera screen.
 */
data class CameraUiState(
    val isCapturing: Boolean = false,
    val captureSuccess: Boolean = false,
    val error: String? = null,
    val totalCaptured: Int = 0,
    val lastPrediction: PredictionResult? = null
)
