"""
API tests for ObjectCategory endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from objects.models import ObjectCategory


@pytest.mark.django_db
class TestObjectCategoryAPI:
    """Test suite for ObjectCategory API endpoints."""
    
    def test_list_categories_unauthenticated(self, api_client):
        """Test listing categories without authentication."""
        ObjectCategory.objects.create(name='Car')
        ObjectCategory.objects.create(name='Dog')
        
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_list_categories_authenticated(self, auth_client):
        """Test listing categories with authentication."""
        ObjectCategory.objects.create(name='Cat')
        ObjectCategory.objects.create(name='Person')
        
        url = reverse('category-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_retrieve_category(self, api_client):
        """Test retrieving a single category."""
        category = ObjectCategory.objects.create(
            name='Bicycle',
            description='Two-wheeled vehicles'
        )
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Bicycle'
        assert response.data['description'] == 'Two-wheeled vehicles'
    
    def test_create_category_authenticated(self, admin_client):
        """Test creating a category with admin authentication."""
        url = reverse('category-list')
        data = {
            'name': 'Truck',
            'description': 'Large vehicles'
        }
        
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        # Name is slugified/lowercased
        assert response.data['name'].lower() == 'truck'
        
        # Verify it was created in database
        assert ObjectCategory.objects.filter(name__iexact='Truck').exists()
    
    def test_create_category_duplicate_name(self, admin_client):
        """Test creating a category with duplicate name fails."""
        ObjectCategory.objects.create(name='Car')
        
        url = reverse('category-list')
        data = {'name': 'Car', 'description': 'Another car'}
        
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_category(self, admin_client):
        """Test updating a category with admin authentication."""
        category = ObjectCategory.objects.create(
            name='Dog',
            description='Old description'
        )
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {
            'name': 'Dog',
            'description': 'Updated description'
        }
        
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Updated description'
        
        # Verify database was updated
        category.refresh_from_db()
        assert category.description == 'Updated description'
    
    def test_partial_update_category(self, admin_client):
        """Test partially updating a category with admin authentication."""
        category = ObjectCategory.objects.create(
            name='Cat',
            description='Original'
        )
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'description': 'Patched description'}
        
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Patched description'
        assert response.data['name'] == 'Cat'  # Name should remain unchanged
    
    def test_delete_category(self, admin_client):
        """Test deleting a category (soft delete) with admin authentication."""
        category = ObjectCategory.objects.create(name='Airplane')
        category_id = category.id
        
        url = reverse('category-detail', kwargs={'pk': category_id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Should not be in default queryset
        assert not ObjectCategory.objects.filter(id=category_id).exists()
        
        # Should be soft deleted
        assert ObjectCategory.all_objects.filter(id=category_id).exists()
    
    def test_activate_category(self, admin_client):
        """Test activating a deactivated category with admin authentication."""
        category = ObjectCategory.objects.create(
            name='Train',
            is_active=False
        )
        
        url = reverse('category-activate', kwargs={'pk': category.id})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        category.refresh_from_db()
        assert category.is_active is True
    
    def test_deactivate_category(self, admin_client):
        """Test deactivating an active category with admin authentication."""
        category = ObjectCategory.objects.create(
            name='Boat',
            is_active=True
        )
        
        url = reverse('category-deactivate', kwargs={'pk': category.id})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        category.refresh_from_db()
        assert category.is_active is False
    
    def test_filter_by_active(self, api_client):
        """Test filtering categories by is_active."""
        ObjectCategory.objects.create(name='Active1', is_active=True)
        ObjectCategory.objects.create(name='Active2', is_active=True)
        ObjectCategory.objects.create(name='Inactive', is_active=False)
        
        url = reverse('category-list')
        response = api_client.get(url, {'is_active': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_search_by_name(self, api_client):
        """Test searching categories by name."""
        ObjectCategory.objects.create(name='Car')
        ObjectCategory.objects.create(name='Cargo Ship')
        ObjectCategory.objects.create(name='Dog')
        
        url = reverse('category-list')
        response = api_client.get(url, {'search': 'car'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Car and Cargo Ship
    
    def test_ordering_by_name(self, api_client):
        """Test ordering categories by name."""
        ObjectCategory.objects.create(name='Zebra')
        ObjectCategory.objects.create(name='Apple')
        ObjectCategory.objects.create(name='Monkey')
        
        url = reverse('category-list')
        response = api_client.get(url, {'ordering': 'name'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['name'] == 'Apple'
        assert results[1]['name'] == 'Monkey'
        assert results[2]['name'] == 'Zebra'
    
    def test_pagination(self, api_client):
        """Test pagination of category list."""
        # Create more than one page of categories (page size is 20)
        for i in range(25):
            ObjectCategory.objects.create(name=f'Category {i:02d}')
        
        url = reverse('category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # First page
        assert 'next' in response.data
        assert response.data['next'] is not None
    
    def test_category_with_images_count(self, api_client):
        """Test that category response includes image counts."""
        category = ObjectCategory.objects.create(name='Car')
        
        # Update the count directly
        category.training_images_count = 5
        category.save()
        
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['training_images_count'] == 5
