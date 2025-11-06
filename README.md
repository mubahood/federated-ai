# Federated AI - Object Detection System

A production-grade federated learning system for dynamic object detection that enables privacy-preserving distributed training across multiple devices.

## 🚀 Features

- **Dynamic Object Management**: Add/remove objects without retraining entire model
- **Federated Learning**: Train on distributed devices without sharing raw data
- **Real-time Detection**: Fast inference with confidence scoring
- **Privacy-Preserving**: Differential privacy + secure aggregation
- **Cross-Platform**: Web, desktop, and mobile (iOS/Android) support

## 📋 Prerequisites

- Python 3.10+
- MySQL 8.0+
- Redis 7.0+
- Git

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/federated-ai.git
cd federated-ai
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements/server.txt  # For server
pip install -r requirements/client.txt  # For client
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Set up database

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE federated_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# Run migrations
cd server
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start Redis (if not running)

```bash
redis-server
```

### 7. Start the server

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Flower FL server
python fl_server/server.py
```

## 📚 Documentation

- [Project Guidelines](PROJECT_GUIDELINES.md) - Complete technical specification
- [Task List](TASK_LIST.md) - Development task tracking
- [API Documentation](docs/api/) - REST API reference
- [User Guide](docs/user-guides/) - How to use the system

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=server --cov=client

# Run specific test
pytest tests/server/test_models.py
```

## 🏗️ Project Structure

```
federated-ai/
├── server/           # Central server (Django + Flower)
├── client/           # Federated clients
├── shared/           # Shared code
├── web_interface/    # Web UI
├── tests/            # Test suite
├── docs/             # Documentation
└── requirements/     # Python dependencies
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

## 📧 Contact

Project Link: [https://github.com/yourusername/federated-ai](https://github.com/yourusername/federated-ai)

---

**Status**: 🔄 In Development  
**Version**: 0.1.0  
**Last Updated**: November 6, 2025
