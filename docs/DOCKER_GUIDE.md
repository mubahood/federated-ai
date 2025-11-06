# Docker Setup Guide

## 🐳 Why Docker?

Docker solves these problems:
- ✅ No dependency conflicts
- ✅ Consistent environment (dev = production)
- ✅ Easy database setup (MySQL, Redis, MinIO)
- ✅ Simple multi-client testing
- ✅ One-command deployment

## 📋 Prerequisites

1. **Install Docker Desktop**
   - Mac: https://docs.docker.com/desktop/install/mac-install/
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Linux: https://docs.docker.com/desktop/install/linux-install/

2. **Verify Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

## 🚀 Quick Start

### 1. Start Core Services

```bash
cd federated-ai
./scripts/docker-start.sh
# Choose option 1
```

This starts:
- MySQL (port 3306)
- Redis (port 6379)
- MinIO (ports 9000, 9001)
- Django API (port 8000)
- Celery worker

### 2. Create Superuser

```bash
docker-compose exec django python server/manage.py createsuperuser
```

### 3. Access Services

- **Django API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin`

## 📚 Common Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Start with clients for testing
docker-compose --profile with-clients up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart django

# View service status
docker-compose ps
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs django
docker-compose logs mysql
```

### Django Management Commands

```bash
# Run migrations
docker-compose exec django python server/manage.py migrate

# Create superuser
docker-compose exec django python server/manage.py createsuperuser

# Run Django shell
docker-compose exec django python server/manage.py shell

# Create new app
docker-compose exec django python server/manage.py startapp myapp

# Collect static files
docker-compose exec django python server/manage.py collectstatic
```

### Database Operations

```bash
# Access MySQL shell
docker-compose exec mysql mysql -u root -proot fed

# Backup database
docker-compose exec mysql mysqldump -u root -proot fed > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u root -proot fed < backup.sql

# View database tables
docker-compose exec mysql mysql -u root -proot fed -e "SHOW TABLES;"
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check Redis keys
docker-compose exec redis redis-cli KEYS '*'

# Flush all Redis data
docker-compose exec redis redis-cli FLUSHALL
```

### Container Shell Access

```bash
# Access Django container shell
docker-compose exec django bash

# Access MySQL container shell
docker-compose exec mysql bash

# Run Python in Django container
docker-compose exec django python
```

## 🧪 Development Workflow

### 1. Code Changes

Changes to code in `server/`, `client/`, `shared/` are automatically reflected (volumes are mounted).

### 2. Dependency Changes

If you modify `requirements/*.txt`:

```bash
# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d
```

### 3. Database Schema Changes

```bash
# Create migrations
docker-compose exec django python server/manage.py makemigrations

# Apply migrations
docker-compose exec django python server/manage.py migrate

# View migration status
docker-compose exec django python server/manage.py showmigrations
```

## 🔧 Troubleshooting

### Service Won't Start

```bash
# View detailed logs
docker-compose logs [service_name]

# Check if port is already in use
lsof -i :8000  # Django
lsof -i :3306  # MySQL
lsof -i :6379  # Redis

# Kill process on port
kill -9 $(lsof -t -i:8000)
```

### Database Connection Issues

```bash
# Verify MySQL is running
docker-compose ps mysql

# Check MySQL logs
docker-compose logs mysql

# Test connection
docker-compose exec django python -c "
import pymysql
conn = pymysql.connect(host='mysql', user='root', password='root', database='fed')
print('✅ Connection successful!')
conn.close()
"
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec django python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
print('✅ Redis PING:', r.ping())
"
```

### Container Keeps Restarting

```bash
# View exit code and error
docker-compose ps

# Check logs for errors
docker-compose logs [service_name]

# Remove and recreate container
docker-compose rm [service_name]
docker-compose up -d [service_name]
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

### Reset Everything

```bash
# Stop and remove all containers, volumes, and networks
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## 🎯 Testing Federated Learning

### Start with Multiple Clients

```bash
# Start with 2 test clients
docker-compose --profile with-clients up -d

# View client logs
docker-compose logs flower_client_1
docker-compose logs flower_client_2

# Scale to more clients
docker-compose --profile with-clients up -d --scale flower_client_1=5
```

### Monitor Training

```bash
# Watch Flower server logs
docker-compose logs -f flower_server

# Watch Django logs for training rounds
docker-compose logs -f django

# Check Celery worker logs
docker-compose logs -f celery
```

## 📦 Production Deployment

For production, update `docker-compose.yml`:

1. **Security**
   - Change all default passwords
   - Use environment variables for secrets
   - Enable SSL/TLS

2. **Performance**
   - Use production WSGI server (Gunicorn)
   - Configure connection pooling
   - Set up load balancing

3. **Monitoring**
   - Add Prometheus & Grafana containers
   - Configure log aggregation
   - Set up health checks

## 🔗 Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django in Docker Best Practices](https://docs.docker.com/samples/django/)

## ❓ Need Help?

Check the troubleshooting section or open an issue on GitHub.
