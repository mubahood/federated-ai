package com.federated.client.domain.usecase.ml

import android.graphics.Bitmap
import com.federated.client.ml.pytorch.PredictionResult
import com.federated.client.ml.pytorch.PyTorchModelManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import timber.log.Timber
import javax.inject.Inject

/**
 * Use case for running inference on images.
 * 
 * Handles:
 * - Image preprocessing
 * - Model inference execution
 * - Error handling
 */
class RunInferenceUseCase @Inject constructor(
    private val modelManager: PyTorchModelManager
) {

    /**
     * Run inference on a bitmap image.
     * 
     * @param bitmap Input image
     * @return PredictionResult or null if inference fails
     */
    suspend operator fun invoke(bitmap: Bitmap): Result<PredictionResult> = withContext(Dispatchers.Default) {
        try {
            // Check if model is ready
            if (!modelManager.isReady()) {
                Timber.w("Model not loaded, cannot run inference")
                return@withContext Result.failure(
                    IllegalStateException("Model not initialized. Please initialize model first.")
                )
            }
            
            // Preprocess bitmap if needed
            val processedBitmap = if (bitmap.width != 224 || bitmap.height != 224) {
                Timber.d("Preprocessing bitmap: ${bitmap.width}x${bitmap.height} -> 224x224")
                modelManager.preprocessBitmap(bitmap)
            } else {
                bitmap
            }
            
            // Run inference
            Timber.d("Running inference...")
            val result = modelManager.predict(processedBitmap)
            
            if (result != null) {
                Timber.i("Inference successful: ${result.predictedClass} (${result.getConfidencePercentage()}%)")
                Result.success(result)
            } else {
                Timber.e("Inference returned null")
                Result.failure(Exception("Inference failed"))
            }
            
        } catch (e: Exception) {
            Timber.e(e, "Error during inference")
            Result.failure(e)
        }
    }
    
    /**
     * Check if model is ready for inference.
     */
    fun isReady(): Boolean = modelManager.isReady()
    
    /**
     * Get model information.
     */
    fun getModelInfo() = modelManager.getModelInfo()
}
