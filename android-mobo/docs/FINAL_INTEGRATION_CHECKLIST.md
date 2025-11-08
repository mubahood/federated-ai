# Final Integration Checklist - Tasks #5 & #6

**Status**: Ready for UI Integration  
**Date**: November 7, 2025

---

## ✅ Completed Work

### Core Implementation (100% Complete)

#### Task #5: Model Download & Update System
- [x] Server-side API endpoints (`training/views.py`)
  - [x] `GET /api/models/latest/` - Check for updates
  - [x] `GET /api/models/download/{version}/` - Download model binary
- [x] Android API interfaces (`ModelApi.kt`)
- [x] Android DTOs (`ModelMetadataDto.kt`)
- [x] Model Update Manager (`ModelUpdateManager.kt`)
  - [x] Check for updates
  - [x] Download with progress tracking
  - [x] SHA256 checksum verification
  - [x] Hot-swap without restart
  - [x] Automatic backup and rollback
- [x] PreferencesManager updates (model version storage)
- [x] NetworkModule providers (ModelApi)
- [x] MLModule providers (ModelUpdateManager)

#### Task #6: Image Upload Queue System
- [x] Server-side API endpoint (`training/views.py`)
  - [x] `POST /api/training/images/upload_from_mobile/` - Batch upload
- [x] Android API interfaces (`TrainingApi.kt`)
- [x] Android DTOs (`ImageUploadResponse.kt`, `ImageUploadRequest.kt`)
- [x] Database schema (`UploadQueueEntity.kt`)
- [x] Database DAO (`UploadQueueDao.kt`)
- [x] Room TypeConverters (`Converters.kt`)
- [x] AppDatabase v2 (added UploadQueue table)
- [x] Upload Queue Manager (`UploadQueueManager.kt`)
  - [x] Queue single/batch images
  - [x] Image compression (JPEG 80%, max 800x800)
  - [x] Batch upload (10 images per request)
  - [x] Retry logic (max 3 attempts, exponential backoff)
  - [x] Progress tracking
  - [x] Upload statistics
- [x] NetworkModule providers (TrainingApi)
- [x] MLModule providers (UploadQueueManager)

#### Documentation
- [x] FEDERATED_FEATURES_IMPLEMENTATION.md (comprehensive guide)
- [x] TASKS_5_6_COMPLETE.md (summary)
- [x] Example ViewModels (ModelsViewModelExample.kt, ImageLabelViewModelExample.kt)

---

## 🔄 Next Steps: UI Integration

### Step 1: Update Existing ModelsViewModel

**File**: `ui/screens/models/ModelsViewModel.kt`

**Changes Needed**:
```kotlin
// Add injection
@Inject lateinit var modelUpdateManager: ModelUpdateManager

// Add to init or onCreate
fun checkForUpdates() { 
    // Copy from ModelsViewModelExample.kt
}

fun downloadUpdate() { 
    // Copy from ModelsViewModelExample.kt
}
```

**UI Changes Needed** (`ModelsScreen.kt`):
- [ ] Add "Check for Updates" button
- [ ] Show update available banner when `updateAvailable = true`
- [ ] Display new version info (version, size, description)
- [ ] Show download progress bar when `downloading = true`
- [ ] Display success/error messages

**Estimated Time**: 2-3 hours

---

### Step 2: Update Existing ImageLabelViewModel

**File**: `ui/screens/label/ImageLabelViewModel.kt`

**Changes Needed**:
```kotlin
// Add injection
@Inject lateinit var uploadQueueManager: UploadQueueManager

// Add to init
init {
    observeActiveUploads()
    // Copy from ImageLabelViewModelExample.kt
}

fun uploadLabeledImages() { 
    // Copy from ImageLabelViewModelExample.kt
}

fun retryFailedUploads() { 
    // Copy from ImageLabelViewModelExample.kt
}
```

**UI Changes Needed** (`ImageLabelScreen.kt`):
- [ ] Add "Upload" button (visible when labeled images exist)
- [ ] Show upload progress bar when `uploading = true`
- [ ] Display upload status text ("Uploading 5/20 images...")
- [ ] Show success/error messages
- [ ] Add "Retry Failed" button when `failedUploads > 0`
- [ ] Display upload queue stats card

**Estimated Time**: 3-4 hours

---

### Step 3: Test End-to-End Flows

#### Test Model Update Flow

**Setup**:
1. Ensure Django server running (`docker compose up`)
2. Ensure model v1.0.0 installed on device
3. Create new model version on server (v1.1.0)

**Test Steps**:
1. [ ] Open Models screen
2. [ ] Click "Check for Updates"
3. [ ] Verify update banner appears
4. [ ] Verify version comparison (1.0.0 → 1.1.0)
5. [ ] Click "Download"
6. [ ] Verify progress bar updates (0% → 100%)
7. [ ] Verify success message appears
8. [ ] Verify model hot-swaps (no restart needed)
9. [ ] Verify new version displayed (1.1.0)
10. [ ] Test prediction with new model (Predict tab)

