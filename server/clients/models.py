import uuid
from django.db import models
from django.contrib.auth import get_user_model
from core.models import SoftDeleteModel

User = get_user_model()


class Client(SoftDeleteModel):
    """
    Represents a federated learning client (device).
    Can be a phone, computer, or any device participating in training.
    """
    
    class DeviceType(models.TextChoices):
        MOBILE = 'mobile', 'Mobile Device'
        DESKTOP = 'desktop', 'Desktop Computer'
        LAPTOP = 'laptop', 'Laptop'
        TABLET = 'tablet', 'Tablet'
        SERVER = 'server', 'Server'
        OTHER = 'other', 'Other'
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        TRAINING = 'training', 'Training'
        ERROR = 'error', 'Error'
        BANNED = 'banned', 'Banned'
    
    # Identification
    device_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Unique identifier for the device"
    )
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name for the device"
    )
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.OTHER,
        help_text="Type of device"
    )
    
    # Ownership
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clients',
        null=True,
        blank=True,
        help_text="User who owns this device"
    )
    
    # Status and connectivity
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INACTIVE,
        db_index=True,
        help_text="Current status of the client"
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Last time this client connected"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Last known IP address"
    )
    
    # Capabilities
    capabilities = models.JSONField(
        default=dict,
        help_text="Device capabilities (CPU, GPU, RAM, etc.)"
    )
    
    # Statistics
    total_training_rounds = models.IntegerField(
        default=0,
        help_text="Total number of training rounds participated in"
    )
    total_samples_contributed = models.IntegerField(
        default=0,
        help_text="Total training samples contributed"
    )
    average_training_time = models.FloatField(
        default=0.0,
        help_text="Average time per training round (seconds)"
    )
    
    # Authentication
    api_key = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        help_text="API key for authentication"
    )

    class Meta:
        verbose_name = "Federated Client"
        verbose_name_plural = "Federated Clients"
        ordering = ['-last_seen', 'name']
        indexes = [
            models.Index(fields=['status', 'last_seen']),
            models.Index(fields=['device_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_type})"

    def is_online(self):
        """Check if client is currently online."""
        if not self.last_seen:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.last_seen < timedelta(minutes=5)

    def update_last_seen(self):
        """Update the last_seen timestamp."""
        from django.utils import timezone
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen', 'updated_at'])

    def increment_training_stats(self, samples_count, training_time):
        """Update training statistics."""
        self.total_training_rounds += 1
        self.total_samples_contributed += samples_count
        
        # Update moving average of training time
        if self.average_training_time == 0:
            self.average_training_time = training_time
        else:
            self.average_training_time = (
                (self.average_training_time * (self.total_training_rounds - 1) + training_time)
                / self.total_training_rounds
            )
        
        self.save(update_fields=[
            'total_training_rounds',
            'total_samples_contributed',
            'average_training_time',
            'updated_at'
        ])
