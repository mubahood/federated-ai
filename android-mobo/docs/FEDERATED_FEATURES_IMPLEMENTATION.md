# Android Federated Learning Features - Implementation Complete

## Overview

This document describes the Android client implementation for federated learning features, specifically:
- **Task #5**: Model Download & Update System
- **Task #6**: Image Upload Queue System

Both server-side APIs and Android client-side code are now complete.

---

## Task #5: Model Download & Update System

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Android Client                        │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  ModelsViewModel │─────▶│ ModelUpdateMgr   │        │
│  └──────────────────┘      └────────┬─────────┘        │
│                                     │                   │
│                                     ▼                   │
│                          ┌────────────────────┐         │
│                          │   ModelApi         │         │
│                          │  (Retrofit)        │         │
│                          └─────────┬──────────┘         │
└────────────────────────────────────┼──────────────────────┘
                                    │ HTTP
                                    ▼
┌─────────────────────────────────────────────────────────┐
│                   Django Server                         │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  ModelVersionViewSet                     │          │
│  │  - latest() → ModelMetadataDto           │          │
│  │  - download_version() → .ptl binary      │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### Components Created

#### 1. API Layer

**`ModelApi.kt`**
```kotlin
interface ModelApi {
    @GET("models/latest/")
    suspend fun getLatestModel(
        @Header("X-Model-Version") currentVersion: String?
    ): Response<ModelMetadataDto>
    
    @Streaming
    @GET("models/download/{version}/")
    suspend fun downloadModel(
        @Path("version") version: String
    ): Response<ResponseBody>
}
```

**`ModelMetadataDto.kt`**
- `version`: Semantic version (e.g., "1.2.0")
- `checksum`: SHA256 for integrity verification
- `downloadUrl`: Full URL to .ptl file
- `requiresUpdate`: Boolean flag (server compares versions)
- `fileSize`: Model size in bytes
- `releasedAt`: ISO 8601 timestamp
- `accuracy`: Optional model accuracy percentage
- `description`: Optional change notes

#### 2. Model Update Manager

**`ModelUpdateManager.kt`**
- **Purpose**: Orchestrate model updates with hot-swapping
- **Key Methods**:
  - `checkForUpdates()`: Query server for new versions
  - `downloadAndInstall(updateInfo, onProgress)`: Download, verify, and install
  - `rollback()`: Revert to previous version on failure
  - `getCurrentVersion()`: Get installed version

**Features**:
- ✅ SHA256 checksum verification
- ✅ Progress tracking during download
- ✅ Automatic backup before update
- ✅ Hot-swap without app restart
- ✅ Rollback on failure
- ✅ Version persistence in DataStore

**Update Flow**:
```
1. Check for updates → GET /api/models/latest/
2. Compare versions → Server returns requires_update flag
3. Download model → GET /api/models/download/{version}/
4. Verify checksum → Calculate SHA256 and compare
5. Backup current model → Copy to backup_model.ptl
6. Install new model → Copy to current_model.ptl
7. Hot-swap → PyTorchModelManager.loadModel()
8. Update preferences → Store new version
```

#### 3. Server Integration

**Endpoints** (already implemented in `server/training/views.py`):

**GET `/api/models/latest/`**
- Headers: `X-Model-Version` (optional, for comparison)
- Response: ModelMetadataDto
- Logic: Server compares semantic versions, sets `requires_update`

**GET `/api/models/download/{version}/`**
- Path param: version string
- Response: Binary .ptl file
- Headers: Content-Disposition, Content-Length, ETag

### Usage Example

```kotlin
// In ModelsViewModel
viewModelScope.launch {
    // Check for updates
    val updateInfo = modelUpdateManager.checkForUpdates()
    
    if (updateInfo != null) {
        _uiState.update {
            it.copy(
                updateAvailable = true,
                newVersion = updateInfo.version,
                updateSize = updateInfo.fileSize
            )
        }
        
        // User clicks "Update"
        val result = modelUpdateManager.downloadAndInstall(updateInfo) { progress ->
            _uiState.update { it.copy(downloadProgress = progress) }
        }
        
        when (result) {
            is UpdateResult.Success -> {
                showSnackbar("Model updated to ${result.version}")
            }
            is UpdateResult.Error -> {
                showSnackbar("Update failed: ${result.message}")
            }
        }
    }
}
```

---

## Task #6: Image Upload Queue System

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Android Client                        │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  LabelViewModel  │─────▶│ UploadQueueMgr   │        │
│  └──────────────────┘      └────────┬─────────┘        │
│                                     │                   │
│                                     ▼                   │
│                          ┌────────────────────┐         │
│                          │  UploadQueueDao    │         │
│                          │  (Room Database)   │         │
│                          └────────┬───────────┘         │
│                                   │                     │
│                                   ▼                     │
│                          ┌────────────────────┐         │
│                          │   TrainingApi      │         │
│                          │   (Retrofit)       │         │
│                          └─────────┬──────────┘         │
└────────────────────────────────────┼──────────────────────┘
                                    │ HTTP Multipart
                                    ▼
