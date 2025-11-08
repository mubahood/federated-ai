"""
Mobile Model Conversion Script

Converts trained PyTorch MobileNetV3 models to mobile-friendly formats:
1. PyTorch Mobile (.ptl) - Optimized for Android with PyTorch Mobile
2. ONNX (.onnx) - Platform-agnostic format
3. Quantized versions for smaller size and faster inference

Usage:
    python convert_to_mobile.py --model_path checkpoints/best_model.pth --output_dir mobile_models/
    
    # With quantization
    python convert_to_mobile.py --model_path checkpoints/best_model.pth --quantize

Author: Federated AI Team
Date: November 7, 2025
"""

import torch
import torch.nn as nn
from torch.utils.mobile_optimizer import optimize_for_mobile
import argparse
from pathlib import Path
import logging
import sys
import json
from typing import Dict, Any, Tuple
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from ml.models.model_factory import MobileNetV3Classifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_model(model_path: Path, num_classes: int = 5) -> Tuple[nn.Module, Dict[str, Any]]:
    """
    Load trained PyTorch model from checkpoint.
    
    Args:
        model_path: Path to model checkpoint
        num_classes: Number of output classes
        
    Returns:
        Tuple of (model, checkpoint_dict)
    """
    logger.info(f"Loading model from {model_path}")
    
    # Create model architecture
    model = MobileNetV3Classifier(num_classes=num_classes, pretrained=False)
    
    # Load checkpoint
    checkpoint = torch.load(model_path, map_location='cpu')
    
    # Load state dict
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"Loaded model from epoch {checkpoint.get('epoch', 'unknown')}")
        logger.info(f"Best validation accuracy: {checkpoint.get('best_val_acc', 'unknown')}")
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    return model, checkpoint


def convert_to_pytorch_mobile(
    model: nn.Module,
    output_path: Path,
    example_input: torch.Tensor,
    optimize: bool = True
) -> Path:
    """
    Convert PyTorch model to PyTorch Mobile format (.ptl).
    
    Args:
        model: PyTorch model
        output_path: Output file path
        example_input: Example input tensor for tracing
        optimize: Whether to apply mobile optimizations
        
    Returns:
        Path to saved mobile model
    """
    logger.info("Converting to PyTorch Mobile format...")
    
    # Trace the model with example input
    traced_model = torch.jit.trace(model, example_input)
    
    # Optimize for mobile if requested
    if optimize:
        logger.info("Applying mobile optimizations...")
        traced_model = optimize_for_mobile(traced_model)
    
    # Save the mobile model
    traced_model._save_for_lite_interpreter(str(output_path))
    
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    logger.info(f"✓ PyTorch Mobile model saved to {output_path} ({file_size:.2f} MB)")
    
    return output_path


def convert_to_onnx(
    model: nn.Module,
    output_path: Path,
    example_input: torch.Tensor,
    opset_version: int = 14
) -> Path:
    """
    Convert PyTorch model to ONNX format.
    
    Args:
        model: PyTorch model
        output_path: Output file path
        example_input: Example input tensor
        opset_version: ONNX opset version
        
    Returns:
        Path to saved ONNX model
    """
    logger.info("Converting to ONNX format...")
    
    torch.onnx.export(
        model,
        example_input,
        str(output_path),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    logger.info(f"✓ ONNX model saved to {output_path} ({file_size:.2f} MB)")
    
    return output_path


def apply_quantization(model: nn.Module) -> nn.Module:
    """
    Apply dynamic quantization to reduce model size.
    
    Args:
        model: PyTorch model
        
    Returns:
        Quantized model
    """
    logger.info("Applying dynamic quantization...")
    
    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {nn.Linear},
        dtype=torch.qint8
    )
    
    logger.info("✓ Model quantized")
    return quantized_model


def test_model_inference(
    model: nn.Module,
    example_input: torch.Tensor,
    is_traced: bool = False
) -> Tuple[torch.Tensor, float]:
    """
    Test model inference and measure time.
    
    Args:
        model: Model to test
        example_input: Input tensor
        is_traced: Whether model is traced (affects how to call it)
        
    Returns:
        Tuple of (output, inference_time_ms)
    """
    import time
    
    model.eval()
    with torch.no_grad():
        # Warm up
        for _ in range(5):
            _ = model(example_input)
        
        # Measure inference time
        start_time = time.time()
        output = model(example_input)
        inference_time = (time.time() - start_time) * 1000  # ms
    
    return output, inference_time


