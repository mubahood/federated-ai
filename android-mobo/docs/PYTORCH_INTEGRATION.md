# Android PyTorch Mobile Integration Guide

## Overview

This guide covers the complete integration of the trained PyTorch Mobile model into the Android app for real-time object detection.

**Model Details:**
- Architecture: MobileNetV3-Small
- Accuracy: 98.47% validation
- Size: 5.8 MB (.ptl format)
- Inference Time: ~4.7ms on device
- Classes: Bicycle, Car, Cat, Dog, Person

---

## 1. Dependencies Added

### build.gradle.kts

```kotlin
// PyTorch Mobile - For object detection model
implementation("org.pytorch:pytorch_android_lite:1.13.1")
implementation("org.pytorch:pytorch_android_torchvision_lite:1.13.1")
```

**Why PyTorch Lite?**
- Smaller APK size (no need for full PyTorch library)
- Optimized for mobile inference
- Includes TorchVision utilities for image preprocessing

---

## 2. Components Created

### 2.1 PyTorchModelManager.kt

**Purpose:** Core model management and inference engine

**Key Features:**
- Model loading from file system or assets
- Image preprocessing (resize to 224x224, ImageNet normalization)
- Inference execution with timing
- Softmax probability calculation
- Top-K predictions

**Usage Example:**
```kotlin
val modelManager = PyTorchModelManager(context)

// Load model
val modelFile = File(context.filesDir, "model.ptl")
if (modelManager.loadModel(modelFile)) {
    // Run inference
    val result = modelManager.predict(bitmap)
    result?.let {
        println("Predicted: ${it.predictedClass}")
        println("Confidence: ${it.getConfidencePercentage()}%")
        println("Inference time: ${it.inferenceTimeMs}ms")
    }
}
```

**Methods:**
- `loadModel(file: File): Boolean` - Load from file
- `loadModelFromAssets(name: String): Boolean` - Load from assets
- `predict(bitmap: Bitmap): PredictionResult?` - Run inference
- `preprocessBitmap(bitmap: Bitmap): Bitmap` - Prepare image
- `isReady(): Boolean` - Check if loaded
- `release()` - Free resources
- `getModelInfo(): ModelInfo` - Get metadata

### 2.2 ModelDownloadManager.kt

**Purpose:** Download and cache models from the Django API

**Key Features:**
- Download model from server with progress tracking
- Store in internal storage for offline use
- Check if model exists locally
- Fetch model metadata from API
- Token-based authentication support

**Usage Example:**
```kotlin
val downloadManager = ModelDownloadManager(
    context = context,
    baseUrl = "http://10.0.2.2:8000",
    authToken = "your-auth-token-here"
)

// Download model
viewModelScope.launch {
    val result = downloadManager.downloadModel { progress ->
        println("Download progress: ${(progress * 100).toInt()}%")
    }
    
    when (result) {
        is DownloadResult.Success -> {
            val modelFile = result.file
            // Load into PyTorchModelManager
        }
        is DownloadResult.Error -> {
            println("Download failed: ${result.message}")
        }
    }
}
```

**Methods:**
- `downloadModel(onProgress): DownloadResult` - Download from server
- `fetchModelMetadata(): ModelMetadata?` - Get model info from API
- `getLocalModel(): File?` - Get cached model
- `isModelDownloaded(): Boolean` - Check if exists
- `deleteModel(): Boolean` - Remove cached model
- `getModelSize(): Float?` - Get file size in MB

---

## 3. Integration Steps

### Step 1: Download Model on First Launch

```kotlin
class ModelInitializer @Inject constructor(
    private val downloadManager: ModelDownloadManager,
    private val modelManager: PyTorchModelManager,
    private val preferencesManager: PreferencesManager
) {
    suspend fun initializeModel(): Boolean {
        // Check if already downloaded
        if (downloadManager.isModelDownloaded()) {
            val modelFile = downloadManager.getLocalModel()
            return modelFile?.let { modelManager.loadModel(it) } ?: false
        }
        
        // Download from server
        when (val result = downloadManager.downloadModel()) {
            is DownloadResult.Success -> {
                return modelManager.loadModel(result.file)
            }
            is DownloadResult.Error -> {
                Timber.e("Model download failed: ${result.message}")
                return false
            }
        }
    }
}
```

### Step 2: Add to ViewModel

