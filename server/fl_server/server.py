"""
Federated Learning Server Implementation.

This module implements the Flower FL server that orchestrates federated
learning rounds across multiple clients.
"""
import os
import sys
from typing import Optional

import flwr as fl
from flwr.server import ServerConfig

# Setup Django - must be done before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from training.models import TrainingSession
from fl_server.config import FLServerConfig, default_config
from fl_server.strategy import DjangoFedAvg, weighted_average


class FederatedLearningServer:
    """
    Federated Learning Server orchestrator.
    
    This class manages the FL server lifecycle:
    - Initializes the FL strategy
    - Configures server settings
    - Starts and monitors FL rounds
    - Tracks training in Django database
    """
    
    def __init__(
        self,
        training_session_id: int,
        config: Optional[FLServerConfig] = None,
    ):
        """
        Initialize the FL server.
        
        Args:
            training_session_id: ID of the TrainingSession in Django
            config: Optional server configuration (uses default if None)
        """
        self.training_session_id = training_session_id
        self.config = config or default_config
        self.training_session = None
        
        # Load training session from database
        self._load_training_session()
        
        # Initialize strategy
        self.strategy = self._create_strategy()
    
    def _load_training_session(self) -> None:
        """Load training session from database."""
        try:
            self.training_session = TrainingSession.objects.get(
                id=self.training_session_id
            )
            print(f"✓ Loaded training session: {self.training_session.name}")
            print(f"  Model: {self.training_session.model_name}")
            print(f"  Status: {self.training_session.status}")
        except TrainingSession.DoesNotExist:
            raise ValueError(
                f"TrainingSession with ID {self.training_session_id} not found"
            )
    
    def _create_strategy(self) -> DjangoFedAvg:
        """
        Create the FL strategy with Django integration.
        
        Returns:
            Configured DjangoFedAvg strategy
        """
        strategy = DjangoFedAvg(
            training_session_id=self.training_session_id,
            num_classes=self.config.num_classes,
            model_name=self.config.model_name,
            fraction_fit=self.config.fraction_fit,
            fraction_evaluate=self.config.fraction_evaluate,
            min_fit_clients=self.config.min_fit_clients,
            min_evaluate_clients=self.config.min_evaluate_clients,
            min_available_clients=self.config.min_available_clients,
            evaluate_metrics_aggregation_fn=weighted_average,
            fit_metrics_aggregation_fn=weighted_average,
            accept_failures=self.config.accept_failures,
        )
        
        print(f"✓ Created FedAvg strategy with {self.config.num_rounds} rounds")
        return strategy
    
    def start(self) -> None:
        """
        Start the FL server.
        
        This method:
        1. Updates training session status to 'running'
        2. Starts the Flower server
        3. Orchestrates FL rounds
        4. Updates training session status on completion
        """
        print("\n" + "="*60)
        print("Starting Federated Learning Server")
        print("="*60)
        print(f"Training Session: {self.training_session.name}")
        print(f"Server Address: {self.config.server_address}")
        print(f"Number of Rounds: {self.config.num_rounds}")
        print(f"Min Clients: {self.config.min_available_clients}")
        print("="*60 + "\n")
        
        # Update training session status
        self.training_session.status = 'running'
        self.training_session.save()
        
        try:
            # Create server config
            server_config = ServerConfig(num_rounds=self.config.num_rounds)
            
            # Start FL server
            fl.server.start_server(
                server_address=self.config.server_address,
                config=server_config,
                strategy=self.strategy,
            )
            
            # Update status on completion
            self.training_session.status = 'completed'
            self.training_session.save()
            
            print("\n" + "="*60)
            print("Federated Learning Complete!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ FL Server error: {e}")
            self.training_session.status = 'failed'
            self.training_session.save()
            raise


def start_fl_server(
    training_session_id: int,
    config: Optional[FLServerConfig] = None,
) -> None:
    """
    Convenience function to start the FL server.
    
    Args:
        training_session_id: ID of the TrainingSession in Django
        config: Optional server configuration
    """
    server = FederatedLearningServer(
        training_session_id=training_session_id,
        config=config,
    )
    server.start()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Federated Learning Server")
    parser.add_argument(
        "--session-id",
        type=int,
        required=True,
        help="Training session ID from Django database"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=10,
        help="Number of FL rounds (default: 10)"
    )
    parser.add_argument(
        "--min-clients",
        type=int,
        default=2,
        help="Minimum number of clients (default: 2)"
    )
    parser.add_argument(
        "--address",
        type=str,
        default="[::]:8080",
        help="Server address (default: [::]:8080)"
    )
    
    args = parser.parse_args()
    
    # Create config with overrides
    config = FLServerConfig(
        server_address=args.address,
        num_rounds=args.rounds,
        min_fit_clients=args.min_clients,
        min_evaluate_clients=args.min_clients,
        min_available_clients=args.min_clients,
    )
    
    # Start server
    start_fl_server(
        training_session_id=args.session_id,
        config=config,
    )
