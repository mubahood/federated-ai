# 🚀 Quick Start: Testing Guide

**Status**: ✅ Implementation Complete - Ready to Test  
**Date**: November 7, 2025

---

## ⚡ Quick Start (5 minutes)

### 1. Start Server Stack
```bash
cd /Users/mac/Desktop/github/federated-ai
docker compose -f docker/docker-compose.yml up -d
```

### 2. Start Celery Worker
```bash
docker compose -f docker/docker-compose.yml exec django \
  celery -A config worker -l info
```

### 3. Verify Server
```bash
# Check Django is running
curl http://localhost:8000/api/health/

# Check Redis
docker compose -f docker/docker-compose.yml exec redis redis-cli ping
```

### 4. Build & Run Android App
```bash
cd android-mobo
# Open in Android Studio
# Build → Make Project
# Run → Run 'app'
```

---

## 🧪 Testing Phases

### Phase 1: Model Update Testing (2 hours)
**Document**: `E2E_TESTING_GUIDE.md` → Test Suite 1

**Quick Tests**:
1. Open Models tab → Click "Check for Updates"
2. Expected: "You have the latest model version"
3. (To test update): Create new ModelVersion on server with version 1.1.0
4. Click "Check for Updates" again
5. Expected: Update banner appears
6. Click "Download Update"
7. Expected: Progress bar animates, success message, version updates

**Pass Criteria**: ✅ All 6 tests pass

---

### Phase 2: Upload Queue Testing (2 hours)
**Document**: `E2E_TESTING_GUIDE.md` → Test Suite 2

**Quick Tests**:
1. Train tab → Capture 10 images
2. Gallery → Label Images → Label all 10
3. After labeling complete → Click "Upload Labeled Images"
4. Expected: Progress bar, statistics update, success message
5. Turn off WiFi → Upload more → Expected: Failed uploads
6. Turn on WiFi → Click "Retry Failed"
7. Expected: Retry succeeds

**Pass Criteria**: ✅ All 7 tests pass

---

### Phase 3: Model Performance Testing (2 hours)
**Document**: `MODEL_PERFORMANCE_TESTING.md`

**Quick Tests**:
1. Predict tab → Capture/select 10 images per class (50 total)
2. Record predictions and confidence scores
3. Calculate accuracy per class
4. Overall accuracy should be ≥ 80%

**Pass Criteria**: ✅ Accuracy ≥ 80%, inference < 500ms

---

## 📊 Success Checklist

### Before Starting
- [ ] Docker running
- [ ] Server accessible (http://localhost:8000)
- [ ] Celery worker running
- [ ] Redis running
- [ ] Android app builds successfully
- [ ] App installs on device/emulator

### Phase 1: Model Updates
- [ ] Check for updates works
- [ ] Update banner appears (when update available)
- [ ] Download shows progress bar
- [ ] Download completes successfully
- [ ] Hot-swap works (no restart needed)
- [ ] Error handling works (network off)

### Phase 2: Upload Queue
- [ ] Label images works
- [ ] Upload button appears
- [ ] Upload progress shows
- [ ] Statistics update correctly
- [ ] Failed uploads show
- [ ] Retry works
- [ ] Compression reduces size

### Phase 3: Model Performance
- [ ] Bicycle: __/10 (≥7)
- [ ] Car: __/10 (≥7)
- [ ] Cat: __/10 (≥7)
- [ ] Dog: __/10 (≥7)
- [ ] Person: __/10 (≥7)
- [ ] **Total: __/50 (≥40)**

---

## 🐛 Quick Troubleshooting

### Server not responding
```bash
# Check containers
docker compose -f docker/docker-compose.yml ps

# Check logs
docker compose -f docker/docker-compose.yml logs django

# Restart if needed
docker compose -f docker/docker-compose.yml restart django
```

### App won't connect to server
```bash
# If using emulator, use 10.0.2.2 instead of localhost
# Check NetworkModule.kt BASE_URL

# If using physical device, use computer's IP
# Example: http://192.168.1.100:8000
```

### Celery not processing tasks
```bash
# Check Celery is running
docker compose -f docker/docker-compose.yml exec django \
  ps aux | grep celery

# Restart Celery
docker compose -f docker/docker-compose.yml restart django
```

### Model predictions all wrong
```bash
# Check model file exists
ls android-mobo/app/src/main/assets/mobilenetv3.ptl

# Check model loaded
# Models tab should show "Ready for Inference"

# Check class labels
# Models tab should show: Bicycle, Car, Cat, Dog, Person
```

---

## 📝 Report Results

### After Testing, Document:

**Phase 1 Results**:
- Tests Passed: __/6
- Model download time: __ seconds
- Hot-swap worked: ✅ Yes ⬜ No
- Issues found: __________

**Phase 2 Results**:
- Tests Passed: __/7
- Upload 20 images time: __ seconds
- Compression ratio: __%
- Retry worked: ✅ Yes ⬜ No
- Issues found: __________

**Phase 3 Results**:
- Overall Accuracy: __%
- Bicycle: __ / 10
- Car: __ / 10
- Cat: __ / 10
- Dog: __ / 10
- Person: __ / 10
- Inference time: __ ms
- Issues found: __________

**Overall Status**: ⬜ PASS ⬜ FAIL

---

## 🎯 Next Steps

### If All Pass ✅
1. Mark Tasks #3, #5, #6 complete
2. Celebrate! 🎉
3. Move to Task #7: User Feedback Loop

### If Some Fail ❌
1. Review detailed test guides
2. Debug specific failures
3. Fix issues
4. Re-test
5. Document fixes

---

## 📚 Full Documentation

**For detailed testing**:
- `E2E_TESTING_GUIDE.md` - 15 comprehensive tests
- `MODEL_PERFORMANCE_TESTING.md` - 50-image test plan

**For reference**:
- `IMPLEMENTATION_SUMMARY_ABC.md` - Quick summary
- `FINAL_SUMMARY_ABC.md` - Complete overview

---

## ⏱️ Time Estimates

| Phase | Time | Priority |
|-------|------|----------|
| Setup | 5 min | Required |
| Phase 1 | 2 hours | High |
| Phase 2 | 2 hours | High |
| Phase 3 | 2 hours | Medium |
| **Total** | **~6 hours** | - |

---

## 🎉 You're Ready!

Everything is implemented and ready to test. Follow this guide for quick validation, or use the detailed guides for comprehensive testing.

**Start testing now** → Phase 1: Model Updates

Good luck! 🚀
