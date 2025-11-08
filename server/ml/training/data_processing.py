"""
Data Processing utilities for training and evaluation.

This module provides:
- Image transforms for training and validation
- Custom dataset class for TrainingImage model
- Data loaders with proper configuration
"""

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from typing import Optional, Tuple, List
import logging
from pathlib import Path
import django
import os

# Initialize Django if not already done
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from training.models import TrainingImage
from objects.models import ObjectCategory

logger = logging.getLogger(__name__)


# ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_training_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Get data augmentation transforms for training.
    
    Args:
        image_size: Target image size (default: 224 for MobileNetV3)
    
    Returns:
        Composed transforms for training
    """
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def get_validation_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Get transforms for validation/testing (no augmentation).
    
    Args:
        image_size: Target image size (default: 224 for MobileNetV3)
    
    Returns:
        Composed transforms for validation
    """
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


class ObjectDetectionDataset(Dataset):
    """
    Custom dataset for loading TrainingImage instances.
    
    This dataset loads images from the Django TrainingImage model and
    applies the specified transforms.
    """
    
    def __init__(
        self,
        category_ids: Optional[List[int]] = None,
        validated_only: bool = True,
        transform: Optional[transforms.Compose] = None,
        cache_images: bool = False
    ):
        """
        Initialize the dataset.
        
        Args:
            category_ids: List of category IDs to include (None = all)
            validated_only: Whether to only include validated images
            transform: Transforms to apply to images
            cache_images: Whether to cache loaded images in memory
        """
        self.transform = transform
        self.cache_images = cache_images
        self.image_cache = {}
        
        # Build category mapping (name -> index)
        all_categories = ObjectCategory.objects.filter(is_active=True).order_by('name')
        self.category_to_idx = {cat.id: idx for idx, cat in enumerate(all_categories)}
        self.idx_to_category = {idx: cat for cat, idx in self.category_to_idx.items()}
        self.category_names = {idx: cat.name for idx, cat in enumerate(all_categories)}
        
        # Load training images
        queryset = TrainingImage.objects.filter(
            object_category__is_active=True
        ).select_related('object_category')
        
        if category_ids:
            queryset = queryset.filter(object_category_id__in=category_ids)
        
        if validated_only:
            queryset = queryset.filter(is_validated=True)
        
        self.images = list(queryset)
        
        logger.info(
            f"Loaded dataset with {len(self.images)} images "
            f"across {len(self.category_to_idx)} categories"
        )
    
    def __len__(self) -> int:
        """Return the number of images in the dataset."""
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get an image and its label.
        
        Args:
            idx: Index of the image
        
        Returns:
            Tuple of (image_tensor, label_index)
        """
        training_image = self.images[idx]
        
        # Load image
        if self.cache_images and idx in self.image_cache:
            image = self.image_cache[idx]
        else:
            try:
                image = Image.open(training_image.image.path).convert('RGB')
                if self.cache_images:
                    self.image_cache[idx] = image
            except Exception as e:
                logger.error(f"Error loading image {training_image.id}: {e}")
                # Return a blank image on error
                image = Image.new('RGB', (224, 224), color=(128, 128, 128))
        
        # Get label
        category_id = training_image.object_category_id
        label = self.category_to_idx.get(category_id, 0)
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def get_class_weights(self) -> torch.Tensor:
        """
        Calculate class weights for handling imbalanced datasets.
        
        Returns:
            Tensor of class weights (inverse frequency)
        """
        # Count samples per class
        class_counts = torch.zeros(len(self.category_to_idx))
        
        for img in self.images:
            category_id = img.object_category_id
            label = self.category_to_idx.get(category_id, 0)
            class_counts[label] += 1
        
        # Calculate inverse frequency weights
        total_samples = len(self.images)
        class_weights = total_samples / (len(self.category_to_idx) * class_counts)
        
        # Normalize weights
        class_weights = class_weights / class_weights.sum() * len(self.category_to_idx)
        
        return class_weights


def create_data_loaders(
    train_split: float = 0.8,
    batch_size: int = 32,
    num_workers: int = 4,
    category_ids: Optional[List[int]] = None,
    validated_only: bool = True
) -> Tuple[DataLoader, DataLoader]:
    """
    Create training and validation data loaders.
    
    Args:
        train_split: Fraction of data to use for training (rest for validation)
        batch_size: Batch size for data loaders
        num_workers: Number of worker processes for data loading
        category_ids: List of category IDs to include (None = all)
        validated_only: Whether to only include validated images
    
    Returns:
        Tuple of (train_loader, val_loader)
    """
    # Create datasets with appropriate transforms
    train_dataset = ObjectDetectionDataset(
        category_ids=category_ids,
        validated_only=validated_only,
        transform=get_training_transforms(),
        cache_images=False  # Don't cache for training (memory intensive)
    )
    
    val_dataset = ObjectDetectionDataset(
        category_ids=category_ids,
        validated_only=validated_only,
        transform=get_validation_transforms(),
        cache_images=False
    )
    
    # Split dataset
    total_size = len(train_dataset)
    train_size = int(train_split * total_size)
    val_size = total_size - train_size
    
    # Use the same images for both, but different transforms are already applied
    train_indices = list(range(train_size))
    val_indices = list(range(train_size, total_size))
    
    train_subset = torch.utils.data.Subset(train_dataset, train_indices)
    val_subset = torch.utils.data.Subset(val_dataset, val_indices)
    
    # Create data loaders
    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    
    logger.info(
        f"Created data loaders: {len(train_subset)} training, "
        f"{len(val_subset)} validation samples"
    )
    
    return train_loader, val_loader


def get_category_mapping() -> dict:
    """
    Get the mapping between category IDs and indices.
    
    Returns:
        Dictionary with category mappings and names
    """
    categories = ObjectCategory.objects.filter(is_active=True).order_by('name')
    
    return {
        'id_to_idx': {cat.id: idx for idx, cat in enumerate(categories)},
        'idx_to_id': {idx: cat.id for idx, cat in enumerate(categories)},
        'idx_to_name': {idx: cat.name for idx, cat in enumerate(categories)},
        'name_to_idx': {cat.name: idx for idx, cat in enumerate(categories)}
    }
