"""
Checkpoint management utilities.
"""

import torch
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def save_checkpoint(
    state: Dict,
    filepath: str,
    is_best: bool = False,
    best_filepath: Optional[str] = None
) -> None:
    """
    Save a training checkpoint.
    
    Args:
        state: State dictionary to save
        filepath: Path to save checkpoint
        is_best: Whether this is the best model so far
        best_filepath: Path to save best model (if is_best=True)
    """
    # Create directory if it doesn't exist
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Save checkpoint
    torch.save(state, filepath)
    logger.info(f"Checkpoint saved to {filepath}")
    
    # Save as best model if applicable
    if is_best and best_filepath:
        torch.save(state, best_filepath)
        logger.info(f"Best model saved to {best_filepath}")


def load_checkpoint(
    filepath: str,
    device: Optional[str] = None
) -> Dict:
    """
    Load a checkpoint.
    
    Args:
        filepath: Path to checkpoint file
        device: Device to load checkpoint on
    
    Returns:
        State dictionary
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    checkpoint = torch.load(filepath, map_location=device)
    logger.info(f"Checkpoint loaded from {filepath}")
    
    return checkpoint


def clean_old_checkpoints(
    checkpoint_dir: str,
    keep_last_n: int = 3
) -> None:
    """
    Delete old checkpoints, keeping only the last N.
    
    Args:
        checkpoint_dir: Directory containing checkpoints
        keep_last_n: Number of recent checkpoints to keep
    """
    checkpoint_dir = Path(checkpoint_dir)
    
    if not checkpoint_dir.exists():
        return
    
    # Get all checkpoint files
    checkpoints = sorted(
        checkpoint_dir.glob("checkpoint_epoch*.pt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Delete old checkpoints
    for checkpoint in checkpoints[keep_last_n:]:
        checkpoint.unlink()
        logger.info(f"Deleted old checkpoint: {checkpoint.name}")
