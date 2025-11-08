from django.contrib import admin
from django.urls import reverse

# Core models are abstract, so nothing to register here.
# This file is kept for potential future use.

# Customize the default admin site
admin.site.site_header = 'Federated AI Control Center'
admin.site.site_title = 'Federated AI Admin'
admin.site.index_title = 'System Overview'

# Store original index method
_original_index = admin.site.index

def custom_index(request, extra_context=None):
    """
    Override the default admin index to redirect to our custom dashboard.
    """
    from django.shortcuts import redirect
    return redirect('admin_dashboard')

# Replace the index method
admin.site.index = custom_index
