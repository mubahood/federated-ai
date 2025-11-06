from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import SoftDeleteModel, TimeStampedModel

User = get_user_model()


class TrainingImage(SoftDeleteModel):
    """
    Individual training image uploaded by users.
    """
    object_category = models.ForeignKey(
        'objects.ObjectCategory',
        on_delete=models.CASCADE,
        related_name='training_images',
        help_text="Category this image belongs to"
    )
    image = models.ImageField(
        upload_to='training_images/%Y/%m/%d/',
        help_text="Training image file"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_images',
        help_text="User who uploaded this image"
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_images',
        help_text="Client device that uploaded this image"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (dimensions, format, etc.)"
    )
    
    # Validation status
    is_validated = models.BooleanField(
        default=False,
        help_text="Whether this image has been validated"
    )
    validation_notes = models.TextField(
        blank=True,
        help_text="Notes from validation process"
    )
    
    # Usage tracking
    times_used_in_training = models.IntegerField(
        default=0,
        help_text="Number of times used in training rounds"
    )

    class Meta:
        verbose_name = "Training Image"
        verbose_name_plural = "Training Images"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['object_category', 'is_validated']),
            models.Index(fields=['uploaded_by', 'created_at']),
        ]

    def __str__(self):
        return f"{self.object_category.name} - {self.id}"


class TrainingRound(TimeStampedModel):
    """
    Represents a single federated learning training round.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    round_number = models.IntegerField(
        unique=True,
        db_index=True,
        help_text="Sequential round number"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Current status of the training round"
    )
    
    # Participants
    participants = models.ManyToManyField(
        'clients.Client',
        related_name='training_rounds',
        help_text="Clients participating in this round"
    )
    min_clients = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)],
        help_text="Minimum number of clients required"
    )
    
    # Timing
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When training started"
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When training completed"
    )
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Total duration in seconds"
    )
    
    # Configuration
    config = models.JSONField(
        default=dict,
        help_text="Training configuration (learning rate, epochs, etc.)"
    )
    
    # Metrics
    metrics = models.JSONField(
        default=dict,
        help_text="Aggregated metrics from all clients"
    )
    average_loss = models.FloatField(
        null=True,
        blank=True,
        help_text="Average loss across all clients"
    )
    average_accuracy = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Average accuracy across all clients"
    )
    
    # Results
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or observations"
    )

    class Meta:
        verbose_name = "Training Round"
        verbose_name_plural = "Training Rounds"
        ordering = ['-round_number']
        indexes = [
            models.Index(fields=['status', 'round_number']),
        ]

    def __str__(self):
        return f"Round {self.round_number} - {self.status}"

    def calculate_duration(self):
        """Calculate and save the duration."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = delta.total_seconds()
            self.save(update_fields=['duration_seconds', 'updated_at'])


class ModelVersion(TimeStampedModel):
    """
    Represents a version of the trained model.
    """
    version = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Version string (e.g., '1.0.0', 'v2-20231106')"
    )
    training_round = models.OneToOneField(
        TrainingRound,
        on_delete=models.CASCADE,
        related_name='model_version',
        help_text="Training round that produced this model"
    )
    
    # Model file
    model_file = models.FileField(
        upload_to='models/%Y/%m/',
        help_text="Trained model file"
    )
    model_size_mb = models.FloatField(
        null=True,
        blank=True,
        help_text="Model file size in MB"
    )
    
    # Performance metrics
    accuracy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Model accuracy on validation set"
    )
    precision = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Model precision"
    )
    recall = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Model recall"
    )
    f1_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="F1 score"
    )
    
    # Deployment
    is_production = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this is the production model"
    )
    deployed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this model was deployed to production"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional model metadata"
    )
    notes = models.TextField(
        blank=True,
        help_text="Release notes or description"
    )

    class Meta:
        verbose_name = "Model Version"
        verbose_name_plural = "Model Versions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_production', '-created_at']),
        ]

    def __str__(self):
        return f"Model {self.version} ({'Production' if self.is_production else 'Development'})"

    def save(self, *args, **kwargs):
        # Calculate model size if not set
        if self.model_file and not self.model_size_mb:
            self.model_size_mb = self.model_file.size / (1024 * 1024)
        super().save(*args, **kwargs)
