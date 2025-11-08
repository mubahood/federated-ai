"""
Device management utilities for PyTorch.
"""

import torch
import logging

logger = logging.getLogger(__name__)


def get_device(prefer_cuda: bool = True) -> str:
    """
    Get the best available device.
    
    Args:
        prefer_cuda: Whether to prefer CUDA if available
    
    Returns:
        Device string ('cuda' or 'cpu')
    """
    if prefer_cuda and torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
    
    logger.info(f"Using device: {device}")
    
    return device


def print_device_info() -> None:
    """Print information about available devices."""
    print("\n" + "=" * 60)
    print("PyTorch Device Information")
    print("=" * 60)
    
    # PyTorch version
    print(f"PyTorch version: {torch.__version__}")
    
    # CUDA availability
    if torch.cuda.is_available():
        print(f"CUDA available: Yes")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"\nGPU {i}:")
            print(f"  Name: {torch.cuda.get_device_name(i)}")
            print(f"  Compute Capability: {torch.cuda.get_device_capability(i)}")
            
            # Memory info
            total_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"  Total Memory: {total_memory:.2f} GB")
    else:
        print(f"CUDA available: No")
        print(f"Using CPU for training")
    
    # MPS (Apple Silicon) availability
    if hasattr(torch.backends, 'mps'):
        print(f"\nMPS (Apple Silicon) available: {torch.backends.mps.is_available()}")
    
    print("=" * 60 + "\n")


def set_seed(seed: int = 42) -> None:
    """
    Set random seeds for reproducibility.
    
    Args:
        seed: Random seed value
    """
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    
    logger.info(f"Random seed set to {seed}")
