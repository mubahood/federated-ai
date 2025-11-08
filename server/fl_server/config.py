"""
Federated Learning Server Configuration.

This module contains configuration settings for the Flower FL server.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class FLServerConfig:
    """Configuration for the Federated Learning server."""
    
    # Server settings
    server_address: str = "[::]:8080"
    num_rounds: int = 10
    
    # Client selection
    min_fit_clients: int = 2
    min_evaluate_clients: int = 2
    min_available_clients: int = 2
    
    # Strategy settings
    fraction_fit: float = 1.0  # Fraction of clients to use for training
    fraction_evaluate: float = 1.0  # Fraction of clients to use for evaluation
    
    # Model settings
    model_name: str = "mobilenet_v3_small"
    num_classes: int = 5
    
    # Training settings
    local_epochs: int = 1
    batch_size: int = 32
    learning_rate: float = 0.001
    
    # Timeouts (seconds)
    round_timeout: Optional[float] = 600.0  # 10 minutes per round
    
    # Aggregation settings
    accept_failures: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.min_fit_clients < 1:
            raise ValueError("min_fit_clients must be at least 1")
        if self.min_evaluate_clients < 1:
            raise ValueError("min_evaluate_clients must be at least 1")
        if self.min_available_clients < max(self.min_fit_clients, self.min_evaluate_clients):
            raise ValueError(
                "min_available_clients must be >= max(min_fit_clients, min_evaluate_clients)"
            )
        if not 0 < self.fraction_fit <= 1.0:
            raise ValueError("fraction_fit must be in (0, 1]")
        if not 0 < self.fraction_evaluate <= 1.0:
            raise ValueError("fraction_evaluate must be in (0, 1]")


# Default configuration instance
default_config = FLServerConfig()


def get_config(**kwargs) -> FLServerConfig:
    """
    Get FL server configuration with optional overrides.
    
    Args:
        **kwargs: Configuration overrides
        
    Returns:
        FLServerConfig instance
    """
    return FLServerConfig(**kwargs)
