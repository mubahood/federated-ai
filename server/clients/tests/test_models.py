"""
Unit tests for Client model.
"""
import uuid
import secrets
import pytest
from django.utils import timezone
from datetime import timedelta
from clients.models import Client


@pytest.mark.django_db
class TestClientModel:
    """Test suite for Client model."""
    
    def test_create_client(self):
        """Test basic client creation with all fields."""
        api_key = secrets.token_urlsafe(32)
        client = Client.objects.create(
            name='iPhone 15 Pro',
            device_type='mobile',
            api_key=api_key,
            status='active'
        )
        
        assert client.id is not None
        assert isinstance(client.device_id, uuid.UUID)
        assert client.name == 'iPhone 15 Pro'
        assert client.device_type == 'mobile'
        assert client.api_key == api_key
        assert client.status == 'active'
        assert client.total_training_rounds == 0
        assert client.total_samples_contributed == 0
        assert client.average_training_time == 0.0
    
    def test_client_string_representation(self):
        """Test __str__ method."""
        client = Client.objects.create(
            name='Test Device',
            device_type='desktop',
            api_key=secrets.token_urlsafe(32)
        )
        
        assert str(client) == 'Test Device (desktop)'
    
    def test_api_key_unique(self):
        """Test that API keys must be unique."""
        api_key = secrets.token_urlsafe(32)
        
        Client.objects.create(
            name='Client 1',
            device_type='mobile',
            api_key=api_key
        )
        
        # Attempting to create another client with same API key should fail
        with pytest.raises(Exception):  # Django will raise IntegrityError
            Client.objects.create(
                name='Client 2',
                device_type='mobile',
                api_key=api_key
            )
    
    def test_update_last_seen(self):
        """Test update_last_seen method."""
        client = Client.objects.create(
            name='Test Client',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        # Initially last_seen is None
        assert client.last_seen is None
        
        # Update and verify it's now set
        client.update_last_seen()
        assert client.last_seen is not None
        
        # Update again and verify it changed
        old_last_seen = client.last_seen
        client.update_last_seen()
        assert client.last_seen >= old_last_seen
    
    def test_device_type_choices(self):
        """Test all device type choices."""
        device_types = ['mobile', 'desktop', 'laptop', 'tablet', 'server', 'other']
        
        for device_type in device_types:
            client = Client.objects.create(
                name=f'{device_type} Device',
                device_type=device_type,
                api_key=secrets.token_urlsafe(32)
            )
            assert client.device_type == device_type
    
    def test_status_field(self):
        """Test status field and choices."""
        client = Client.objects.create(
            name='Test Device',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32),
            status='active'
        )
        
        assert client.status == 'active'
        
        client.status = 'inactive'
        client.save()
        client.refresh_from_db()
        
        assert client.status == 'inactive'
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        client = Client.objects.create(
            name='Delete Me',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        client_id = client.device_id
        
        # Soft delete
        client.delete()
        
        # Should not be in default queryset
        assert not Client.objects.filter(device_id=client_id).exists()
        
        # Should be in all_objects queryset with is_deleted=True
        deleted_client = Client.all_objects.get(device_id=client_id)
        assert deleted_client.is_deleted is True
        assert deleted_client.deleted_at is not None
    
    def test_device_id_is_uuid(self):
        """Test that device_id is a UUID."""
        client = Client.objects.create(
            name='UUID Test',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        assert isinstance(client.device_id, uuid.UUID)
        # device_id is unique but not the primary key
        assert client.device_id is not None
        assert client.id is not None
    
    def test_increment_training_stats(self):
        """Test increment_training_stats method."""
        client = Client.objects.create(
            name='Training Client',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        assert client.total_training_rounds == 0
        assert client.total_samples_contributed == 0
        assert client.average_training_time == 0.0
        
        # Increment stats
        client.increment_training_stats(samples_count=100, training_time=5.5)
        
        assert client.total_training_rounds == 1
        assert client.total_samples_contributed == 100
        assert client.average_training_time == 5.5
        
        # Increment again - average should be calculated
        client.increment_training_stats(samples_count=50, training_time=3.2)
        
        assert client.total_training_rounds == 2
        assert client.total_samples_contributed == 150
        # Average of 5.5 and 3.2 is 4.35
        assert abs(client.average_training_time - 4.35) < 0.01
    
    def test_is_online(self):
        """Test is_online method."""
        client = Client.objects.create(
            name='Online Test',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        # Newly created client should be considered offline (no last_seen)
        assert not client.is_online()
        
        # Update last_seen to now
        client.update_last_seen()
        assert client.is_online()
        
        # Set last_seen to 10 minutes ago (beyond 5 minute threshold)
        client.last_seen = timezone.now() - timedelta(minutes=10)
        client.save()
        assert not client.is_online()
    
    def test_capabilities_json_field(self):
        """Test capabilities JSON field."""
        capabilities = {
            'cpu': 'Apple M2',
            'ram': '16GB',
            'gpu': 'Integrated',
            'os': 'macOS 14',
            'python_version': '3.11'
        }
        
        client = Client.objects.create(
            name='Capable Device',
            device_type='desktop',
            api_key=secrets.token_urlsafe(32),
            capabilities=capabilities
        )
        
        client.refresh_from_db()
        assert client.capabilities == capabilities
        assert client.capabilities['cpu'] == 'Apple M2'
        assert client.capabilities['ram'] == '16GB'
