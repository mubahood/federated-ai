from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimeStampedModel

User = get_user_model()


class DetectionResult(TimeStampedModel):
    """
    Represents a single object detection result.
    """
    # Image being analyzed
    image = models.ImageField(
        upload_to='detections/%Y/%m/%d/',
        help_text="Image that was analyzed"
    )
    
    # Detection results
    detected_object = models.ForeignKey(
        'objects.ObjectCategory',
        on_delete=models.CASCADE,
        related_name='detections',
        null=True,
        blank=True,
        help_text="Detected object category (null if no detection)"
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score (0.0 to 1.0)"
    )
    
    # Bounding box (normalized coordinates 0-1)
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box coordinates {x, y, width, height}"
    )
    
    # Source
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detections',
        help_text="Client that performed the detection"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detections',
        help_text="User who initiated the detection"
    )
    
    # Model used
    model_version = models.ForeignKey(
        'training.ModelVersion',
        on_delete=models.SET_NULL,
        null=True,
        related_name='detections',
        help_text="Model version used for detection"
    )
    
    # Timing
    inference_time_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Inference time in milliseconds"
    )
    
    # Feedback
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="User feedback on detection accuracy"
    )
    feedback_notes = models.TextField(
        blank=True,
        help_text="User feedback or notes"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional detection metadata"
    )

    class Meta:
        verbose_name = "Detection Result"
        verbose_name_plural = "Detection Results"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['detected_object', 'confidence']),
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        if self.detected_object:
            return f"{self.detected_object.name} ({self.confidence:.2f}) - {self.created_at}"
        return f"No detection - {self.created_at}"

    @property
    def is_high_confidence(self):
        """Check if detection has high confidence (>0.7)."""
        return self.confidence > 0.7

    @property
    def is_low_confidence(self):
        """Check if detection has low confidence (<0.5)."""
        return self.confidence < 0.5
