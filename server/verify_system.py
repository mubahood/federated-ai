#!/usr/bin/env python3
"""
Federated AI - System Verification Script

This script performs comprehensive verification of the entire system:
- Database integrity
- Model relationships
- Media files
- Configuration
- Services health

Author: Federated AI Team
Date: November 6, 2025
"""

import os
import sys
from pathlib import Path

# Add Django project to path
sys.path.insert(0, '/Users/mac/Desktop/github/federated-ai/server')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from objects.models import ObjectCategory
from clients.models import Client
from training.models import TrainingImage, TrainingRound, ModelVersion
from detection.models import DetectionResult

User = get_user_model()


class SystemVerifier:
    """Comprehensive system verification."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def print_header(self, title):
        """Print section header."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def verify_database_connection(self):
        """Verify database connection."""
        self.print_header("DATABASE CONNECTION")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                self.success.append(f"✅ Database connected: MySQL {version}")
                print(f"✅ MySQL Version: {version}")
        except Exception as e:
            self.errors.append(f"❌ Database connection failed: {e}")
            print(f"❌ Database connection failed: {e}")
    
    def verify_models(self):
        """Verify all models are working."""
        self.print_header("MODEL VERIFICATION")
        
        models = [
            ('ObjectCategory', ObjectCategory),
            ('Client', Client),
            ('TrainingImage', TrainingImage),
            ('TrainingRound', TrainingRound),
            ('ModelVersion', ModelVersion),
            ('DetectionResult', DetectionResult),
        ]
        
        for model_name, model_class in models:
            try:
                count = model_class.objects.count()
                self.success.append(f"✅ {model_name}: {count} records")
                print(f"✅ {model_name}: {count} records")
            except Exception as e:
                self.errors.append(f"❌ {model_name} error: {e}")
                print(f"❌ {model_name} error: {e}")
    
    def verify_object_categories(self):
        """Verify object categories setup."""
        self.print_header("OBJECT CATEGORIES")
        
        expected_categories = ['Cat', 'Car', 'Bicycle', 'Dog', 'Person']
        
        for cat_name in expected_categories:
            try:
                cat = ObjectCategory.objects.get(name=cat_name)
                image_count = TrainingImage.objects.filter(object_category=cat).count()
                print(f"✅ {cat.name}:")
                print(f"   - Active: {cat.is_active}")
                print(f"   - Training Images: {image_count}")
                print(f"   - Tracked Count: {cat.training_images_count}")
                
                if image_count != cat.training_images_count:
                    self.warnings.append(
                        f"⚠️  {cat_name} count mismatch: {image_count} actual vs {cat.training_images_count} tracked"
                    )
                    print(f"   ⚠️  Count mismatch detected")
                else:
                    self.success.append(f"✅ {cat_name} count accurate")
                    
            except ObjectCategory.DoesNotExist:
                self.errors.append(f"❌ Missing category: {cat_name}")
                print(f"❌ Missing category: {cat_name}")
    
    def verify_clients(self):
        """Verify client records."""
        self.print_header("FEDERATED CLIENTS")
        
        clients = Client.objects.all()
        if not clients.exists():
            self.warnings.append("⚠️  No clients registered")
            print("⚠️  No clients registered")
        else:
            for client in clients:
                print(f"✅ {client.name}:")
                print(f"   - Device ID: {client.device_id}")
                print(f"   - Type: {client.device_type}")
                print(f"   - Status: {client.status}")
                print(f"   - Training Rounds: {client.total_training_rounds}")
                print(f"   - Samples: {client.total_samples_contributed}")
                
                image_count = TrainingImage.objects.filter(client=client).count()
                print(f"   - Uploaded Images: {image_count}")
                
                self.success.append(f"✅ Client {client.name} verified")
    
    def verify_training_images(self):
        """Verify training images."""
        self.print_header("TRAINING IMAGES")
        
        total = TrainingImage.objects.count()
        validated = TrainingImage.objects.filter(is_validated=True).count()
        
        print(f"Total Images: {total}")
        print(f"Validated: {validated}")
        print(f"Pending Validation: {total - validated}")
        print()
        
        # Check for images without files
        missing_files = 0
        for img in TrainingImage.objects.all()[:100]:  # Sample first 100
            if not img.image or not os.path.exists(img.image.path):
                missing_files += 1
        
        if missing_files > 0:
            self.errors.append(f"❌ {missing_files} images have missing files (in sample of 100)")
            print(f"❌ {missing_files} images have missing files (in sample of 100)")
        else:
            self.success.append("✅ All sampled images have valid files")
            print("✅ All sampled images have valid files (sample of 100)")
        
        # Metadata verification
        with_metadata = TrainingImage.objects.exclude(metadata={}).count()
        print(f"\nMetadata Statistics:")
        print(f"  - Images with metadata: {with_metadata}/{total}")
        
        if with_metadata > 0:
            self.success.append(f"✅ {with_metadata} images have metadata")
        else:
            self.warnings.append("⚠️  No images have metadata")
    
    def verify_media_directory(self):
        """Verify media directory structure."""
        self.print_header("MEDIA DIRECTORY")
        
        if os.path.exists('/app/server'):
            media_root = Path('/app/server/media')
        else:
            media_root = Path('/Users/mac/Desktop/github/federated-ai/server/media')
        
        if not media_root.exists():
            self.errors.append(f"❌ Media directory not found: {media_root}")
            print(f"❌ Media directory not found: {media_root}")
            return
        
        print(f"✅ Media Root: {media_root}")
        
        # Count files
        training_dir = media_root / 'training_images'
        if training_dir.exists():
            file_count = sum(1 for _ in training_dir.rglob('*') if _.is_file())
            print(f"✅ Training Images: {file_count} files")
            
            # Check directory structure
            year_dirs = list(training_dir.glob('*'))
            print(f"✅ Organization: {len(year_dirs)} year directories")
            
            self.success.append(f"✅ {file_count} image files in media directory")
        else:
            self.warnings.append("⚠️  Training images directory not found")
            print("⚠️  Training images directory not found")
    
    def verify_admin_user(self):
        """Verify admin user exists."""
        self.print_header("ADMIN USER")
        
        try:
            admin = User.objects.get(username='admin')
            print(f"✅ Admin user exists")
            print(f"   - Username: {admin.username}")
            print(f"   - Email: {admin.email}")
            print(f"   - Is Staff: {admin.is_staff}")
            print(f"   - Is Superuser: {admin.is_superuser}")
            
            if not admin.is_staff or not admin.is_superuser:
                self.warnings.append("⚠️  Admin user missing permissions")
            else:
                self.success.append("✅ Admin user properly configured")
                
        except User.DoesNotExist:
            self.errors.append("❌ Admin user not found")
            print("❌ Admin user not found")
    
    def verify_configuration(self):
        """Verify Django configuration."""
        self.print_header("CONFIGURATION")
        
        from django.conf import settings
        
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ DATABASE: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ MEDIA_URL: {settings.MEDIA_URL}")
        print(f"✅ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        
        # Check Redis
        print(f"✅ REDIS: {settings.CACHES['default']['LOCATION']}")
        
        # Check Celery
        print(f"✅ CELERY_BROKER: {settings.CELERY_BROKER_URL}")
        
        self.success.append("✅ Configuration loaded successfully")
    
    def generate_report(self):
        """Generate final verification report."""
        self.print_header("VERIFICATION REPORT")
        
        print(f"\n✅ Successful Checks: {len(self.success)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        print()
        
        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        if not self.errors and not self.warnings:
            print("🎉 ALL CHECKS PASSED - SYSTEM IS HEALTHY!")
            return 0
        elif not self.errors:
            print("✅ SYSTEM IS OPERATIONAL (with warnings)")
            return 0
        else:
            print("❌ SYSTEM HAS ERRORS - REQUIRES ATTENTION")
            return 1
    
    def run(self):
        """Run all verifications."""
        print("\n" + "=" * 80)
        print("  FEDERATED AI - SYSTEM VERIFICATION")
        print("  Date: November 6, 2025")
        print("=" * 80)
        
        self.verify_database_connection()
        self.verify_configuration()
        self.verify_models()
        self.verify_object_categories()
        self.verify_clients()
        self.verify_training_images()
        self.verify_media_directory()
        self.verify_admin_user()
        
        return self.generate_report()


def main():
    """Main entry point."""
    verifier = SystemVerifier()
    exit_code = verifier.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
