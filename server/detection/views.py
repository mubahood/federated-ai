"""
API views for the detection app.
"""
from rest_framework import viewsets, filters, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import DetectionResult
from .serializers import (
    DetectionResultSerializer,
    DetectionResultListSerializer,
    DetectionSubmitSerializer,
    DetectionFeedbackSerializer
)
from core.permissions import IsClientOrAdmin, IsOwnerOrReadOnly


class DetectionResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DetectionResult CRUD operations.
    
    Provides:
    - list: Get all detection results (with filtering, search, ordering)
    - retrieve: Get single detection result by ID
    - create: Submit new detection result
    - update/partial_update: Update detection metadata
    - destroy: Delete detection result
    
    Filters:
    - detected_object: Filter by detected category ID
    - client: Filter by client ID
    - is_correct: Filter by feedback status
    
    Ordering:
    - created_at, confidence
    """
    queryset = DetectionResult.objects.select_related(
        'detected_object', 
        'client', 
        'user', 
        'model_version'
    )
    serializer_class = DetectionResultSerializer
    permission_classes = [IsClientOrAdmin]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['detected_object', 'client', 'is_correct']
    ordering_fields = ['created_at', 'confidence']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return DetectionResultListSerializer
        elif self.action == 'submit':
            return DetectionSubmitSerializer
        return DetectionResultSerializer
    
    def perform_create(self, serializer):
        """Set the user field to the current user."""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """
        Submit feedback on a detection result.
        
        POST /api/v1/detection/results/{id}/feedback/
        Body: {
            "is_correct": true,
            "feedback_notes": "Perfect detection!"
        }
        """
        detection = self.get_object()
        serializer = DetectionFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        detection.is_correct = serializer.validated_data['is_correct']
        detection.feedback_notes = serializer.validated_data.get('feedback_notes', '')
        detection.save()
        
        result_serializer = self.get_serializer(detection)
        return Response(result_serializer.data)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """
        Submit a new detection result.
        
        POST /api/v1/detection/results/submit/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if request.user.is_authenticated:
            detection = serializer.save(user=request.user)
        else:
            detection = serializer.save()
        
        result_serializer = DetectionResultSerializer(detection, context={'request': request})
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get detection statistics.
        
        GET /api/v1/detection/results/statistics/
        """
        detections = self.get_queryset()
        
        # Calculate statistics
        total = detections.count()
        with_feedback = detections.exclude(is_correct__isnull=True).count()
        correct = detections.filter(is_correct=True).count()
        incorrect = detections.filter(is_correct=False).count()
        
        accuracy = (correct / with_feedback * 100) if with_feedback > 0 else 0
        
        # Average confidence
        avg_confidence = 0
        if total > 0:
            total_confidence = sum(d.confidence for d in detections)
            avg_confidence = total_confidence / total
        
        # Average inference time
        detections_with_time = detections.exclude(inference_time_ms__isnull=True)
        avg_inference_time = 0
        if detections_with_time.exists():
            total_time = sum(d.inference_time_ms for d in detections_with_time)
            avg_inference_time = total_time / detections_with_time.count()
        
        # Detections by category
        from objects.models import ObjectCategory
        detections_by_category = {}
        for category in ObjectCategory.objects.all():
            count = detections.filter(detected_object=category).count()
            detections_by_category[category.name] = count
        
        stats = {
            'total_detections': total,
            'detections_with_feedback': with_feedback,
            'correct_detections': correct,
            'incorrect_detections': incorrect,
            'accuracy_percentage': round(accuracy, 2),
            'average_confidence': round(avg_confidence, 4),
            'average_inference_time_ms': round(avg_inference_time, 2),
            'detections_by_category': detections_by_category
        }
        
        return Response(stats)
