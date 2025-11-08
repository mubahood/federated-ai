package com.federated.client.domain.usecase.ml

import com.federated.client.ml.pytorch.DownloadResult
import com.federated.client.ml.pytorch.ModelDownloadManager
import com.federated.client.ml.pytorch.PyTorchModelManager
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import timber.log.Timber
import javax.inject.Inject

/**
 * Use case for initializing the ML model.
 * 
 * Handles:
 * - Checking if model exists locally
 * - Downloading model from server if needed
 * - Loading model into memory
 * - Reporting progress and status
 */
class InitializeModelUseCase @Inject constructor(
    private val downloadManager: ModelDownloadManager,
    private val modelManager: PyTorchModelManager
) {

    /**
     * Initialize model with progress updates.
     * 
     * @return Flow emitting ModelInitStatus updates
     */
    operator fun invoke(): Flow<ModelInitStatus> = flow {
        try {
            emit(ModelInitStatus.Checking)
            
            // Check if model is already loaded
            if (modelManager.isReady()) {
                Timber.d("Model already loaded and ready")
                emit(ModelInitStatus.Success)
                return@flow
            }
            
            // 1. Try to load from assets (bundled model)
            Timber.d("Checking for bundled model in assets...")
            emit(ModelInitStatus.Loading)
            
            val loadedFromAssets = modelManager.loadModelFromAssets("model.ptl")
            if (loadedFromAssets) {
                Timber.i("Model loaded successfully from assets")
                emit(ModelInitStatus.Success)
                return@flow
            }
            
            // 2. Check if model exists locally (downloaded previously)
            val localModel = downloadManager.getLocalModel()
            
            if (localModel != null) {
                Timber.d("Found local model, loading...")
                emit(ModelInitStatus.Loading)
                
                val loaded = modelManager.loadModel(localModel)
                if (loaded) {
                    Timber.i("Model loaded successfully from cache")
                    emit(ModelInitStatus.Success)
                } else {
                    Timber.e("Failed to load local model")
                    emit(ModelInitStatus.Error("Failed to load cached model"))
                }
            } else {
                // 3. Need to download model from server
                Timber.d("No local model found, downloading from server...")
                emit(ModelInitStatus.Downloading(0f))
                
                when (val result = downloadManager.downloadModel { progress ->
                    // This doesn't emit to flow, but we could add a channel if needed
                    Timber.v("Download progress: ${(progress * 100).toInt()}%")
                }) {
                    is DownloadResult.Success -> {
                        Timber.i("Model downloaded successfully")
                        emit(ModelInitStatus.Loading)
                        
                        val loaded = modelManager.loadModel(result.file)
                        if (loaded) {
                            Timber.i("Model loaded successfully after download")
                            emit(ModelInitStatus.Success)
                        } else {
                            Timber.e("Failed to load downloaded model")
                            emit(ModelInitStatus.Error("Failed to load downloaded model"))
                        }
                    }
                    is DownloadResult.Error -> {
                        Timber.e("Model download failed: ${result.message}")
                        emit(ModelInitStatus.Error("Download failed: ${result.message}"))
                    }
                }
            }
            
        } catch (e: Exception) {
            Timber.e(e, "Error initializing model")
            emit(ModelInitStatus.Error(e.message ?: "Unknown error"))
        }
    }
    
    /**
     * Check if model is ready without initialization.
     */
    fun isModelReady(): Boolean = modelManager.isReady()
}

/**
 * Sealed class representing model initialization status.
 */
sealed class ModelInitStatus {
    object Checking : ModelInitStatus()
    data class Downloading(val progress: Float) : ModelInitStatus()
    object Loading : ModelInitStatus()
    object Success : ModelInitStatus()
    data class Error(val message: String) : ModelInitStatus()
}
