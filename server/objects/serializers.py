"""
Serializers for the objects app.
"""
from rest_framework import serializers
from .models import ObjectCategory


class ObjectCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for ObjectCategory model.
    Handles CRUD operations for object categories.
    """
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = ObjectCategory
        fields = [
            'id',
            'name',
            'description',
            'icon',
            'is_active',
            'created_by',
            'created_by_username',
            'training_images_count',
            'detection_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'training_images_count',
            'detection_count',
            'created_at',
            'updated_at',
        ]
    
    def validate_name(self, value):
        """
        Ensure category name is lowercase and alphanumeric.
        """
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")
        
        # Convert to lowercase for consistency
        value = value.strip().lower()
        
        # Check for basic alphanumeric with spaces and hyphens
        if not all(c.isalnum() or c in ' -_' for c in value):
            raise serializers.ValidationError(
                "Category name can only contain letters, numbers, spaces, hyphens, and underscores."
            )
        
        return value


class ObjectCategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing object categories.
    Excludes heavy fields like description and icon.
    """
    class Meta:
        model = ObjectCategory
        fields = [
            'id',
            'name',
            'is_active',
            'training_images_count',
            'detection_count',
        ]


class ObjectCategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for ObjectCategory with all fields and computed data.
    """
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        allow_null=True
    )
    icon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ObjectCategory
        fields = [
            'id',
            'name',
            'description',
            'icon',
            'icon_url',
            'is_active',
            'created_by',
            'created_by_username',
            'training_images_count',
            'detection_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'training_images_count',
            'detection_count',
            'created_at',
            'updated_at',
        ]
    
    def get_icon_url(self, obj):
        """
        Get the full URL for the category icon.
        """
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
