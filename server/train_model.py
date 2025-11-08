"""
Train MobileNetV3 Model for Object Classification

This script trains the model using images from the database with proper
category labels. It handles data loading, augmentation, training, and
model checkpointing.

Usage:
    python train_model.py --epochs 30 --batch_size 32 --lr 0.001
"""

import os
import sys
import django
import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
from pathlib import Path
import logging
from tqdm import tqdm
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import after Django setup
from training.models import TrainingImage
from objects.models import ObjectCategory

# Import ML components
sys.path.append(str(Path(__file__).parent))
from ml.models.model_factory import MobileNetV3Classifier
from ml.training.trainer import Trainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingImageDataset(Dataset):
    """Dataset for training images from Django database."""
    
    def __init__(self, images, category_to_idx, transform=None):
        """
        Args:
            images: QuerySet of TrainingImage objects
            category_to_idx: Dict mapping category names to indices
            transform: Torchvision transforms
        """
        self.images = list(images)
        self.category_to_idx = category_to_idx
        self.transform = transform
        
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_obj = self.images[idx]
        
        # Load image
        img_path = img_obj.image.path
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            logger.error(f"Error loading image {img_path}: {e}")
            # Return a black image as fallback
            image = Image.new('RGB', (224, 224), (0, 0, 0))
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get label
        label = self.category_to_idx[img_obj.object_category.name]
        
        return image, label


def get_transforms(is_training=True):
    """Get image transforms for training or validation."""
    
    if is_training:
        # Training transforms with augmentation
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    else:
        # Validation transforms without augmentation
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])


def prepare_data(batch_size=32, val_split=0.2):
    """
    Prepare data loaders from database.
    
    Args:
        batch_size: Batch size for training
        val_split: Validation split ratio
        
    Returns:
        train_loader, val_loader, category_to_idx, idx_to_category
    """
    logger.info("Loading training images from database...")
    
    # Get all training images with categories
    images = TrainingImage.objects.filter(
        object_category__isnull=False
    ).select_related('object_category')
    
    total_images = images.count()
    logger.info(f"Found {total_images} labeled training images")
    
    if total_images == 0:
        raise ValueError("No labeled training images found in database!")
    
    # Get unique categories
    categories = ObjectCategory.objects.all().order_by('name')
    category_to_idx = {cat.name: idx for idx, cat in enumerate(categories)}
    idx_to_category = {idx: cat.name for idx, cat in enumerate(categories)}
    
    num_classes = len(category_to_idx)
    logger.info(f"Number of classes: {num_classes}")
    logger.info(f"Categories: {list(category_to_idx.keys())}")
    
    # Count images per category
    for cat_name in category_to_idx.keys():
        count = images.filter(object_category__name=cat_name).count()
        logger.info(f"  {cat_name}: {count} images")
    
    # Create full dataset
    full_transform = get_transforms(is_training=True)
    full_dataset = TrainingImageDataset(images, category_to_idx, full_transform)
    
    # Split into train and validation
    val_size = int(len(full_dataset) * val_split)
    train_size = len(full_dataset) - val_size
    
    train_dataset, val_indices = random_split(
        full_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Create validation dataset with different transforms
    val_transform = get_transforms(is_training=False)
    val_images = [images[i] for i in val_indices.indices]
    val_dataset = TrainingImageDataset(val_images, category_to_idx, val_transform)
    
    logger.info(f"Train size: {len(train_dataset)}, Val size: {len(val_dataset)}")
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,  # Use multiple workers on native Mac for faster data loading
        pin_memory=True if torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()) else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,  # Use multiple workers on native Mac
        pin_memory=True if torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()) else False
    )
    
    return train_loader, val_loader, category_to_idx, idx_to_category


