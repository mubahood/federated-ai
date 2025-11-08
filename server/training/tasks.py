"""
Celery tasks for training jobs.

Background tasks for:
- Training models
- Exporting models to mobile format
- Updating model versions
"""
import logging
import os
from pathlib import Path
from datetime import datetime
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_training_job(self, training_round_id, job_id):
    """
    Run a complete training job:
    1. Load labeled images from database
    2. Train/fine-tune model
    3. Export to mobile format (.ptl)
    4. Create ModelVersion entry
    5. Update TrainingRound status
    
    Args:
        training_round_id: ID of TrainingRound object
        job_id: Unique job identifier
    
    Returns:
        dict: Training results with metrics
    """
    from .models import TrainingRound, ModelVersion
    from training.models import TrainingImage
    from objects.models import ObjectCategory
    import sys
    import subprocess
    
    logger.info(f"Starting training job {job_id} for round {training_round_id}")
    
    try:
        # Get training round
        training_round = TrainingRound.objects.get(id=training_round_id)
        training_round.status = TrainingRound.Status.IN_PROGRESS
        training_round.start_time = timezone.now()
        training_round.save()
        
        # Get hyperparameters
        hyperparams = training_round.hyperparameters
        epochs = hyperparams.get('epochs', 20)
        batch_size = hyperparams.get('batch_size', 32)
        learning_rate = hyperparams.get('learning_rate', 0.001)
        use_existing_model = hyperparams.get('use_existing_model', True)
        
        # Get all validated images
        images = TrainingImage.objects.filter(
            is_validated=True,
            deleted_at__isnull=True
        ).select_related('object_category')
        
        total_images = images.count()
        logger.info(f"Found {total_images} validated images for training")
        
        # Get category distribution
        category_counts = {}
        for img in images:
            cat_name = img.object_category.name if img.object_category else 'Unknown'
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
        logger.info(f"Category distribution: {category_counts}")
        
        # Run training script
        server_dir = Path(settings.BASE_DIR)
        train_script = server_dir / 'train_model.py'
        
        if not train_script.exists():
            raise FileNotFoundError(f"Training script not found: {train_script}")
        
        # Build command
        cmd = [
            sys.executable,
            str(train_script),
            '--epochs', str(epochs),
            '--batch_size', str(batch_size),
            '--lr', str(learning_rate),
        ]
        
        if not use_existing_model:
            cmd.append('--from_scratch')
        
        logger.info(f"Running training command: {' '.join(cmd)}")
        
        # Run training
        result = subprocess.run(
            cmd,
            cwd=str(server_dir),
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Training failed: {result.stderr}")
            raise Exception(f"Training failed with exit code {result.returncode}: {result.stderr}")
        
        logger.info("Training completed successfully")
        logger.info(f"Training output: {result.stdout[-500:]}")  # Last 500 chars
        
        # Parse training metrics from output
        metrics = {
            'total_images': total_images,
            'category_distribution': category_counts,
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
        }
        
        # Extract metrics from training output
        for line in result.stdout.split('\n'):
            if 'Final Train Accuracy' in line:
                try:
                    accuracy = float(line.split(':')[-1].strip().replace('%', ''))
                    metrics['train_accuracy'] = accuracy
                except:
                    pass
            elif 'Final Validation Accuracy' in line:
                try:
                    accuracy = float(line.split(':')[-1].strip().replace('%', ''))
                    metrics['val_accuracy'] = accuracy
                except:
                    pass
            elif 'Best Model Saved' in line:
                try:
                    path = line.split(':')[-1].strip()
                    metrics['checkpoint_path'] = path
                except:
                    pass
        
        # Check if mobile model was created
        mobile_model_path = server_dir / 'mobile_models' / 'model.ptl'
        if not mobile_model_path.exists():
            raise FileNotFoundError(f"Mobile model not found at {mobile_model_path}")
        
        model_size_mb = mobile_model_path.stat().st_size / (1024 * 1024)
        metrics['model_size_mb'] = round(model_size_mb, 2)
        
        logger.info(f"Mobile model created: {mobile_model_path} ({model_size_mb:.2f} MB)")
        
        # Get current version and increment
        latest_version = ModelVersion.objects.order_by('-version').first()
        if latest_version:
            # Parse version (e.g., "1.2.0" -> [1, 2, 0])
            parts = [int(x) for x in latest_version.version.split('.')]
            parts[1] += 1  # Increment minor version
            new_version = '.'.join(str(x) for x in parts)
        else:
            new_version = "1.0.0"
        
        # Create ModelVersion
        model_version = ModelVersion.objects.create(
            version=new_version,
            training_round=training_round,
            model_file=f"mobile_models/model_{new_version}.ptl",
            accuracy=metrics.get('val_accuracy', 0.0),
            model_size=int(model_size_mb * 1024 * 1024),  # bytes
            is_production=False,  # Don't auto-deploy
            hyperparameters=hyperparams,
            metrics=metrics
        )
        
        # Copy model file with version
        import shutil
        versioned_model_path = server_dir / f'mobile_models/model_{new_version}.ptl'
        shutil.copy(mobile_model_path, versioned_model_path)
        logger.info(f"Model saved as version {new_version}")
        
        # Update training round
        training_round.status = TrainingRound.Status.COMPLETED
        training_round.end_time = timezone.now()
        training_round.calculate_duration()
        training_round.metrics.update(metrics)
        training_round.save()
        
        logger.info(f"Training job {job_id} completed successfully")
        
        return {
            'success': True,
            'job_id': job_id,
            'training_round_id': training_round_id,
            'model_version': new_version,
            'model_version_id': model_version.id,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"Training job {job_id} failed: {str(e)}", exc_info=True)
        
        # Update training round as failed
        try:
            training_round = TrainingRound.objects.get(id=training_round_id)
            training_round.status = TrainingRound.Status.FAILED
            training_round.end_time = timezone.now()
            training_round.calculate_duration()
            training_round.metrics['error'] = str(e)
            training_round.save()
        except:
            pass
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying training job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
        
        return {
            'success': False,
            'job_id': job_id,
            'error': str(e)
        }


@shared_task
def cleanup_old_models(days=30):
    """
    Clean up model files older than specified days (except production models).
    
    Args:
        days: Number of days to keep models
    """
    from .models import ModelVersion
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_models = ModelVersion.objects.filter(
        created_at__lt=cutoff_date,
        is_production=False
    )
    
    deleted_count = 0
    for model in old_models:
        try:
            # Delete file
            model_path = Path(settings.BASE_DIR) / model.model_file
            if model_path.exists():
                model_path.unlink()
                logger.info(f"Deleted old model file: {model_path}")
            
            # Delete database entry
            model.delete()
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete model {model.id}: {e}")
    
    logger.info(f"Cleaned up {deleted_count} old models")
    return {' success': True, 'deleted_count': deleted_count}
