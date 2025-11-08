package com.federated.client

import android.app.Application
import androidx.hilt.work.HiltWorkerFactory
import androidx.work.Configuration
import com.federated.client.domain.usecase.ml.InitializeModelUseCase
import dagger.hilt.android.HiltAndroidApp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * Main application class for FederatedAI.
 * Initializes Hilt dependency injection, Timber logging, WorkManager, and ML model.
 */
@HiltAndroidApp
class FederatedAIApp : Application(), Configuration.Provider {

    @Inject
    lateinit var workerFactory: HiltWorkerFactory
    
    @Inject
    lateinit var initializeModelUseCase: InitializeModelUseCase
    
    // Application scope for background tasks
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()
        
        // Initialize Timber for logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
        
        Timber.d("FederatedAI Application initialized")
        
        // Initialize ML model in background
        initializeModel()
    }
    
    /**
     * Initialize ML model on app startup.
     * Downloads and loads the PyTorch model for inference.
     */
    private fun initializeModel() {
        applicationScope.launch {
            try {
                Timber.d("Starting model initialization...")
                initializeModelUseCase().collect { status ->
                    when (status) {
                        is com.federated.client.domain.usecase.ml.ModelInitStatus.Checking -> {
                            Timber.d("Checking for local model...")
                        }
                        is com.federated.client.domain.usecase.ml.ModelInitStatus.Downloading -> {
                            Timber.d("Downloading model: ${(status.progress * 100).toInt()}%")
                        }
                        is com.federated.client.domain.usecase.ml.ModelInitStatus.Loading -> {
                            Timber.d("Loading model into memory...")
                        }
                        is com.federated.client.domain.usecase.ml.ModelInitStatus.Success -> {
                            Timber.i("✓ Model initialized successfully - Ready for inference!")
                        }
                        is com.federated.client.domain.usecase.ml.ModelInitStatus.Error -> {
                            Timber.w("Model initialization failed: ${status.message}")
                            Timber.w("App will continue, but on-device inference won't be available")
                        }
                    }
                }
            } catch (e: Exception) {
                Timber.e(e, "Error during model initialization")
            }
        }
    }

    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .setMinimumLoggingLevel(if (BuildConfig.DEBUG) android.util.Log.DEBUG else android.util.Log.INFO)
            .build()
}
