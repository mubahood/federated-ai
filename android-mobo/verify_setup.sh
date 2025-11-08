#!/bin/bash

# Android Project Verification Script
# Checks if the Android project is properly configured

echo "=========================================="
echo "FederatedAI Android Project Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
CHECKS=0
PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    CHECKS=$((CHECKS+1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        PASSED=$((PASSED+1))
        return 0
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        FAILED=$((FAILED+1))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    CHECKS=$((CHECKS+1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        PASSED=$((PASSED+1))
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        FAILED=$((FAILED+1))
        return 1
    fi
}

echo "Checking project structure..."
echo ""

# Root files
echo "Root Configuration:"
check_file "android-mobo/settings.gradle.kts"
check_file "android-mobo/build.gradle.kts"
check_file "android-mobo/gradle.properties"
check_file "android-mobo/.gitignore"
check_file "android-mobo/README.md"
echo ""

# App module
echo "App Module:"
check_file "android-mobo/app/build.gradle.kts"
check_file "android-mobo/app/proguard-rules.pro"
check_file "android-mobo/app/src/main/AndroidManifest.xml"
echo ""

# Core classes
echo "Core Application Classes:"
check_file "android-mobo/app/src/main/java/com/federated/client/FederatedAIApp.kt"
check_file "android-mobo/app/src/main/java/com/federated/client/MainActivity.kt"
echo ""

# DI modules
echo "Dependency Injection:"
check_dir "android-mobo/app/src/main/java/com/federated/client/di"
check_file "android-mobo/app/src/main/java/com/federated/client/di/AppModule.kt"
check_file "android-mobo/app/src/main/java/com/federated/client/di/NetworkModule.kt"
echo ""

# Data layer
echo "Data Layer:"
check_dir "android-mobo/app/src/main/java/com/federated/client/data/local/prefs"
check_file "android-mobo/app/src/main/java/com/federated/client/data/local/prefs/PreferencesManager.kt"
check_dir "android-mobo/app/src/main/java/com/federated/client/data/remote/api"
check_file "android-mobo/app/src/main/java/com/federated/client/data/remote/api/AuthApi.kt"
check_dir "android-mobo/app/src/main/java/com/federated/client/data/remote/dto"
echo ""

# Architecture packages
echo "Architecture Packages:"
check_dir "android-mobo/app/src/main/java/com/federated/client/domain/models"
check_dir "android-mobo/app/src/main/java/com/federated/client/domain/repository"
check_dir "android-mobo/app/src/main/java/com/federated/client/domain/usecases"
check_dir "android-mobo/app/src/main/java/com/federated/client/ui/screens"
check_dir "android-mobo/app/src/main/java/com/federated/client/ui/components"
check_dir "android-mobo/app/src/main/java/com/federated/client/ui/theme"
check_dir "android-mobo/app/src/main/java/com/federated/client/ui/navigation"
echo ""

# ML packages
echo "ML/FL Packages:"
check_dir "android-mobo/app/src/main/java/com/federated/client/ml/tflite"
check_dir "android-mobo/app/src/main/java/com/federated/client/ml/flower"
check_dir "android-mobo/app/src/main/java/com/federated/client/ml/training"
check_dir "android-mobo/app/src/main/java/com/federated/client/workers"
echo ""

# Resources
echo "Resources:"
check_file "android-mobo/app/src/main/res/values/strings.xml"
check_file "android-mobo/app/src/main/res/xml/file_paths.xml"
check_file "android-mobo/app/src/main/res/xml/backup_rules.xml"
check_file "android-mobo/app/src/main/res/xml/data_extraction_rules.xml"
echo ""

# Summary
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo -e "Total Checks: ${CHECKS}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: ${FAILED}${NC}"
else
    echo -e "${GREEN}Failed: 0${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Project structure is correct.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open project in Android Studio"
    echo "  2. Let Gradle sync complete"
    echo "  3. Build project: ./gradlew build"
    echo "  4. Run on device/emulator"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the missing files/directories.${NC}"
    exit 1
fi
