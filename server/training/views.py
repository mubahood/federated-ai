"""
API views for the training app.
"""
from rest_framework import viewsets, filters, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import TrainingImage, TrainingRound, ModelVersion
from .serializers import (
    TrainingImageSerializer,
    TrainingImageListSerializer,
    TrainingImageUploadSerializer,
    TrainingRoundSerializer,
    TrainingRoundListSerializer,
    ModelVersionSerializer,
    ModelVersionListSerializer
)
from core.permissions import CanUploadImages, IsOwnerOrReadOnly, IsClientOrAdmin


class TrainingImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TrainingImage CRUD operations.
    
    Provides:
    - list: Get all training images (with filtering, search, ordering)
    - retrieve: Get single training image by ID
    - create: Upload new training image
    - update/partial_update: Update image metadata
    - destroy: Soft delete image
    
    Filters:
    - object_category: Filter by category ID
    - is_validated: Filter by validation status
    - client: Filter by client ID
    
    Search:
    - Search in metadata and validation_notes
    
    Ordering:
    - created_at, times_used_in_training
    """
    queryset = TrainingImage.objects.select_related('object_category', 'client', 'uploaded_by')
    serializer_class = TrainingImageSerializer
    permission_classes = [CanUploadImages]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['object_category', 'is_validated', 'client']
    search_fields = ['metadata', 'validation_notes']
    ordering_fields = ['created_at', 'times_used_in_training']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return TrainingImageListSerializer
        elif self.action == 'upload':
            return TrainingImageUploadSerializer
        return TrainingImageSerializer
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to the current user."""
        if self.request.user.is_authenticated:
            serializer.save(uploaded_by=self.request.user)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete the image."""
        instance.soft_delete()
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Mark an image as validated.
        
        POST /api/v1/training/images/{id}/validate/
        Body: {"validation_notes": "Looks good!"}
        """
        image = self.get_object()
        image.is_validated = True
        image.validation_notes = request.data.get('validation_notes', '')
        image.save()
        serializer = self.get_serializer(image)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invalidate(self, request, pk=None):
        """
        Mark an image as invalid.
        
        POST /api/v1/training/images/{id}/invalidate/
        Body: {"validation_notes": "Poor quality"}
        """
        image = self.get_object()
        image.is_validated = False
        image.validation_notes = request.data.get('validation_notes', '')
        image.save()
        serializer = self.get_serializer(image)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Upload multiple training images at once.
        
        POST /api/v1/training/images/bulk_upload/
        """
        images = request.FILES.getlist('images')
        category_id = request.data.get('object_category')
        client_id = request.data.get('client')
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not category_id:
            return Response(
                {'error': 'object_category is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image_file in images:
            data = {
                'object_category': category_id,
                'image': image_file,
                'client': client_id,
            }
            serializer = TrainingImageUploadSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                if request.user.is_authenticated:
                    instance = serializer.save(uploaded_by=request.user)
                else:
                    instance = serializer.save()
                created_images.append(instance)
        
        result_serializer = TrainingImageListSerializer(created_images, many=True, context={'request': request})
        return Response({
            'count': len(created_images),
            'images': result_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def upload_from_mobile(self, request):
        """
        Upload labeled images from mobile app.
        
        POST /api/v1/training/images/upload_from_mobile/
        
        Supports:
        - Single or multiple images
        - Batch metadata
        - Client identification
        - Automatic validation
        
        Body (multipart/form-data):
        {
            "images": [files],
            "labels": ["Cat", "Dog", "Car"],  // One label per image
            "client_id": "device_uuid",
            "batch_id": "optional_batch_id",
            "auto_validate": true  // Auto-mark as validated
        }
        
        Returns: {
            "uploaded": 3,
            "failed": 0,
            "images": [...]
        }
        """
        from objects.models import ObjectCategory
        from clients.models import Client
        
        images = request.FILES.getlist('images')
        labels_json = request.data.get('labels', '[]')
        client_id = request.data.get('client_id')
        batch_id = request.data.get('batch_id')
        auto_validate = request.data.get('auto_validate', 'true').lower() == 'true'
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse labels
        try:
            if isinstance(labels_json, str):
                import json
                labels = json.loads(labels_json)
            else:
                labels = labels_json
        except:
            labels = []
        
        if len(labels) != len(images):
            return Response(
                {
                    'error': f'Number of labels ({len(labels)}) must match number of images ({len(images)})',
                    'images_count': len(images),
                    'labels_count': len(labels)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create client
        client = None
        if client_id:
            client, _ = Client.objects.get_or_create(
                device_id=client_id,
                defaults={'name': f'Mobile Client {client_id[:8]}'}
            )
        
        # Process each image
        created_images = []
        failed_images = []
        
        for idx, (image_file, label) in enumerate(zip(images, labels)):
            try:
                # Get category by name
                category = ObjectCategory.objects.filter(
                    name__iexact=label,
                    is_active=True
                ).first()
                
                if not category:
                    failed_images.append({
                        'index': idx,
                        'filename': image_file.name,
                        'error': f'Category "{label}" not found'
                    })
                    continue
                
                # Create training image
                training_image = TrainingImage.objects.create(
                    image=image_file,
                    object_category=category,
                    client=client,
                    uploaded_by=request.user if request.user.is_authenticated else None,
                    is_validated=auto_validate,
                    metadata={
                        'batch_id': batch_id,
                        'uploaded_from': 'mobile_app',
                        'original_filename': image_file.name,
                        'file_size': image_file.size
                    }
                )
                
                created_images.append(training_image)
                
            except Exception as e:
                failed_images.append({
                    'index': idx,
                    'filename': image_file.name,
                    'error': str(e)
                })
        
        # Serialize results
        result_serializer = TrainingImageListSerializer(
            created_images, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'uploaded': len(created_images),
            'failed': len(failed_images),
            'total': len(images),
            'images': result_serializer.data,
            'failures': failed_images if failed_images else [],
            'batch_id': batch_id
        }, status=status.HTTP_201_CREATED if created_images else status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get training images statistics.
        
        GET /api/v1/training/images/statistics/
        """
        images = self.get_queryset()
        
        stats = {
            'total_images': images.count(),
            'validated_images': images.filter(is_validated=True).count(),
            'unvalidated_images': images.filter(is_validated=False).count(),
            'total_training_uses': sum(img.times_used_in_training for img in images),
            'images_by_category': {}
        }
        
        # Group by category
        from objects.models import ObjectCategory
        for category in ObjectCategory.objects.all():
            count = images.filter(object_category=category).count()
            stats['images_by_category'][category.name] = count
        
        return Response(stats)


class TrainingRoundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TrainingRound CRUD operations.
    
    Provides:
    - list: Get all training rounds
    - retrieve: Get single training round
    - create: Start new training round
    - update/partial_update: Update training round
    """
    queryset = TrainingRound.objects.prefetch_related('participants')
    serializer_class = TrainingRoundSerializer
    permission_classes = [IsClientOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['round_number', 'start_time', 'end_time']
    ordering = ['-round_number']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return TrainingRoundListSerializer
        return TrainingRoundSerializer
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start a training round.
        
        POST /api/v1/training/rounds/{id}/start/
        """
        round_obj = self.get_object()
        if round_obj.status != TrainingRound.Status.PENDING:
            return Response(
                {'error': 'Training round is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        round_obj.status = TrainingRound.Status.IN_PROGRESS
        round_obj.start_time = timezone.now()
        round_obj.save()
        
        serializer = self.get_serializer(round_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a training round as complete.
        
        POST /api/v1/training/rounds/{id}/complete/
        Body: {"metrics": {...}}
        """
        round_obj = self.get_object()
        if round_obj.status != TrainingRound.Status.IN_PROGRESS:
            return Response(
                {'error': 'Training round is not in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        round_obj.status = TrainingRound.Status.COMPLETED
        round_obj.end_time = timezone.now()
        round_obj.calculate_duration()
        
        # Update metrics if provided
        metrics = request.data.get('metrics')
        if metrics:
            round_obj.metrics.update(metrics)
        
        round_obj.save()
        
        serializer = self.get_serializer(round_obj)
        return Response(serializer.data)


class ModelVersionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ModelVersion CRUD operations.
    
    Provides:
    - list: Get all model versions
    - retrieve: Get single model version
    - create: Create new model version
    - update/partial_update: Update model version
    """
    queryset = ModelVersion.objects.select_related('training_round')
    serializer_class = ModelVersionSerializer
    permission_classes = [IsClientOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_production']
    ordering_fields = ['version', 'created_at']
    ordering = ['-version']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return ModelVersionListSerializer
        return ModelVersionSerializer
    
    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        """
        Deploy a model version (mark as deployed).
        
        POST /api/v1/models/{id}/deploy/
        """
        from django.utils import timezone
        
        model = self.get_object()
        
        # Undeploy all other models
        ModelVersion.objects.filter(is_production=True).update(is_production=False, deployed_at=None)
        
        # Deploy this model
        model.is_production = True
        model.deployed_at = timezone.now()
        model.save()
        
        serializer = self.get_serializer(model)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def undeploy(self, request, pk=None):
        """
        Undeploy a model version.
        
        POST /api/v1/models/{id}/undeploy/
        """
        model = self.get_object()
        model.is_production = False
        model.deployed_at = None
        model.save()
        
        serializer = self.get_serializer(model)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def deployed(self, request):
        """
        Get currently deployed model.
        
        GET /api/v1/models/deployed/
        """
        deployed_model = self.get_queryset().filter(is_production=True).first()
        if not deployed_model:
            return Response(
                {'error': 'No model is currently deployed'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(deployed_model)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def train(self, request):
        """
        Trigger a new training round.
        
        POST /api/v1/models/train/
        Body: {
            "epochs": 20,
            "batch_size": 32,
            "learning_rate": 0.001,
            "use_existing_model": true  // Fine-tune existing model or train from scratch
        }
        
        Returns: {
            "job_id": "uuid",
            "status": "queued",
            "message": "Training job started"
        }
        """
        import uuid
        from django.db import transaction
        
        # Get parameters
        epochs = request.data.get('epochs', 20)
        batch_size = request.data.get('batch_size', 32)
        learning_rate = request.data.get('learning_rate', 0.001)
        use_existing_model = request.data.get('use_existing_model', True)
        
        # Validate parameters
        if epochs < 1 or epochs > 100:
            return Response(
                {'error': 'epochs must be between 1 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if batch_size < 1 or batch_size > 256:
            return Response(
                {'error': 'batch_size must be between 1 and 256'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if enough labeled images exist
        labeled_count = TrainingImage.objects.filter(
            is_validated=True,
            deleted_at__isnull=True
        ).count()
        
        if labeled_count < 50:
            return Response(
                {
                    'error': f'Not enough labeled images for training. Have {labeled_count}, need at least 50',
                    'labeled_count': labeled_count,
                    'required_count': 50
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create training round
        with transaction.atomic():
            training_round = TrainingRound.objects.create(
                hyperparameters={
                    'epochs': epochs,
                    'batch_size': batch_size,
                    'learning_rate': learning_rate,
                    'use_existing_model': use_existing_model
                },
                status=TrainingRound.Status.PENDING,
                metrics={'total_images': labeled_count}
            )
            
            job_id = str(uuid.uuid4())
            
            # Queue the training job (async)
            from .tasks import run_training_job
            result = run_training_job.delay(training_round.id, job_id)
            
            training_round.metrics['celery_task_id'] = result.id
            training_round.metrics['job_id'] = job_id
            training_round.save()
        
        return Response({
            'job_id': job_id,
            'training_round_id': training_round.id,
            'status': 'queued',
            'message': f'Training job started with {labeled_count} images',
            'parameters': {
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'use_existing_model': use_existing_model
            }
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'], url_path='training-status/(?P<job_id>[^/.]+)')
    def training_status(self, request, job_id=None):
        """
        Check status of a training job.
        
        GET /api/v1/models/training-status/{job_id}/
        
        Returns: {
            "job_id": "uuid",
            "status": "in_progress",
            "progress": 45,
            "metrics": {...},
            "model_version": "1.1.0"
        }
        """
        from celery.result import AsyncResult
        
        # Find training round by job_id
        training_round = TrainingRound.objects.filter(
            metrics__job_id=job_id
        ).first()
        
        if not training_round:
            return Response(
                {'error': 'Training job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get Celery task status if available
        celery_task_id = training_round.metrics.get('celery_task_id')
        celery_status = None
        if celery_task_id:
            task = AsyncResult(celery_task_id)
            celery_status = task.status
        
        # Map training round status
        status_map = {
            TrainingRound.Status.PENDING: 'queued',
            TrainingRound.Status.IN_PROGRESS: 'in_progress',
            TrainingRound.Status.COMPLETED: 'completed',
            TrainingRound.Status.FAILED: 'failed'
        }
        
        response_data = {
            'job_id': job_id,
            'training_round_id': training_round.id,
            'status': status_map.get(training_round.status, 'unknown'),
            'celery_status': celery_status,
            'start_time': training_round.start_time,
            'end_time': training_round.end_time,
            'duration_minutes': training_round.duration_minutes,
            'metrics': training_round.metrics,
            'hyperparameters': training_round.hyperparameters
        }
        
        # Add model version if completed
        if training_round.status == TrainingRound.Status.COMPLETED:
            model_version = training_round.modelversion_set.first()
            if model_version:
                response_data['model_version'] = model_version.version
                response_data['model_version_id'] = model_version.id
                response_data['accuracy'] = model_version.accuracy
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get information about the latest production model.
        
        GET /api/v1/models/latest/
        
        Returns: {
            "version": "1.2.0",
            "model_version_id": 15,
            "accuracy": 96.5,
            "model_size_mb": 8.1,
            "created_at": "2025-11-07T17:30:00Z",
            "download_url": "/api/v1/models/download/1.2.0/",
            "checksum": "sha256:abc123...",
            "classes": ["Bicycle", "Car", "Cat", "Dog", "Person"],
            "requires_update": false
        }
        """
        # Get latest production model
        latest_model = ModelVersion.objects.filter(
            is_production=True
        ).order_by('-version').first()
        
        if not latest_model:
            # Fallback to latest model regardless of production status
            latest_model = ModelVersion.objects.order_by('-version').first()
        
        if not latest_model:
            return Response(
                {'error': 'No models available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate checksum
        import hashlib
        from pathlib import Path
        from django.conf import settings
        
        model_path = Path(settings.BASE_DIR) / latest_model.model_file
        checksum = None
        if model_path.exists():
            sha256_hash = hashlib.sha256()
            with open(model_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            checksum = f"sha256:{sha256_hash.hexdigest()}"
        
        # Get class labels from model metadata
        classes = latest_model.hyperparameters.get('classes', [
            "Bicycle", "Car", "Cat", "Dog", "Person"
        ])
        
        # Check if client needs update (compare with request header)
        client_version = request.headers.get('X-Model-Version', '0.0.0')
        requires_update = self._compare_versions(client_version, latest_model.version) < 0
        
        response_data = {
            'version': latest_model.version,
            'model_version_id': latest_model.id,
            'accuracy': latest_model.accuracy,
            'model_size_mb': round(latest_model.model_size / (1024 * 1024), 2),
            'created_at': latest_model.created_at,
            'download_url': f'/api/v1/models/download/{latest_model.version}/',
            'checksum': checksum,
            'classes': classes,
            'requires_update': requires_update,
            'is_production': latest_model.is_production
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'], url_path='download/(?P<version>[^/.]+)')
    def download_version(self, request, version=None):
        """
        Download a specific model version.
        
        GET /api/v1/models/download/{version}/
        
        Returns: Binary .ptl file
        """
        from django.http import FileResponse
        from pathlib import Path
        from django.conf import settings
        
        # Get model by version
        model = ModelVersion.objects.filter(version=version).first()
        
        if not model:
            return Response(
                {'error': f'Model version {version} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get model file path
        model_path = Path(settings.BASE_DIR) / model.model_file
        
        if not model_path.exists():
            return Response(
                {'error': 'Model file not found on server'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return file
        response = FileResponse(
            open(model_path, 'rb'),
            content_type='application/octet-stream',
            as_attachment=True,
            filename=f'model_{version}.ptl'
        )
        
        response['Content-Length'] = model_path.stat().st_size
        response['X-Model-Version'] = version
        response['X-Model-Accuracy'] = str(model.accuracy)
        response['X-Model-Size-MB'] = str(round(model.model_size / (1024 * 1024), 2))
        
        return response
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two semantic version strings.
        
        Returns:
        - -1 if v1 < v2
        - 0 if v1 == v2
        - 1 if v1 > v2
        """
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_val = v1_parts[i] if i < len(v1_parts) else 0
                v2_val = v2_parts[i] if i < len(v2_parts) else 0
                
                if v1_val < v2_val:
                    return -1
                elif v1_val > v2_val:
                    return 1
            
            return 0
        except:
            return 0
