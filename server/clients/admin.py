from django.contrib import admin
from django.utils.html import format_html
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'device_type',
        'status_badge',
        'owner',
        'online_indicator',
        'total_training_rounds',
        'last_seen'
    ]
    list_filter = ['status', 'device_type', 'created_at', 'is_deleted']
    search_fields = ['name', 'device_id', 'ip_address']
    readonly_fields = [
        'device_id',
        'total_training_rounds',
        'total_samples_contributed',
        'average_training_time',
        'created_at',
        'updated_at',
        'deleted_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('device_id', 'name', 'device_type', 'owner')
        }),
        ('Status', {
            'fields': ('status', 'last_seen', 'ip_address')
        }),
        ('Capabilities', {
            'fields': ('capabilities',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'total_training_rounds',
                'total_samples_contributed',
                'average_training_time'
            ),
            'classes': ('collapse',)
        }),
        ('Authentication', {
            'fields': ('api_key',),
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
    
    def status_badge(self, obj):
        """Display colored status badge."""
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'training': 'blue',
            'error': 'red',
            'banned': 'black'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def online_indicator(self, obj):
        """Display online/offline indicator."""
        if obj.is_online():
            return format_html(
                '<span style="color: green;">● Online</span>'
            )
        return format_html(
            '<span style="color: gray;">○ Offline</span>'
        )
    online_indicator.short_description = "Online"
    
    def get_queryset(self, request):
        """Include soft-deleted objects in admin."""
        return self.model.all_objects.get_queryset()
