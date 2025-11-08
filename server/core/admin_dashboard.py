"""
Custom Admin Dashboard for Federated AI System

Provides comprehensive overview of the entire federated learning system.
"""

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from clients.models import Client
from training.models import TrainingImage, TrainingRound, ModelVersion, TrainingSession
from detection.models import DetectionResult
from objects.models import ObjectCategory


@staff_member_required
def dashboard_view(request):
    """
    Main dashboard view showing system overview.
    """
    # Time ranges
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # ===== CLIENT STATISTICS =====
    total_clients = Client.objects.filter(is_deleted=False).count()
    active_clients = Client.objects.filter(
        is_deleted=False,
        last_seen__gte=week_ago
    ).count()
    online_clients = Client.objects.filter(
        is_deleted=False,
        status='active',
        last_seen__gte=now - timedelta(minutes=5)
    ).count()
    
    # Client breakdown by device type
    clients_by_device = Client.objects.filter(
        is_deleted=False
    ).values('device_type').annotate(count=Count('id'))
    
    # ===== TRAINING DATA STATISTICS =====
    total_training_images = TrainingImage.objects.filter(is_deleted=False).count()
    validated_images = TrainingImage.objects.filter(
        is_deleted=False,
        is_validated=True
    ).count()
    pending_validation = TrainingImage.objects.filter(
        is_deleted=False,
        is_validated=False
    ).count()
    
    # Images by category
    images_by_category = TrainingImage.objects.filter(
        is_deleted=False
    ).values('object_category__name').annotate(count=Count('id')).order_by('-count')
    
    # Images uploaded this week
    images_this_week = TrainingImage.objects.filter(
        is_deleted=False,
        created_at__gte=week_ago
    ).count()
    
    # ===== MODEL STATISTICS =====
    total_model_versions = ModelVersion.objects.count()
    latest_model = ModelVersion.objects.order_by('-version').first()
    
    # Model performance stats
    if latest_model:
        latest_model_stats = {
            'version': latest_model.version,
            'accuracy': latest_model.accuracy,
            'created_at': latest_model.created_at,
            'file_size_mb': round(latest_model.file_size / (1024 * 1024), 2) if latest_model.file_size else 0,
        }
    else:
        latest_model_stats = None
    
    # ===== TRAINING STATISTICS =====
    total_training_rounds = TrainingRound.objects.count()
    completed_rounds = TrainingRound.objects.filter(status='completed').count()
    active_training = TrainingSession.objects.filter(status='running').count()
    
    # Recent training sessions
    recent_sessions = TrainingSession.objects.order_by('-created_at')[:5].values(
        'id', 'name', 'status', 'model_name', 'current_round', 'num_rounds', 'created_at'
    )
    
    # Training rounds this month
    rounds_this_month = TrainingRound.objects.filter(
        created_at__gte=month_ago
    ).count()
    
    # Average training time
    avg_training_time = TrainingRound.objects.filter(
        status='completed',
        end_time__isnull=False
    ).aggregate(
        avg_duration=Avg('end_time') - Avg('start_time')
    )
    
    # ===== DETECTION/INFERENCE STATISTICS =====
    total_detections = DetectionResult.objects.count()
    detections_this_week = DetectionResult.objects.filter(
        created_at__gte=week_ago
    ).count()
    
    # Average inference time
    avg_inference_time = DetectionResult.objects.aggregate(
        avg_time=Avg('inference_time_ms')
    )['avg_time'] or 0
    
    # Detections by category
    detections_by_category = DetectionResult.objects.values(
        'detected_object__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    # Average confidence
    avg_confidence = DetectionResult.objects.aggregate(
        avg_conf=Avg('confidence')
    )['avg_conf'] or 0
    
    # Feedback stats
    correct_predictions = DetectionResult.objects.filter(is_correct=True).count()
    incorrect_predictions = DetectionResult.objects.filter(is_correct=False).count()
    total_feedback = correct_predictions + incorrect_predictions
    accuracy_from_feedback = (correct_predictions / total_feedback * 100) if total_feedback > 0 else 0
    
    # ===== CATEGORY STATISTICS =====
    total_categories = ObjectCategory.objects.filter(
        is_deleted=False,
        is_active=True
    ).count()
    
    categories_with_stats = ObjectCategory.objects.filter(
        is_deleted=False,
        is_active=True
    ).annotate(
        current_training_images=Count('training_images', filter=Q(training_images__is_deleted=False)),
        current_detections=Count('detections')
    ).order_by('-current_training_images')[:10]
    
    # ===== SYSTEM HEALTH =====
    system_health = {
        'status': 'healthy',
        'issues': []
    }
    
    # Check for issues
    if pending_validation > validated_images * 0.5:
        system_health['issues'].append('High number of images pending validation')
    
    if active_clients == 0:
        system_health['issues'].append('No active clients in the last week')
        system_health['status'] = 'warning'
    
    if total_training_images < 100:
        system_health['issues'].append('Insufficient training data (< 100 images)')
        system_health['status'] = 'warning'
    
    if not latest_model:
        system_health['issues'].append('No model versions available')
        system_health['status'] = 'error'
    
    # ===== ACTIVITY TIMELINE =====
    # Recent activity across the system
    recent_activities = []
    
    # Recent clients
    for client in Client.objects.filter(is_deleted=False).order_by('-created_at')[:3]:
        recent_activities.append({
            'type': 'client',
            'icon': '📱',
            'title': f'New client: {client.name}',
            'timestamp': client.created_at
        })
    
    # Recent images
    for image in TrainingImage.objects.filter(is_deleted=False).select_related('object_category').order_by('-created_at')[:3]:
        recent_activities.append({
            'type': 'image',
            'icon': '📸',
            'title': f'New training image uploaded ({image.object_category.name if image.object_category else "Uncategorized"})',
            'timestamp': image.created_at
        })
    
    # Recent training rounds
    for training_round in TrainingRound.objects.order_by('-created_at')[:3]:
        recent_activities.append({
            'type': 'training',
            'icon': '🎓',
            'title': f'Training round #{training_round.round_number} {training_round.get_status_display()}',
            'timestamp': training_round.created_at
        })
    
    # Recent models
    for model in ModelVersion.objects.order_by('-created_at')[:2]:
        recent_activities.append({
            'type': 'model',
            'icon': '🤖',
            'title': f'New model version {model.version} deployed',
            'timestamp': model.created_at
        })
    
    # Sort by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]
    
    context = {
        # Clients
        'total_clients': total_clients,
        'active_clients': active_clients,
        'online_clients': online_clients,
        'clients_by_device': list(clients_by_device),
        
        # Training Data
        'total_training_images': total_training_images,
        'validated_images': validated_images,
        'pending_validation': pending_validation,
        'images_this_week': images_this_week,
        'images_by_category': list(images_by_category)[:5],
        
        # Models
        'total_model_versions': total_model_versions,
        'latest_model_stats': latest_model_stats,
        
        # Training
        'total_training_rounds': total_training_rounds,
        'completed_rounds': completed_rounds,
        'active_training': active_training,
        'recent_sessions': list(recent_sessions),
        'rounds_this_month': rounds_this_month,
        
        # Detection/Inference
        'total_detections': total_detections,
        'detections_this_week': detections_this_week,
        'avg_inference_time': round(avg_inference_time, 2),
        'detections_by_category': list(detections_by_category),
        'avg_confidence': round(avg_confidence * 100, 2),
        'accuracy_from_feedback': round(accuracy_from_feedback, 2),
        'correct_predictions': correct_predictions,
        'incorrect_predictions': incorrect_predictions,
        
        # Categories
        'total_categories': total_categories,
        'categories_with_stats': list(categories_with_stats),
        
        # System Health
        'system_health': system_health,
        
        # Activity Timeline
        'recent_activities': recent_activities,
        
        # Metadata
        'dashboard_updated': now,
    }
    
    return render(request, 'admin/dashboard.html', context)
