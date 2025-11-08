# 🧠 Model Performance Testing Guide (Task #3)

**Date**: November 7, 2025  
**Model**: MobileNetV3-Small Pre-trained  
**Classes**: Bicycle, Car, Cat, Dog, Person  
**Task**: Verify model accuracy on real-world images

---

## 🎯 Testing Objective

Test the pre-trained MobileNetV3 model in the Predict tab to verify:
1. ✅ Predictions are accurate (>80% confidence for correct class)
2. ✅ All 5 classes work correctly
3. ✅ Model performs better than random (50-50)
4. ✅ Inference speed is acceptable (<500ms per image)

---

## 📋 Test Setup

### Requirements
- [ ] Android app installed and running
- [ ] Model loaded successfully (check Models tab)
- [ ] Access to test images for all 5 classes
- [ ] Camera permission granted

### Test Image Sources
1. **Capture real photos** with device camera
2. **Use stock images** from phone gallery
3. **Download test images** from internet (optional)

---

## 🧪 Test Procedure

### Test 1: Bicycle Recognition

**Images to Test**: 10 different bicycle images
- Mountain bike
- Road bike
- BMX bike
- Electric bike
- Tandem bike
- Bicycle from different angles
- Bicycle with rider
- Bicycle without rider
- Bicycle in motion (if possible)
- Bicycle parked

**Steps**:
1. Open app → **Predict** tab
2. Tap camera icon or select from gallery
3. Capture/select bicycle image
4. Wait for prediction
5. Record results

**Results Table**:

| Image | Top Prediction | Confidence | Correct? | Notes |
|-------|----------------|------------|----------|-------|
| 1. Mountain bike | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 2. Road bike | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 3. BMX bike | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 4. Electric bike | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 5. Tandem bike | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 6. Different angle | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 7. With rider | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 8. Without rider | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 9. In motion | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 10. Parked | _________ | ___% | ⬜ Yes ⬜ No | _____ |

**Summary**:
- Total Correct: ___ / 10
- Average Confidence (correct): ___%
- Average Confidence (incorrect): ___%
- **Accuracy**: ___%

---

### Test 2: Car Recognition

**Images to Test**: 10 different car images
- Sedan
- SUV
- Sports car
- Pickup truck
- Van
- Car from front
- Car from side
- Car from back
- Multiple cars
- Car in parking lot

**Results Table**:

| Image | Top Prediction | Confidence | Correct? | Notes |
|-------|----------------|------------|----------|-------|
| 1. Sedan | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 2. SUV | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 3. Sports car | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 4. Pickup truck | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 5. Van | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 6. Front view | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 7. Side view | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 8. Back view | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 9. Multiple cars | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 10. Parking lot | _________ | ___% | ⬜ Yes ⬜ No | _____ |

**Summary**:
- Total Correct: ___ / 10
- Average Confidence (correct): ___%
- Average Confidence (incorrect): ___%
- **Accuracy**: ___%

---

### Test 3: Cat Recognition

**Images to Test**: 10 different cat images
- Tabby cat
- Black cat
- White cat
- Orange cat
- Siamese cat
- Cat face close-up
- Full body cat
- Cat sitting
- Cat lying down
- Multiple cats

**Results Table**:

| Image | Top Prediction | Confidence | Correct? | Notes |
|-------|----------------|------------|----------|-------|
| 1. Tabby cat | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 2. Black cat | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 3. White cat | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 4. Orange cat | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 5. Siamese cat | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 6. Face close-up | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 7. Full body | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 8. Sitting | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 9. Lying down | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 10. Multiple cats | _________ | ___% | ⬜ Yes ⬜ No | _____ |

**Summary**:
- Total Correct: ___ / 10
- Average Confidence (correct): ___%
- Average Confidence (incorrect): ___%
- **Accuracy**: ___%

---

### Test 4: Dog Recognition

**Images to Test**: 10 different dog images
- Golden Retriever
- German Shepherd
- Poodle
- Chihuahua
- Bulldog
- Dog face close-up
- Full body dog
- Dog sitting
- Dog running
- Multiple dogs

**Results Table**:

| Image | Top Prediction | Confidence | Correct? | Notes |
|-------|----------------|------------|----------|-------|
| 1. Golden Retriever | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 2. German Shepherd | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 3. Poodle | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 4. Chihuahua | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 5. Bulldog | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 6. Face close-up | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 7. Full body | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 8. Sitting | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 9. Running | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 10. Multiple dogs | _________ | ___% | ⬜ Yes ⬜ No | _____ |

**Summary**:
- Total Correct: ___ / 10
- Average Confidence (correct): ___%
- Average Confidence (incorrect): ___%
- **Accuracy**: ___%

---

### Test 5: Person Recognition

**Images to Test**: 10 different person images
- Single person
- Multiple people
- Person standing
- Person sitting
- Person walking
- Person close-up (face)
- Person full body
- Person from side
- Person from back
- Crowd

**Results Table**:

| Image | Top Prediction | Confidence | Correct? | Notes |
|-------|----------------|------------|----------|-------|
| 1. Single person | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 2. Multiple people | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 3. Standing | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 4. Sitting | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 5. Walking | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 6. Close-up (face) | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 7. Full body | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 8. From side | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 9. From back | _________ | ___% | ⬜ Yes ⬜ No | _____ |
| 10. Crowd | _________ | ___% | ⬜ Yes ⬜ No | _____ |

