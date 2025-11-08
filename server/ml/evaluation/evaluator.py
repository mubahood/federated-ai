"""
Model Evaluation System.

This module provides comprehensive evaluation metrics:
- Accuracy, Precision, Recall, F1 Score
- Per-class metrics
- Confusion matrix
- Evaluation reports
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
import logging

logger = logging.getLogger(__name__)


class Evaluator:
    """
    Evaluator class for comprehensive model evaluation.
    """
    
    def __init__(
        self,
        model: nn.Module,
        data_loader: DataLoader,
        class_names: Dict[int, str],
        device: Optional[str] = None
    ):
        """
        Initialize the evaluator.
        
        Args:
            model: Model to evaluate
            data_loader: Data loader with test/validation data
            class_names: Dictionary mapping class indices to names
            device: Device to evaluate on ('cuda', 'cpu', or None for auto)
        """
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        self.model = model.to(device)
        self.data_loader = data_loader
        self.class_names = class_names
        self.num_classes = len(class_names)
        
        logger.info(f"Evaluator initialized on {device}")
    
    def evaluate(self) -> Dict:
        """
        Perform comprehensive evaluation.
        
        Returns:
            Dictionary containing all evaluation metrics
        """
        self.model.eval()
        
        all_predictions = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for images, labels in self.data_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                probs = torch.softmax(outputs, dim=1)
                _, predicted = outputs.max(1)
                
                # Collect results
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
        
        # Convert to numpy arrays
        all_predictions = np.array(all_predictions)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        # Calculate metrics
        metrics = calculate_metrics(
            all_labels,
            all_predictions,
            all_probs,
            self.class_names
        )
        
        logger.info(f"Evaluation complete: Accuracy = {metrics['accuracy']:.4f}")
        
        return metrics
    
    def generate_report(self, metrics: Dict) -> str:
        """
        Generate a human-readable evaluation report.
        
        Args:
            metrics: Metrics dictionary from evaluate()
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("MODEL EVALUATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Overall metrics
        report.append("Overall Metrics:")
        report.append(f"  Accuracy:  {metrics['accuracy']:.4f}")
        report.append(f"  Precision: {metrics['macro_precision']:.4f}")
        report.append(f"  Recall:    {metrics['macro_recall']:.4f}")
        report.append(f"  F1 Score:  {metrics['macro_f1']:.4f}")
        report.append("")
        
        # Per-class metrics
        report.append("Per-Class Metrics:")
        report.append("-" * 70)
        report.append(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Support':<10}")
        report.append("-" * 70)
        
        for idx, name in sorted(self.class_names.items()):
            precision = metrics['per_class_precision'][idx]
            recall = metrics['per_class_recall'][idx]
            f1 = metrics['per_class_f1'][idx]
            support = metrics['per_class_support'][idx]
            
            report.append(
                f"{name:<15} {precision:<12.4f} {recall:<12.4f} "
                f"{f1:<12.4f} {support:<10d}"
            )
        
        report.append("-" * 70)
        report.append("")
        
        # Confusion matrix
        report.append("Confusion Matrix:")
        cm = metrics['confusion_matrix']
        
        # Header
        header = "True\\Pred  " + "".join(f"{self.class_names[i]:<10}" for i in range(len(cm)))
        report.append(header)
        
        # Rows
        for i, row in enumerate(cm):
            row_str = f"{self.class_names[i]:<10} " + "".join(f"{val:<10d}" for val in row)
            report.append(row_str)
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def calculate_metrics(
    labels: np.ndarray,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    class_names: Dict[int, str]
) -> Dict:
    """
    Calculate comprehensive evaluation metrics.
    
    Args:
        labels: Ground truth labels
        predictions: Predicted labels
        probabilities: Prediction probabilities
        class_names: Dictionary mapping class indices to names
    
    Returns:
        Dictionary containing all metrics
    """
    # Overall accuracy
    accuracy = accuracy_score(labels, predictions)
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        labels,
        predictions,
        average=None,
        zero_division=0
    )
    
    # Macro-averaged metrics
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average='macro',
        zero_division=0
    )
    
    # Weighted-averaged metrics
    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average='weighted',
        zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(labels, predictions)
    
    # Top-k accuracy (k=3)
    top_k_acc = top_k_accuracy(labels, probabilities, k=3)
    
    metrics = {
        # Overall metrics
        'accuracy': float(accuracy),
        'macro_precision': float(macro_precision),
        'macro_recall': float(macro_recall),
        'macro_f1': float(macro_f1),
        'weighted_precision': float(weighted_precision),
        'weighted_recall': float(weighted_recall),
        'weighted_f1': float(weighted_f1),
        'top_3_accuracy': float(top_k_acc),
        
        # Per-class metrics
        'per_class_precision': {i: float(p) for i, p in enumerate(precision)},
        'per_class_recall': {i: float(r) for i, r in enumerate(recall)},
        'per_class_f1': {i: float(f) for i, f in enumerate(f1)},
        'per_class_support': {i: int(s) for i, s in enumerate(support)},
        
        # Confusion matrix
        'confusion_matrix': cm.tolist(),
        
        # Sample info
        'total_samples': len(labels),
        'num_classes': len(class_names)
    }
    
    return metrics


def top_k_accuracy(labels: np.ndarray, probabilities: np.ndarray, k: int = 3) -> float:
    """
    Calculate top-k accuracy.
    
    Args:
        labels: Ground truth labels
        probabilities: Prediction probabilities
        k: Number of top predictions to consider
    
    Returns:
        Top-k accuracy
    """
    # Get top-k predictions
    top_k_preds = np.argsort(probabilities, axis=1)[:, -k:]
    
    # Check if true label is in top-k
    correct = np.any(top_k_preds == labels[:, None], axis=1)
    
    return float(correct.mean())


def calculate_per_image_metrics(
    model: nn.Module,
    image: torch.Tensor,
    true_label: int,
    class_names: Dict[int, str],
    device: str = 'cpu'
) -> Dict:
    """
    Calculate metrics for a single image prediction.
    
    Args:
        model: Model to use for prediction
        image: Input image tensor
        true_label: Ground truth label
        class_names: Dictionary mapping class indices to names
        device: Device to use
    
    Returns:
        Dictionary with prediction results
    """
    model.eval()
    
    with torch.no_grad():
        image = image.unsqueeze(0).to(device)
        output = model(image)
        probs = torch.softmax(output, dim=1)[0]
        pred_label = output.argmax(dim=1).item()
    
    # Get top-3 predictions
    top3_probs, top3_indices = torch.topk(probs, min(3, len(probs)))
    
    top_predictions = [
        {
            'class_idx': int(idx),
            'class_name': class_names[int(idx)],
            'probability': float(prob)
        }
        for idx, prob in zip(top3_indices, top3_probs)
    ]
    
    return {
        'predicted_label': pred_label,
        'predicted_class': class_names[pred_label],
        'true_label': true_label,
        'true_class': class_names[true_label],
        'is_correct': pred_label == true_label,
        'confidence': float(probs[pred_label]),
        'top_predictions': top_predictions
    }
