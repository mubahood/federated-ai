# FederatedAI - Android Mobile Client

[![Platform](https://img.shields.io/badge/Platform-Android-green.svg)](https://www.android.com/)
[![API](https://img.shields.io/badge/API-26%2B-brightgreen.svg)](https://android-arsenal.com/api?level=26)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.20-blue.svg)](https://kotlinlang.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)

Privacy-first federated learning mobile client for Android. Train AI models locally on your device without sending raw data to the server.

## 🌟 Features

- **Privacy-First**: Your data never leaves your device
- **Federated Learning**: Contribute to global AI models while maintaining privacy
- **Image Capture & Labeling**: Easy-to-use camera interface for data collection
- **Real-Time Training**: Watch model training progress in real-time
- **Background Processing**: Training continues even when app is in background
- **Offline-First**: Queue operations and sync when online
- **Material Design 3**: Beautiful, modern UI with dark theme support

## 📋 Requirements

- **Android Studio**: Hedgehog (2023.1.1) or later
- **Android SDK**: API 26 (Android 8.0) minimum, API 34 (Android 14) target
- **JDK**: 17 or later
- **Gradle**: 8.1+
- **Kotlin**: 1.9.20

## 🏗️ Architecture

This app follows **Clean Architecture** with MVVM pattern:

```
app/
├── data/                 # Data layer
│   ├── local/           # Room DB, DataStore, File Storage
│   ├── remote/          # Retrofit APIs, DTOs
│   └── repository/      # Repository implementations
├── domain/              # Business logic layer
│   ├── models/         # Domain models
│   ├── repository/     # Repository interfaces
│   └── usecases/       # Use cases (business logic)
├── ui/                 # Presentation layer
│   ├── screens/        # Compose screens
│   ├── components/     # Reusable UI components
│   ├── navigation/     # Navigation graph
│   └── theme/          # Material Design 3 theme
├── ml/                 # Machine Learning layer
│   ├── tflite/        # TensorFlow Lite integration
│   ├── flower/        # Flower client for FL
│   └── training/      # Local training logic
├── workers/           # Background WorkManager tasks
├── di/               # Dependency Injection (Hilt)
└── utils/            # Utility classes
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
cd federated-ai
```

The Android project is in the `android-mobo/` directory.

### 2. Configure Backend URL

Edit `app/build.gradle.kts` to set your backend URL:

```kotlin
buildConfigField("String", "BASE_URL", "\"http://YOUR_BACKEND_IP:8000/api/\"")
buildConfigField("String", "FLOWER_HOST", "\"YOUR_BACKEND_IP\"")
buildConfigField("int", "FLOWER_PORT", "8080")
```

**For Emulator**: Use `10.0.2.2` to access localhost  
**For Physical Device**: Use your computer's local IP (e.g., `192.168.1.100`)

### 3. Open in Android Studio

1. Open Android Studio
2. Click "Open" and select `federated-ai/android-mobo/`
3. Wait for Gradle sync to complete
4. Build the project (Build → Make Project)

### 4. Run the App

1. Connect an Android device or start an emulator
2. Click the "Run" button or press `Shift+F10`
3. Select your device/emulator
4. Wait for installation and app launch

## 📦 Dependencies

### Core
- **Jetpack Compose**: Modern declarative UI
- **Hilt**: Dependency injection
- **Room**: Local database
- **DataStore**: Preferences storage
- **WorkManager**: Background tasks

### Networking
- **Retrofit**: REST API client
- **OkHttp**: HTTP client
- **Gson**: JSON serialization

### Machine Learning
- **TensorFlow Lite**: On-device ML inference
- **Flower Android**: Federated learning framework
- **gRPC**: Communication with FL server

### UI & Media
- **CameraX**: Camera integration
- **Coil**: Image loading
- **Material Design 3**: Modern UI components
- **MPAndroidChart**: Data visualization

## 🔧 Development

### Build Variants

- **Debug**: Development build with logging enabled
- **Release**: Production build with ProGuard enabled

### Code Style

This project follows [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html).

Run code formatting:
```bash
./gradlew ktlintFormat
```

### Testing

Run unit tests:
```bash
./gradlew test
```

Run instrumented tests:
```bash
./gradlew connectedAndroidTest
```

### Generate APK

Debug APK:
```bash
./gradlew assembleDebug
```

Release APK:
```bash
./gradlew assembleRelease
```

APK location: `app/build/outputs/apk/`

## 🔐 Security

- **Encrypted Storage**: Sensitive data encrypted at rest
- **TLS/SSL**: All network communication encrypted
- **No Raw Data Transfer**: Only model parameters sent to server
- **Certificate Pinning**: Prevents MITM attacks (Release builds)

## 📱 Screens

1. **Onboarding**: Welcome carousel and registration
2. **Dashboard**: Global stats and user contribution
3. **Camera**: Image capture and labeling
4. **Training**: Live federated learning progress
5. **Statistics**: Training history and visualizations
6. **Detection**: Real-time object detection
7. **Settings**: Privacy controls and preferences

## 🛠️ Troubleshooting

### Gradle Sync Failed

```bash
./gradlew clean
./gradlew build --refresh-dependencies
```

### Cannot Connect to Backend

- Ensure backend server is running
- Check `BASE_URL` in `build.gradle.kts`
- For emulator: Use `10.0.2.2` not `localhost`
- For device: Check firewall settings

### Camera Not Working

- Grant camera permission in app settings
- Check device has working camera
- Ensure AndroidManifest has camera permissions

## 📚 Documentation

- [Architecture Details](../docs/PHASE_5_ANDROID_ARCHITECTURE.md)
- [TODO List](../docs/PHASE_5_TODO_LIST.md)
- [API Documentation](../docs/API_DOCUMENTATION.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review the TODO list for known limitations

---

**Built with ❤️ using Kotlin and Jetpack Compose**
