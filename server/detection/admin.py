from django.contrib import admin
from django.utils.html import format_html
from .models import DetectionResult


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'image_thumbnail',
        'detected_object',
        'confidence_badge',
        'client',
        'model_version',
        'inference_time_ms',
        'feedback_status',
        'created_at'
    ]
    list_filter = ['detected_object', 'is_correct', 'created_at']
    search_fields = ['detected_object__name', 'client__name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Detection Information', {
            'fields': (
                'image',
                'detected_object',
                'confidence',
                'bounding_box'
            )
        }),
        ('Source', {
            'fields': ('client', 'user', 'model_version')
        }),
        ('Performance', {
            'fields': ('inference_time_ms',),
            'classes': ('collapse',)
        }),
        ('Feedback', {
            'fields': ('is_correct', 'feedback_notes')
        }),
        ('Metadata', {
            'fields': ('metadata',),
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
    
    def confidence_badge(self, obj):
        """Display colored confidence badge."""
        if obj.is_high_confidence:
            color = 'green'
        elif obj.is_low_confidence:
            color = 'red'
        else:
            color = 'orange'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{:.1%}</span>',
            color,
            obj.confidence
        )
    confidence_badge.short_description = "Confidence"
    
    def feedback_status(self, obj):
        """Display feedback status."""
        if obj.is_correct is None:
            return format_html('<span style="color: gray;">No feedback</span>')
        elif obj.is_correct:
            return format_html('<span style="color: green;">✓ Correct</span>')
        else:
            return format_html('<span style="color: red;">✗ Incorrect</span>')
    feedback_status.short_description = "Feedback"