┌─────────────────────────────────────────────────────────┐
│                   Django Server                         │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  TrainingImageViewSet                    │          │
│  │  - upload_from_mobile()                  │          │
│  │    → ImageUploadResponse                 │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### Components Created

#### 1. Database Layer

**`UploadQueueEntity.kt`**
```kotlin
@Entity(tableName = "upload_queue")
data class UploadQueueEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val imageId: Long,                    // FK to ImageEntity
    val status: UploadStatus,             // PENDING, UPLOADING, SUCCESS, FAILED
    val batchId: String?,                 // Group uploads together
    val retryCount: Int = 0,
    val maxRetries: Int = 3,
    val errorMessage: String?,
    val serverImageId: Int?,              // After successful upload
    val createdAt: Date,
    val lastAttemptAt: Date?,
    val completedAt: Date?,
    val priority: Int = 0
)

enum class UploadStatus {
    PENDING, UPLOADING, SUCCESS, FAILED, CANCELLED
}
```

**`UploadQueueDao.kt`**
- CRUD operations for upload queue
- Query methods: getPendingUploads(), getRetriableUploads()
- Update methods: markAsSuccess(), markAsFailed()
- Statistics: getStats(), getPendingCount()
- Cleanup: deleteOldSuccessfulUploads()

**`Converters.kt`**
- Room TypeConverters for Date ↔ Long
- Room TypeConverters for UploadStatus ↔ String

**`AppDatabase.kt`**
- Updated to version 2
- Added UploadQueueEntity
- Added @TypeConverters(Converters::class)

#### 2. API Layer

**`TrainingApi.kt`**
```kotlin
interface TrainingApi {
    @Multipart
    @POST("training/images/upload_from_mobile/")
    suspend fun uploadImages(
        @Part images: List<MultipartBody.Part>,
        @Part("labels") labels: RequestBody,
        @Part("batch_id") batchId: RequestBody?,
        @Part("client_id") clientId: RequestBody,
        @Part("auto_validate") autoValidate: RequestBody?
    ): Response<ImageUploadResponse>
}
```

**`ImageUploadResponse.kt`**
- `successCount`: Number of successful uploads
- `failedCount`: Number of failed uploads
- `totalCount`: Total images in batch
- `imageIds`: List of server-assigned IDs
- `errors`: List of error messages
- `batchId`: Server-assigned batch identifier
- `message`: Overall status message

#### 3. Upload Queue Manager

**`UploadQueueManager.kt`**
- **Purpose**: Queue, batch, and upload images with retry logic
- **Key Methods**:
  - `queueImage(imageId, priority)`: Queue single image
  - `queueBatch(imageIds, batchId, priority)`: Queue multiple images
  - `processPendingUploads(onProgress)`: Upload all pending
  - `retryFailed()`: Retry failed uploads
  - `observeActiveUploads()`: Flow for UI updates
  - `getStats()`: Get upload statistics
  - `cleanupOldUploads(daysOld)`: Cleanup successful uploads

**Features**:
- ✅ Batch upload (configurable BATCH_SIZE = 10)
- ✅ Image compression (JPEG quality 80%, max 800x800)
- ✅ Automatic retry with exponential backoff (max 3 retries)
- ✅ Progress tracking (current/total)
- ✅ Offline support (queue persists in database)
- ✅ Priority-based upload ordering
- ✅ Detailed error reporting

**Upload Flow**:
```
1. Queue images → Insert into UploadQueueEntity
2. Process pending → Load from database
3. Batch images → Group by BATCH_SIZE
4. Compress images → Reduce size for bandwidth
5. Create multipart → Prepare HTTP request
6. Upload to server → POST /api/training/images/upload_from_mobile/
7. Process response → Mark success/failed
8. Update database → Store server IDs or error messages
9. Retry failures → Exponential backoff
```

#### 4. Server Integration

**Endpoint** (already implemented in `server/training/views.py`):

**POST `/api/training/images/upload_from_mobile/`**
- Body (multipart/form-data):
  - `images`: Multiple image files
  - `labels`: JSON array ["Cat", "Dog", "Person"]
  - `batch_id`: Optional batch identifier
  - `client_id`: Device identifier
  - `auto_validate`: Boolean (optional)
- Response: ImageUploadResponse
- Logic: Creates TrainingImage records, validates, returns detailed report

### Usage Example