```kotlin
class CameraViewModel @Inject constructor(
    private val modelManager: PyTorchModelManager
) : ViewModel() {
    
    private val _predictionResult = MutableStateFlow<PredictionResult?>(null)
    val predictionResult: StateFlow<PredictionResult?> = _predictionResult.asStateFlow()
    
    fun analyzeImage(bitmap: Bitmap) {
        viewModelScope.launch(Dispatchers.Default) {
            val result = modelManager.predict(bitmap)
            _predictionResult.value = result
        }
    }
}
```

### Step 3: Use in Camera Screen

```kotlin
@Composable
fun CameraScreen(
    viewModel: CameraViewModel = hiltViewModel()
) {
    val predictionResult by viewModel.predictionResult.collectAsState()
    
    Column {
        CameraPreview(
            onCapture = { bitmap ->
                viewModel.analyzeImage(bitmap)
            }
        )
        
        predictionResult?.let { result ->
            Card {
                Text("Object: ${result.predictedClass}")
                Text("Confidence: ${result.getConfidencePercentage()}%")
                Text("Time: ${result.inferenceTimeMs}ms")
                
                // Show all predictions
                result.getTopK(3).forEach { (label, prob) ->
                    Text("$label: ${(prob * 100).toInt()}%")
                }
            }
        }
    }
}
```

