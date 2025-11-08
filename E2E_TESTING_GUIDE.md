# 🧪 End-to-End Testing Guide

**Date**: November 7, 2025  
**Status**: Ready for Testing  
**Features**: Model Updates (Task #5) + Image Upload Queue (Task #6)

---

## 🎯 Testing Overview

This guide covers end-to-end testing of the complete federated learning system:
1. **Model Download & Update** (Task #5)
2. **Image Upload Queue** (Task #6)
3. **Full Federated Learning Loop**

---

## ✅ Pre-Testing Checklist

### Server Setup
- [ ] Docker containers running (`docker compose -f docker/docker-compose.yml up -d`)
- [ ] PostgreSQL database accessible
- [ ] Redis running on port 6379
- [ ] Django server running on http://localhost:8000
- [ ] Celery worker running (`celery -A config worker -l info`)

### Android App Setup
- [ ] Android Studio project synced
- [ ] No compilation errors
- [ ] Emulator or physical device connected
- [ ] App installed and running
- [ ] Network permissions granted
- [ ] Storage permissions granted

### Verify Server Endpoints
```bash
# Check server health
curl http://localhost:8000/api/health/

# Check models endpoint
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/models/latest/

# Check training endpoint
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/training/images/upload_from_mobile/
```

---

## 🧪 Test Suite 1: Model Download & Update (Task #5)

### Test 1.1: Check for Updates (No Update Available)

**Scenario**: Server has same version as client

**Steps**:
1. Open Android app
2. Navigate to **Models** tab
3. Click **"Check for Updates"** button
4. Observe UI state

**Expected Results**:
- ✅ Button shows loading spinner
- ✅ Request completes in < 2 seconds
- ✅ Snackbar shows: "You have the latest model version"
- ✅ No update banner appears
- ✅ Current model version displayed correctly

**How to Test**:
```bash
# On server, ensure no newer version exists
# Current app has version 1.0.0, so server should return same or older
```

---

### Test 1.2: Check for Updates (Update Available)

**Scenario**: Server has newer version than client

**Steps**:
1. On server, create new ModelVersion (version 1.1.0)
2. Open Android app → Models tab
3. Click **"Check for Updates"**
4. Observe UI

**Expected Results**:
- ✅ Update available banner appears
- ✅ Banner shows: "Version 1.0.0 → 1.1.0"
- ✅ Download button visible
- ✅ File size displayed (e.g., "8.5 MB")
- ✅ Banner has secondary color scheme

**Server Setup**:
```bash
# Create test model version
docker compose -f docker/docker-compose.yml exec django python manage.py shell

from training.models import ModelVersion
ModelVersion.objects.create(
    version="1.1.0",
    model_file="models/mobilenetv3_v1.1.0.ptl",
    checksum="abc123...",
    accuracy=0.987,
    size_bytes=8500000,
    is_active=True
)
```

---

### Test 1.3: Download Model Update

**Scenario**: Download new model version with progress tracking

**Steps**:
1. Ensure Test 1.2 passed (update available)
2. Click **"Download Update"** button in banner
3. Watch progress bar
4. Wait for completion

**Expected Results**:
- ✅ Download button disabled during download
- ✅ Progress bar animates from 0% to 100%
- ✅ Percentage text updates (e.g., "45%")
- ✅ Download completes in 5-10 seconds (WiFi)
- ✅ Success snackbar appears: "Model updated to version 1.1.0"
- ✅ Banner disappears after success
- ✅ Current model version updates to 1.1.0
- ✅ No app restart required (hot-swap)

**Performance**:
- Download time: 5-10 seconds for 8MB file (WiFi)
- Checksum verification: < 100ms
- Hot-swap time: < 500ms

---

### Test 1.4: Download with Network Error

**Scenario**: Simulate network failure during download

**Steps**:
1. Start download
2. Turn off WiFi/cellular mid-download
3. Observe error handling

**Expected Results**:
- ✅ Error snackbar appears
- ✅ Error message clear: "Download failed: Network error"
- ✅ Progress bar resets to 0%
- ✅ Download button re-enabled
- ✅ Can retry download
- ✅ Old model still active (no corruption)

---

### Test 1.5: Checksum Verification Failure

**Scenario**: Downloaded file has wrong checksum

**Steps**:
1. On server, modify checksum in ModelVersion to incorrect value
2. Download model
3. Observe verification failure

**Expected Results**:
- ✅ Download completes
- ✅ Verification fails
- ✅ Error message: "Checksum verification failed"
- ✅ Downloaded file deleted
- ✅ Old model still active
- ✅ Automatic rollback successful

---

### Test 1.6: Hot-Swap Verification

**Scenario**: Verify model actually swaps without restart

**Steps**:
1. Note current model version in Models tab
2. Download update (version 1.1.0)
3. Navigate to **Predict** tab
4. Run inference on test image
5. Check predictions

**Expected Results**:
- ✅ Predict tab still works after update
- ✅ No app restart needed
- ✅ Predictions use new model
- ✅ Model version in Models tab shows 1.1.0

---

## 🧪 Test Suite 2: Image Upload Queue (Task #6)

### Test 2.1: Label Images

**Scenario**: Create labeled images for upload

**Steps**:
1. Open app → **Train** tab
2. Capture or select 20 images
3. Navigate to **Gallery** → **Label Images**
4. Label all images with correct categories
5. Navigate back to Gallery

**Expected Results**:
- ✅ All 20 images captured
- ✅ All images labeled successfully
- ✅ Progress shows "20 of 20"
- ✅ "All Images Labeled!" screen appears

---

### Test 2.2: Upload Labeled Images

**Scenario**: Upload all labeled images to server

**Steps**:
1. From "All Images Labeled!" screen
2. Click **"Upload Labeled Images"** button
3. Observe upload progress
4. Wait for completion

**Expected Results**:
- ✅ Progress bar appears
- ✅ Progress animates from 0% to 100%
- ✅ Text shows "Uploading X images... Y%"
- ✅ Upload completes in 10-20 seconds (20 images, WiFi)
- ✅ Success snackbar: "Successfully uploaded 20 images"
- ✅ Upload statistics update:
  - Pending: 0
  - Success: 20
  - Failed: 0

**Performance**:
- Image compression: < 200ms per image
- Compression ratio: ~70% size reduction
- Batch upload time: 10-20 seconds for 20 images

**Server Verification**:
```bash
# Check uploaded images on server
docker compose -f docker/docker-compose.yml exec django python manage.py shell

from training.models import TrainingImage
print(f"Total images: {TrainingImage.objects.count()}")
print(f"From mobile: {TrainingImage.objects.filter(source='mobile').count()}")
```

---

### Test 2.3: Upload with Network Error

**Scenario**: Simulate network failure during upload

**Steps**:
1. Label 10 images
2. Click "Upload"
3. Turn off network after 2-3 seconds
4. Wait for timeout
5. Turn network back on

**Expected Results**:
- ✅ Upload starts successfully
- ✅ Some images upload before network failure
- ✅ Failed images move to "Failed" status
- ✅ Error snackbar appears
- ✅ Upload statistics show:
  - Pending: 0
  - Success: ~5 (uploaded before failure)
  - Failed: ~5 (failed after network off)
- ✅ **"Retry Failed"** button appears

---

### Test 2.4: Retry Failed Uploads

**Scenario**: Retry uploads that failed

**Steps**:
1. Ensure Test 2.3 has failed uploads
2. Turn network back on
3. Click **"Retry Failed Uploads"** button
4. Observe retry process

**Expected Results**:
- ✅ Retry button shows count: "Retry 5 Failed Uploads"
- ✅ Progress bar appears
- ✅ Failed images retry one by one
- ✅ Success snackbar: "Retry completed"
- ✅ Upload statistics update:
  - Pending: 0
  - Success: 10 (all succeeded)
  - Failed: 0
- ✅ Retry button disappears

**Exponential Backoff**:
- 1st attempt: immediate
- 2nd attempt: after 5 seconds
- 3rd attempt: after 10 seconds
- Max retries: 3

---

### Test 2.5: Upload Statistics Persistence

**Scenario**: Verify upload queue persists across app restarts

**Steps**:
1. Label 10 images
2. Click "Upload"
3. Turn off network (cause failures)
4. Close app completely
5. Reopen app
6. Navigate to Gallery → All Labeled screen

**Expected Results**:
- ✅ Upload statistics still visible
- ✅ Failed count preserved
- ✅ "Retry Failed" button still available
- ✅ Can retry after app restart

---

### Test 2.6: Image Compression Verification

**Scenario**: Verify images are compressed before upload

**Steps**:
1. Capture high-res image (e.g., 4000x3000, 5MB)
2. Label image
3. Upload image
4. Check upload size (network inspector or server logs)

**Expected Results**:
- ✅ Original: ~5MB (4000x3000)
- ✅ After compression: ~1.5MB (800x800, JPEG 80%)
- ✅ Compression ratio: ~70% reduction
- ✅ Image quality still good for training
- ✅ Upload faster due to smaller size

---

### Test 2.7: Batch Upload (Large Dataset)

**Scenario**: Upload 50+ images in batch

**Steps**:
1. Label 50 images (mix of all 5 categories)
2. Click "Upload Labeled Images"
3. Observe batch processing

**Expected Results**:
- ✅ Images uploaded in batches of 10
- ✅ Progress updates smoothly
- ✅ Total time: ~50-60 seconds for 50 images
- ✅ Server receives all 50 images
- ✅ No memory issues
- ✅ App remains responsive

**Batch Processing**:
- Batch size: 10 images per request
- 50 images = 5 batches
- ~10-12 seconds per batch

---

## 🧪 Test Suite 3: Full Federated Learning Loop

### Test 3.1: Complete End-to-End Flow

**Scenario**: Full cycle from image capture to model update

**Steps**:
1. **Capture & Label** (Client)
   - Capture 20 images per class (100 total)
   - Label all images correctly
   
2. **Upload** (Client → Server)
   - Upload all labeled images
   - Verify upload success
   
3. **Train** (Server)
   - Trigger training via API
   - Monitor Celery worker logs
   - Wait for training completion
   
4. **Publish** (Server)
   - Verify new ModelVersion created
   - Check model file exists
   - Verify checksum calculated
   
5. **Update** (Server → Client)
   - Check for updates in app
   - Download new model
   - Verify hot-swap
   
6. **Validate** (Client)
   - Run predictions with new model
   - Compare accuracy with old model
   - Verify improved performance

**Expected Results**:
- ✅ Complete loop in < 30 minutes
- ✅ All steps successful
- ✅ New model shows improved accuracy
- ✅ No errors or crashes
- ✅ User sees seamless experience

---

### Test 3.2: Training API Trigger

**Scenario**: Manually trigger training after uploads

**Steps**:
```bash
# Trigger training via API
curl -X POST http://localhost:8000/api/models/train/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 10,
    "batch_size": 32,
    "learning_rate": 0.001
  }'

# Response:
{
  "job_id": "abc123...",
  "status": "pending",
  "message": "Training job submitted"
}

# Check status
curl http://localhost:8000/api/models/training-status/abc123.../ \
  -H "Authorization: Token YOUR_TOKEN"

# Response (in progress):
{
  "status": "running",
  "progress": 45,
  "current_epoch": 4,
  "total_epochs": 10,
  "training_loss": 0.234,
  "validation_accuracy": 0.89
}

# Response (complete):
{
  "status": "completed",
  "model_version": "1.2.0",
  "final_accuracy": 0.95,
  "training_time": "8m 32s"
}
```

**Expected Results**:
- ✅ Training starts within 5 seconds
- ✅ Status endpoint shows progress
- ✅ Training completes in 5-15 minutes (depends on data size)
- ✅ ModelVersion created automatically
- ✅ Model file saved to media/models/
- ✅ Checksum calculated correctly

---

## 📊 Performance Benchmarks

### Model Updates (Task #5)
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Check for updates | < 2s | ___s | ⏱️ |
| Download 8MB model | 5-10s | ___s | ⏱️ |
| Checksum verification | < 100ms | ___ms | ⏱️ |
| Hot-swap time | < 500ms | ___ms | ⏱️ |
| Total update time | < 15s | ___s | ⏱️ |

### Image Uploads (Task #6)
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Image compression | < 200ms | ___ms | ⏱️ |
| Compression ratio | ~70% | ___%  | ⏱️ |
| Upload 20 images | 10-20s | ___s | ⏱️ |
| Batch size | 10 images | ___ | ⏱️ |
| Retry delay (1st) | 5s | ___s | ⏱️ |
| Retry delay (2nd) | 10s | ___s | ⏱️ |
| Max retries | 3 | ___ | ⏱️ |

### Training Pipeline (Task #4)
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Training start | < 5s | ___s | ⏱️ |
| Training time (100 images) | 5-15min | ___min | ⏱️ |
| Model export | < 10s | ___s | ⏱️ |
| ModelVersion creation | < 1s | ___s | ⏱️ |

---

## 🐛 Common Issues & Solutions

### Issue 1: "No update available" when update exists
**Solution**: Check server ModelVersion table. Ensure `is_active=True` and version > current client version.

### Issue 2: Download stuck at 0%
**Solution**: Check network connectivity. Verify server URL in NetworkModule.kt. Check authorization token.

### Issue 3: Upload fails with "Unauthorized"
**Solution**: Ensure user is logged in. Check token in PreferencesManager. Verify token in server database.

### Issue 4: Images not compressing
**Solution**: Check JPEG compression code in UploadQueueManager. Verify max dimensions (800x800).

### Issue 5: Training job never starts
**Solution**: Check Celery worker is running: `celery -A config worker -l info`. Verify Redis connection. Check Celery logs for errors.

### Issue 6: Hot-swap not working
**Solution**: Check PyTorchModelManager.loadModel() called correctly. Verify model file saved to correct path. Check file permissions.

---

## ✅ Test Sign-Off

### Task #5: Model Download & Update
- [ ] Test 1.1: Check for updates (no update) ✅
- [ ] Test 1.2: Check for updates (update available) ✅
- [ ] Test 1.3: Download model update ✅
- [ ] Test 1.4: Network error handling ✅
- [ ] Test 1.5: Checksum verification ✅
- [ ] Test 1.6: Hot-swap verification ✅

**Overall Status**: ⬜ Pass ⬜ Fail

---

### Task #6: Image Upload Queue
- [ ] Test 2.1: Label images ✅
- [ ] Test 2.2: Upload labeled images ✅
- [ ] Test 2.3: Network error handling ✅
- [ ] Test 2.4: Retry failed uploads ✅
- [ ] Test 2.5: Upload statistics persistence ✅
- [ ] Test 2.6: Image compression ✅
- [ ] Test 2.7: Batch upload (large dataset) ✅

**Overall Status**: ⬜ Pass ⬜ Fail

---

### Task #4: Training Pipeline Integration
- [ ] Test 3.1: Complete end-to-end flow ✅
- [ ] Test 3.2: Training API trigger ✅

**Overall Status**: ⬜ Pass ⬜ Fail

---

## 📝 Test Summary

**Date Tested**: ___________  
**Tester**: ___________  
**Environment**: ⬜ Emulator ⬜ Physical Device  
**Android Version**: ___________  
**Server Version**: ___________

**Total Tests**: 15  
**Passed**: ___  
**Failed**: ___  
**Blocked**: ___

**Overall Result**: ⬜ PASS ⬜ FAIL ⬜ NEEDS FIXES

---

**Next Steps**: After all tests pass, proceed to **Phase C: Test Model Performance (Task #3)**

