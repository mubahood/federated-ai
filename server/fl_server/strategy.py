"""
Federated Learning Strategy Implementation.

This module implements custom FL strategies using Flower's FedAvg algorithm,
with Django integration for tracking rounds and metrics.
"""
import os
import sys
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from flwr.common import (
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    MetricsAggregationFn,
    NDArrays,
    Parameters,
    Scalar,
    parameters_to_ndarrays,
    ndarrays_to_parameters,
)
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg

# Setup Django - must be done before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from training.models import TrainingRound, TrainingSession
from ml.models.model_factory import create_model, get_model_parameters


class DjangoFedAvg(FedAvg):
    """
    Custom FedAvg strategy with Django integration.
    
    This strategy extends Flower's FedAvg to:
    - Track training rounds in Django database
    - Log aggregated metrics
    - Save global model checkpoints
    - Provide hooks for custom behavior
    """
    
    def __init__(
        self,
        training_session_id: int,
        num_classes: int = 5,
        model_name: str = "mobilenet_v3_small",
        **kwargs
    ):
        """
        Initialize the Django-integrated FedAvg strategy.
        
        Args:
            training_session_id: ID of the TrainingSession in Django
            num_classes: Number of output classes
            model_name: Name of the model architecture (currently unused, always MobileNetV3)
            **kwargs: Additional arguments passed to FedAvg
        """
        self.training_session_id = training_session_id
        self.num_classes = num_classes
        self.model_name = model_name
        self.current_round = 0
        
        # Initialize with model parameters
        model = create_model(num_classes=num_classes, pretrained=True)
        initial_parameters = get_model_parameters(model)
        initial_parameters_array = [param.cpu().numpy() for param in initial_parameters]
        
        super().__init__(
            initial_parameters=ndarrays_to_parameters(initial_parameters_array),
            **kwargs
        )
    
    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """
        Aggregate training results from clients.
        
        Args:
            server_round: Current round number
            results: Successful client results
            failures: Failed client results
            
        Returns:
            Tuple of (aggregated_parameters, metrics_dict)
        """
        self.current_round = server_round
        
        # Log round start
        print(f"\n{'='*60}")
        print(f"Round {server_round}: Aggregating fit results from {len(results)} clients")
        print(f"Failures: {len(failures)}")
        
        # Extract client metrics before aggregation
        client_metrics = []
        for client_proxy, fit_res in results:
            if fit_res.metrics:
                client_metrics.append({
                    'client_id': client_proxy.cid,
                    'loss': fit_res.metrics.get('loss', 0.0),
                    'accuracy': fit_res.metrics.get('accuracy', 0.0),
                    'num_examples': fit_res.num_examples,
                })
        
        # Call parent's aggregate_fit
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(
            server_round, results, failures
        )
        
        # Save to Django database
        if aggregated_parameters is not None:
            self._save_round_to_db(
                round_number=server_round,
                num_clients=len(results),
                aggregated_metrics=aggregated_metrics,
                client_metrics=client_metrics,
            )
        
        return aggregated_parameters, aggregated_metrics
    
    def aggregate_evaluate(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """
        Aggregate evaluation results from clients.
        
        Args:
            server_round: Current round number
            results: Successful client results
            failures: Failed client results
            
        Returns:
            Tuple of (aggregated_loss, metrics_dict)
        """
        print(f"Round {server_round}: Aggregating evaluate results from {len(results)} clients")
        
        # Call parent's aggregate_evaluate
        aggregated_loss, aggregated_metrics = super().aggregate_evaluate(
            server_round, results, failures
        )
        
        # Update round with evaluation metrics
        if aggregated_metrics:
            self._update_round_evaluation(
                round_number=server_round,
                loss=aggregated_loss,
                metrics=aggregated_metrics,
            )
        
        print(f"Round {server_round} complete: loss={aggregated_loss:.4f}")
        print(f"{'='*60}\n")
        
        return aggregated_loss, aggregated_metrics
    
    def _save_round_to_db(
        self,
        round_number: int,
        num_clients: int,
        aggregated_metrics: Dict[str, Scalar],
        client_metrics: List[Dict],
    ) -> None:
        """
        Save training round information to Django database.
        
        Args:
            round_number: Round number
            num_clients: Number of participating clients
            aggregated_metrics: Aggregated metrics from all clients
            client_metrics: Individual client metrics
        """
        try:
            # Get or create TrainingRound
            training_round, created = TrainingRound.objects.get_or_create(
                training_session_id=self.training_session_id,
                round_number=round_number,
                defaults={
                    'num_clients': num_clients,
                    'status': 'completed',
                }
            )
            
            if not created:
                training_round.num_clients = num_clients
                training_round.status = 'completed'
            
            # Store metrics as JSON
            training_round.metrics = {
                'aggregated': dict(aggregated_metrics),
                'clients': client_metrics,
                'timestamp': str(django.utils.timezone.now()),
            }
            
            training_round.save()
            
            print(f"✓ Saved round {round_number} to database (ID: {training_round.id})")
            
        except Exception as e:
            print(f"✗ Failed to save round to database: {e}")
    
    def _update_round_evaluation(
        self,
        round_number: int,
        loss: Optional[float],
        metrics: Dict[str, Scalar],
    ) -> None:
        """
        Update round with evaluation metrics.
        
        Args:
            round_number: Round number
            loss: Aggregated evaluation loss
            metrics: Aggregated evaluation metrics
        """
        try:
            training_round = TrainingRound.objects.get(
                training_session_id=self.training_session_id,
                round_number=round_number,
            )
            
            # Update with evaluation metrics
            if training_round.metrics is None:
                training_round.metrics = {}
            
            training_round.metrics['evaluation'] = {
                'loss': float(loss) if loss is not None else None,
                'metrics': dict(metrics),
            }
            
            training_round.save()
            
            print(f"✓ Updated round {round_number} with evaluation metrics")
            
        except TrainingRound.DoesNotExist:
            print(f"✗ Round {round_number} not found in database")
        except Exception as e:
            print(f"✗ Failed to update round evaluation: {e}")


def weighted_average(metrics: List[Tuple[int, Dict[str, Scalar]]]) -> Dict[str, Scalar]:
    """
    Aggregate metrics from multiple clients using weighted average.
    
    Args:
        metrics: List of (num_examples, metrics_dict) tuples
        
    Returns:
        Dictionary of aggregated metrics
    """
    if not metrics:
        return {}
    
    # Calculate total examples
    total_examples = sum(num_examples for num_examples, _ in metrics)
    
    # Aggregate metrics
    aggregated = {}
    
    # Get all metric keys
    all_keys = set()
    for _, metric_dict in metrics:
        all_keys.update(metric_dict.keys())
    
    # Calculate weighted average for each metric
    for key in all_keys:
        weighted_sum = sum(
            num_examples * metric_dict.get(key, 0.0)
            for num_examples, metric_dict in metrics
        )
        aggregated[key] = weighted_sum / total_examples
    
    return aggregated