### Step 4: Add to Dependency Injection

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object MLModule {
    
    @Provides
    @Singleton
    fun providePyTorchModelManager(
        @ApplicationContext context: Context
    ): PyTorchModelManager {
        return PyTorchModelManager(context)
    }
    
    @Provides
    @Singleton
    fun provideModelDownloadManager(
        @ApplicationContext context: Context,
        preferencesManager: PreferencesManager
    ): ModelDownloadManager {
        val authToken = preferencesManager.getAuthToken() // Get from prefs
        return ModelDownloadManager(
            context = context,
            baseUrl = BuildConfig.BASE_URL.removeSuffix("/api/"),
            authToken = authToken
        )
    }
}
```

---

## 4. Testing

### 4.1 Unit Tests

Create `PyTorchModelManagerTest.kt`:

```kotlin
class PyTorchModelManagerTest {
    private lateinit var context: Context
    private lateinit var modelManager: PyTorchModelManager
    
    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        modelManager = PyTorchModelManager(context)
    }
    
    @Test
    fun `test model loading`() {
        val modelFile = File(context.filesDir, "test_model.ptl")
        // Copy test model to location
        val success = modelManager.loadModel(modelFile)
        assertTrue(success)
        assertTrue(modelManager.isReady())
    }
    
    @Test
    fun `test inference`() {
        // Load model
        modelManager.loadModel(testModelFile)
        
        // Create test bitmap
        val bitmap = Bitmap.createBitmap(224, 224, Bitmap.Config.ARGB_8888)
        
        // Run inference
        val result = modelManager.predict(bitmap)
        
        assertNotNull(result)
        assertThat(result!!.predictedClass).isIn(modelManager.classLabels)
        assertThat(result.confidence).isGreaterThan(0f)
        assertThat(result.confidence).isLessThan(1f)
        assertThat(result.inferenceTimeMs).isGreaterThan(0L)
    }
}
```

### 4.2 Integration Test

Test model download and inference end-to-end:

```kotlin
@Test
fun `test model download and inference`() = runTest {
    val downloadManager = ModelDownloadManager(context)
    
    // Download model
    val result = downloadManager.downloadModel()
    assertTrue(result is DownloadResult.Success)
    
    // Load model
    val modelFile = (result as DownloadResult.Success).file
    val modelManager = PyTorchModelManager(context)
    assertTrue(modelManager.loadModel(modelFile))
    
    // Test inference
    val testBitmap = loadTestImage()
    val prediction = modelManager.predict(testBitmap)
    assertNotNull(prediction)
}
```

### 4.3 Manual Testing Checklist

- [ ] Model downloads successfully from server
- [ ] Download progress updates correctly
- [ ] Model loads without errors
- [ ] Inference completes in <100ms
- [ ] Predictions are accurate for test images
- [ ] Multiple consecutive inferences work
- [ ] App handles model loading failures gracefully
- [ ] Cached model is reused on app restart

---

## 5. Performance Optimization

### 5.1 Image Preprocessing

Already optimized in `PyTorchModelManager`:
- Direct bitmap to tensor conversion
- ImageNet normalization applied
- No intermediate copies

### 5.2 Inference Threading

Run inference on background thread:

```kotlin
fun analyzeImage(bitmap: Bitmap) {
    viewModelScope.launch(Dispatchers.Default) {
        val result = modelManager.predict(bitmap)
        withContext(Dispatchers.Main) {
            _predictionResult.value = result
        }
    }
}
```

### 5.3 Batch Processing

For multiple images:

```kotlin
suspend fun analyzeBatch(bitmaps: List<Bitmap>): List<PredictionResult?> {
    return withContext(Dispatchers.Default) {
        bitmaps.map { modelManager.predict(it) }
    }
}
```

---

## 6. Error Handling

### Common Errors and Solutions

#### Model Not Found (404)
```kotlin
when (downloadResult) {
    is DownloadResult.Error -> {
        if (downloadResult.message.contains("404")) {
            // Model hasn't been trained yet
            showDialog("Please train the model first")
        }
    }
}
```

#### Out of Memory
```kotlin
try {
    val result = modelManager.predict(bitmap)
} catch (e: OutOfMemoryError) {
    // Reduce bitmap size
    val scaledBitmap = Bitmap.createScaledBitmap(bitmap, 224, 224, true)
    val result = modelManager.predict(scaledBitmap)
}
```

#### Authentication Error (401)
```kotlin
if (response.code == 401) {
    // Token expired, refresh authentication
    authRepository.refreshToken()
}
```

---

## 7. API Endpoints

### GET /api/v1/model/metadata/

**Authentication:** None (public)

**Response:**
```json
{
  "model_info": {
    "architecture": "MobileNetV3-Small",
    "num_classes": 5,
    "validation_accuracy": 98.47,
    "format": "PyTorch Mobile (.ptl)"
  },
  "categories": {
    "0": "Bicycle",
    "1": "Car",
    "2": "Cat",
    "3": "Dog",
    "4": "Person"
  },
  "preprocessing": {
    "input_size": [224, 224],
    "normalization": {
      "mean": [0.485, 0.456, 0.406],
      "std": [0.229, 0.224, 0.225]
    }
  },
  "performance": {
    "model_size_mb": 5.8,
    "mobile_inference_ms": 4.7
  }
}
```

### GET /api/v1/model/download/

**Authentication:** Required (Token)

**Headers:**
```
Authorization: Token <your-token-here>
```

**Response:** Binary .ptl file (5.8 MB)

---

## 8. Troubleshooting

### Model fails to load

Check:
1. File exists: `modelFile.exists()`
2. File size matches expected: `~5.8 MB`
3. File permissions: Read access
4. Sufficient storage space

### Inference crashes

Check:
1. Model is loaded: `modelManager.isReady()`
2. Bitmap is valid (not recycled)
3. Bitmap size is reasonable (<10 MB)
4. Sufficient memory available

### Slow inference (>100ms)

Possible causes:
1. Large input bitmap (should be 224x224)
2. Running on main thread
3. Multiple concurrent inferences
4. Device thermal throttling

---

## 9. Next Steps

### A. Add to Existing Camera Flow

Modify `CaptureScreen.kt` to run inference after capture:

```kotlin
when (val result = captureUseCase.captureImage()) {
    is CaptureResult.Success -> {
        // Existing code: save to DB, upload to server
        
        // NEW: Run inference
        val prediction = modelManager.predict(result.bitmap)
        prediction?.let {
            // Show prediction overlay
            // Save prediction with image metadata
        }
    }
}
```

### B. Add Model Management Screen

Create `ModelSettingsScreen.kt`:
- Show model status (loaded/not loaded)
- Display model metadata (accuracy, size)
- Button to download/update model
- Clear cache option

### C. Add Inference History

Store predictions in Room database:

```kotlin
@Entity(tableName = "predictions")
data class PredictionEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val imageId: Long,
    val predictedClass: String,
    val confidence: Float,
    val inferenceTimeMs: Long,
    val timestamp: Long = System.currentTimeMillis()
)
```

---

## 10. Summary

**Completed:**
- ✅ PyTorch Mobile dependencies added
- ✅ PyTorchModelManager class created (inference engine)
- ✅ ModelDownloadManager class created (model fetching)
- ✅ Integration guide documented

**Ready for Integration:**
- Model serving API endpoints working
- Android classes ready to use
- Download and inference flow designed
- Error handling in place

**Estimated Integration Time:** 30-40 minutes
1. Add Hilt module (5 min)
2. Initialize model on app start (10 min)
3. Add inference to camera capture (10 min)
4. Test end-to-end (10 min)

**Expected Performance:**
- Model size: 5.8 MB
- Download time: ~2-5 seconds (on WiFi)
- Inference time: <100ms per image
- Accuracy: 98.47% (excellent)

---

**Last Updated:** November 7, 2025  
**Model Version:** 1.0.0  
**API Version:** v1