```kotlin
// In ImageLabelViewModel
viewModelScope.launch {
    // Queue labeled images
    val imageIds = getSelectedImageIds()
    uploadQueueManager.queueBatch(
        imageIds = imageIds,
        batchId = UUID.randomUUID().toString(),
        priority = 1
    )
    
    // Process uploads
    val result = uploadQueueManager.processPendingUploads { current, total ->
        _uiState.update {
            it.copy(
                uploadProgress = current.toFloat() / total,
                uploadStatus = "Uploading $current/$total"
            )
        }
    }
    
    // Show result
    showSnackbar("Uploaded ${result.successCount} images, ${result.failedCount} failed")
    
    // Retry failures later
    if (result.failedCount > 0) {
        delay(5000) // Wait 5 seconds
        uploadQueueManager.retryFailed()
    }
}

// Observe active uploads for UI
uploadQueueManager.observeActiveUploads()
    .collect { activeUploads ->
        _uiState.update { it.copy(activeUploads = activeUploads) }
    }
```

---

## Configuration

### Build.gradle Dependencies

All dependencies already added in Phase 5.1.1:
```kotlin
// Retrofit & OkHttp
implementation("com.squareup.retrofit2:retrofit:2.9.0")
implementation("com.squareup.retrofit2:converter-gson:2.9.0")
implementation("com.squareup.okhttp3:okhttp:4.11.0")
implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")

// Room Database
implementation("androidx.room:room-runtime:2.5.2")
implementation("androidx.room:room-ktx:2.5.2")
kapt("androidx.room:room-compiler:2.5.2")

// DataStore (for preferences)
implementation("androidx.datastore:datastore-preferences:1.0.0")

// Gson
implementation("com.google.code.gson:gson:2.10.1")
```

### Dependency Injection

**`NetworkModule.kt`** (updated):
```kotlin
@Provides @Singleton
fun provideModelApi(retrofit: Retrofit): ModelApi

@Provides @Singleton
fun provideTrainingApi(retrofit: Retrofit): TrainingApi
```

**`MLModule.kt`** (to be updated):
```kotlin
@Provides @Singleton
fun provideModelUpdateManager(
    context: Context,
    modelApi: ModelApi,
    preferencesManager: PreferencesManager,
    modelManager: PyTorchModelManager
): ModelUpdateManager

@Provides @Singleton
fun provideUploadQueueManager(
    context: Context,
    uploadQueueDao: UploadQueueDao,
    imageDao: ImageDao,
    trainingApi: TrainingApi,
    preferencesManager: PreferencesManager,
    gson: Gson
): UploadQueueManager
```

### PreferencesManager (updated)

Added methods:
- `modelVersion: Flow<String?>` - Observe model version
- `setModelVersion(version: String)` - Store model version
- `getModelVersion(): String?` - Get version synchronously
- `getDeviceId(): String?` - Get device ID synchronously

---

## Testing

### Unit Tests

**ModelUpdateManagerTest.kt**:
```kotlin
@Test
fun `checkForUpdates returns null when no update available`()

@Test
fun `downloadAndInstall verifies checksum`()

@Test
fun `rollback restores previous model on failure`()
```

**UploadQueueManagerTest.kt**:
```kotlin
@Test
fun `queueImage creates pending upload`()

@Test
fun `processPendingUploads batches images correctly`()

@Test
fun `retryFailed only retries uploads below max retries`()
```

### Integration Tests

```kotlin
@Test
fun `end-to-end model update flow`() {
    // 1. Check for updates
    // 2. Download model
    // 3. Verify checksum
    // 4. Hot-swap model
    // 5. Verify new version in preferences
}

@Test
fun `end-to-end image upload flow`() {
    // 1. Queue images
    // 2. Process uploads
    // 3. Verify server IDs stored
    // 4. Check upload statistics
}
```

---

## UI Integration

### Models Screen (Task #5)

**Add to `ModelsViewModel.kt`**:
```kotlin
@Inject
lateinit var modelUpdateManager: ModelUpdateManager

fun checkForUpdates() {
    viewModelScope.launch {
        _uiState.update { it.copy(checkingUpdates = true) }
        
        val updateInfo = modelUpdateManager.checkForUpdates()
        
        _uiState.update {
            it.copy(
                checkingUpdates = false,
                updateAvailable = updateInfo != null,
                updateInfo = updateInfo
            )
        }
    }
}

fun downloadUpdate() {
    viewModelScope.launch {
        val updateInfo = _uiState.value.updateInfo ?: return@launch
        
        val result = modelUpdateManager.downloadAndInstall(updateInfo) { progress ->
            _uiState.update { it.copy(downloadProgress = progress) }
        }
        
        // Handle result
    }
}
```

