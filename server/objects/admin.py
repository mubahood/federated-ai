from django.contrib import admin
from django.utils.html import format_html
from .models import ObjectCategory


@admin.register(ObjectCategory)
class ObjectCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'icon_thumbnail',
        'is_active',
        'training_images_count',
        'detection_count',
        'created_by',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'is_deleted']
    search_fields = ['name', 'description']
    readonly_fields = [
        'training_images_count',
        'detection_count',
        'created_at',
        'updated_at',
        'deleted_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon', 'is_active', 'created_by')
        }),
        ('Statistics', {
            'fields': ('training_images_count', 'detection_count'),
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
    
    def icon_thumbnail(self, obj):
        """Display thumbnail of the icon."""
        if obj.icon:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.icon.url
            )
        return "-"
    icon_thumbnail.short_description = "Icon"
    
    def get_queryset(self, request):
        """Include soft-deleted objects in admin."""
        return self.model.all_objects.get_queryset()
