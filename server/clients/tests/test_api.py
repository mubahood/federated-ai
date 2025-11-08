"""
API tests for Client endpoints.
"""
import secrets
import pytest
from django.urls import reverse
from rest_framework import status
from clients.models import Client


@pytest.mark.django_db
class TestClientAPI:
    """Test suite for Client API endpoints."""
    
    def test_list_clients_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list clients."""
        Client.objects.create(
            name='Test Client 1',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        url = reverse('client-list')
        response = api_client.get(url)
        
        # Should require authentication
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_clients_authenticated(self, auth_client):
        """Test listing clients with authentication."""
        Client.objects.create(
            name='Client 1',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='Client 2',
            device_type='desktop',
            api_key=secrets.token_urlsafe(32)
        )
        
        url = reverse('client-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_retrieve_client(self, admin_client):
        """Test retrieving a single client with admin access."""
        client = Client.objects.create(
            name='My Device',
            device_type='laptop',
            api_key=secrets.token_urlsafe(32),
            status='active'
        )
        
        url = reverse('client-detail', kwargs={'pk': client.id})
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'My Device'
        assert response.data['device_type'] == 'laptop'
        assert response.data['status'] == 'active'
    
    def test_create_client_authenticated(self, auth_client):
        """Test creating a client with authentication."""
        url = reverse('client-list')
        data = {
            'name': 'New Device',
            'device_type': 'mobile',
            'api_key': secrets.token_urlsafe(32)
        }
        
        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Device'
        
        # Verify it was created in database
        assert Client.objects.filter(name='New Device').exists()
    
    def test_create_client_auto_generate_api_key(self, auth_client):
        """Test creating a client with auto-generated API key."""
        url = reverse('client-list')
        data = {
            'name': 'Client 2',
            'device_type': 'desktop'
            # Don't provide api_key, let it auto-generate
        }
        
        response = auth_client.post(url, data, format='json')
        
        # Should succeed
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Client 2'
        
        # Verify API key was generated in database
        client = Client.objects.get(name='Client 2')
        assert client.api_key is not None
        assert len(client.api_key) > 0
    
    def test_update_client(self, admin_client):
        """Test updating a client with admin access."""
        client = Client.objects.create(
            name='Old Name',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        url = reverse('client-detail', kwargs={'pk': client.id})
        data = {
            'name': 'New Name',
            'device_type': 'desktop',
            'api_key': client.api_key
        }
        
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'New Name'
        assert response.data['device_type'] == 'desktop'
        
        # Verify database was updated
        client.refresh_from_db()
        assert client.name == 'New Name'
    
    def test_partial_update_client(self, admin_client):
        """Test partially updating a client with admin access."""
        client = Client.objects.create(
            name='Original Name',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32),
            status='inactive'
        )
        
        url = reverse('client-detail', kwargs={'pk': client.id})
        data = {'status': 'active'}
        
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'active'
        assert response.data['name'] == 'Original Name'  # Name unchanged
    
    def test_delete_client(self, admin_client):
        """Test deleting a client (soft delete) with admin access."""
        client = Client.objects.create(
            name='To Delete',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        client_id = client.id
        
        url = reverse('client-detail', kwargs={'pk': client_id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Should not be in default queryset
        assert not Client.objects.filter(id=client_id).exists()
        
        # Should be soft deleted
        assert Client.all_objects.filter(id=client_id).exists()
    
    def test_heartbeat_action(self, admin_client):
        """Test heartbeat custom action with admin access."""
        client = Client.objects.create(
            name='Test Client',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        assert client.last_seen is None
        
        url = reverse('client-heartbeat', kwargs={'pk': client.id})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        client.refresh_from_db()
        assert client.last_seen is not None
        assert client.status == 'active'
    
    def test_start_training_action(self, admin_client):
        """Test start_training custom action with admin access."""
        client = Client.objects.create(
            name='Test Client',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32),
            status='active'
        )
        
        url = reverse('client-start-training', kwargs={'pk': client.id})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        client.refresh_from_db()
        assert client.status == 'training'
    
    def test_finish_training_action(self, admin_client):
        """Test finish_training custom action with admin access."""
        client = Client.objects.create(
            name='Test Client',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32),
            status='training'
        )
        
        url = reverse('client-finish-training', kwargs={'pk': client.id})
        data = {
            'training_time': 120.5,
            'samples_count': 100
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        client.refresh_from_db()
        assert client.status == 'active'
        assert client.total_training_rounds >= 1
    
    def test_filter_by_status(self, auth_client):
        """Test filtering clients by status."""
        Client.objects.create(
            name='Active 1',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32),
            status='active'
        )
        Client.objects.create(
            name='Active 2',
            device_type='desktop',
            api_key=secrets.token_urlsafe(32),
            status='active'
        )
        Client.objects.create(
            name='Inactive',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32),
            status='inactive'
        )
        
        url = reverse('client-list')
        response = auth_client.get(url, {'status': 'active'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_filter_by_device_type(self, auth_client):
        """Test filtering clients by device type."""
        Client.objects.create(
            name='Mobile 1',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='Mobile 2',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='Desktop',
            device_type='desktop',
            api_key=secrets.token_urlsafe(32)
        )
        
        url = reverse('client-list')
        response = auth_client.get(url, {'device_type': 'mobile'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_search_by_name(self, auth_client):
        """Test searching clients by name."""
        Client.objects.create(
            name='iPhone 15',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='iPhone 14',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='Samsung',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        url = reverse('client-list')
        response = auth_client.get(url, {'search': 'iPhone'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_ordering(self, auth_client):
        """Test ordering clients."""
        Client.objects.create(
            name='Zebra',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='Apple',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        Client.objects.create(
            name='Microsoft',
            device_type='mobile',
            api_key=secrets.token_urlsafe(32)
        )
        
        url = reverse('client-list')
        response = auth_client.get(url, {'ordering': 'name'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['name'] == 'Apple'
        assert results[1]['name'] == 'Microsoft'
        assert results[2]['name'] == 'Zebra'
    
    def test_pagination(self, auth_client):
        """Test pagination of client list."""
        # Create more than one page of clients
        for i in range(25):
            Client.objects.create(
                name=f'Client {i:02d}',
                device_type='mobile',
                api_key=secrets.token_urlsafe(32)
            )
        
        url = reverse('client-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # Default page size
        assert 'next' in response.data
        assert response.data['next'] is not None