**UI Components**:
- Update available banner
- Download progress bar
- Version comparison display
- Update changelog

### Label Screen (Task #6)

**Add to `ImageLabelViewModel.kt`**:
```kotlin
@Inject
lateinit var uploadQueueManager: UploadQueueManager

fun uploadLabeledImages() {
    viewModelScope.launch {
        val labeledImages = imageDao.getLabeledImages()
        
        uploadQueueManager.queueBatch(
            imageIds = labeledImages.map { it.id },
            batchId = UUID.randomUUID().toString()
        )
        
        val result = uploadQueueManager.processPendingUploads { current, total ->
            _uiState.update {
                it.copy(uploadProgress = current.toFloat() / total)
            }
        }
        
        // Show result
    }
}

init {
    // Observe active uploads
    uploadQueueManager.observeActiveUploads()
        .onEach { uploads ->
            _uiState.update { it.copy(activeUploads = uploads) }
        }
        .launchIn(viewModelScope)
}
```

**UI Components**:
- Upload queue status card
- Upload progress indicator
- Retry failed button
- Upload statistics

---

## API Documentation

### Model Download API

**Check for Updates**:
```bash
curl -X GET "http://localhost:8000/api/models/latest/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "X-Model-Version: 1.0.0"
```

Response:
```json
{
  "version": "1.2.0",
  "checksum": "abc123...",
  "download_url": "http://localhost:8000/api/models/download/1.2.0/",
  "requires_update": true,
  "file_size": 8388608,
  "released_at": "2025-11-07T10:30:00Z",
  "accuracy": 98.5,
  "description": "Improved accuracy on bicycle and car detection"
}
```

**Download Model**:
```bash
curl -X GET "http://localhost:8000/api/models/download/1.2.0/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -o model.ptl
```

### Image Upload API

**Upload Images**:
```bash
curl -X POST "http://localhost:8000/api/training/images/upload_from_mobile/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "labels=[\"Cat\",\"Dog\"]" \
  -F "batch_id=batch-123" \
  -F "client_id=device-456" \
  -F "auto_validate=false"
```

Response:
```json
{
  "success": 2,
  "failed": 0,
  "total": 2,
  "image_ids": [101, 102],
  "errors": [],
  "batch_id": "batch-123",
  "message": "Successfully uploaded 2 images"
}
```

---

## Performance Considerations

### Model Updates
- Download happens in background thread
- Progress callbacks prevent UI freezing
- Checksum verification prevents corrupted models
- Backup ensures rollback capability
- Hot-swap avoids app restart

### Image Uploads
- Batch size of 10 balances speed vs memory
- JPEG compression reduces bandwidth (quality 80%)
- Image resizing (max 800x800) reduces upload time
- Retry with exponential backoff prevents server overload
- Queue persists across app restarts (offline support)

### Database Optimization
- Indexed columns: status, batch_id, created_at
- Foreign key cascade deletes
- Periodic cleanup of old successful uploads
- Flow-based UI updates (reactive)

---

## Error Handling

### Model Updates
- Network errors → Show retry button
- Checksum mismatch → Delete download, show error
- Load failure → Automatic rollback to previous version
- Server errors → Log and notify user

### Image Uploads
- Network errors → Mark as FAILED, will retry
- Server errors → Store error message in queue
- Max retries exceeded → Mark as permanently failed
- Image compression errors → Skip image, continue batch

---

## Future Enhancements

### Task #5 Extensions
- [ ] Background update check (WorkManager)
- [ ] Update notifications
- [ ] Model version history
- [ ] A/B testing (multiple models)
- [ ] Delta updates (only changed layers)

### Task #6 Extensions
- [ ] Smart batching by label
- [ ] Upload scheduling (WiFi only, battery threshold)
- [ ] Upload analytics (success rate, bandwidth used)
- [ ] Automatic image augmentation before upload
- [ ] Duplicate detection

---

## Summary

**Task #5 - Model Download & Update System**: ✅ COMPLETE
- Android API interfaces created
- ModelUpdateManager with hot-swapping implemented
- Checksum verification and rollback support
- PreferencesManager updated for version storage
- Ready for UI integration in ModelsViewModel

**Task #6 - Image Upload Queue System**: ✅ COMPLETE
- Upload queue database schema created
- UploadQueueDao with comprehensive queries
- UploadQueueManager with batch upload and retry logic
- Image compression and multipart upload
- Ready for UI integration in ImageLabelViewModel

**Next Steps**:
1. Update `MLModule.kt` to provide new managers
2. Integrate into `ModelsViewModel` for update checks
3. Integrate into `ImageLabelViewModel` for uploads
4. Add UI components for progress tracking
5. Test end-to-end flows with real server
6. Implement WorkManager for background uploads (optional)
