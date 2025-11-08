from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TrainingImage, TrainingRound, ModelVersion, TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'status_badge',
        'model_name',
        'progress',
        'created_by',
        'created_at'
    ]
    list_filter = ['status', 'model_name', 'created_at']
    search_fields = ['name', 'created_by__username']
    readonly_fields = ['current_round', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'model_name', 'status', 'created_by')
        }),
        ('Configuration', {
            'fields': ('num_rounds', 'current_round', 'config'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display colored badge for status."""
        colors = {
            'pending': 'gray',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def progress(self, obj):
        """Display training progress."""
        if obj.num_rounds > 0:
            percentage = (obj.current_round / obj.num_rounds) * 100
            return format_html(
                '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
                '<div style="width: {}%; background-color: #4CAF50; color: white; padding: 2px; text-align: center; border-radius: 3px;">'
                '{}%</div></div>',
                percentage,
                int(percentage)
            )
        return "-"
    progress.short_description = "Progress"


@admin.register(TrainingImage)
class TrainingImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'image_thumbnail',
        'object_category',
        'uploaded_by',
        'is_validated',
        'times_used_in_training',
        'created_at'
    ]
    list_filter = ['object_category', 'is_validated', 'created_at', 'is_deleted']
    search_fields = ['object_category__name', 'uploaded_by__username']
    readonly_fields = [
        'times_used_in_training',
        'created_at',
        'updated_at',
        'deleted_at'
    ]
    fieldsets = (
        ('Image Information', {
            'fields': ('object_category', 'image', 'uploaded_by', 'client')
        }),
        ('Validation', {
            'fields': ('is_validated', 'validation_notes')
        }),
        ('Metadata', {
            'fields': ('metadata', 'times_used_in_training'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_thumbnail(self, obj):
        """Display thumbnail of the image."""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "-"
    image_thumbnail.short_description = "Image"
    
    def get_queryset(self, request):
        """Include soft-deleted objects in admin."""
        return self.model.all_objects.get_queryset()


@admin.register(TrainingRound)
class TrainingRoundAdmin(admin.ModelAdmin):
    list_display = [
        'round_number',
        'status_badge',
        'participant_count',
        'average_accuracy',
        'average_loss',
        'duration_display',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['round_number']
    readonly_fields = [
        'duration_seconds',
        'created_at',
        'updated_at'
    ]
    filter_horizontal = ['participants']
    fieldsets = (
        ('Basic Information', {
            'fields': ('training_session', 'round_number', 'status', 'num_clients')
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_seconds')
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('metrics', 'average_loss', 'average_accuracy')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'pending': 'orange',
            'in_progress': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def participant_count(self, obj):
        """Display number of participants."""
        return obj.participants.count()
    participant_count.short_description = "Participants"
    
    def duration_display(self, obj):
        """Display formatted duration."""
        if obj.duration_seconds:
            minutes = int(obj.duration_seconds // 60)
            seconds = int(obj.duration_seconds % 60)
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = "Duration"


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = [
        'version',
        'production_badge',
        'accuracy',
        'model_size_mb',
        'training_round',
        'created_at'
    ]
    list_filter = ['is_production', 'created_at']
    search_fields = ['version', 'notes']
    readonly_fields = [
        'model_size_mb',
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Version Information', {
            'fields': ('version', 'training_round', 'model_file', 'model_size_mb')
        }),
        ('Performance Metrics', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score')
        }),
        ('Deployment', {
            'fields': ('is_production', 'deployed_at')
        }),
        ('Additional Information', {
            'fields': ('metadata', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def production_badge(self, obj):
        """Display production status badge."""
        if obj.is_production:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">PRODUCTION</span>'
            )
        return format_html(
            '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">DEV</span>'
        )
    production_badge.short_description = "Status"