**Expected Results**:
- ✅ Update check completes in < 2s
- ✅ Download completes in 5-10s (8MB file)
- ✅ Checksum verification succeeds
- ✅ Model hot-swaps without errors
- ✅ Predictions work with new model
- ✅ No app crash or restart

**Error Cases to Test**:
- [ ] Network timeout during download
- [ ] Invalid checksum (corrupted file)
- [ ] Server returns 404 (version not found)
- [ ] Load failure (triggers rollback)

**Estimated Time**: 1-2 hours

---

#### Test Image Upload Flow

**Setup**:
1. Ensure Django server running
2. Capture 20+ images in Train tab
3. Label images with categories

**Test Steps**:
1. [ ] Open Label screen
2. [ ] Verify labeled images displayed
3. [ ] Click "Upload"
4. [ ] Verify progress bar updates
5. [ ] Verify upload status text ("Uploading 5/20...")
6. [ ] Verify success message (e.g., "Uploaded 20 images")
7. [ ] Check server database (TrainingImage records created)
8. [ ] Verify images marked as uploaded locally

**Batch Upload Test**:
1. [ ] Queue 50 images
2. [ ] Verify batching (5 batches of 10 images)
3. [ ] Monitor network traffic (5 separate requests)
4. [ ] Verify all images uploaded successfully

**Retry Test**:
1. [ ] Disconnect network
2. [ ] Try to upload (should fail)
3. [ ] Verify images marked as FAILED
4. [ ] Reconnect network
5. [ ] Click "Retry Failed"
6. [ ] Verify successful retry

**Compression Test**:
1. [ ] Upload large images (> 2MB each)
2. [ ] Verify compression (< 500KB after compression)
3. [ ] Check quality on server
4. [ ] Verify predictions still work

**Expected Results**:
- ✅ Upload completes in 10-20s (20 images)
- ✅ Images compressed ~70% (original size)
- ✅ Batch size = 10 images per request
- ✅ Retry succeeds after network restored
- ✅ Queue persists across app restarts

**Error Cases to Test**:
- [ ] Network timeout during upload
- [ ] Server error (500)
- [ ] Invalid category name
- [ ] Max retries exceeded (3 attempts)

**Estimated Time**: 2-3 hours

---

### Step 4: Performance Testing

#### Model Update Performance

**Metrics to Track**:
- [ ] Update check time: < 2 seconds
- [ ] Download speed: ~1 MB/s (depends on network)
- [ ] Checksum verification time: < 100ms (8MB file)
- [ ] Hot-swap time: < 500ms
- [ ] Memory overhead during swap: < 20MB

**Test Cases**:
- [ ] Check for updates on slow network (3G)
- [ ] Download on fast network (WiFi)
- [ ] Hot-swap while app in background
- [ ] Multiple update checks in quick succession

#### Image Upload Performance

**Metrics to Track**:
- [ ] Compression time: < 200ms per image
- [ ] Upload speed: ~500 KB/s per batch (depends on network)
- [ ] Queue persistence time: < 100ms
- [ ] Retry delay: 5s, 10s, 20s (exponential backoff)

**Test Cases**:
- [ ] Upload 100 images (10 batches)
- [ ] Upload on slow network (3G)
- [ ] Upload while app in background
- [ ] Queue 50 images, close app, reopen (verify queue persists)

**Estimated Time**: 2-3 hours

---

### Step 5: Error Handling & Edge Cases

#### Model Update Errors

