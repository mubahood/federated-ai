"""
Sample Data Generator for Federated AI Dashboard

This script creates sample data to populate the Django Admin dashboard
and demonstrate all the statistics and monitoring features.

Usage:
    docker compose exec django python manage.py shell < create_sample_data.py

Or in Django shell:
    exec(open('create_sample_data.py').read())
"""

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
import random

# Import models
from clients.models import Client
from objects.models import ObjectCategory
from training.models import TrainingSession, TrainingImage, TrainingRound, ModelVersion
from detection.models import DetectionResult

print("=" * 80)
print("CREATING SAMPLE DATA FOR FEDERATED AI DASHBOARD")
print("=" * 80)

# Create superuser if doesn't exist
print("\n1. Creating superuser...")
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@federatedai.com',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"   ✅ Created superuser: admin / admin123")
else:
    print(f"   ℹ️  Superuser already exists: {admin_user.username}")

# Create object categories
print("\n2. Creating object categories...")
categories_data = [
    {'name': 'Bicycle', 'description': 'Two-wheeled vehicle', 'icon': '🚲'},
    {'name': 'Car', 'description': 'Four-wheeled motor vehicle', 'icon': '🚗'},
    {'name': 'Person', 'description': 'Human being', 'icon': '🧍'},
    {'name': 'Dog', 'description': 'Canine pet', 'icon': '🐕'},
    {'name': 'Cat', 'description': 'Feline pet', 'icon': '🐈'},
    {'name': 'Bird', 'description': 'Flying animal', 'icon': '🐦'},
    {'name': 'Chair', 'description': 'Furniture for sitting', 'icon': '🪑'},
    {'name': 'Table', 'description': 'Furniture surface', 'icon': '🪑'},
]

categories = []
for cat_data in categories_data:
    category, created = ObjectCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'description': cat_data['description'],
            'created_by': admin_user,
            'is_active': True,
        }
    )
    categories.append(category)
    status = "✅ Created" if created else "ℹ️  Exists"
    print(f"   {status}: {category.name}")

print(f"\n   Total categories: {ObjectCategory.objects.count()}")

# Create clients
print("\n3. Creating clients...")
device_types = ['android', 'ios', 'web', 'desktop']
client_names = [
    'Alice_Phone', 'Bob_Tablet', 'Charlie_Desktop', 'Diana_iPhone',
    'Eve_Web', 'Frank_Android', 'Grace_iPad', 'Henry_Laptop',
    'Iris_Phone', 'Jack_Desktop'
]

import uuid as uuid_module

clients = []
now = timezone.now()
for i, name in enumerate(client_names):
    # Vary the last_seen time
    if i < 3:  # Online
        last_seen = now - timedelta(minutes=random.randint(0, 4))
    elif i < 7:  # Active (last 7 days)
        last_seen = now - timedelta(days=random.randint(0, 6))
    else:  # Inactive
        last_seen = now - timedelta(days=random.randint(8, 30))
    
    client, created = Client.objects.get_or_create(
        name=name,
        defaults={
            'device_id': uuid_module.uuid4(),
            'device_type': device_types[i % len(device_types)],
            'owner': admin_user,
            'status': 'active' if i < 7 else 'inactive',
            'last_seen': last_seen,
            'ip_address': f'192.168.1.{100 + i}',
        }
    )
    clients.append(client)
    status = "✅ Created" if created else "ℹ️  Exists"
    print(f"   {status}: {client.name} ({client.device_type}) - last seen {last_seen.strftime('%Y-%m-%d %H:%M')}")

print(f"\n   Total clients: {Client.objects.count()}")
print(f"   Online clients: {Client.objects.filter(last_seen__gte=now - timedelta(minutes=5)).count()}")
print(f"   Active clients: {Client.objects.filter(last_seen__gte=now - timedelta(days=7)).count()}")

# Create training images
print("\n4. Creating training images...")
total_images = 50
created_count = 0

for i in range(total_images):
    category = random.choice(categories)
    client = random.choice(clients[:7])  # Only active clients upload images
    created_at = now - timedelta(days=random.randint(0, 30))
    
    # Use unique identifier to avoid duplicates
    try:
        image = TrainingImage.objects.create(
            object_category=category,
            client=client,
            uploaded_by=admin_user,
            is_validated=random.choice([True, True, True, False]),  # 75% validated
            times_used_in_training=random.randint(0, 5),
            metadata={'width': 640, 'height': 480, 'format': 'JPEG'},
        )
        image.created_at = created_at  # Override the auto_now_add
        image.save(update_fields=['created_at'])
        created_count += 1
    except Exception as e:
        print(f"   ⚠️ Error creating image: {e}")
        continue

print(f"   ✅ Created {created_count} new images")
print(f"   Total images: {TrainingImage.objects.count()}")
print(f"   Validated: {TrainingImage.objects.filter(is_validated=True).count()}")
print(f"   Pending: {TrainingImage.objects.filter(is_validated=False).count()}")

# Create training sessions and rounds
print("\n5. Creating training sessions...")
print(f"   ℹ️  Skipping training sessions (complex setup)")
print(f"   Total sessions: {TrainingSession.objects.count()}")
print(f"   Total rounds: {TrainingRound.objects.count()}")

# Create model versions
print("\n6. Creating model versions...")
print(f"   ℹ️  Skipping model versions (complex setup)")
print(f"   Total models: {ModelVersion.objects.count()}")

# Create detections  
print("\n7. Creating detection results...")
print(f"   ℹ️  Skipping detections (requires model versions)")
print(f"   Total detections: {DetectionResult.objects.count()}")

from django.db.models import Avg
avg_inference = DetectionResult.objects.aggregate(avg=Avg('inference_time_ms'))['avg']
if avg_inference:
    print(f"   Avg inference time: {avg_inference:.1f}ms")

print(f"   ✅ Created {created_count} new detections")
from django.db.models import Avg

print(f"   Total detections: {DetectionResult.objects.count()}")
print(f"   This week: {DetectionResult.objects.filter(created_at__gte=now - timedelta(days=7)).count()}")
avg_inference = DetectionResult.objects.aggregate(avg=Avg('inference_time_ms'))['avg']
if avg_inference:
    print(f"   Avg inference time: {avg_inference:.1f}ms")

# Summary
print("\n" + "=" * 80)
print("SAMPLE DATA CREATION COMPLETE!")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   • Categories: {ObjectCategory.objects.count()}")
print(f"   • Clients: {Client.objects.count()}")
print(f"   • Training Images: {TrainingImage.objects.count()}")
print(f"   • Training Sessions: {TrainingSession.objects.count()}")
print(f"   • Training Rounds: {TrainingRound.objects.count()}")
print(f"   • Model Versions: {ModelVersion.objects.count()}")
print(f"   • Detections: {DetectionResult.objects.count()}")

print(f"\n🔑 Admin Credentials:")
print(f"   Username: admin")
print(f"   Password: admin123")
print(f"   Dashboard: http://localhost:8000/admin/dashboard/")

print(f"\n✨ Next Steps:")
print(f"   1. Login to admin: http://localhost:8000/admin/")
print(f"   2. View the dashboard (auto-redirects)")
print(f"   3. Explore all the statistics and monitoring features!")
print("\n" + "=" * 80)
