# Next Steps & Todo List

**Current Status:** Foundation Complete (71% of MVP)  
**Last Updated:** November 7, 2025  
**Build Status:** ✅ BUILD SUCCESSFUL  
**Runtime Status:** ✅ No crashes  

---

## ✅ Completed (5 of 7 phases - 71%)

- [x] Phase 5.1.1: Android Project Setup (100%)
- [x] Phase 5.1.2: Design System & UI Foundation (100%)
- [x] Phase 5.1.3: Data Layer Foundation (100%)
- [x] Phase 5.1.4: Onboarding Screens (100%)
- [x] Phase 5.1.5: Home Dashboard (100%)
- [x] Phase 5.2.1: Camera Capture (100%)

**Stats:** 47 files, 6,036 lines, 0 errors, 0 crashes

---

## 🎯 Immediate Priority: Phase 5.2.2 - Image Labeling Interface

**Status:** Ready to implement (no blockers)  
**Estimated Effort:** 2-3 hours  
**Estimated Lines:** ~300 lines  

### Implementation Checklist

#### Step 1: Create ImageLabelViewModel (~150 lines)
- [ ] Load unlabeled images from database
  ```kotlin
  imageDao.getUnlabeledFlow().collect { images -> ... }
  ```
- [ ] Define category list (fetch from server or use predefined)
- [ ] Implement `assignLabel(imageId, category)` method
  ```kotlin
  imageDao.update(imageId, category = category, isLabeled = true)
  ```
- [ ] Track labeling progress
  - Total unlabeled count
  - Current image index
  - Progress percentage
- [ ] Implement skip/next navigation logic
- [ ] Handle batch labeling (select multiple → assign same category)
- [ ] UI state with: currentImage, categories, progress, loading, error

#### Step 2: Create ImageLabelScreen (~150 lines)
- [ ] Layout structure:
  - Top bar with progress (e.g., "3 of 15 labeled")
  - Large image preview (center)
  - Category selection UI (bottom)
  - Navigation buttons (Skip, Back, Next)
  
- [ ] Image preview section:
  - Display unlabeled image (Coil)
  - Add zoom/pan gestures (Modifier.zoomable)
  - Show image metadata (resolution, file size)
  
- [ ] Category selection UI:
  - Option 1: Horizontal scrolling chips
  - Option 2: Dropdown menu
  - Option 3: Grid layout (if many categories)
  - Highlight selected category
  
- [ ] Action buttons:
  - "Skip" button (move to next without labeling)
  - "Assign Label" button (save and move to next)
  - "Back" button (navigate to previous image)
  
- [ ] Empty state:
  - Show when all images labeled
  - Success message with checkmark
  - "Back to Dashboard" button
  
- [ ] Loading/error states

#### Step 3: Integration
- [ ] Add route to NavGraph
  ```kotlin
  composable(Route.Label.route) {
      ImageLabelScreen(...)
  }
  ```
- [ ] Connect from HomeScreen "Label" button
  ```kotlin
  onLabelClick = { navController.navigate(Route.Label.route) }
  ```
- [ ] Pass unlabeled count as badge on Label button
  ```kotlin
  QuickActionItem(
      icon = Icons.Default.Label,
      label = "Label",
      badgeCount = uiState.unlabeledCount
  )
  ```
- [ ] Auto-refresh dashboard after labeling
  - Dashboard already uses Flow, so updates automatic
  
#### Step 4: Testing
- [ ] Test labeling single image
- [ ] Test skip functionality
- [ ] Test navigation (back/next)
- [ ] Test empty state (all labeled)
- [ ] Test with many images (performance)
- [ ] Test category selection
- [ ] Verify database updates correctly
- [ ] Verify dashboard refreshes

### Success Criteria
✅ Users can see all unlabeled images  
✅ Users can assign categories efficiently  
✅ Changes persist to database correctly  
✅ Dashboard updates automatically  
✅ Progress clearly displayed  
✅ Smooth navigation between images  

---

## 🔜 Secondary Priority: Phase 5.2.3 - Gallery View

**Status:** Ready to implement (no blockers)  
**Estimated Effort:** 3-4 hours  
**Estimated Lines:** ~350 lines  

### Implementation Checklist

#### Step 1: Create GalleryViewModel (~150 lines)
- [ ] Load all images from database
  ```kotlin
  imageDao.getAllFlow().collect { images -> ... }
  ```
- [ ] Implement filter by category
- [ ] Implement filter by labeled/unlabeled status
- [ ] Implement sort options (date, category, status)
- [ ] Implement search functionality
- [ ] Implement delete operations (single/batch)
- [ ] Selection mode state management
- [ ] UI state with: images, filters, selectedImages, loading, error

