# 🤖 Federated AI - Distributed Object Detection System

<div align="center">

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![PyTorch 2.0+](https://img.shields.io/badge/pytorch-2.0+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade federated learning system for collaborative object detection that enables privacy-preserving distributed training across multiple devices without sharing raw data.

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🚀 Features

### Core Capabilities
- **🔐 Federated Learning**: Train on distributed devices without sharing raw data (Flower framework)
- **📱 Native Android App**: Full-featured mobile client with on-device inference
- **🎯 Real-time Detection**: MobileNetV3-based fast inference (<500ms)
- **🔄 Dynamic Model Updates**: Hot-swap models without app restart
- **📊 Django Admin Dashboard**: Real-time monitoring of training, clients, and system health
- **🌐 RESTful API**: Complete API with authentication and documentation

### Privacy & Security
- **Differential Privacy**: Configurable privacy budgets (ε, δ)
- **Secure Aggregation**: Model updates aggregated on server
- **Token Authentication**: Secure API access with JWT
- **Data Encryption**: TLS/SSL for all communications

### ML Pipeline
- **PyTorch Mobile**: Optimized .ptl models for on-device inference  
- **Celery Async Training**: Background training with Redis message broker
- **Model Versioning**: SHA256 verification and automatic rollback
- **Image Upload Queue**: Batch processing with exponential backoff retry

## ⚡ Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/federated-ai.git
cd federated-ai

# Copy environment file
cp .env.example .env

# Start all services with Docker Compose
cd docker
docker compose up -d

# Create Django superuser
docker compose exec django python /app/server/manage.py createsuperuser

# Access the system
# 🌐 Django Admin: http://localhost:8000/admin
# 📊 Dashboard: http://localhost:8000/admin/dashboard
# 🔧 API Docs: http://localhost:8000/api/schema/swagger-ui/
# 📦 MinIO: http://localhost:9001 (minioadmin/minioadmin)
```

### Android App Setup

```bash
# Build and install the Android app
cd android-mobo
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk

# Or open in Android Studio and run
```

**App Features:**
- **Train Tab**: Capture and label images for training
- **Predict Tab**: Real-time object detection with ML model
- **Models Tab**: Download and manage model versions
- Upload queue with progress tracking and retry logic

---

## 📋 Prerequisites

**Required:**
- Docker & Docker Compose (recommended) OR:
  - Python 3.11+
  - MySQL 8.0+
  - Redis 7.0+
  - Node.js 16+ (for web interface)
- Git

**For Android Development:**
- Android Studio Hedgehog or newer
- Android SDK 24+ (Android 7.0)
- Kotlin 1.9+

---

## 🛠️ Installation

### Option 1: Docker (Recommended) 🐳

See [Quick Start](#-quick-start) above.

**Additional Docker Commands:**

```bash
# View logs
docker compose logs -f django

# Restart services
docker compose restart

# Stop services
docker compose down

# Complete reset (removes volumes)
docker compose down -v
```

**Docker Commands:**

```bash
# Start core services
docker-compose up -d

# Start with Flower clients (for testing)
docker-compose --profile with-clients up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset all data
docker-compose down -v
```

---

### Option 2: Manual Installation

**Prerequisites:**
- Python 3.10+
- MySQL 8.0+
- Redis 7.0+

**Steps:**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/federated-ai.git
cd federated-ai

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements/server.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your MySQL and Redis credentials

# 5. Set up database
mysql -u root -p
CREATE DATABASE fed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# 6. Run migrations
cd server
python manage.py migrate
python manage.py createsuperuser

# 7. Start services (in separate terminals)
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery
celery -A config worker -l info

# Terminal 3: Flower FL server
python fl_server/server.py
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](API_DOCUMENTATION.md) | Complete REST API reference with examples |
| [API Guide](API_DOCUMENTATION_GUIDE.md) | How to use the API with authentication |
| [E2E Testing Guide](E2E_TESTING_GUIDE.md) | End-to-end testing procedures |
| [Model Performance Testing](MODEL_PERFORMANCE_TESTING.md) | How to test ML model accuracy |
| [Federated Training Pipeline](FEDERATED_TRAINING_PIPELINE.md) | Training architecture and workflow |
| [Authentication Guide](AUTHENTICATION_GUIDE.md) | Security and auth implementation |
| [Quick Start Testing](QUICK_START_TESTING.md) | Quick validation of system setup |
| [Project Guidelines](PROJECT_GUIDELINES.md) | Technical specifications and standards |

### API Endpoints

Access interactive API documentation at `http://localhost:8000/api/schema/swagger-ui/`

**Key endpoints:**
- `POST /api/clients/register/` - Register new device
- `POST /api/images/upload/` - Upload training images
- `POST /api/models/train/` - Trigger training job
- `GET /api/models/latest/` - Download latest model
- `POST /api/detections/` - Submit detection results

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=server --cov=client

# Run specific test
pytest tests/server/test_models.py
```

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Android App    │◄───────►│   Django Server  │
│  (Kotlin/Java)  │  REST   │   (Python/ML)    │
└─────────────────┘   API   └──────────────────┘
        │                            │
        │                            ▼
        │                    ┌──────────────────┐
        │                    │  Celery Worker   │
        │                    │  (Async Training)│
        │                    └──────────────────┘
        │                            │
        ▼                            ▼
┌─────────────────┐         ┌──────────────────┐
│  PyTorch Mobile │         │   MySQL + Redis  │
│   (.ptl model)  │         │   (Storage)      │
└─────────────────┘         └──────────────────┘
```

### Key Components

1. **Django Backend** (`server/`)
   - RESTful API with DRF
   - Admin dashboard for monitoring
   - Celery tasks for async training
   - Model versioning and storage

2. **Android App** (`android-mobo/`)
   - Jetpack Compose UI
   - Hilt dependency injection
   - Room database for local storage
   - Retrofit for API communication
   - PyTorch Mobile for inference

3. **ML Pipeline** (`server/ml/`)
   - MobileNetV3 architecture
   - PyTorch training loop
   - Model export to TorchScript (.ptl)
   - Federated aggregation (Flower)

4. **Infrastructure** (`docker/`)
   - MySQL 8.0 database
   - Redis message broker
   - MinIO object storage
   - Nginx reverse proxy (optional)

---

## 📁 Project Structure

```
federated-ai/
├── server/                    # Django backend
│   ├── config/               # Django settings
│   ├── core/                 # Auth, permissions, dashboard
│   ├── clients/              # Client registration API
│   ├── training/             # Training data management
│   ├── detection/            # Inference results
│   ├── objects/              # Object categories
│   ├── ml/                   # ML training pipeline
│   │   ├── models/          # PyTorch model definitions
│   │   └── training/        # Training scripts
│   ├── templates/           # Django templates
│   └── manage.py
│
├── android-mobo/             # Android native app
│   ├── app/src/main/
│   │   ├── java/.../        # Kotlin source code
│   │   │   ├── data/       # Repository, DAO, API
│   │   │   ├── di/         # Hilt modules
│   │   │   ├── domain/     # Use cases, models
│   │   │   ├── ml/         # PyTorch Mobile integration
│   │   │   └── presentation/ # ViewModels, Compose UI
│   │   ├── assets/         # ML models (.ptl)
│   │   └── res/            # Resources
│   └── build.gradle.kts
│
├── docker/                   # Docker setup
│   ├── docker-compose.yml
│   ├── Dockerfile.django
│   └── nginx/
│
├── requirements/             # Python dependencies
│   ├── server.txt
│   └── server_docker.txt
│
├── docs/                     # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── E2E_TESTING_GUIDE.md
│   └── MODEL_PERFORMANCE_TESTING.md
│
└── tests/                    # Test suite
    ├── server/
    └── integration/
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- [Flower Framework](https://flower.ai/) - Federated learning framework
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [Django](https://www.djangoproject.com/) - Web framework

## 🎯 Roadmap

- [x] **Phase 1**: Core Infrastructure (Django + MySQL + Redis + Docker)
- [x] **Phase 2**: RESTful API with authentication and documentation
- [x] **Phase 3**: ML training pipeline with Celery async tasks
- [x] **Phase 4**: Android app with PyTorch Mobile integration
- [x] **Phase 5**: Django Admin dashboard for monitoring
- [ ] **Phase 6**: Federated learning with Flower (in progress)
- [ ] **Phase 7**: Differential privacy implementation
- [ ] **Phase 8**: Web interface for administrators
- [ ] **Phase 9**: iOS app development
- [ ] **Phase 10**: Production deployment and scaling

---

## � System Requirements

### Development
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB for Docker images and models
- **OS**: macOS, Linux, or Windows with WSL2

### Production
- **CPU**: 8+ cores
- **RAM**: 16GB minimum
- **Storage**: 50GB+ for models and training data
- **Database**: MySQL 8.0+ with InnoDB
- **Cache**: Redis 7.0+ with persistence

---

## 🐛 Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Check what's using port 8000
lsof -i :8000
# Kill the process or change port in docker-compose.yml
```

**Permission denied:**
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
# Logout and login again
```

### Django Issues

**Migration errors:**
```bash
docker compose exec django python /app/server/manage.py migrate --run-syncdb
```

**Static files not loading:**
```bash
docker compose exec django python /app/server/manage.py collectstatic --no-input
```

### Android Issues

**Build fails:**
```bash
# Clean and rebuild
cd android-mobo
./gradlew clean
./gradlew assembleDebug
```

**App crashes on startup:**
- Check if server is running and accessible
- Verify API base URL in `BuildConfig.BASE_URL`
- Check logcat for errors: `adb logcat | grep Federated`

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/federated-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/federated-ai/discussions)
- **Documentation**: [docs/](docs/)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Status**: � Active Development  
**Version**: 1.0.0-alpha  
**Last Updated**: November 8, 2025

Made with ❤️ for privacy-preserving AI

</div>
