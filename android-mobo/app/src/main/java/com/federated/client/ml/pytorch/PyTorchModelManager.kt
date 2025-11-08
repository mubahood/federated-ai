package com.federated.client.ml.pytorch

import android.content.Context
import android.graphics.Bitmap
import org.pytorch.IValue
import org.pytorch.LiteModuleLoader
import org.pytorch.Module
import org.pytorch.torchvision.TensorImageUtils
import timber.log.Timber
import java.io.File
import java.io.FileOutputStream
import kotlin.math.exp

/**
 * Manager class for PyTorch Mobile model inference.
 * 
 * Handles:
 * - Model loading from file system
 * - Image preprocessing (resize, normalize)
 * - Inference execution
 * - Softmax and prediction parsing
 * 
 * Model Input: 224x224 RGB image, ImageNet normalized
 * Model Output: 5 class probabilities (Bicycle, Car, Cat, Dog, Person)
 */
class PyTorchModelManager(private val context: Context) {

    private var model: Module? = null
    private var isModelLoaded = false
    
    // ImageNet normalization (same as training)
    private val normMeanRGB = floatArrayOf(0.485f, 0.456f, 0.406f)
    private val normStdRGB = floatArrayOf(0.229f, 0.224f, 0.225f)
    
    // Class labels (must match training order)
    val classLabels = arrayOf(
        "Bicycle",  // Index 0
        "Car",      // Index 1
        "Cat",      // Index 2
        "Dog",      // Index 3
        "Person"    // Index 4
    )

    /**
     * Load model from internal storage.
     * 
     * @param modelFile File object pointing to the .ptl model
     * @return Boolean indicating success
     */
    fun loadModel(modelFile: File): Boolean {
        return try {
            if (!modelFile.exists()) {
                Timber.e("Model file does not exist: ${modelFile.absolutePath}")
                return false
            }
            
            Timber.d("Loading PyTorch model from: ${modelFile.absolutePath}")
            Timber.d("Model file size: ${modelFile.length() / 1024 / 1024}MB")
            
            model = LiteModuleLoader.load(modelFile.absolutePath)
            isModelLoaded = true
            
            Timber.i("PyTorch model loaded successfully")
            true
        } catch (e: Exception) {
            Timber.e(e, "Failed to load PyTorch model")
            isModelLoaded = false
            false
        }
    }

    /**
     * Load model from assets folder.
     * 
     * @param assetName Name of the model file in assets (e.g., "model.ptl")
     * @return Boolean indicating success
     */
    fun loadModelFromAssets(assetName: String): Boolean {
        return try {
            // Copy from assets to internal storage
            val modelFile = File(context.filesDir, assetName)
            
            if (!modelFile.exists()) {
                Timber.d("Copying model from assets to internal storage")
                context.assets.open(assetName).use { inputStream ->
                    FileOutputStream(modelFile).use { outputStream ->
                        inputStream.copyTo(outputStream)
                    }
                }
            }
            
            loadModel(modelFile)
        } catch (e: Exception) {
            Timber.e(e, "Failed to load model from assets")
            false
        }
    }

    /**
     * Run inference on a bitmap image.
     * 
     * @param bitmap Input image (will be resized to 224x224)
     * @return PredictionResult with top prediction and all probabilities
     */
    fun predict(bitmap: Bitmap): PredictionResult? {
        if (!isModelLoaded || model == null) {
            Timber.e("Model not loaded. Call loadModel() first.")
            return null
        }

        return try {
            val startTime = System.currentTimeMillis()
            
            // Convert bitmap to tensor with ImageNet normalization
            val inputTensor = TensorImageUtils.bitmapToFloat32Tensor(
                bitmap,
                normMeanRGB,
                normStdRGB
            )
            
            // Run inference
            val outputTensor = model!!.forward(IValue.from(inputTensor)).toTensor()
            val scores = outputTensor.dataAsFloatArray
            
            // Apply softmax to get probabilities
            val probabilities = softmax(scores)
            
            // Find top prediction
            val maxIndex = probabilities.indices.maxByOrNull { probabilities[it] } ?: 0
            val maxProbability = probabilities[maxIndex]
            val predictedClass = classLabels[maxIndex]
            
            val inferenceTime = System.currentTimeMillis() - startTime
            
            Timber.d("Inference completed in ${inferenceTime}ms")
            Timber.d("Prediction: $predictedClass (${(maxProbability * 100).toInt()}%)")
            
            PredictionResult(
                predictedClass = predictedClass,
                confidence = maxProbability,
                allProbabilities = probabilities.mapIndexed { index, prob ->
                    classLabels[index] to prob
                },
                inferenceTimeMs = inferenceTime
            )
        } catch (e: Exception) {
            Timber.e(e, "Inference failed")
            null
        }
    }

    /**
     * Preprocess bitmap for model input.
     * Resizes to 224x224 and converts to RGB.
     * 
     * @param bitmap Original bitmap
     * @return Preprocessed bitmap
     */
    fun preprocessBitmap(bitmap: Bitmap): Bitmap {
        return Bitmap.createScaledBitmap(bitmap, 224, 224, true).let {
            // Ensure RGB format
            if (it.config != Bitmap.Config.ARGB_8888) {
                it.copy(Bitmap.Config.ARGB_8888, false)
            } else {
                it
            }
        }
    }

    /**
     * Apply softmax to convert logits to probabilities.
     */
    private fun softmax(logits: FloatArray): FloatArray {
        val maxLogit = logits.maxOrNull() ?: 0f
        val expScores = logits.map { exp((it - maxLogit).toDouble()).toFloat() }
        val sumExp = expScores.sum()
        return expScores.map { it / sumExp }.toFloatArray()
    }

    /**
     * Check if model is loaded and ready.
     */
    fun isReady(): Boolean = isModelLoaded && model != null

    /**
     * Release model resources.
     */
    fun release() {
        try {
            model = null
            isModelLoaded = false
            Timber.d("PyTorch model released")
        } catch (e: Exception) {
            Timber.e(e, "Error releasing model")
        }
    }

    /**
     * Get model information.
     */
    fun getModelInfo(): ModelInfo {
        return ModelInfo(
            architecture = "MobileNetV3-Small",
            numClasses = classLabels.size,
            inputSize = 224,
            isLoaded = isModelLoaded
        )
    }
}

/**
 * Data class for prediction results.
 */
data class PredictionResult(
    val predictedClass: String,
    val confidence: Float,
    val allProbabilities: List<Pair<String, Float>>,
    val inferenceTimeMs: Long
) {
    fun getTopK(k: Int): List<Pair<String, Float>> {
        return allProbabilities.sortedByDescending { it.second }.take(k)
    }
    
    fun getConfidencePercentage(): Int = (confidence * 100).toInt()
}

/**
 * Data class for model metadata.
 */
data class ModelInfo(
    val architecture: String,
    val numClasses: Int,
    val inputSize: Int,
    val isLoaded: Boolean
)
