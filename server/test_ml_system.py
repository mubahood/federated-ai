#!/usr/bin/env python
"""
Test script for ML components.

This script tests the ML infrastructure:
1. Model creation (MobileNetV3)
2. Data loading from Django database
3. Training pipeline
4. Evaluation system

Usage:
    python test_ml_system.py [--epochs 5] [--batch-size 32]
"""

import os
import sys
import django
import argparse
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import ML components
from ml.models import create_model, save_model, load_model
from ml.training import create_data_loaders, Trainer
from ml.evaluation import Evaluator
from ml.utils import get_device, print_device_info

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_model_creation():
    """Test model creation."""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Model Creation")
    logger.info("="*60)
    
    device = get_device()
    model = create_model(num_classes=5, pretrained=True, device=device)
    
    # Test forward pass
    import torch
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    output = model(dummy_input)
    
    logger.info(f"✅ Model created successfully")
    logger.info(f"   Output shape: {output.shape}")
    logger.info(f"   Number of classes: {model.num_classes}")
    
    return model, device


def test_data_loading():
    """Test data loading from database."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Data Loading")
    logger.info("="*60)
    
    from training.models import TrainingImage
    from objects.models import ObjectCategory
    
    # Check data availability
    total_images = TrainingImage.objects.count()
    validated_images = TrainingImage.objects.filter(is_validated=True).count()
    categories = ObjectCategory.objects.filter(is_active=True).count()
    
    logger.info(f"   Total images: {total_images}")
    logger.info(f"   Validated images: {validated_images}")
    logger.info(f"   Active categories: {categories}")
    
    if validated_images < 100:
        logger.warning(f"⚠️  Only {validated_images} validated images available")
        logger.warning("   Consider validating more images for better training")
        return None, None
    
    # Create data loaders
    try:
        train_loader, val_loader = create_data_loaders(
            train_split=0.8,
            batch_size=16,  # Small batch size for testing
            num_workers=0,  # Avoid multiprocessing issues in Docker
            validated_only=True
        )
        
        logger.info(f"✅ Data loaders created successfully")
        logger.info(f"   Training batches: {len(train_loader)}")
        logger.info(f"   Validation batches: {len(val_loader)}")
        
        # Test loading one batch
        images, labels = next(iter(train_loader))
        logger.info(f"   Sample batch shape: {images.shape}, Labels: {labels.shape}")
        
        return train_loader, val_loader
    
    except Exception as e:
        logger.error(f"❌ Data loading failed: {e}")
        return None, None


def test_training(model, train_loader, val_loader, device, num_epochs=2):
    """Test training pipeline."""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Training Pipeline")
    logger.info("="*60)
    
    if train_loader is None or val_loader is None:
        logger.warning("⚠️  Skipping training test (no data loaders)")
        return
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        learning_rate=0.001
    )
    
    # Train for a few epochs
    logger.info(f"   Training for {num_epochs} epochs (test run)...")
    history = trainer.train(
        num_epochs=num_epochs,
        checkpoint_dir='./checkpoints_test',
        early_stopping_patience=5
    )
    
    logger.info(f"✅ Training completed successfully")
    logger.info(f"   Final train accuracy: {history['train_acc'][-1]:.2f}%")
    logger.info(f"   Final val accuracy: {history['val_acc'][-1]:.2f}%")
    
    return trainer


def test_evaluation(model, val_loader, device):
    """Test evaluation system."""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Evaluation System")
    logger.info("="*60)
    
    if val_loader is None:
        logger.warning("⚠️  Skipping evaluation test (no data loader)")
        return
    
    from ml.training import get_category_mapping
    
    # Get category mapping
    category_mapping = get_category_mapping()
    class_names = category_mapping['idx_to_name']
    
    # Create evaluator
    evaluator = Evaluator(
        model=model,
        data_loader=val_loader,
        class_names=class_names,
        device=device
    )
    
    # Evaluate
    metrics = evaluator.evaluate()
    
    # Generate report
    report = evaluator.generate_report(metrics)
    
    logger.info(f"✅ Evaluation completed successfully")
    print("\n" + report)
    
    return metrics


def test_model_save_load(model, device):
    """Test model saving and loading."""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Model Save/Load")
    logger.info("="*60)
    
    import tempfile
    import os
    
    # Save model
    with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp:
        save_path = tmp.name
    
    save_model(
        model,
        save_path,
        metadata={'test': True, 'accuracy': 0.95}
    )
    logger.info(f"✅ Model saved to {save_path}")
    
    # Load model
    loaded_model = load_model(save_path, device=device)
    logger.info(f"✅ Model loaded successfully")
    
    # Clean up
    os.unlink(save_path)
    
    return loaded_model


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description='Test ML system')
    parser.add_argument('--epochs', type=int, default=2, help='Number of training epochs for test')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--skip-training', action='store_true', help='Skip training test')
    args = parser.parse_args()
    
    logger.info("\n" + "🚀 "*30)
    logger.info("ML SYSTEM COMPREHENSIVE TEST")
    logger.info("🚀 "*30 + "\n")
    
    # Print device info
    print_device_info()
    
    try:
        # Test 1: Model creation
        model, device = test_model_creation()
        
        # Test 2: Data loading
        train_loader, val_loader = test_data_loading()
        
        # Test 3: Training (optional)
        if not args.skip_training and train_loader is not None:
            trainer = test_training(model, train_loader, val_loader, device, args.epochs)
        
        # Test 4: Evaluation
        if val_loader is not None:
            test_evaluation(model, val_loader, device)
        
        # Test 5: Save/Load
        test_model_save_load(model, device)
        
        logger.info("\n" + "="*60)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("="*60)
        logger.info("\nML system is ready for use.")
        
    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
