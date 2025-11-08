"""
Serializers for the training app.
"""
from rest_framework import serializers
from .models import TrainingImage, TrainingRound, ModelVersion


class TrainingImageSerializer(serializers.ModelSerializer):
    """
    Serializer for TrainingImage model.
    Handles image uploads and metadata.
    """
    object_category_name = serializers.CharField(
        source='object_category.name',
        read_only=True
    )
    uploaded_by_username = serializers.CharField(
        source='uploaded_by.username',
        read_only=True,
        allow_null=True
    )
    client_name = serializers.CharField(
        source='client.name',
        read_only=True,
        allow_null=True
    )
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingImage
        fields = [
            'id',
            'object_category',
            'object_category_name',
            'image',
            'image_url',
            'uploaded_by',
            'uploaded_by_username',
            'client',
            'client_name',
            'metadata',
            'is_validated',
            'validation_notes',
            'times_used_in_training',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'uploaded_by',
            'times_used_in_training',
            'created_at',
            'updated_at',
        ]
    
    def get_image_url(self, obj):
        """Get the full URL for the image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def create(self, validated_data):
        """
        Create training image and extract metadata.
        """
        image = validated_data.get('image')
        if image:
            # Extract image metadata
            metadata = validated_data.get('metadata', {})
            metadata.update({
                'filename': image.name,
                'size': image.size,
                'content_type': image.content_type,
            })
            validated_data['metadata'] = metadata
        
        return super().create(validated_data)


class TrainingImageListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing training images.
    """
    object_category_name = serializers.CharField(
        source='object_category.name',
        read_only=True
    )
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingImage
        fields = [
            'id',
            'object_category',
            'object_category_name',
            'image_url',
            'is_validated',
            'times_used_in_training',
            'created_at',
        ]
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class TrainingImageUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for bulk image upload.
    """
    class Meta:
        model = TrainingImage
        fields = [
            'object_category',
            'image',
            'client',
            'metadata',
        ]
    
    def create(self, validated_data):
        """
        Create training image with metadata extraction.
        """
        image = validated_data.get('image')
        if image:
            metadata = validated_data.get('metadata', {})
            metadata.update({
                'filename': image.name,
                'size': image.size,
                'content_type': image.content_type,
            })
            validated_data['metadata'] = metadata
        
        return super().create(validated_data)


class TrainingRoundSerializer(serializers.ModelSerializer):
    """
    Serializer for TrainingRound model.
    """
    participants_count = serializers.IntegerField(
        source='participants.count',
        read_only=True
    )
    # Use PKs only to avoid circular references in schema generation
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = TrainingRound
        fields = [
            'id',
            'round_number',
            'status',
            'participants',
            'participants_count',
            'min_clients',
            'start_time',
            'end_time',
            'duration_seconds',
            'config',
            'metrics',
            'average_loss',
            'average_accuracy',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'round_number',
            'duration_seconds',
            'created_at',
            'updated_at',
        ]


class TrainingRoundListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing training rounds.
    """
    participants_count = serializers.IntegerField(
        source='participants.count',
        read_only=True
    )
    
    class Meta:
        model = TrainingRound
        fields = [
            'id',
            'round_number',
            'status',
            'participants_count',
            'start_time',
            'end_time',
            'duration_seconds',
        ]


class ModelVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for ModelVersion model.
    """
    training_round_number = serializers.IntegerField(
        source='training_round.round_number',
        read_only=True,
        allow_null=True
    )
    model_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ModelVersion
        fields = [
            'id',
            'version',
            'training_round',
            'training_round_number',
            'model_file',
            'model_file_url',
            'model_size_mb',
            'accuracy',
            'precision',
            'recall',
            'f1_score',
            'is_production',
            'deployed_at',
            'metadata',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'version',
            'created_at',
            'updated_at',
        ]
    
    def get_model_file_url(self, obj):
        """Get the full URL for the model file."""
        if obj.model_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.model_file.url)
            return obj.model_file.url
        return None


class ModelVersionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing model versions.
    """
    class Meta:
        model = ModelVersion
        fields = [
            'id',
            'version',
            'is_production',
            'deployed_at',
            'accuracy',
            'f1_score',
            'created_at',
        ]
