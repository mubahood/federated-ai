"""
Custom permission classes for the Federated AI API.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed to any request.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        # Check for different owner field names
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If no owner field, allow staff/admin only
        return request.user and request.user.is_staff


class IsClientOrAdmin(permissions.BasePermission):
    """
    Permission that allows:
    - Admins: Full access
    - Authenticated clients: Limited access to their own data
    - Unauthenticated: No access
    """
    
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
        
        # Authenticated users can access
        if request.user and request.user.is_authenticated:
            return True
        
        # Check if client has valid API key in header
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            from clients.models import Client
            try:
                client = Client.objects.get(api_key=api_key)
                # Attach client to request for later use
                request.client = client
                return True
            except Client.DoesNotExist:
                pass
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
        
        # Check if object belongs to the requesting client
        if hasattr(request, 'client') and hasattr(obj, 'client'):
            return obj.client == request.client
        
        # Check if object belongs to the requesting user
        if request.user and request.user.is_authenticated:
            if hasattr(obj, 'owner'):
                return obj.owner == request.user
            elif hasattr(obj, 'uploaded_by'):
                return obj.uploaded_by == request.user
            elif hasattr(obj, 'created_by'):
                return obj.created_by == request.user
            elif hasattr(obj, 'user'):
                return obj.user == request.user
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows:
    - Admins: Full access
    - Others: Read-only access
    """
    
    def has_permission(self, request, view):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins
        return request.user and request.user.is_staff


class IsValidatedOrAdmin(permissions.BasePermission):
    """
    Permission that only allows validated objects to be accessed,
    unless user is admin.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users can see everything
        if request.user and request.user.is_staff:
            return True
        
        # Others can only see validated objects
        if hasattr(obj, 'is_validated'):
            return obj.is_validated
        
        return True


class CanUploadImages(permissions.BasePermission):
    """
    Permission that allows image uploads for authenticated users and valid clients.
    """
    
    def has_permission(self, request, view):
        # Admin users can always upload
        if request.user and request.user.is_staff:
            return True
        
        # Authenticated users can upload
        if request.user and request.user.is_authenticated:
            return True
        
        # Check for valid API key
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            from clients.models import Client
            try:
                client = Client.objects.get(api_key=api_key, status=Client.Status.ACTIVE)
                request.client = client
                return True
            except Client.DoesNotExist:
                pass
        
        return False