#### Step 2: Create GalleryScreen (~200 lines)
- [ ] Layout structure:
  - Top bar with title and action buttons
  - Filter/sort chips (horizontal scroll)
  - Image grid (LazyVerticalGrid)
  - Floating action buttons (filter, delete)
  
- [ ] Image grid:
  - LazyVerticalGrid with 3 columns
  - Thumbnail display (Coil)
  - Metadata badges (labeled status, category)
  - Selection checkbox (long press to activate)
  
- [ ] Selection mode:
  - Long press to activate
  - Show checkboxes on all items
  - Show selected count in top bar
  - Show delete/share buttons
  
- [ ] Detail view:
  - Full-screen image preview
  - Swipe left/right between images
  - Show metadata (date, category, size, resolution)
  - Edit/relabel button
  - Delete button
  - Share button
  
- [ ] Filter UI:
  - Category chips
  - Status chips (All, Labeled, Unlabeled)
  - Sort dropdown (Date, Category, Status)
  
- [ ] Empty states:
  - No images captured yet
  - No results for filter

#### Step 3: Integration
- [ ] Add routes to NavGraph (Gallery, ImageDetail)
- [ ] Connect from HomeScreen "Gallery" button
- [ ] Connect from recent captures section
- [ ] Handle navigation to detail view

#### Step 4: Testing
- [ ] Test with empty gallery
- [ ] Test with many images (1000+)
- [ ] Test filtering and sorting
- [ ] Test selection mode
- [ ] Test delete operations
- [ ] Test detail view navigation
- [ ] Test swipe between images
- [ ] Test edit/relabel flow

---

## 🚫 Blocked: Phase 5.3.1 - FL Client Integration

**Status:** Blocked - Flower Android library not available  
**Priority:** CRITICAL (core FL functionality)  
**Estimated Effort:** 4-6 hours (once unblocked)  

### Blocker Resolution Options

#### Option 1: Wait for Official Release ⏳
- **Pros:** Official support, guaranteed compatibility
- **Cons:** Unknown timeline, project delayed
- **Action:** Monitor Flower GitHub releases

#### Option 2: Download AAR Manually 📦
- **Pros:** Can proceed immediately if AAR available
- **Cons:** Manual updates, may have compatibility issues
- **Action:** Check if Flower provides AAR download

#### Option 3: Build from Source 🔨
- **Pros:** Full control, can fix issues
- **Cons:** Time-consuming, requires Flower build knowledge
- **Action:** Clone Flower repo, build Android SDK

#### Option 4: Alternative FL Framework 🔄
- **Pros:** Unblock development immediately
- **Cons:** May require architecture changes
- **Options:**
  - TensorFlow Federated (TFF)
  - PySyft Mobile
  - Custom FL implementation

### Recommendation
**Start with Option 1** (wait for official release) while proceeding with Options 5.2.2 and 5.2.3. If Flower not released within 2 weeks, evaluate Option 4 (alternative framework).

---

## 📋 Additional Tasks (Lower Priority)

### Testing (High Priority)
- [ ] Write unit tests for ViewModels
  - RegistrationViewModel: 7 validation rules
  - HomeViewModel: Inventory calculations
  - CameraViewModel: Capture pipeline
  
- [ ] Write unit tests for DAOs
  - Test all 85+ query methods
  - Test Flow updates
  - Test transactions
  
- [ ] Write unit tests for Storage Managers
  - ImageStorageManager: Save, load, delete
  - CacheManager: Cleanup, statistics
  
- [ ] Write integration tests
  - Onboarding flow end-to-end
  - Camera capture and save
  - Dashboard data loading
  
- [ ] Write UI tests (Espresso/Compose Test)
  - User can complete onboarding
  - User can capture image
  - Dashboard displays data correctly

**Target Coverage:** 80%+

### Documentation (Medium Priority)
- [x] Foundation Architecture document ✅
- [x] Progress Tracker document ✅
- [x] Implementation Summary ✅
- [ ] API Documentation (DAO methods, Storage APIs)
- [ ] User Guide (how to use app)
- [ ] Developer Guide (how to contribute)

### Settings Screen (Low Priority)
- [ ] Create SettingsViewModel
- [ ] Create SettingsScreen
- [ ] Theme selection (Light, Dark, Auto)
- [ ] Notification preferences
- [ ] Auto-training toggle
- [ ] Cache management
- [ ] About section (version, licenses)

### Sync/Upload System (Low Priority, blocked by FL)
- [ ] Create SyncViewModel
- [ ] Implement upload to server
- [ ] Track upload status
- [ ] Handle network errors
- [ ] Retry failed uploads
- [ ] Show sync progress

