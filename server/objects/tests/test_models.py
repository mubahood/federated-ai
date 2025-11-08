"""
Unit tests for ObjectCategory model.
"""
import pytest
from django.core.exceptions import ValidationError
from objects.models import ObjectCategory


@pytest.mark.django_db
class TestObjectCategoryModel:
    """Test suite for ObjectCategory model."""
    
    def test_create_object_category(self):
        """Test creating a basic object category."""
        category = ObjectCategory.objects.create(
            name='Car',
            description='Vehicles with four wheels'
        )
        
        assert category.id is not None
        assert category.name == 'Car'
        assert category.description == 'Vehicles with four wheels'
        assert category.is_active is True
        assert category.created_at is not None
        assert category.updated_at is not None
        assert category.training_images_count == 0
        assert category.detection_count == 0
    
    def test_object_category_string_representation(self):
        """Test __str__ method."""
        category = ObjectCategory.objects.create(
            name='Dog',
            description='Domestic canines'
        )
        assert str(category) == 'Dog'
    
    def test_object_category_name_unique(self):
        """Test that category names must be unique."""
        ObjectCategory.objects.create(name='Cat')
        
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            ObjectCategory.objects.create(name='Cat')
    
    def test_object_category_default_active(self):
        """Test that categories are active by default."""
        category = ObjectCategory.objects.create(name='Person')
        assert category.is_active is True
    
    def test_object_category_deactivate(self):
        """Test deactivating a category."""
        category = ObjectCategory.objects.create(name='Bicycle')
        category.is_active = False
        category.save()
        
        category.refresh_from_db()
        assert category.is_active is False
    
    def test_training_images_count_field(self):
        """Test training_images_count field."""
        category = ObjectCategory.objects.create(name='Car')
        
        # Initially zero
        assert category.training_images_count == 0
        
        # Can be updated
        category.training_images_count = 10
        category.save()
        
        category.refresh_from_db()
        assert category.training_images_count == 10
    
    def test_detection_count_field(self):
        """Test detection_count field."""
        category = ObjectCategory.objects.create(name='Dog')
        
        # Initially zero
        assert category.detection_count == 0
        
        # Can be updated
        category.detection_count = 50
        category.save()
        
        category.refresh_from_db()
        assert category.detection_count == 50
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        category = ObjectCategory.objects.create(name='Truck')
        category_id = category.id
        
        # Soft delete
        category.delete()
        
        # Should not be in default queryset
        assert not ObjectCategory.objects.filter(id=category_id).exists()
        
        # Should be in all_objects queryset
        assert ObjectCategory.all_objects.filter(id=category_id).exists()
        
        # Check deleted_at is set
        deleted_category = ObjectCategory.all_objects.get(id=category_id)
        assert deleted_category.deleted_at is not None
    
    def test_soft_delete_excludes_from_default_manager(self):
        """Test that soft deleted categories are excluded from default manager."""
        category = ObjectCategory.objects.create(name='Boat')
        category_id = category.id
        
        # Before delete - should be in default queryset
        assert ObjectCategory.objects.filter(id=category_id).exists()
        
        # After delete - should NOT be in default queryset
        category.delete()
        assert not ObjectCategory.objects.filter(id=category_id).exists()
        
        # But should still be in all_objects
        assert ObjectCategory.all_objects.filter(id=category_id).exists()
    
    def test_icon_optional(self):
        """Test that icon is optional."""
        category = ObjectCategory.objects.create(
            name='Airplane',
            description='Flying vehicles'
        )
        # Icon should be nullable
        assert not category.icon
    
    def test_description_can_be_blank(self):
        """Test that description can be blank."""
        category = ObjectCategory.objects.create(name='Train')
        assert category.description == ''
    
    def test_ordering(self):
        """Test default ordering by name."""
        ObjectCategory.objects.create(name='Zebra')
        ObjectCategory.objects.create(name='Apple')
        ObjectCategory.objects.create(name='Monkey')
        
        categories = list(ObjectCategory.objects.all())
        assert categories[0].name == 'Apple'
        assert categories[1].name == 'Monkey'
        assert categories[2].name == 'Zebra'
