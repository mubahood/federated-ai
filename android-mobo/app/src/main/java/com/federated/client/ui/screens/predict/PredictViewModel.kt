package com.federated.client.ui.screens.predict

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.domain.usecase.ml.RunInferenceUseCase
import com.federated.client.ml.pytorch.PredictionResult
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import timber.log.Timber
import javax.inject.Inject

/**
 * ViewModel for Predict Screen.
 * Handles ML model inference on user-selected images.
 */
@HiltViewModel
class PredictViewModel @Inject constructor(
    private val runInferenceUseCase: RunInferenceUseCase,
    private val imageDao: ImageDao
) : ViewModel() {

    private val _uiState = MutableStateFlow(PredictUiState())
    val uiState: StateFlow<PredictUiState> = _uiState.asStateFlow()

    /**
     * Run prediction on an image from URI.
     */
    fun predictImage(uri: Uri, bitmap: Bitmap) {
        _uiState.update { 
            it.copy(
                isLoading = true, 
                error = null,
                selectedImageUri = uri.toString(),
                selectedBitmap = bitmap,
                prediction = null
            ) 
        }

        viewModelScope.launch {
            try {
                if (!runInferenceUseCase.isReady()) {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = "Model not loaded yet. Please wait a moment and try again."
                        ) 
                    }
                    return@launch
                }

                // Run inference
                val result = runInferenceUseCase(bitmap)
                
                result.onSuccess { prediction ->
                    Timber.d("Prediction: ${prediction.predictedClass} (${prediction.confidence}%)")
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            prediction = prediction,
                            error = null
                        ) 
                    }
                }.onFailure { error ->
                    Timber.e(error, "Prediction failed")
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = "Prediction failed: ${error.message}"
                        ) 
                    }
                }
            } catch (e: Exception) {
                Timber.e(e, "Error during prediction")
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        error = "Prediction error: ${e.message}"
                    ) 
                }
            }
        }
    }

    /**
     * Submit feedback on prediction (correct/incorrect).
     */
    fun submitFeedback(isCorrect: Boolean, correctLabel: String? = null) {
        viewModelScope.launch {
            try {
                val prediction = _uiState.value.prediction ?: return@launch
                
                // Log feedback for model improvement
                Timber.i("Feedback: isCorrect=$isCorrect, predicted=${prediction.predictedClass}, correct=$correctLabel")
                
                // TODO: Send feedback to server for federated learning
                // This will be part of the training feedback loop
                
                _uiState.update { 
                    it.copy(
                        feedbackSubmitted = true,
                        feedbackMessage = if (isCorrect) {
                            "Thank you! Your feedback helps improve the model."
                        } else {
                            "Thank you! We'll use this to retrain the model."
                        }
                    ) 
                }
            } catch (e: Exception) {
                Timber.e(e, "Error submitting feedback")
                _uiState.update { 
                    it.copy(
                        error = "Failed to submit feedback: ${e.message}"
                    ) 
                }
            }
        }
    }

    /**
     * Clear current prediction and reset state.
     */
    fun clearPrediction() {
        _uiState.update { 
            PredictUiState() 
        }
    }

    /**
     * Check if model is ready for inference.
     */
    fun isModelReady(): Boolean = runInferenceUseCase.isReady()
}

/**
 * UI state for Predict screen.
 */
data class PredictUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val selectedImageUri: String? = null,
    val selectedBitmap: Bitmap? = null,
    val prediction: PredictionResult? = null,
    val feedbackSubmitted: Boolean = false,
    val feedbackMessage: String? = null
) {
    val hasPrediction: Boolean
        get() = prediction != null
    
    val canSubmitFeedback: Boolean
        get() = hasPrediction && !feedbackSubmitted
}
