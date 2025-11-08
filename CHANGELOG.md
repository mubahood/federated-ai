# Changelog

All notable changes to the Federated AI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Django Admin dashboard with real-time system monitoring
- Android app with native ML integration (PyTorch Mobile)
- Model versioning system with SHA256 verification
- Image upload queue with retry logic
- Celery async training pipeline
- Comprehensive API documentation with Swagger/OpenAPI
- Docker Compose setup for easy deployment
- Token-based authentication system

### Changed
- Migrated from SQLite to MySQL 8.0 for production readiness
- Updated model architecture to MobileNetV3 for better mobile performance
- Improved API response times with Redis caching

### Fixed
- Template loading issues in Django Admin dashboard
- Field name mismatches in ORM queries
- Android app build configuration errors

## [1.0.0-alpha] - 2025-11-08

### Added
- Initial release with core federated learning infrastructure
- RESTful API for client registration and data upload
- PyTorch-based training pipeline
- Django backend with MySQL database
- Redis message broker for Celery
- MinIO object storage integration
- Basic Android app with image capture

### Infrastructure
- Docker containerization for all services
- Nginx reverse proxy configuration
- Environment-based configuration
- Automated database migrations

### Documentation
- Project README with quick start guide
- API documentation and usage guides
- E2E testing documentation
- Model performance testing guide
- Contributing guidelines

---

## Version History

- `1.0.0-alpha` - Initial alpha release (2025-11-08)
- `0.1.0` - Development version

---

## Migration Notes

### From 0.x to 1.0.0-alpha

1. Update database schema:
   ```bash
   python manage.py migrate
   ```

2. Update environment variables (see `.env.example`)

3. Regenerate API keys for all clients

4. Rebuild Android app with new API endpoints

---

For more details, see the [commit history](https://github.com/yourusername/federated-ai/commits/).
