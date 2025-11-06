from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with created and updated timestamps.
    All models should inherit from this.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract model with soft delete functionality.
    Objects are marked as deleted instead of being removed from the database.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager that includes deleted objects

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete by default. Pass hard=True to permanently delete.
        """
        if hard:
            super().delete(using=using, keep_parents=keep_parents)
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
