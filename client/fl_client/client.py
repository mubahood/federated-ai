"""
Federated Learning Client Implementation.

This module implements the Flower FL client that performs local training
and communicates with the FL server.
"""
import os
import sys
from typing import Dict, List, Tuple

import torch
import flwr as fl
from flwr.common import (
    Code,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    GetParametersIns,
    GetParametersRes,
    Parameters,
    Status,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.dirname(current_dir)
if client_dir not in sys.path:
    sys.path.insert(0, client_dir)

# Add server directory for ML imports
server_dir = os.path.join(os.path.dirname(client_dir), 'server')
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

from ml.models.model_factory import create_model, get_model_parameters, set_model_parameters
from ml.training.trainer import Trainer
from ml.evaluation.evaluator import Evaluator
from ml.utils.device import get_device


class FLClient(fl.client.NumPyClient):
    """
    Flower NumPy Client for federated learning.
    
    This client:
    - Receives global model parameters from server
    - Trains model locally on client data
    - Evaluates model on local validation data
    - Sends updated parameters back to server
    """
    
    def __init__(
        self,
        client_id: str,
        train_loader,
        val_loader,
        model_name: str = "mobilenet_v3_small",
        num_classes: int = 5,
        local_epochs: int = 1,
        learning_rate: float = 0.001,
    ):
        """
        Initialize the FL client.
        
        Args:
            client_id: Unique client identifier
            train_loader: DataLoader for training data
            val_loader: DataLoader for validation data
            model_name: Name of the model architecture
            num_classes: Number of output classes
            local_epochs: Number of local training epochs per round
            learning_rate: Learning rate for local training
        """
        super().__init__()
        
        self.client_id = client_id
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.model_name = model_name
        self.num_classes = num_classes
        self.local_epochs = local_epochs
        self.learning_rate = learning_rate
        
        # Initialize model
        self.device = get_device()
        self.model = create_model(model_name, num_classes=num_classes)
        self.model.to(self.device)
        
        # Initialize trainer and evaluator
        self.trainer = Trainer(
            model=self.model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=self.device,
            learning_rate=learning_rate,
        )
        
        self.evaluator = Evaluator(
            model=self.model,
            device=self.device,
        )
        
        print(f"✓ Initialized FL Client: {client_id}")
        print(f"  Model: {model_name}")
        print(f"  Device: {self.device}")
        print(f"  Training samples: {len(train_loader.dataset)}")
        print(f"  Validation samples: {len(val_loader.dataset)}")
    
    def get_parameters(self, config: Dict[str, any]) -> GetParametersRes:
        """
        Get model parameters.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            GetParametersRes with current model parameters
        """
        parameters = get_model_parameters(self.model)
        parameters_array = [param.cpu().numpy() for param in parameters]
        
        return GetParametersRes(
            status=Status(code=Code.OK, message="Success"),
            parameters=ndarrays_to_parameters(parameters_array),
        )
    
    def fit(self, parameters: Parameters, config: Dict[str, any]) -> FitRes:
        """
        Train the model on local data.
        
        Args:
            parameters: Global model parameters from server
            config: Training configuration
            
        Returns:
            FitRes with updated parameters and metrics
        """
        print(f"\n[Client {self.client_id}] Starting local training...")
        
        # Update model with global parameters
        parameters_array = parameters_to_ndarrays(parameters)
        parameters_tensors = [torch.tensor(arr) for arr in parameters_array]
        set_model_parameters(self.model, parameters_tensors)
        
        # Get training config
        epochs = config.get("local_epochs", self.local_epochs)
        
        # Train locally
        train_loss = 0.0
        train_acc = 0.0
        
        for epoch in range(epochs):
            metrics = self.trainer.train_epoch()
            train_loss = metrics['train_loss']
            train_acc = metrics['train_acc']
            
            print(f"  Epoch {epoch + 1}/{epochs}: loss={train_loss:.4f}, acc={train_acc:.4f}")
        
        # Get updated parameters
        updated_parameters = get_model_parameters(self.model)
        updated_parameters_array = [param.cpu().numpy() for param in updated_parameters]
        
        # Prepare metrics
        metrics = {
            "loss": train_loss,
            "accuracy": train_acc,
        }
        
        print(f"[Client {self.client_id}] Training complete: loss={train_loss:.4f}, acc={train_acc:.4f}")
        
        return FitRes(
            status=Status(code=Code.OK, message="Success"),
            parameters=ndarrays_to_parameters(updated_parameters_array),
            num_examples=len(self.train_loader.dataset),
            metrics=metrics,
        )
    
    def evaluate(self, parameters: Parameters, config: Dict[str, any]) -> EvaluateRes:
        """
        Evaluate the model on local validation data.
        
        Args:
            parameters: Global model parameters from server
            config: Evaluation configuration
            
        Returns:
            EvaluateRes with loss and metrics
        """
        print(f"\n[Client {self.client_id}] Starting local evaluation...")
        
        # Update model with global parameters
        parameters_array = parameters_to_ndarrays(parameters)
        parameters_tensors = [torch.tensor(arr) for arr in parameters_array]
        set_model_parameters(self.model, parameters_tensors)
        
        # Evaluate on validation data
        metrics = self.evaluator.evaluate(self.val_loader)
        
        loss = metrics['loss']
        accuracy = metrics['accuracy']
        
        print(f"[Client {self.client_id}] Evaluation complete: loss={loss:.4f}, acc={accuracy:.4f}")
        
        return EvaluateRes(
            status=Status(code=Code.OK, message="Success"),
            loss=loss,
            num_examples=len(self.val_loader.dataset),
            metrics={"accuracy": accuracy},
        )


def start_fl_client(
    server_address: str,
    client_id: str,
    train_loader,
    val_loader,
    model_name: str = "mobilenet_v3_small",
    num_classes: int = 5,
    local_epochs: int = 1,
    learning_rate: float = 0.001,
) -> None:
    """
    Start the FL client and connect to server.
    
    Args:
        server_address: Address of the FL server (e.g., "localhost:8080")
        client_id: Unique client identifier
        train_loader: DataLoader for training data
        val_loader: DataLoader for validation data
        model_name: Name of the model architecture
        num_classes: Number of output classes
        local_epochs: Number of local training epochs per round
        learning_rate: Learning rate for local training
    """
    # Create client
    client = FLClient(
        client_id=client_id,
        train_loader=train_loader,
        val_loader=val_loader,
        model_name=model_name,
        num_classes=num_classes,
        local_epochs=local_epochs,
        learning_rate=learning_rate,
    )
    
    print(f"\n{'='*60}")
    print(f"Connecting to FL Server: {server_address}")
    print(f"Client ID: {client_id}")
    print(f"{'='*60}\n")
    
    # Start client
    fl.client.start_client(
        server_address=server_address,
        client=client.to_client(),
    )
    
    print(f"\n{'='*60}")
    print(f"Client {client_id} disconnected")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    # Setup Django for data loading
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    
    from ml.training.data_processing import create_data_loaders
    
    parser = argparse.ArgumentParser(description="Start Federated Learning Client")
    parser.add_argument(
        "--server",
        type=str,
        default="localhost:8080",
        help="FL server address (default: localhost:8080)"
    )
    parser.add_argument(
        "--client-id",
        type=str,
        required=True,
        help="Unique client identifier"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of local training epochs (default: 1)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size (default: 32)"
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate (default: 0.001)"
    )
    
    args = parser.parse_args()
    
    # Create data loaders
    train_loader, val_loader = create_data_loaders(
        batch_size=args.batch_size,
        validation_split=0.2,
    )
    
    # Start client
    start_fl_client(
        server_address=args.server,
        client_id=args.client_id,
        train_loader=train_loader,
        val_loader=val_loader,
        local_epochs=args.epochs,
        learning_rate=args.lr,
    )
