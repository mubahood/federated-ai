"""
Serializers for the clients app.
"""
import secrets
from rest_framework import serializers
from django.utils import timezone
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client model.
    Handles registration and management of federated learning clients.
    """
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True,
        allow_null=True
    )
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'owner',
            'owner_username',
            'status',
            'last_seen',
            'ip_address',
            'capabilities',
            'total_training_rounds',
            'total_samples_contributed',
            'average_training_time',
            'is_online',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'device_id',
            'owner',
            'last_seen',
            'total_training_rounds',
            'total_samples_contributed',
            'average_training_time',
            'created_at',
            'updated_at',
        ]
    
    def get_is_online(self, obj):
        """Check if client is currently online."""
        return obj.is_online()
    
    def create(self, validated_data):
        """
        Create a new client and generate API key.
        """
        # Generate API key
        validated_data['api_key'] = secrets.token_urlsafe(32)
        return super().create(validated_data)


class ClientListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing clients.
    """
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'status',
            'last_seen',
            'is_online',
            'total_training_rounds',
        ]
    
    def get_is_online(self, obj):
        return obj.is_online()


class ClientDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Client with all information.
    """
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True,
        allow_null=True
    )
    is_online = serializers.SerializerMethodField()
    api_key = serializers.CharField(read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'owner',
            'owner_username',
            'status',
            'last_seen',
            'ip_address',
            'capabilities',
            'total_training_rounds',
            'total_samples_contributed',
            'average_training_time',
            'api_key',
            'is_online',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'device_id',
            'owner',
            'api_key',
            'last_seen',
            'total_training_rounds',
            'total_samples_contributed',
            'average_training_time',
            'created_at',
            'updated_at',
        ]
    
    def get_is_online(self, obj):
        return obj.is_online()


class ClientRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for new client registration.
    Returns API key on successful registration.
    """
    api_key = serializers.CharField(read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'capabilities',
            'api_key',
        ]
        read_only_fields = ['id', 'device_id', 'api_key']
    
    def create(self, validated_data):
        """
        Create a new client with generated API key.
        """
        validated_data['api_key'] = secrets.token_urlsafe(32)
        validated_data['status'] = Client.Status.ACTIVE
        validated_data['last_seen'] = timezone.now()
        return super().create(validated_data)