def train_model(args):
    """Main training function."""
    
    logger.info("=" * 60)
    logger.info("MobileNetV3 Model Training")
    logger.info("=" * 60)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    train_loader, val_loader, category_to_idx, idx_to_category = prepare_data(
        batch_size=args.batch_size,
        val_split=args.val_split
    )
    
    num_classes = len(category_to_idx)
    
    # Save category mapping
    mapping_path = output_dir / "category_mapping.json"
    with open(mapping_path, 'w') as f:
        json.dump({
            'category_to_idx': category_to_idx,
            'idx_to_category': idx_to_category,
            'num_classes': num_classes
        }, f, indent=2)
    logger.info(f"Saved category mapping to {mapping_path}")
    
    # Create model
    logger.info(f"Creating MobileNetV3 model with {num_classes} classes...")
    model = MobileNetV3Classifier(
        num_classes=num_classes,
        pretrained=True  # Use ImageNet pretrained weights
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        learning_rate=args.lr,
        weight_decay=args.weight_decay
    )
    
    # Training loop
    logger.info("Starting training...")
    logger.info(f"Epochs: {args.epochs}, Batch size: {args.batch_size}, LR: {args.lr}")
    logger.info("=" * 60)
    
    best_val_acc = 0.0
    patience_counter = 0
    
    for epoch in range(args.epochs):
        logger.info(f"\nEpoch {epoch + 1}/{args.epochs}")
        logger.info("-" * 60)
        
        # Train
        train_loss, train_acc = trainer.train_epoch()
        logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        
        # Validate
        val_loss, val_acc = trainer.validate()
        logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Update history
        trainer.history['train_loss'].append(train_loss)
        trainer.history['train_acc'].append(train_acc)
        trainer.history['val_loss'].append(val_loss)
        trainer.history['val_acc'].append(val_acc)
        
        # Learning rate scheduling
        trainer.scheduler.step(val_loss)
        
        # Save checkpoint if best
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            
            checkpoint_path = output_dir / "best_model.pth"
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': trainer.optimizer.state_dict(),
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc,
                'best_val_acc': best_val_acc,
                'category_to_idx': category_to_idx,
                'num_classes': num_classes
            }, checkpoint_path)
            
            logger.info(f"✓ Saved best model (val_acc: {val_acc:.4f})")
            trainer.best_model_path = str(checkpoint_path)
        else:
            patience_counter += 1
        
        # Early stopping
        if args.early_stopping > 0 and patience_counter >= args.early_stopping:
            logger.info(f"\nEarly stopping after {epoch + 1} epochs")
            break
        
        # Save checkpoint every N epochs
        if (epoch + 1) % args.save_freq == 0:
            checkpoint_path = output_dir / f"checkpoint_epoch_{epoch + 1}.pth"
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': trainer.optimizer.state_dict(),
                'train_loss': train_loss,
                'val_acc': val_acc,
                'category_to_idx': category_to_idx,
                'num_classes': num_classes
            }, checkpoint_path)
    
    # Training complete
    logger.info("\n" + "=" * 60)
    logger.info("Training Complete!")
    logger.info("=" * 60)
    logger.info(f"Best validation accuracy: {best_val_acc:.4f}")
    logger.info(f"Best model saved to: {trainer.best_model_path}")
    logger.info(f"Category mapping saved to: {mapping_path}")
    
    # Save training history
    history_path = output_dir / "training_history.json"
    with open(history_path, 'w') as f:
        json.dump(trainer.history, f, indent=2)
    logger.info(f"Training history saved to: {history_path}")
    
    return trainer.best_model_path


def main():
    parser = argparse.ArgumentParser(description="Train MobileNetV3 model")
    
    # Training parameters
    parser.add_argument('--epochs', type=int, default=30,
                        help='Number of training epochs (default: 30)')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size (default: 32)')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate (default: 0.001)')
    parser.add_argument('--weight_decay', type=float, default=1e-4,
                        help='Weight decay for L2 regularization (default: 1e-4)')
    parser.add_argument('--val_split', type=float, default=0.2,
                        help='Validation split ratio (default: 0.2)')
    
    # Early stopping
    parser.add_argument('--early_stopping', type=int, default=5,
                        help='Early stopping patience (0 to disable, default: 5)')
    
    # Output
    parser.add_argument('--output_dir', type=str, default='checkpoints',
                        help='Output directory for checkpoints (default: checkpoints)')
    parser.add_argument('--save_freq', type=int, default=10,
                        help='Save checkpoint every N epochs (default: 10)')
    
    args = parser.parse_args()
    
    try:
        model_path = train_model(args)
        logger.info(f"\n✅ Training successful! Model saved to: {model_path}")
        return 0
    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
