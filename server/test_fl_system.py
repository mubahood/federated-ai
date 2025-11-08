"""
Test suite for Federated Learning system.

Tests the FL server, client, and end-to-end federated training.
"""
import os
import sys
import time
import threading
import unittest
from unittest.mock import Mock, patch

# Add server directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import torch
from torch.utils.data import DataLoader, TensorDataset

from fl_server.config import FLServerConfig, get_config
from fl_server.strategy import DjangoFedAvg, weighted_average
from training.models import TrainingSession, TrainingRound
from django.contrib.auth import get_user_model

User = get_user_model()


class TestFLConfig(unittest.TestCase):
    """Test FL configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = FLServerConfig()
        
        self.assertEqual(config.server_address, "[::]:8080")
        self.assertEqual(config.num_rounds, 10)
        self.assertEqual(config.min_fit_clients, 2)
        self.assertEqual(config.min_evaluate_clients, 2)
        self.assertEqual(config.min_available_clients, 2)
        self.assertEqual(config.num_classes, 5)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = get_config(
            num_rounds=20,
            min_fit_clients=3,
            min_evaluate_clients=3,
            min_available_clients=3,
            learning_rate=0.01,
        )
        
        self.assertEqual(config.num_rounds, 20)
        self.assertEqual(config.min_fit_clients, 3)
        self.assertEqual(config.learning_rate, 0.01)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Invalid min_fit_clients
        with self.assertRaises(ValueError):
            FLServerConfig(min_fit_clients=0)
        
        # Invalid fraction_fit
        with self.assertRaises(ValueError):
            FLServerConfig(fraction_fit=1.5)
        
        # Invalid min_available_clients
        with self.assertRaises(ValueError):
            FLServerConfig(
                min_fit_clients=5,
                min_available_clients=3,
            )


class TestFLStrategy(unittest.TestCase):
    """Test FL strategy."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Get or create test user
        try:
            cls.user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            cls.user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
        
        # Create test training session
        cls.training_session = TrainingSession.objects.create(
            name='Test FL Session',
            model_name='mobilenet_v3_small',
            status='pending',
            created_by=cls.user,
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        TrainingRound.objects.filter(training_session=cls.training_session).delete()
        cls.training_session.delete()
        # Don't delete user - it might be shared
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        strategy = DjangoFedAvg(
            training_session_id=self.training_session.id,
            num_classes=5,
            model_name='mobilenet_v3_small',
            min_fit_clients=2,
            min_evaluate_clients=2,
            min_available_clients=2,
        )
        
        self.assertEqual(strategy.training_session_id, self.training_session.id)
        self.assertEqual(strategy.num_classes, 5)
        self.assertEqual(strategy.model_name, 'mobilenet_v3_small')
        self.assertIsNotNone(strategy.initial_parameters)
    
    def test_weighted_average(self):
        """Test weighted average aggregation."""
        metrics = [
            (100, {"accuracy": 0.8, "loss": 0.2}),
            (50, {"accuracy": 0.9, "loss": 0.1}),
        ]
        
        result = weighted_average(metrics)
        
        # Expected: (100*0.8 + 50*0.9) / 150 = 0.833...
        self.assertAlmostEqual(result["accuracy"], 0.8333, places=3)
        # Expected: (100*0.2 + 50*0.1) / 150 = 0.1666...
        self.assertAlmostEqual(result["loss"], 0.1667, places=3)
    
    def test_weighted_average_empty(self):
        """Test weighted average with empty metrics."""
        result = weighted_average([])
        self.assertEqual(result, {})


class TestFLClient(unittest.TestCase):
    """Test FL client."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create dummy data loaders
        X = torch.randn(100, 3, 224, 224)
        y = torch.randint(0, 5, (100,))
        dataset = TensorDataset(X, y)
        
        self.train_loader = DataLoader(dataset, batch_size=32)
        self.val_loader = DataLoader(dataset, batch_size=32)
    
    def test_client_initialization(self):
        """Test client initialization."""
        # Import locally to avoid issues if client module doesn't exist in server container
        import sys
        import os
        client_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
        if client_dir not in sys.path and os.path.exists(client_dir):
            sys.path.insert(0, client_dir)
        
        try:
            from fl_client.client import FLClient
            
            client = FLClient(
                client_id="test_client_1",
                train_loader=self.train_loader,
                val_loader=self.val_loader,
                num_classes=5,
                local_epochs=1,
            )
            
            self.assertEqual(client.client_id, "test_client_1")
            self.assertEqual(client.num_classes, 5)
            self.assertEqual(client.local_epochs, 1)
            self.assertIsNotNone(client.model)
            self.assertIsNotNone(client.trainer)
            self.assertIsNotNone(client.evaluator)
        except ImportError:
            self.skipTest("Client module not available in server container")
    
    def test_client_get_parameters(self):
        """Test client get_parameters method."""
        # Import locally to avoid issues if client module doesn't exist in server container
        import sys
        import os
        client_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
        if client_dir not in sys.path and os.path.exists(client_dir):
            sys.path.insert(0, client_dir)
        
        try:
            from fl_client.client import FLClient
            
            client = FLClient(
                client_id="test_client_2",
                train_loader=self.train_loader,
                val_loader=self.val_loader,
                num_classes=5,
            )
            
            result = client.get_parameters({})
            
            self.assertIsNotNone(result)
            self.assertIsNotNone(result.parameters)
        except ImportError:
            self.skipTest("Client module not available in server container")


class TestFLIntegration(unittest.TestCase):
    """Test FL integration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Get or create test user
        try:
            cls.user = User.objects.get(username='testuser_integration')
        except User.DoesNotExist:
            cls.user = User.objects.create_user(
                username='testuser_integration',
                email='integration@example.com',
                password='testpass123'
            )
        
        # Create test training session
        cls.training_session = TrainingSession.objects.create(
            name='Test FL Integration',
            model_name='mobilenet_v3_small',
            status='pending',
            created_by=cls.user,
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        TrainingRound.objects.filter(training_session=cls.training_session).delete()
        cls.training_session.delete()
        # Don't delete user - it might be shared
    
    def test_server_initialization(self):
        """Test server initialization with Django integration."""
        from fl_server.server import FederatedLearningServer
        
        config = FLServerConfig(num_rounds=2, min_fit_clients=1)
        
        server = FederatedLearningServer(
            training_session_id=self.training_session.id,
            config=config,
        )
        
        self.assertEqual(server.training_session_id, self.training_session.id)
        self.assertIsNotNone(server.training_session)
        self.assertIsNotNone(server.strategy)
        self.assertEqual(server.config.num_rounds, 2)


def run_tests():
    """Run all FL tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFLConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestFLStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestFLClient))
    suite.addTests(loader.loadTestsFromTestCase(TestFLIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
