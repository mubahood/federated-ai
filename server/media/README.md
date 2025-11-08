# Media Directory

This directory stores uploaded media files from the federated learning system:

- `training_images/` - Training images uploaded by clients (not tracked in git)
- `uploaded_images/` - Raw uploaded images before processing
- `temp/` - Temporary files during processing

**Note:** Actual image files are excluded from version control due to size constraints. The directory structure is maintained for deployment purposes.

## Setup

On a new deployment, this directory will be automatically created by Django. If deploying manually:

```bash
mkdir -p server/media/training_images
chmod 755 server/media
```

## Storage Recommendations

- **Development:** Local file system (current setup)
- **Production:** Use object storage (S3, MinIO, GCS) for scalability
- **Docker:** Mount as volume in docker-compose.yml
