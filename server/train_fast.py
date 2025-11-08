# Quick Training Script (No Django DB needed)
# Uses images directly from filesystem

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
from pathlib import Path
import argparse
import logging
import json
import sys
from tqdm import tqdm

# Add ml modules to path
sys.path.append(str(Path(__file__).parent / 'ml' / 'models'))
sys.path.append(str(Path(__file__).parent / 'ml' / 'training'))
from model_factory import MobileNetV3Classifier
from trainer import Trainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageFolderDataset(Dataset):
    """Load images directly from category folders."""
    
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        self.class_to_idx = {}
        self.idx_to_class = {}
        
        # Scan category folders
        category_folders = [d for d in self.root_dir.iterdir() if d.is_dir()]
        for idx, cat_dir in enumerate(sorted(category_folders)):
            self.class_to_idx[cat_dir.name] = idx
            self.idx_to_class[idx] = cat_dir.name
            
            # Find all images in category
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                for img_path in cat_dir.glob(f'**/{ext}'):
                    self.samples.append((img_path, idx))
        
        logger.info(f"Found {len(self.samples)} images in {len(self.class_to_idx)} categories")
        
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            logger.warning(f"Error loading {img_path}: {e}")
            image = Image.new('RGB', (224, 224), (0, 0, 0))
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


def get_transforms(is_training=True):
    if is_training:
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='media/training_images/2025/11/06',
                        help='Directory with category folders')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--val_split', type=float, default=0.2)
    parser.add_argument('--early_stopping', type=int, default=5)
    parser.add_argument('--output_dir', type=str, default='checkpoints')
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("GPU-Accelerated Model Training (M1 Max)")
    logger.info("="*60)
    
    # Check GPU
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = 'mps'
        logger.info("🚀 Using Apple M1 Max GPU (Metal Performance Shaders)")
    elif torch.cuda.is_available():
        device = 'cuda'
        logger.info("🚀 Using NVIDIA CUDA GPU")
    else:
        device = 'cpu'
        logger.info("⚠️  Using CPU (slow)")
    
    # Load data
    full_dataset = ImageFolderDataset(args.data_dir, get_transforms(True))
    
    if len(full_dataset) == 0:
        logger.error(f"No images found in {args.data_dir}")
        return 1
    
    # Split
    val_size = int(len(full_dataset) * args.val_split)
    train_size = len(full_dataset) - val_size
    train_dataset, val_indices = random_split(full_dataset, [train_size, val_size], 
                                               generator=torch.Generator().manual_seed(42))
    
    # Create val dataset with different transforms
    val_dataset = ImageFolderDataset(args.data_dir, get_transforms(False))
    val_dataset.samples = [full_dataset.samples[i] for i in val_indices.indices]
    val_dataset.class_to_idx = full_dataset.class_to_idx
    
    logger.info(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    logger.info(f"Classes: {list(full_dataset.class_to_idx.keys())}")
    
    # Data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True,
                             num_workers=4, pin_memory=True if device != 'cpu' else False)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False,
                           num_workers=4, pin_memory=True if device != 'cpu' else False)
    
    # Model
    num_classes = len(full_dataset.class_to_idx)
    model = MobileNetV3Classifier(num_classes=num_classes, pretrained=True)
    
    # Trainer
    trainer = Trainer(model, train_loader, val_loader, device=device,
                     learning_rate=args.lr, weight_decay=1e-4)
    
    # Training loop
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save mapping
    with open(output_dir / 'category_mapping.json', 'w') as f:
        json.dump({
            'category_to_idx': full_dataset.class_to_idx,
            'idx_to_category': full_dataset.idx_to_class,
            'num_classes': num_classes
        }, f, indent=2)
    
    logger.info(f"\nStarting training... (Device: {device})")
    logger.info(f"Epochs: {args.epochs}, Batch: {args.batch_size}, LR: {args.lr}")
    logger.info("="*60)
    
    best_val_acc = 0.0
    patience_counter = 0
    
    for epoch in range(args.epochs):
        logger.info(f"\nEpoch {epoch+1}/{args.epochs}")
        logger.info("-"*60)
        
        # Train & validate
        train_loss, train_acc = trainer.train_epoch()
        val_loss, val_acc = trainer.validate()
        
        logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save history
        trainer.history['train_loss'].append(train_loss)
        trainer.history['train_acc'].append(train_acc)
        trainer.history['val_loss'].append(val_loss)
        trainer.history['val_acc'].append(val_acc)
        
        # LR scheduling
        trainer.scheduler.step(val_loss)
        
        # Save best
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            
            checkpoint_path = output_dir / 'best_model.pth'
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': trainer.optimizer.state_dict(),
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc,
                'best_val_acc': best_val_acc,
                'category_to_idx': full_dataset.class_to_idx,
                'num_classes': num_classes
            }, checkpoint_path)
            
            logger.info(f"✓ Saved best model (val_acc: {val_acc:.2f}%)")
        else:
            patience_counter += 1
        
        # Early stopping
        if args.early_stopping > 0 and patience_counter >= args.early_stopping:
            logger.info(f"\nEarly stopping after {epoch + 1} epochs")
            break
    
    # Save history
    with open(output_dir / 'training_history.json', 'w') as f:
        json.dump(trainer.history, f, indent=2)
    
    logger.info("\n" + "="*60)
    logger.info("Training Complete!")
    logger.info(f"Best validation accuracy: {best_val_acc:.2f}%")
    logger.info(f"Model saved to: {output_dir / 'best_model.pth'}")
    logger.info("="*60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