**Summary**:
- Total Correct: ___ / 10
- Average Confidence (correct): ___%
- Average Confidence (incorrect): ___%
- **Accuracy**: ___%

---

## 📊 Overall Performance Summary

### Accuracy by Class

| Class | Correct | Total | Accuracy | Avg Confidence |
|-------|---------|-------|----------|----------------|
| Bicycle | ___ | 10 | ___% | ___% |
| Car | ___ | 10 | ___% | ___% |
| Cat | ___ | 10 | ___% | ___% |
| Dog | ___ | 10 | ___% | ___% |
| Person | ___ | 10 | ___% | ___% |
| **Total** | ___ | 50 | **___%** | **___%** |

### Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Overall Accuracy | >80% | ___% | ⬜ Pass ⬜ Fail |
| Average Confidence (correct) | >80% | ___% | ⬜ Pass ⬜ Fail |
| Inference Time | <500ms | ___ms | ⬜ Pass ⬜ Fail |
| Model Load Time | <2s | ___s | ⬜ Pass ⬜ Fail |

---

## 🔍 Detailed Analysis

### Common Misclassifications

List the most common errors:

1. **Class A misclassified as Class B**: ___ times
   - Example: Cat misclassified as Dog
   - Possible reason: Similar features, poor lighting, etc.

2. **Class C misclassified as Class D**: ___ times
   - Example: _______
   - Possible reason: _______

3. **Other misclassifications**: _______

### Challenging Scenarios

List scenarios where model struggled:

1. **Multiple objects in frame**: _______
   - Example: Person riding bicycle
   - Prediction: _______
   - Expected: Should predict dominant object

2. **Poor lighting conditions**: _______
   - Example: Night photo of car
   - Prediction: _______
   - Expected: Should still recognize with lower confidence

3. **Partial objects**: _______
   - Example: Half of bicycle visible
   - Prediction: _______
   - Expected: May fail, acceptable

---

## 🐛 Troubleshooting

### Issue 1: Low Confidence (<50%) for Correct Class

**Possible Causes**:
- Image preprocessing incorrect
- Model not loaded properly
- Poor image quality
- Object partially obscured

**How to Verify**:
1. Check Models tab → Model status should be "Ready"
2. Try same image multiple times (should give consistent results)
3. Try very clear, high-quality image of same class

**Solution**:
- If preprocessing issue: Check PyTorchModelManager normalization
- If model load issue: Restart app, check model file exists
- If image quality issue: Use better quality images

---

### Issue 2: Completely Wrong Predictions

**Possible Causes**:
- Model file corrupted
- Wrong class labels mapping
- Image preprocessing bug

**How to Verify**:
1. Check Models tab → Model version, accuracy, size
2. Check class labels in Models tab (should show: Bicycle, Car, Cat, Dog, Person)
3. Test with multiple images of same class

**Solution**:
- Re-download model from server
- Check class labels order in PyTorchModelManager
- Verify preprocessing code (224x224, ImageNet normalization)

---

### Issue 3: Predictions Take Too Long (>1 second)

**Possible Causes**:
- Model not optimized
- Running on CPU instead of GPU
- Image too large (not resized properly)

**How to Verify**:
1. Check inference time in logs
2. Check device CPU/GPU usage
3. Test with smaller image

**Solution**:
- Ensure model is .ptl format (TorchScript)
- Enable GPU acceleration if available
- Verify image resized to 224x224 before inference

---

## ✅ Success Criteria

**Task #3 passes if**:
- [ ] Overall accuracy ≥ 80% (40+ correct out of 50)
- [ ] Each class accuracy ≥ 70% (7+ correct out of 10)
- [ ] Average confidence (correct) ≥ 80%
- [ ] Inference time < 500ms per image
- [ ] No crashes or errors during testing

**If criteria not met**:
1. Identify problematic classes
2. Collect more training data for those classes
3. Retrain model with more epochs
4. Consider data augmentation
5. Test again

---

## 📝 Next Steps

### If Model Performance is Good (≥80% accuracy):
✅ **Task #3 Complete!**
- Move to Task #7: User Feedback Loop
- Continue building federated learning features

### If Model Performance is Poor (<80% accuracy):
🔄 **Need Improvement**
1. Analyze misclassifications (see Detailed Analysis section)
2. Collect more training data for weak classes
3. Consider fine-tuning options:
   - More epochs (20-30 instead of 10)
   - Data augmentation (rotation, flip, zoom)
   - Class balancing (equal samples per class)
   - Transfer learning from larger model
4. Retrain and test again

---

## 📊 Test Results Summary

**Date Tested**: ___________  
**Tester**: ___________  
**Device**: ___________  
**Android Version**: ___________  
**Model Version**: ___________

**Overall Accuracy**: ____%  
**Pass/Fail**: ⬜ PASS ⬜ FAIL ⬜ NEEDS IMPROVEMENT

**Comments**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Recommendations**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Next Task**: 
- If PASS → Task #7: User Feedback Loop
- If FAIL → Retrain model with more data

