"""
Training Pipeline for MobileNetV3 Object Classification.

This module provides the Trainer class for training models with:
- Training and validation loops
- Loss computation and optimization
- Metrics tracking
- Checkpointing
- Early stopping
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Optional, Tuple, List
import logging
from pathlib import Path
import time
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Trainer:
    """
    Trainer class for training object classification models.
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: Optional[str] = None,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4,
        class_weights: Optional[torch.Tensor] = None
    ):
        """
        Initialize the trainer.
        
        Args:
            model: Model to train
            train_loader: Training data loader
            val_loader: Validation data loader
            device: Device to train on ('cuda', 'mps', 'cpu', or None for auto)
            learning_rate: Learning rate for optimizer
            weight_decay: L2 regularization weight
            class_weights: Class weights for handling imbalanced data
        """
        # Auto-detect device with M1 Mac GPU support
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = 'mps'  # Apple Silicon GPU
            else:
                device = 'cpu'
        
        self.device = device
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        
        # Loss function
        if class_weights is not None:
            class_weights = class_weights.to(device)
        self.criterion = nn.CrossEntropyLoss(weight=class_weights)
        
        # Optimizer
        self.optimizer = optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=3
        )
        
        # Training history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        self.best_val_acc = 0.0
        self.best_model_path = None
        
        logger.info(f"Trainer initialized on {device}")
        logger.info(f"Learning rate: {learning_rate}, Weight decay: {weight_decay}")
    
    def train_epoch(self) -> Tuple[float, float]:
        """
        Train for one epoch.
        
        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc='Training')
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': loss.item(),
                'acc': 100. * correct / total
            })
        
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self) -> Tuple[float, float]:
        """
        Validate the model.
        
        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc='Validation')
            for images, labels in pbar:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                # Statistics
                running_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                # Update progress bar
                pbar.set_postfix({
                    'loss': loss.item(),
                    'acc': 100. * correct / total
                })
        
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(
        self,
        num_epochs: int,
        checkpoint_dir: Optional[str] = None,
        early_stopping_patience: int = 5
    ) -> Dict[str, List[float]]:
        """
        Train the model for multiple epochs.
        
        Args:
            num_epochs: Number of epochs to train
            checkpoint_dir: Directory to save checkpoints (None = don't save)
            early_stopping_patience: Stop if no improvement for N epochs
        
        Returns:
            Training history dictionary
        """
        if checkpoint_dir:
            Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
        no_improve_count = 0
        start_time = time.time()
        
        for epoch in range(1, num_epochs + 1):
            logger.info(f"\nEpoch {epoch}/{num_epochs}")
            logger.info("-" * 50)
            
            # Train
            train_loss, train_acc = self.train_epoch()
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            
            # Validate
            val_loss, val_acc = self.validate()
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # Update learning rate
            self.scheduler.step(val_loss)
            
            # Log metrics
            logger.info(
                f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%"
            )
            logger.info(
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%"
            )
            
            # Save best model
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                no_improve_count = 0
                
                if checkpoint_dir:
                    self.best_model_path = Path(checkpoint_dir) / f"best_model_epoch{epoch}.pt"
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': self.model.state_dict(),
                        'optimizer_state_dict': self.optimizer.state_dict(),
                        'train_loss': train_loss,
                        'train_acc': train_acc,
                        'val_loss': val_loss,
                        'val_acc': val_acc,
                        'history': self.history
                    }, self.best_model_path)
                    logger.info(f"✅ Best model saved: {val_acc:.2f}% accuracy")
            else:
                no_improve_count += 1
            
            # Early stopping
            if early_stopping_patience and no_improve_count >= early_stopping_patience:
                logger.info(
                    f"Early stopping triggered after {epoch} epochs "
                    f"(no improvement for {early_stopping_patience} epochs)"
                )
                break
        
        # Training complete
        total_time = time.time() - start_time
        logger.info("\n" + "=" * 50)
        logger.info(f"Training complete in {total_time/60:.2f} minutes")
        logger.info(f"Best validation accuracy: {self.best_val_acc:.2f}%")
        
        return self.history
    
    def save_checkpoint(self, path: str, epoch: int, **kwargs) -> None:
        """
        Save a training checkpoint.
        
        Args:
            path: Path to save checkpoint
            epoch: Current epoch number
            **kwargs: Additional metadata to save
        """
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'history': self.history,
            'best_val_acc': self.best_val_acc
        }
        checkpoint.update(kwargs)
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str) -> int:
        """
        Load a training checkpoint.
        
        Args:
            path: Path to checkpoint file
        
        Returns:
            Epoch number from checkpoint
        """
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.history = checkpoint['history']
        self.best_val_acc = checkpoint.get('best_val_acc', 0.0)
        
        epoch = checkpoint['epoch']
        logger.info(f"Checkpoint loaded from {path} (epoch {epoch})")
        
        return epoch
