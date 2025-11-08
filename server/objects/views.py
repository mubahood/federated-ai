"""
API views for the objects app.
"""
import json
import os
from pathlib import Path
from django.http import FileResponse, Http404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse

from .models import ObjectCategory
from .serializers import (
    ObjectCategorySerializer,
    ObjectCategoryListSerializer,
    ObjectCategoryDetailSerializer
)
from core.permissions import IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List object categories",
        description="Get a paginated list of all object categories with filtering, search, and ordering capabilities.",
        tags=["Object Categories"],
    ),
    retrieve=extend_schema(
        summary="Get category details",
        description="Retrieve detailed information about a specific object category by ID.",
        tags=["Object Categories"],
    ),
    create=extend_schema(
        summary="Create new category",
        description="Create a new object category. Requires admin permissions.",
        tags=["Object Categories"],
    ),
    update=extend_schema(
        summary="Update category",
        description="Update all fields of an object category. Requires admin permissions.",
        tags=["Object Categories"],
    ),
    partial_update=extend_schema(
        summary="Partially update category",
        description="Update specific fields of an object category. Requires admin permissions.",
        tags=["Object Categories"],
    ),
    destroy=extend_schema(
        summary="Delete category",
        description="Soft delete an object category. Requires admin permissions.",
        tags=["Object Categories"],
    ),
)
class ObjectCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ObjectCategory CRUD operations.
    
    Provides:
    - list: Get all categories (with filtering, search, ordering)
    - retrieve: Get single category by ID
    - create: Create new category
    - update/partial_update: Update category
    - destroy: Soft delete category
    
    Filters:
    - is_active: Filter by active status
    - name: Filter by exact name
    
    Search:
    - Search in name and description fields
    
    Ordering:
    - name, created_at, training_images_count, detection_count
    """
    queryset = ObjectCategory.objects.all()
    serializer_class = ObjectCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'training_images_count', 'detection_count']
    ordering = ['name']  # Default ordering
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'list':
            return ObjectCategoryListSerializer
        elif self.action == 'retrieve':
            return ObjectCategoryDetailSerializer
        return ObjectCategorySerializer
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        """
        Soft delete the category instead of hard delete.
        """
        instance.delete()  # Soft delete by default
    
    @extend_schema(
        summary="Activate category",
        description="Mark a category as active so it can be used for training and detection.",
        tags=["Object Categories"],
        responses={200: ObjectCategorySerializer},
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a category.
        
        POST /api/v1/categories/{id}/activate/
        """
        category = self.get_object()
        category.is_active = True
        category.save()
        serializer = self.get_serializer(category)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Deactivate category",
        description="Mark a category as inactive to prevent it from being used in new training or detection.",
        tags=["Object Categories"],
        responses={200: ObjectCategorySerializer},
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a category.
        
        POST /api/v1/categories/{id}/deactivate/
        """
        category = self.get_object()
        category.is_active = False
        category.save()
        serializer = self.get_serializer(category)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get category statistics",
        description="Retrieve aggregate statistics across all object categories including counts of categories, training images, and detections.",
        tags=["Object Categories"],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_categories': {'type': 'integer'},
                    'active_categories': {'type': 'integer'},
                    'inactive_categories': {'type': 'integer'},
                    'total_training_images': {'type': 'integer'},
                    'total_detections': {'type': 'integer'},
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall statistics for all categories.
        
        GET /api/v1/categories/statistics/
        
        Returns:
        - total_categories: Total number of categories
        - active_categories: Number of active categories
        - total_training_images: Total training images across all categories
        - total_detections: Total detections across all categories
        """
        categories = self.get_queryset()
        
        stats = {
            'total_categories': categories.count(),
            'active_categories': categories.filter(is_active=True).count(),
            'inactive_categories': categories.filter(is_active=False).count(),
            'total_training_images': sum(c.training_images_count for c in categories),
            'total_detections': sum(c.detection_count for c in categories),
            'categories': ObjectCategoryListSerializer(categories, many=True).data
        }
        
        return Response(stats)


# ==================== Model Serving Views ====================

@extend_schema(
    summary="Download mobile model",
    description="Download the PyTorch Mobile model (.ptl) file for Android deployment. Requires authentication.",
    tags=["ML Model"],
    responses={
        200: OpenApiResponse(
            description="Model file (.ptl)",
            response={'type': 'file'}
        ),
        404: OpenApiResponse(description="Model file not found")
    }
)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_model(request):
    """
    Download the trained PyTorch Mobile model file.
    
    GET /api/v1/model/download/
    
    Returns:
    - Binary .ptl model file (application/octet-stream)
    
    The downloaded model can be directly integrated into Android apps
    using PyTorch Mobile library.
    """
    model_path = Path(__file__).parent.parent / 'mobile_models' / 'model.ptl'
    
    if not model_path.exists():
        raise Http404("Model file not found. Please train and convert the model first.")
    
    # Get file size for response headers
    file_size = model_path.stat().st_size
    
    response = FileResponse(
        open(model_path, 'rb'),
        content_type='application/octet-stream',
        as_attachment=True,
        filename='object_detection_model.ptl'
    )
    response['Content-Length'] = file_size
    response['X-Model-Version'] = '1.0.0'
    response['X-Model-Size-MB'] = f"{file_size / (1024 * 1024):.2f}"
    
    return response


@extend_schema(
    summary="Get model metadata",
    description="Get metadata information about the trained model including architecture, performance metrics, preprocessing requirements, and category mappings.",
    tags=["ML Model"],
    responses={
        200: OpenApiResponse(
            description="Model metadata",
            response={
                'type': 'object',
                'properties': {
                    'model_info': {'type': 'object'},
                    'categories': {'type': 'object'},
                    'preprocessing': {'type': 'object'},
                    'performance': {'type': 'object'},
                    'usage': {'type': 'object'},
                }
            }
        ),
        404: OpenApiResponse(description="Metadata file not found")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def model_metadata(request):
    """
    Get model metadata and configuration.
    
    GET /api/v1/model/metadata/
    
    Returns:
    - model_info: Architecture details, accuracy, training info
    - categories: Category index to name mapping
    - preprocessing: Input requirements and normalization
    - performance: Model size, inference time, speedup
    - usage: Integration examples for Android
    - dataset: Training dataset statistics
    
    This endpoint is public and doesn't require authentication.
    """
    metadata_path = Path(__file__).parent.parent / 'mobile_models' / 'model_metadata.json'
    
    if not metadata_path.exists():
        raise Http404("Model metadata not found. Please train and convert the model first.")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return Response(metadata)