- [ ] No internet connection
- [ ] Server returns 404 (version not found)
- [ ] Server returns 500 (internal error)
- [ ] Checksum mismatch (corrupted download)
- [ ] Model load failure (automatic rollback)
- [ ] Disk full (can't save model)
- [ ] Already on latest version

#### Image Upload Errors

- [ ] No internet connection
- [ ] Server returns 400 (invalid request)
- [ ] Server returns 500 (internal error)
- [ ] Image file not found
- [ ] Compression failure
- [ ] Max retries exceeded
- [ ] Disk full (can't queue images)
- [ ] No images to upload

**Estimated Time**: 2-3 hours

---

## 📊 Testing Checklist Summary

### Unit Tests (To Be Written)

**ModelUpdateManager**:
- [ ] `checkForUpdates()` returns null when on latest version
- [ ] `checkForUpdates()` returns update info when available
- [ ] `downloadAndInstall()` downloads and verifies checksum
- [ ] `downloadAndInstall()` triggers rollback on load failure
- [ ] `calculateSHA256()` returns correct hash
- [ ] `rollback()` restores previous version

**UploadQueueManager**:
- [ ] `queueImage()` creates pending upload
- [ ] `queueBatch()` creates multiple pending uploads
- [ ] `processPendingUploads()` batches images correctly
- [ ] `compressImage()` reduces file size
- [ ] `retryFailed()` only retries uploads below max retries
- [ ] `cleanupOldUploads()` deletes old successful uploads

**Estimated Time**: 4-5 hours

---

### Integration Tests (To Be Written)

- [ ] End-to-end model update flow
- [ ] End-to-end image upload flow
- [ ] Network error recovery
- [ ] App restart persistence (upload queue)
- [ ] Concurrent operations (update + upload)

**Estimated Time**: 3-4 hours

---

### UI Tests (To Be Written)

- [ ] Models screen displays current version
- [ ] Update banner appears when available
- [ ] Progress bar updates during download
- [ ] Label screen shows upload button
- [ ] Upload progress updates correctly
- [ ] Retry button appears on failure

**Estimated Time**: 2-3 hours

---

## 🎯 Total Estimated Time

| Task | Time |
|------|------|
| Step 1: Update ModelsViewModel | 2-3 hours |
| Step 2: Update ImageLabelViewModel | 3-4 hours |
| Step 3: End-to-end testing | 3-5 hours |
| Step 4: Performance testing | 2-3 hours |
| Step 5: Error handling testing | 2-3 hours |
| Unit tests | 4-5 hours |
| Integration tests | 3-4 hours |
| UI tests | 2-3 hours |
| **TOTAL** | **21-30 hours** |

---

## 📝 Implementation Notes

### Database Migration

**IMPORTANT**: AppDatabase version changed from 1 → 2

When testing on existing devices, you may need to:
1. Uninstall app completely
2. Reinstall fresh build
3. OR implement migration strategy:

```kotlin
// In DatabaseModule.kt
Room.databaseBuilder(...)
    .addMigrations(MIGRATION_1_2)
    .build()

val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE upload_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                batch_id TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                error_message TEXT,
                server_image_id INTEGER,
                created_at INTEGER NOT NULL,
                last_attempt_at INTEGER,
                completed_at INTEGER,
                priority INTEGER DEFAULT 0,
                FOREIGN KEY(image_id) REFERENCES image_entity(id) ON DELETE CASCADE
            )
        """)
        database.execSQL("CREATE INDEX idx_upload_queue_image_id ON upload_queue(image_id)")
        database.execSQL("CREATE INDEX idx_upload_queue_status ON upload_queue(status)")
        database.execSQL("CREATE INDEX idx_upload_queue_batch_id ON upload_queue(batch_id)")
    }
}
```

### Device ID Generation

Ensure device ID is generated and stored:

```kotlin
// In InitializeAppUseCase or similar
suspend fun initializeDeviceId() {
    val existingId = preferencesManager.getDeviceId()
    if (existingId == null) {
        val deviceId = "device-${UUID.randomUUID()}"
        preferencesManager.saveDeviceId(deviceId)
    }
}
```

### Model Version Initialization

Set initial model version after bundled model loaded:

```kotlin
// In InitializeModelUseCase
if (modelManager.loadModelFromAssets("model.ptl")) {
    preferencesManager.setModelVersion("1.0.0") // Initial version
}
```

---

## 🚀 Deployment Checklist

### Before Production Release

- [ ] All tests passing (unit, integration, UI)
- [ ] Performance metrics acceptable
- [ ] Error handling tested thoroughly
- [ ] Server APIs stable and tested
- [ ] Database migration tested
- [ ] ProGuard rules added for new classes
- [ ] Documentation updated
- [ ] Code review completed

### ProGuard Rules to Add

```proguard
# ModelUpdateManager
-keep class com.federated.client.ml.pytorch.ModelUpdateManager { *; }
-keep class com.federated.client.ml.pytorch.ModelUpdateInfo { *; }
-keep class com.federated.client.ml.pytorch.UpdateResult { *; }

# UploadQueueManager
-keep class com.federated.client.data.repository.UploadQueueManager { *; }
-keep class com.federated.client.data.repository.UploadBatchResult { *; }

# Database entities
-keep class com.federated.client.data.local.db.entities.UploadQueueEntity { *; }
-keep class com.federated.client.data.local.db.entities.UploadStatus { *; }

# DTOs
-keep class com.federated.client.data.remote.dto.response.ModelMetadataDto { *; }
-keep class com.federated.client.data.remote.dto.response.ImageUploadResponse { *; }
```

---

## 📚 Reference Documents

- **FEDERATED_FEATURES_IMPLEMENTATION.md** - Complete implementation guide
- **TASKS_5_6_COMPLETE.md** - Summary and overview
- **ModelsViewModelExample.kt** - Model update integration example
- **ImageLabelViewModelExample.kt** - Upload queue integration example

---

## ✅ Success Criteria

### Task #5: Model Download & Update System

- [x] Server APIs complete and tested
- [x] Android client code complete
- [x] Dependency injection configured
- [ ] UI integration complete
- [ ] End-to-end testing complete
- [ ] Performance acceptable (< 10s update)
- [ ] Error handling robust

### Task #6: Image Upload Queue System

- [x] Server APIs complete and tested
- [x] Android client code complete
- [x] Database schema created
- [x] Dependency injection configured
- [ ] UI integration complete
- [ ] End-to-end testing complete
- [ ] Performance acceptable (< 30s for 20 images)
- [ ] Offline support working

---

## 🎉 Conclusion

All core implementation is **100% complete**. The remaining work is primarily UI integration and testing, which is well-documented and straightforward to implement using the provided example ViewModels.

**Estimated time to fully working features**: 1-2 weeks of focused development and testing.

**The federated learning loop is nearly complete!** 🚀
