#!/bin/bash

# Federated AI - Docker Quick Start Script
# This script helps you quickly start the project with Docker

set -e

echo "🚀 Federated AI - Docker Setup"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"

# Navigate to docker directory
cd "$(dirname "$0")/../docker"

echo ""
echo "Choose an option:"
echo "1. Start core services (MySQL, Redis, MinIO, Django)"
echo "2. Start all services (including Flower server and clients)"
echo "3. Stop all services"
echo "4. View logs"
echo "5. Reset all data (WARNING: This will delete all data!)"
echo "6. Run Django management command"
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🏗️  Building and starting core services..."
        docker-compose up -d mysql redis minio django celery
        echo ""
        echo "✅ Core services started!"
        echo ""
        echo "📝 Access points:"
        echo "   - Django API: http://localhost:8000"
        echo "   - MinIO Console: http://localhost:9001 (admin/minioadmin)"
        echo ""
        echo "📊 View logs: docker-compose logs -f"
        ;;
    2)
        echo ""
        echo "🏗️  Building and starting all services..."
        docker-compose --profile with-clients up -d
        echo ""
        echo "✅ All services started!"
        echo ""
        echo "📝 Access points:"
        echo "   - Django API: http://localhost:8000"
        echo "   - Flower Server: localhost:8080"
        echo "   - MinIO Console: http://localhost:9001"
        echo ""
        echo "📊 View logs: docker-compose logs -f"
        ;;
    3)
        echo ""
        echo "🛑 Stopping all services..."
        docker-compose --profile with-clients down
        echo "✅ All services stopped!"
        ;;
    4)
        echo ""
        echo "📊 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    5)
        echo ""
        read -p "⚠️  Are you sure? This will delete ALL data! (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "🗑️  Stopping services and removing volumes..."
            docker-compose --profile with-clients down -v
            echo "✅ All data has been reset!"
        else
            echo "❌ Cancelled"
        fi
        ;;
    6)
        echo ""
        read -p "Enter Django management command (e.g., createsuperuser): " command
        docker-compose exec django python server/manage.py $command
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Done!"
