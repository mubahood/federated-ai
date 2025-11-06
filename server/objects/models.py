from django.db import models
from django.contrib.auth import get_user_model
from core.models import SoftDeleteModel

User = get_user_model()


class ObjectCategory(SoftDeleteModel):
    """
    Represents an object category that can be trained and detected.
    Examples: 'car', 'person', 'dog', 'apple', etc.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Name of the object category (e.g., 'car', 'person')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the object category"
    )
    icon = models.ImageField(
        upload_to='object_icons/',
        null=True,
        blank=True,
        help_text="Icon representing this category"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this category is available for training/detection"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_categories',
        help_text="User who created this category"
    )
    
    # Statistics (updated periodically)
    training_images_count = models.IntegerField(
        default=0,
        help_text="Total number of training images for this category"
    )
    detection_count = models.IntegerField(
        default=0,
        help_text="Total number of detections made"
    )

    class Meta:
        verbose_name = "Object Category"
        verbose_name_plural = "Object Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def increment_training_images(self):
        """Increment training images count."""
        self.training_images_count += 1
        self.save(update_fields=['training_images_count', 'updated_at'])

    def increment_detections(self):
        """Increment detection count."""
        self.detection_count += 1
        self.save(update_fields=['detection_count', 'updated_at'])
