# Federated AI - Object Detection System
## Project Guidelines & Technical Specification v1.0

**Last Updated:** November 6, 2025  
**Status:** Active Development  
**License:** MIT  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Federated Learning Workflow](#federated-learning-workflow)
9. [Development Phases](#development-phases)
10. [Security & Privacy](#security-privacy)
11. [Performance Requirements](#performance-requirements)
12. [Deployment Strategy](#deployment-strategy)
13. [Testing Strategy](#testing-strategy)
14. [Monitoring & Logging](#monitoring-logging)
15. [Best Practices](#best-practices)

---

## 1. Executive Summary

### 1.1 Project Overview

A production-grade federated learning system for dynamic object detection that enables:
- **Dynamic Object Management**: Add/remove objects without retraining entire model
- **Privacy-Preserving Training**: Train on distributed devices without sharing raw data
- **Real-time Detection**: Fast inference with confidence scoring
- **Cross-Platform Support**: Web, mobile (iOS/Android), and desktop clients

### 1.2 Key Features

✅ **Object Database**: CRUD operations for object categories  
✅ **Federated Training**: Distributed learning across multiple clients  
✅ **Training Interface**: Upload/camera capture with labeling  
✅ **Detection Interface**: Real-time object recognition  
✅ **Model Versioning**: Track and rollback model versions  
✅ **Privacy Protection**: Differential privacy + secure aggregation  
✅ **Mobile Support**: Deploy to iOS and Android devices  

### 1.3 Success Metrics

- **Accuracy**: ≥85% on test set after 100 training rounds
- **Inference Speed**: <100ms per image on mobile CPU
- **Model Size**: <15MB (quantized)
- **Training Rounds**: Converge within 50-100 rounds
- **Client Support**: Handle 100+ concurrent clients

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CENTRAL SERVER                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Django REST API (Port 8000)                         │  │
│  │  - Object Management                                  │  │
│  │  - Client Registration                                │  │
│  │  - Model Download/Upload                              │  │
│  │  - Training Coordination                              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flower Server (Port 8080)                           │  │
│  │  - FL Strategy: FedAvg/FedProx                       │  │
│  │  - Model Aggregation                                  │  │
│  │  - Client Selection                                   │  │
│  │  - Round Management                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Background Tasks (Celery)                           │  │
│  │  - Async training coordination                        │  │
│  │  - Model evaluation                                   │  │
│  │  - Metrics aggregation                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Storage Layer                                       │  │
│  │  PostgreSQL │ Redis │ MinIO/S3                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ gRPC/HTTPS
┌─────────────────────────────────────────────────────────────┐
│                    FEDERATED CLIENTS                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Web      │  │ Desktop  │  │ Android  │  │   iOS    │   │
│  │ Client   │  │ Client   │  │ Client   │  │ Client   │   │
│  │          │  │          │  │          │  │          │   │
│  │ Flower   │  │ Flower   │  │ Flower   │  │ Flower   │   │
│  │ +PyTorch │  │ +PyTorch │  │ +TFLite  │  │ +CoreML  │   │
│  │          │  │          │  │          │  │          │   │
│  │ Local    │  │ Local    │  │ Local    │  │ Local    │   │
│  │ Training │  │ Training │  │ Training │  │ Training │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction

1. **Client Registration**: Client connects to Django API, receives credentials
2. **Model Download**: Client downloads latest global model from server
3. **Local Training**: Client trains on local data (N epochs)
4. **Model Update**: Client sends gradients/weights to Flower Server via gRPC
5. **Aggregation**: Server aggregates updates using FedAvg
6. **Global Update**: Server updates global model
7. **Distribution**: New model available for all clients

---

## 3. Technology Stack

### 3.1 Core Technologies (Stable & Production-Ready)

#### Backend Framework
```yaml
Django: 4.2.7 (LTS)
  - Why: Mature, secure, excellent ORM, admin interface
  - Alternatives Considered: FastAPI (lighter but less batteries-included)
  - Database: Uses MySQL 8.0+ (already installed on your Mac)

Django REST Framework: 3.14.0
  - Why: Industry standard for building APIs
  - Features: Serialization, authentication, permissions
```

#### Federated Learning

```yaml
Flower Framework: 1.11.0+
  - Why: Most mature FL framework, production-ready
  - Supports: PyTorch, TensorFlow, mobile clients
  - Features: Built-in strategies, gRPC, simulation mode
  - GitHub: https://github.com/adap/flower
  - Docs: https://flower.ai/docs/framework/

PyTorch: 2.1.0+
  - Why: Better for research, mobile deployment (TorchScript)
  - Mobile: PyTorch Mobile, ExecuTorch for iOS/Android
  - Export: ONNX for cross-platform compatibility
```

#### Database & Storage

```yaml
MySQL: 8.0+
  - Why: ACID compliance, JSON support, reliable, already installed
  - Use: User data, objects, training metadata
  - Engine: InnoDB (supports transactions)
  - Connector: mysqlclient or PyMySQL

Redis: 7.0+
  - Why: Fast in-memory cache, pub/sub, task queue
  - Use: Model cache, Celery broker, real-time updates

MinIO or AWS S3:
  - Why: Object storage for large model files
  - Use: Model versioning, checkpoints
```

#### Task Queue
```yaml
Celery: 5.3.0+
  - Why: Distributed task queue, async processing
  - Use: Training coordination, model evaluation
```

#### Communication
```yaml
gRPC: 1.59.0+
  - Why: Efficient binary protocol (used by Flower)
  - Features: Bidirectional streaming, protobuf

WebSockets:
  - Why: Real-time updates to web clients
  - Library: Django Channels 4.0+
```

### 3.2 ML Model Architecture

#### Recommended: MobileNetV3 with Transfer Learning

```python
Base Model: MobileNetV3-Large (ImageNet pre-trained)
  - Params: ~5.4M
  - Size: ~21MB (full precision)
  - Size: ~5MB (INT8 quantized)
  - Inference: ~50ms on mobile CPU

Modifications:
  - Remove final classification layer
  - Add custom classification head
  - Support dynamic class addition
  
Input: 224x224x3 RGB images
Output: Softmax probabilities over N classes
```

**Why MobileNetV3?**
- ✅ Optimized for mobile/edge devices
- ✅ Excellent accuracy-to-size ratio
- ✅ Hardware-aware NAS (Neural Architecture Search)
- ✅ Supports quantization (4x smaller)
- ✅ Fast inference (<100ms)

**Alternative: EfficientNet-Lite-B0** (if higher accuracy needed)

### 3.3 Privacy & Security
```yaml
Differential Privacy: Opacus 1.4.0+
  - Noise injection during training
  - Configurable epsilon (ε) budget

Secure Aggregation:
  - Homomorphic encryption (optional)
  - Clients can't see each other's updates

Authentication:
  - JWT tokens (django-rest-framework-simplejwt)
  - Client certificates for gRPC

Encryption:
  - TLS 1.3 for all communications
  - AES-256 for data at rest
```

### 3.4 Development Tools
```yaml
Code Quality:
  - Black: Code formatting
  - Flake8: Linting
  - MyPy: Type checking
  - Pre-commit hooks

Testing:
  - Pytest: Unit tests
  - Pytest-django: Django integration
  - Coverage.py: Code coverage

Monitoring:
  - Prometheus: Metrics collection
  - Grafana: Visualization
  - Sentry: Error tracking
  - MLflow: Experiment tracking

Containerization:
  - Docker: 24.0+
  - Docker Compose: 2.20+
  - Kubernetes: 1.28+ (production)
```

---

## 4. Project Structure

```
federated-ai/
│
├── docs/                           # Documentation
│   ├── api/                        # API documentation
│   ├── architecture/               # Architecture diagrams
│   ├── deployment/                 # Deployment guides
│   └── user-guides/                # User manuals
│
├── server/                         # Central Server
│   ├── config/                     # Configuration files
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── testing.py
│   │   └── __init__.py
│   │
│   ├── apps/                       # Django applications
│   │   ├── core/                   # Core functionality
│   │   │   ├── models.py
│   │   │   ├── admin.py
│   │   │   └── utils.py
│   │   │
│   │   ├── objects/                # Object management
│   │   │   ├── models.py           # Object, Category
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   │
│   │   ├── clients/                # Client management
│   │   │   ├── models.py           # Client, DeviceInfo
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── authentication.py
│   │   │
│   │   ├── training/               # Training management
│   │   │   ├── models.py           # TrainingRound, ModelVersion
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── tasks.py            # Celery tasks
│   │   │   └── coordinators.py
│   │   │
│   │   └── detection/              # Detection interface
│   │       ├── models.py           # DetectionResult
│   │       ├── views.py
│   │       └── inference.py
│   │
│   ├── fl_server/                  # Flower FL Server
│   │   ├── server.py               # Main server instance
│   │   ├── strategies/
│   │   │   ├── fed_avg_custom.py   # Custom FedAvg
│   │   │   ├── fed_prox.py         # FedProx
│   │   │   └── fed_adam.py         # FedAdam
│   │   ├── aggregation.py          # Aggregation logic
│   │   ├── client_manager.py       # Client selection
│   │   └── config.py
│   │
│   ├── ml/                         # ML Components
│   │   ├── models/
│   │   │   ├── mobilenet_v3.py     # Model definition
│   │   │   ├── model_factory.py    # Model creation
│   │   │   └── incremental.py      # Incremental learning
│   │   ├── training/
│   │   │   ├── trainer.py          # Training logic
│   │   │   ├── optimizer.py        # Custom optimizers
│   │   │   └── scheduler.py        # LR schedulers
│   │   ├── data/
│   │   │   ├── transforms.py       # Data augmentation
│   │   │   ├── dataset.py          # Custom datasets
│   │   │   └── loader.py           # Data loaders
│   │   ├── evaluation/
│   │   │   ├── metrics.py          # Accuracy, F1, etc.
│   │   │   └── evaluator.py        # Model evaluation
│   │   ├── registry.py             # Model versioning
│   │   └── utils.py
│   │
│   ├── storage/
│   │   ├── s3_backend.py           # S3/MinIO storage
│   │   ├── cache.py                # Redis cache
│   │   └── model_store.py          # Model storage interface
│   │
│   ├── monitoring/
│   │   ├── prometheus.py           # Metrics
│   │   ├── mlflow_logger.py        # Experiment tracking
│   │   └── health_checks.py
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── client/                         # Federated Clients
│   ├── core/
│   │   ├── flower_client.py        # Flower client impl
│   │   ├── trainer.py              # Local training
│   │   ├── data_manager.py         # Local data handling
│   │   ├── model_manager.py        # Model download/cache
│   │   └── config.py
│   │
│   ├── interfaces/
│   │   ├── cli/                    # Command-line interface
│   │   │   ├── main.py
│   │   │   └── commands.py
│   │   │
│   │   ├── web/                    # Web interface
│   │   │   ├── templates/
│   │   │   ├── static/
│   │   │   └── views.py
│   │   │
│   │   └── mobile/                 # Mobile support
│   │       ├── android/
│   │       └── ios/
│   │
│   ├── privacy/
│   │   ├── differential_privacy.py  # DP implementation
│   │   └── secure_agg.py            # Secure aggregation
│   │
│   ├── utils/
│   │   ├── compression.py           # Model compression
│   │   ├── communication.py         # Network utils
│   │   └── device_info.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── shared/                         # Shared code
│   ├── schemas/
│   │   ├── messages.proto          # Protocol buffers
│   │   └── api_schemas.py
│   ├── config/
│   │   ├── model_config.py
│   │   └── fl_config.py
│   └── utils/
│       ├── crypto.py
│       └── serialization.py
│
├── web_interface/                  # User-facing web app
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html          # Admin dashboard
│   │   ├── objects/
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   └── detail.html
│   │   ├── training/
│   │   │   ├── upload.html
│   │   │   └── camera.html
│   │   └── detection/
│   │       └── detect.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── camera.js
│   │   │   ├── upload.js
│   │   │   └── detection.js
│   │   └── images/
│   │
│   └── forms.py
│
├── scripts/                        # Utility scripts
│   ├── setup/
│   │   ├── setup_environment.sh
│   │   └── create_superuser.py
│   ├── deployment/
│   │   ├── start_server.sh
│   │   ├── start_client.sh
│   │   └── backup_db.sh
│   └── testing/
│       ├── simulate_clients.py
│       └── benchmark.py
│
├── tests/                          # Test suite
│   ├── server/
│   │   ├── test_api.py
│   │   ├── test_fl_server.py
│   │   └── test_models.py
│   ├── client/
│   │   ├── test_client.py
│   │   └── test_training.py
│   ├── integration/
│   │   ├── test_e2e.py
│   │   └── test_federated.py
│   └── conftest.py
│
├── docker/                         # Docker configuration
│   ├── server/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── client/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   └── docker-compose.yml
│
├── kubernetes/                     # K8s manifests (production)
│   ├── server/
│   ├── database/
│   └── ingress/
│
├── .github/                        # GitHub Actions
│   └── workflows/
│       ├── tests.yml
│       ├── lint.yml
│       └── deploy.yml
│
├── .env.example                    # Environment variables template
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml                  # Project config
├── README.md
├── LICENSE
└── PROJECT_GUIDELINES.md           # This file
```

---

## 5. Core Components

### 5.1 Object Management System

**Purpose**: Manage object categories that the model can detect

**Features**:
- CRUD operations for objects
- Category hierarchies (optional future enhancement)
- Sample image storage
- Metadata tracking

**Key Models**:
```python
class ObjectCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    class_index = models.IntegerField(unique=True)  # For model output
    is_active = models.BooleanField(default=True)
    sample_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
```

### 5.2 Federated Learning Server

**Purpose**: Coordinate distributed training across clients

**Core Responsibilities**:
1. **Client Selection**: Choose K clients per round
2. **Model Distribution**: Send global model to clients
3. **Aggregation**: Combine client updates using FedAvg
4. **Evaluation**: Test global model performance
5. **Versioning**: Save model checkpoints

**Flower Strategy Configuration**:
```python
strategy = FedAvg(
    fraction_fit=0.1,              # 10% of clients per round
    fraction_evaluate=0.05,        # 5% for evaluation
    min_fit_clients=5,             # Minimum clients needed
    min_evaluate_clients=2,
    min_available_clients=10,
    initial_parameters=initial_params,
    evaluate_metrics_aggregation_fn=weighted_average,
)
```

### 5.3 Client Application

**Purpose**: Train model locally and communicate with server

**Core Responsibilities**:
1. **Registration**: Authenticate with server
2. **Data Management**: Store and load local training data
3. **Local Training**: Train model for N epochs
4. **Model Updates**: Send weights/gradients to server
5. **Privacy**: Apply differential privacy if enabled

**Training Loop**:
```python
def fit(self, parameters, config):
    self.set_parameters(parameters)
    
    # Train locally
    for epoch in range(config["local_epochs"]):
        train_loss = train_one_epoch(self.model, self.trainloader)
    
    # Apply differential privacy
    if config["use_dp"]:
        apply_differential_privacy(self.model)
    
    # Return updated parameters
    return self.get_parameters(), len(self.trainloader), metrics
```

### 5.4 Training Interface

**Purpose**: Allow users to label and upload training data

**Features**:
- Image upload from computer
- Camera capture (web/mobile)
- Object selection from dropdown
- Batch upload support
- Image preview and validation

**Workflow**:
1. User selects object category
2. User uploads/captures image
3. System validates image (format, size)
4. Image saved to local storage
5. Added to training dataset
6. User can train immediately or batch multiple images

### 5.5 Detection Interface

**Purpose**: Perform real-time object detection

**Features**:
- Image upload or camera feed
- Real-time inference
- Confidence threshold (default: 70%)
- Top-K predictions display
- Bounding boxes (future enhancement)

**Response Format**:
```json
{
  "predictions": [
    {
      "object_name": "coffee_mug",
      "confidence": 0.92,
      "class_index": 5
    },
    {
      "object_name": "laptop",
      "confidence": 0.08,
      "class_index": 12
    }
  ],
  "detected": true,
  "inference_time_ms": 45,
  "model_version": "v1.2.3"
}
```

---

## 6. Database Schema

### 6.1 Core Tables (MySQL)

```sql
-- Object Categories
CREATE TABLE object_categories (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    class_index INTEGER UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sample_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by_id INTEGER REFERENCES auth_user(id)
);

-- Registered Clients
CREATE TABLE clients (
    id UUID PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    device_type VARCHAR(50),  -- web, mobile, desktop
    os_info VARCHAR(100),
    registration_date TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    total_samples INTEGER DEFAULT 0,
    api_key_hash VARCHAR(255) UNIQUE
);

-- Training Rounds
CREATE TABLE training_rounds (
    id SERIAL PRIMARY KEY,
    round_number INTEGER UNIQUE NOT NULL,
    status VARCHAR(20),  -- pending, in_progress, completed, failed
    num_clients_selected INTEGER,
    num_clients_participated INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    global_accuracy FLOAT,
    global_loss FLOAT,
    model_version_id INTEGER REFERENCES model_versions(id)
);

-- Model Versions
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,  -- v1.0.0
    training_round_id INTEGER REFERENCES training_rounds(id),
    model_file_path VARCHAR(500),  -- S3/MinIO path
    model_size_mb FLOAT,
    accuracy FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    is_current BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Training Images
CREATE TABLE training_images (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    object_category_id UUID REFERENCES object_categories(id),
    image_path VARCHAR(500),
    image_hash VARCHAR(64),  -- For deduplication
    uploaded_at TIMESTAMP DEFAULT NOW(),
    is_used_in_training BOOLEAN DEFAULT FALSE
);

-- Detection Results (optional logging)
CREATE TABLE detection_results (
    id SERIAL PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    image_hash VARCHAR(64),
    predicted_object_id UUID REFERENCES object_categories(id),
    confidence FLOAT,
    inference_time_ms FLOAT,
    model_version_id INTEGER REFERENCES model_versions(id),
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Client Metrics
CREATE TABLE client_metrics (
    id SERIAL PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    training_round_id INTEGER REFERENCES training_rounds(id),
    local_accuracy FLOAT,
    local_loss FLOAT,
    num_samples INTEGER,
    training_time_seconds FLOAT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Indexes

```sql
CREATE INDEX idx_object_categories_active ON object_categories(is_active);
CREATE INDEX idx_clients_active ON clients(is_active);
CREATE INDEX idx_training_rounds_status ON training_rounds(status);
CREATE INDEX idx_model_versions_current ON model_versions(is_current);
CREATE INDEX idx_training_images_client ON training_images(client_id);
CREATE INDEX idx_detection_results_client ON detection_results(client_id);
```

---

## 7. API Endpoints

### 7.1 Object Management API

```
Base URL: /api/v1/objects/

GET    /objects/                   # List all objects
POST   /objects/                   # Create new object
GET    /objects/{id}/              # Get object details
PUT    /objects/{id}/              # Update object
DELETE /objects/{id}/              # Delete object
GET    /objects/{id}/stats/        # Get training stats
```

### 7.2 Client API

```
Base URL: /api/v1/clients/

POST   /clients/register/          # Register new client
POST   /clients/authenticate/      # Get JWT token
GET    /clients/me/                # Get client info
PUT    /clients/me/                # Update client info
POST   /clients/heartbeat/         # Update last_seen
```

### 7.3 Training API

```
Base URL: /api/v1/training/

POST   /training/upload/           # Upload training image
POST   /training/start/            # Start training round
GET    /training/status/           # Get training status
GET    /training/rounds/           # List training rounds
GET    /training/rounds/{id}/      # Get round details
POST   /training/submit-metrics/  # Submit client metrics
```

### 7.4 Model API

```
Base URL: /api/v1/models/

GET    /models/current/            # Get current model version
GET    /models/download/           # Download model file
GET    /models/versions/           # List all versions
GET    /models/versions/{id}/      # Get version details
POST   /models/rollback/           # Rollback to version
```

### 7.5 Detection API

```
Base URL: /api/v1/detection/

POST   /detection/predict/         # Detect objects in image
POST   /detection/batch/           # Batch detection
GET    /detection/history/         # Detection history
```

---

## 8. Federated Learning Workflow

### 8.1 Training Round Process

```
Phase 1: Initialization
├── Admin creates object categories
├── Global model initialized with N classes
├── Model uploaded to storage (S3/MinIO)
└── Initial version v0.1.0 created

Phase 2: Client Preparation
├── Client registers with server
├── Client downloads global model
├── Client collects local training data
└── Client waits for training round

Phase 3: Training Round (Repeat for R rounds)
├── Server initiates round (round_number++)
├── Server selects K clients (10% of available)
├── Server broadcasts config to selected clients
│   ├── learning_rate
│   ├── local_epochs
│   ├── batch_size
│   └── differential_privacy settings
├── Selected clients train locally
│   ├── Load local dataset
│   ├── Train for N epochs
│   ├── Compute validation metrics
│   └── Extract model parameters
├── Clients send updates to server
│   ├── Model weights (or gradients)
│   ├── Number of samples used
│   └── Local metrics (accuracy, loss)
├── Server aggregates updates (FedAvg)
│   └── w_global = Σ(n_k/n) * w_k
├── Server evaluates global model
│   ├── Test on validation set
│   ├── Compute global metrics
│   └── Log to MLflow
├── Server updates model version
│   ├── Save checkpoint to S3
│   ├── Update database
│   └── Notify clients
└── Repeat or terminate

Phase 4: Deployment
├── Final model quantized (INT8)
├── Model exported to mobile formats
│   ├── PyTorch Mobile (.ptl)
│   ├── TensorFlow Lite (.tflite)
│   └── Core ML (.mlmodel)
└── Deployed to production
```

### 8.2 Federated Averaging (FedAvg)

**Algorithm**:
```
Server:
  Initialize global model w_0
  
  For each round t = 1 to T:
    Sample K clients from N available
    Broadcast w_t to selected clients
    
    For each client k in parallel:
      w_k^(t+1) = ClientUpdate(k, w_t)
    
    Aggregate:
      w_(t+1) = Σ(n_k/n) * w_k^(t+1)
    
    where n_k = number of samples on client k
          n = total samples across all clients

Client k:
  Receive w_t from server
  Train on local data D_k for E epochs
  Return updated weights w_k^(t+1)
```

### 8.3 Adding New Object Categories

**Incremental Learning Approach**:

1. **Add Category**: Admin adds new object via API
2. **Update Model**: Expand final layer to include new class
3. **Knowledge Distillation** (optional): Preserve old knowledge
4. **Fine-tune**: Train on new + subset of old data
5. **Deploy**: Update model version

**Implementation**:
```python
def expand_model_for_new_class(model, new_class_count):
    old_fc = model.classifier[-1]
    old_weight = old_fc.weight.data
    old_bias = old_fc.bias.data
    
    # Create new final layer
    new_fc = nn.Linear(
        old_fc.in_features,
        old_fc.out_features + new_class_count
    )
    
    # Copy old weights
    new_fc.weight.data[:old_fc.out_features] = old_weight
    new_fc.bias.data[:old_fc.out_features] = old_bias
    
    # Initialize new class weights (Xavier)
    nn.init.xavier_uniform_(
        new_fc.weight.data[old_fc.out_features:]
    )
    
    model.classifier[-1] = new_fc
    return model
```

---

## 9. Development Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Working single-server system

- [ ] Set up Django project structure
- [ ] Configure PostgreSQL + Redis
- [ ] Implement Object CRUD API
- [ ] Create admin interface
- [ ] Basic model training (non-federated)
- [ ] Simple detection endpoint
- [ ] Unit tests for core models

**Deliverable**: Admin can add objects, train model locally, detect objects

### Phase 2: Federated Infrastructure (Week 3-4)
**Goal**: Basic federated learning

- [ ] Integrate Flower framework
- [ ] Implement server-side aggregation
- [ ] Create client application (Python CLI)
- [ ] Test with 3 simulated clients
- [ ] Model versioning system
- [ ] Training round coordination

**Deliverable**: Multiple clients can train collaboratively

### Phase 3: Web Interface (Week 5-6)
**Goal**: User-friendly interfaces

- [ ] Training interface (upload/camera)
- [ ] Detection interface
- [ ] Dashboard (training progress)
- [ ] Client management UI
- [ ] Real-time updates (WebSocket)

**Deliverable**: Users can train and detect via web browser

### Phase 4: Privacy & Security (Week 7-8)
**Goal**: Production-grade security

- [ ] Differential privacy integration
- [ ] TLS/SSL for all communications
- [ ] JWT authentication
- [ ] API rate limiting
- [ ] Input validation and sanitization
- [ ] Security audit

**Deliverable**: System meets privacy regulations (GDPR-ready)

### Phase 5: Optimization (Week 9-10)
**Goal**: Performance and scalability

- [ ] Model quantization (INT8)
- [ ] Model compression techniques
- [ ] Efficient communication (gradient compression)
- [ ] Caching strategy (Redis)
- [ ] Database query optimization
- [ ] Load testing

**Deliverable**: System handles 100+ concurrent clients

### Phase 6: Mobile Support (Week 11-12)
**Goal**: iOS and Android apps

- [ ] Export models (TFLite, Core ML)
- [ ] Android app (Kotlin + Flower)
- [ ] iOS app (Swift + Flower)
- [ ] On-device training
- [ ] Camera integration

**Deliverable**: Mobile apps with full FL capabilities

### Phase 7: Production Deployment (Week 13-14)
**Goal**: Live system

- [ ] Docker containerization
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring setup (Prometheus + Grafana)
- [ ] Documentation
- [ ] User guides

**Deliverable**: Production-ready system

---

## 10. Security & Privacy

### 10.1 Authentication & Authorization

**JWT Token Flow**:
```
1. Client registers → receives API key
2. Client authenticates with API key → receives JWT
3. JWT included in all subsequent requests
4. JWT expires after 24 hours → refresh required
```

**Implementation**:
```python
# Django settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### 10.2 Differential Privacy

**Purpose**: Protect individual training samples from inference attacks

**Implementation with Opacus**:
```python
from opacus import PrivacyEngine

privacy_engine = PrivacyEngine()

model, optimizer, train_loader = privacy_engine.make_private_with_epsilon(
    module=model,
    optimizer=optimizer,
    data_loader=train_loader,
    epochs=10,
    target_epsilon=1.0,  # Privacy budget
    target_delta=1e-5,
    max_grad_norm=1.0,
)
```

**Privacy Budget**:
- ε = 1.0: Strong privacy
- ε = 10.0: Moderate privacy
- ε > 10: Weak privacy

### 10.3 Secure Communication

**TLS Configuration**:
```python
# Flower server with TLS
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=100),
    strategy=strategy,
    certificates=(
        Path("certificates/server.crt").read_bytes(),
        Path("certificates/server.key").read_bytes(),
        Path("certificates/ca.crt").read_bytes(),
    ),
)
```

### 10.4 Data Protection

**At Rest**:
- Database: PostgreSQL with encryption
- Files: AES-256 encryption for stored images
- Models: Encrypted S3/MinIO storage

**In Transit**:
- HTTPS for REST API (TLS 1.3)
- gRPC with TLS for Flower communication
- WebSocket Secure (WSS)

### 10.5 GDPR Compliance

**Right to be Forgotten**:
```python
def delete_client_data(client_id):
    # Delete training images
    TrainingImage.objects.filter(client_id=client_id).delete()
    
    # Anonymize detection history
    DetectionResult.objects.filter(client_id=client_id).update(
        client_id=None
    )
    
    # Delete client record
    Client.objects.filter(id=client_id).delete()
```

---

## 11. Performance Requirements

### 11.1 Latency Targets

```yaml
API Endpoints:
  Object CRUD: < 100ms (p95)
  Model Download: < 2s for 15MB model
  Detection: < 500ms (including inference)
  Training Upload: < 1s per image

Inference:
  Server (GPU): < 50ms per image
  Mobile (CPU): < 100ms per image
  Mobile (GPU): < 30ms per image

Federated Learning:
  Client Selection: < 1s
  Aggregation (100 clients): < 10s
  Round Duration: 5-10 minutes
```

### 11.2 Throughput

```yaml
API:
  Concurrent Requests: 1000 req/s
  Model Downloads: 100 concurrent
  Detection Requests: 500 req/s

Federated Learning:
  Clients per Round: 10-100
  Total Clients Supported: 10,000
  Rounds per Day: 100+
```

### 11.3 Scalability

**Horizontal Scaling**:
- Django: Multiple application servers (load balanced)
- Flower: Distributed server (future)
- Database: Read replicas
- Storage: S3/MinIO (auto-scaling)

**Vertical Scaling**:
- Server: 8 CPU, 16GB RAM (initial)
- Production: 16 CPU, 64GB RAM, GPU optional

### 11.4 Resource Limits

```yaml
Model Size:
  Uncompressed: < 25MB
  Quantized: < 10MB
  Mobile: < 5MB

Memory:
  Server: < 4GB per worker
  Client: < 500MB
  Mobile: < 200MB

Storage:
  Images: 1MB per image (max)
  Models: 50MB per version
  Database: 100GB (estimated for 1M images)
```

---

## 12. Deployment Strategy

### 12.1 Development Environment

```bash
# Local setup
docker-compose up -d

# Services:
# - Django: http://localhost:8000
# - Flower Server: grpc://localhost:8080
# - MySQL: localhost:3306 (using existing Mac installation)
# - Redis: localhost:6379
# - MinIO: http://localhost:9000
```

### 12.2 Staging Environment

```yaml
Infrastructure:
  Provider: AWS / GCP / Azure
  Compute: EC2 / Compute Engine / VM
  Database: RDS MySQL or Cloud SQL MySQL
  Cache: ElastiCache Redis
  Storage: S3 / Cloud Storage / Blob Storage
  
Configuration:
  Auto-scaling: 2-10 instances
  Load Balancer: Application LB
  SSL: Let's Encrypt / ACM
```

### 12.3 Production Environment

```yaml
Kubernetes Cluster:
  Nodes: 5 (3 app, 1 db, 1 monitoring)
  
  Deployments:
    - django-api (3 replicas)
    - flower-server (1 replica)
    - celery-worker (2 replicas)
    - redis (1 replica)
  
  Services:
    - LoadBalancer for Django
    - ClusterIP for internal services
  
  Ingress:
    - NGINX Ingress Controller
    - TLS termination
    - Rate limiting

Monitoring:
  - Prometheus (metrics)
  - Grafana (dashboards)
  - Loki (logs)
  - Alertmanager (alerts)
```

### 12.4 CI/CD Pipeline

```yaml
GitHub Actions:
  
  on: [push, pull_request]
  
  jobs:
    test:
      - Run linters (black, flake8, mypy)
      - Run unit tests (pytest)
      - Run integration tests
      - Check coverage (>80%)
    
    build:
      - Build Docker images
      - Push to registry
    
    deploy-staging:
      - Deploy to staging (on main branch)
      - Run smoke tests
    
    deploy-production:
      - Manual approval required
      - Deploy to production
      - Health check
      - Rollback on failure
```

---

## 13. Testing Strategy

### 13.1 Unit Tests

```python
# Test coverage targets: >80%

tests/
├── server/
│   ├── test_models.py          # Model validation
│   ├── test_serializers.py     # Serialization logic
│   ├── test_views.py           # API endpoints
│   └── test_fl_strategy.py     # Aggregation logic
├── client/
│   ├── test_flower_client.py   # Client implementation
│   └── test_training.py        # Local training
└── ml/
    ├── test_models.py          # Model architecture
    └── test_transforms.py      # Data augmentation
```

### 13.2 Integration Tests

```python
# Test end-to-end workflows

def test_federated_training_round():
    # Setup
    server = start_fl_server()
    clients = [start_client(i) for i in range(3)]
    
    # Execute
    server.start_training_round()
    
    # Assert
    assert server.current_round == 1
    assert server.global_accuracy > 0.5
    assert len(server.received_updates) == 3
```

### 13.3 Performance Tests

```python
# Load testing with Locust

class UserBehavior(TaskSet):
    @task(3)
    def detect_object(self):
        self.client.post("/api/v1/detection/predict/",
                        files={"image": test_image})
    
    @task(1)
    def list_objects(self):
        self.client.get("/api/v1/objects/")
```

### 13.4 Security Tests

- [ ] SQL injection testing
- [ ] XSS vulnerability scanning
- [ ] Authentication bypass attempts
- [ ] Rate limit verification
- [ ] CSRF protection testing

---

## 14. Monitoring & Logging

### 14.1 Metrics to Track

```yaml
System Metrics:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network traffic

Application Metrics:
  - Request rate
  - Response time (p50, p95, p99)
  - Error rate
  - Active connections

ML Metrics:
  - Training rounds completed
  - Global model accuracy
  - Average client accuracy
  - Convergence rate
  - Model size

Business Metrics:
  - Active clients
  - Objects created
  - Images uploaded
  - Detection requests
```

### 14.2 Logging Strategy

```python
# Structured logging with JSON

LOGGING = {
    'version': 1,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
```

### 14.3 Alerting Rules

```yaml
Alerts:
  - name: HighErrorRate
    condition: error_rate > 5%
    action: PagerDuty, Email
  
  - name: SlowResponse
    condition: p95_latency > 1s
    action: Slack
  
  - name: ModelAccuracyDrop
    condition: accuracy < 0.7
    action: Email, Slack
  
  - name: ClientDisconnection
    condition: active_clients < 5
    action: Slack
```

---

## 15. Best Practices

### 15.1 Code Style

```python
# Follow PEP 8 and Django style guide

# Use type hints
def train_model(
    model: torch.nn.Module,
    dataloader: DataLoader,
    epochs: int = 10
) -> Dict[str, float]:
    pass

# Docstrings for all functions
def aggregate_weights(
    client_weights: List[np.ndarray],
    num_samples: List[int]
) -> np.ndarray:
    """
    Aggregate client model weights using FedAvg.
    
    Args:
        client_weights: List of weight arrays from clients
        num_samples: Number of samples each client used
    
    Returns:
        Aggregated global weights
    """
    pass
```

### 15.2 Git Workflow

```bash
# Branch naming
feature/add-object-detection
bugfix/fix-aggregation-error
hotfix/security-patch

# Commit messages (Conventional Commits)
feat: add differential privacy support
fix: resolve model aggregation bug
docs: update API documentation
test: add integration tests for FL
refactor: improve model loading performance
```

### 15.3 Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling implemented
- [ ] Logging added where appropriate

### 15.4 Documentation Standards

```python
# README.md for each module
"""
# Module Name

## Purpose
Brief description of what this module does

## Usage
python
from module import function
result = function(param)


## API Reference
- `function(param)`: Description
- `ClassNae()`: Description

## Tests
bash
pytest tests/test_module.py

"""
```

### 15.5 Environment Variables

```bash
# .env.example - Never commit actual .env

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=mysql://user:pass@localhost:3306/federated_ai

# Redis
REDIS_URL=redis://localhost:6379/0

# S3/MinIO
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=federated-ai-models
AWS_S3_ENDPOINT_URL=http://localhost:9000

# Flower
FLOWER_SERVER_ADDRESS=localhost:8080
FLOWER_NUM_ROUNDS=100

# ML Configuration
MODEL_NAME=mobilenet_v3
BATCH_SIZE=32
LEARNING_RATE=0.001
```

---

## Appendix

### A. References

1. **Flower Framework**: https://flower.ai/docs/framework/
2. **PyTorch Mobile**: https://pytorch.org/mobile/
3. **Federated Learning**: McMahan et al., "Communication-Efficient Learning of Deep Networks from Decentralized Data"
4. **Differential Privacy**: Abadi et al., "Deep Learning with Differential Privacy"
5. **Django Best Practices**: https://docs.djangoproject.com/

### B. Glossary

- **FedAvg**: Federated Averaging - aggregation algorithm
- **Round**: One iteration of federated training
- **Client**: Device participating in federated learning
- **Global Model**: Model on central server
- **Local Model**: Model on client device
- **Differential Privacy**: Privacy-preserving technique
- **Quantization**: Model compression technique

### C. Change Log

- **v1.0.0** (2025-11-06): Initial project guidelines

---

**Document Status**: Active  
**Next Review Date**: 2025-12-06  
**Maintainer**: Development Team  