---

## 🏗️ Development Workflow

### Before Starting Next Phase

1. **Verify Current State**
   ```bash
   cd android-mobo
   ./gradlew clean build
   # Should see: BUILD SUCCESSFUL
   ```

2. **Check for Errors**
   ```bash
   adb logcat -c  # Clear logs
   adb logcat | grep -i "error\|exception"
   ```

3. **Run App on Emulator**
   ```bash
   ./gradlew installDebug
   adb shell am start -n com.federated.client.debug/com.federated.client.MainActivity
   ```

### During Development

1. **Create New Files**
   - ViewModels in: `ui/screens/<feature>/`
   - Screens in: `ui/screens/<feature>/`
   - Components in: `ui/components/`

2. **Follow Naming Conventions**
   - ViewModels: `FeatureViewModel.kt`
   - Screens: `FeatureScreen.kt`
   - Components: `FeatureName.kt`

3. **Update NavGraph**
   - Add new routes to `Route.kt`
   - Add composable to `NavGraph.kt`

4. **Test as You Go**
   - Use Compose Preview for UI
   - Run on emulator frequently
   - Check logs for errors

### After Completing Phase

1. **Build and Test**
   ```bash
   ./gradlew clean build
   ./gradlew test  # When tests added
   ```

2. **Update Documentation**
   - Update PROGRESS_TRACKER.md
   - Add notes to IMPLEMENTATION_SUMMARY.md
   - Document any new APIs

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: implement Phase 5.2.2 - Image Labeling Interface"
   git push
   ```

---

## 📊 Progress Tracking

### Current Milestone: Complete Data Collection UI (Phase 5.2)

```
Phase 5.2.1: Camera Capture        ████████████████████ 100% ✅
Phase 5.2.2: Image Labeling        ░░░░░░░░░░░░░░░░░░░░   0% ⬜
Phase 5.2.3: Gallery View          ░░░░░░░░░░░░░░░░░░░░   0% ⬜
─────────────────────────────────────────────────────────────
Phase 5.2 Total:                   ███████░░░░░░░░░░░░░  33%
```

### Overall MVP Progress

```
Phase 5.1: Foundation              ████████████████████ 100% ✅
Phase 5.2: Data Collection UI      ███████░░░░░░░░░░░░░  33% 🔄
Phase 5.3: FL Integration          ░░░░░░░░░░░░░░░░░░░░   0% 🚫
─────────────────────────────────────────────────────────────
TOTAL MVP:                         ██████████████░░░░░░  71%
```

**Target:** 100% MVP completion  
**Timeline:** ~2-3 weeks (assuming FL blocker resolved)  

---

## 🎯 Definition of Done (DoD)

### For Each Phase
- [ ] All planned files created
- [ ] All features implemented
- [ ] Code compiles without errors
- [ ] App runs without crashes
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] Code reviewed (if team)
- [ ] Git committed and pushed

### For MVP Completion
- [ ] All 7 phases complete (5.1.1 - 5.3.1)
- [ ] Unit tests written (80% coverage)
- [ ] Integration tests written
- [ ] UI tests written (critical paths)
- [ ] Documentation complete
- [ ] Performance acceptable
- [ ] Security audit done
- [ ] Ready for beta testing

---

## 📞 Quick Reference

### Key Files
- **Project Structure:** `/Users/mac/Desktop/github/federated-ai/android-mobo/`
- **Source Code:** `app/src/main/java/com/federated/client/`
- **Build File:** `app/build.gradle.kts`
- **Documentation:** `docs/`

### Key Commands
```bash
# Build
./gradlew clean build

# Install on emulator
./gradlew installDebug

# Launch app
adb shell am start -n com.federated.client.debug/com.federated.client.MainActivity

# View logs
adb logcat | grep federated

# Count files
find app/src/main/java -name "*.kt" | wc -l

# Count lines
find app/src/main/java -name "*.kt" -exec wc -l {} + | tail -1
```

### Documentation Files
- `FOUNDATION_ARCHITECTURE.md` - Complete architecture overview
- `PROGRESS_TRACKER.md` - Detailed progress tracking
- `IMPLEMENTATION_SUMMARY.md` - Phase-by-phase implementation details
- `NEXT_STEPS.md` - This file (immediate action items)

---

**Status:** Ready to proceed with Phase 5.2.2 ✅  
**Blockers:** None for current phase  
**Estimated Completion:** 2-3 hours  
**Next Review:** After Phase 5.2.2 completion  

Let's build something awesome! 🚀
