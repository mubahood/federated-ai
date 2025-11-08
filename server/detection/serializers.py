"""
Serializers for the detection app.
"""
from rest_framework import serializers
from .models import DetectionResult


class DetectionResultSerializer(serializers.ModelSerializer):
    """
    Serializer for DetectionResult model.
    """
    detected_object_name = serializers.CharField(
        source='detected_object.name',
        read_only=True,
        allow_null=True
    )
    client_name = serializers.CharField(
        source='client.name',
        read_only=True,
        allow_null=True
    )
    user_username = serializers.CharField(
        source='user.username',
        read_only=True,
        allow_null=True
    )
    model_version_number = serializers.IntegerField(
        source='model_version.version',
        read_only=True,
        allow_null=True
    )
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DetectionResult
        fields = [
            'id',
            'image',
            'image_url',
            'detected_object',
            'detected_object_name',
            'confidence',
            'bounding_box',
            'client',
            'client_name',
            'user',
            'user_username',
            'model_version',
            'model_version_number',
            'inference_time_ms',
            'is_correct',
            'feedback_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]
    
    def get_image_url(self, obj):
        """Get the full URL for the detection image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class DetectionResultListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing detection results.
    """
    detected_object_name = serializers.CharField(
        source='detected_object.name',
        read_only=True,
        allow_null=True
    )
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DetectionResult
        fields = [
            'id',
            'image_url',
            'detected_object',
            'detected_object_name',
            'confidence',
            'is_correct',
            'created_at',
        ]
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class DetectionSubmitSerializer(serializers.ModelSerializer):
    """
    Serializer for submitting new detection results.
    """
    class Meta:
        model = DetectionResult
        fields = [
            'image',
            'detected_object',
            'confidence',
            'bounding_box',
            'client',
            'model_version',
            'inference_time_ms',
        ]
    
    def validate_confidence(self, value):
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Confidence must be between 0.0 and 1.0")
        return value


class DetectionFeedbackSerializer(serializers.Serializer):
    """
    Serializer for submitting feedback on detection results.
    """
    is_correct = serializers.BooleanField(required=True)
    feedback_notes = serializers.CharField(required=False, allow_blank=True)