def create_model_metadata(
    checkpoint: Dict[str, Any],
    output_dir: Path,
    model_info: Dict[str, Any]
) -> Path:
    """
    Create metadata file for mobile model.
    
    Args:
        checkpoint: Model checkpoint dict
        output_dir: Output directory
        model_info: Additional model information
        
    Returns:
        Path to metadata file
    """
    metadata = {
        "model_name": "MobileNetV3-Small",
        "task": "object_classification",
        "num_classes": model_info.get("num_classes", 5),
        "input_size": [224, 224],
        "input_channels": 3,
        "mean": [0.485, 0.456, 0.406],  # ImageNet normalization
        "std": [0.229, 0.224, 0.225],
        "training_info": {
            "epoch": checkpoint.get("epoch", None),
            "best_val_acc": checkpoint.get("best_val_acc", None),
            "train_loss": checkpoint.get("train_loss", None),
        },
        "conversion_info": {
            "date": "2025-11-07",
            "formats": ["pytorch_mobile", "onnx"],
            "quantized": model_info.get("quantized", False),
            "optimized": model_info.get("optimized", True)
        },
        "usage": {
            "preprocessing": "Resize to 224x224, normalize with ImageNet stats",
            "output": "Logits for each class (apply softmax for probabilities)"
        }
    }
    
    metadata_path = output_dir / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"✓ Metadata saved to {metadata_path}")
    return metadata_path


def main():
    parser = argparse.ArgumentParser(description="Convert PyTorch model to mobile formats")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to trained model checkpoint (.pth)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="mobile_models",
        help="Output directory for converted models"
    )
    parser.add_argument(
        "--num_classes",
        type=int,
        default=5,
        help="Number of object classes"
    )
    parser.add_argument(
        "--quantize",
        action="store_true",
        help="Apply dynamic quantization to reduce model size"
    )
    parser.add_argument(
        "--skip_onnx",
        action="store_true",
        help="Skip ONNX conversion"
    )
    parser.add_argument(
        "--input_size",
        type=int,
        default=224,
        help="Input image size (default: 224)"
    )
    
    args = parser.parse_args()
    
    # Setup paths
    model_path = Path(args.model_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not model_path.exists():
        logger.error(f"Model file not found: {model_path}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("PyTorch Mobile Model Conversion")
    logger.info("=" * 60)
    logger.info(f"Input model: {model_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Quantization: {'enabled' if args.quantize else 'disabled'}")
    logger.info("=" * 60)
    
    # Load model
    model, checkpoint = load_model(model_path, num_classes=args.num_classes)
    
    # Create example input
    example_input = torch.randn(1, 3, args.input_size, args.input_size)
    
    # Test original model
    logger.info("\nTesting original model...")
    original_output, original_time = test_model_inference(model, example_input)
    logger.info(f"Original inference time: {original_time:.2f} ms")
    
    model_info = {
        "num_classes": args.num_classes,
        "quantized": args.quantize,
        "optimized": True
    }
    
    # Apply quantization if requested
    if args.quantize:
        model = apply_quantization(model)
        quantized_output, quantized_time = test_model_inference(model, example_input)
        logger.info(f"Quantized inference time: {quantized_time:.2f} ms")
        logger.info(f"Speedup: {original_time / quantized_time:.2f}x")
        
        # Verify outputs are similar
        diff = torch.abs(original_output - quantized_output).mean().item()
        logger.info(f"Output difference: {diff:.6f}")
    
    # Convert to PyTorch Mobile
    mobile_path = output_dir / ("model_quantized.ptl" if args.quantize else "model.ptl")
    convert_to_pytorch_mobile(model, mobile_path, example_input, optimize=True)
    
    # Test mobile model
    logger.info("\nTesting mobile model...")
    mobile_model = torch.jit.load(str(mobile_path))
    mobile_output, mobile_time = test_model_inference(mobile_model, example_input, is_traced=True)
    logger.info(f"Mobile inference time: {mobile_time:.2f} ms")
    
    # Convert to ONNX
    if not args.skip_onnx:
        onnx_path = output_dir / ("model_quantized.onnx" if args.quantize else "model.onnx")
        convert_to_onnx(model, onnx_path, example_input)
    
    # Create metadata
    create_model_metadata(checkpoint, output_dir, model_info)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Conversion Summary")
    logger.info("=" * 60)
    logger.info(f"✓ PyTorch Mobile: {mobile_path}")
    if not args.skip_onnx:
        logger.info(f"✓ ONNX: {onnx_path}")
    logger.info(f"✓ Metadata: {output_dir / 'model_metadata.json'}")
    logger.info(f"\nInference time: {mobile_time:.2f} ms")
    logger.info(f"Model size: {mobile_path.stat().st_size / (1024 * 1024):.2f} MB")
    logger.info("=" * 60)
    logger.info("✓ Conversion complete!")


if __name__ == "__main__":
    main()
