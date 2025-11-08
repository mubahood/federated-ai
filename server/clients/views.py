"""
API views for the clients app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Client
from .serializers import (
    ClientSerializer,
    ClientListSerializer,
    ClientDetailSerializer,
    ClientRegistrationSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsClientOrAdmin


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client CRUD operations.
    
    Provides:
    - list: Get all clients (with filtering, search, ordering)
    - retrieve: Get single client by ID
    - create: Register new client
    - update/partial_update: Update client information
    - destroy: Soft delete client
    
    Filters:
    - status: Filter by client status
    - device_type: Filter by device type
    
    Search:
    - Search in name and device_id fields
    
    Ordering:
    - name, last_seen, total_training_rounds
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsClientOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'device_type']
    search_fields = ['name', 'device_id']
    ordering_fields = ['name', 'last_seen', 'total_training_rounds', 'created_at']
    ordering = ['-last_seen']  # Default ordering
    
    def get_permissions(self):
        """Allow anyone to register a client."""
        if self.action == 'register':
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'list':
            return ClientListSerializer
        elif self.action == 'retrieve':
            return ClientDetailSerializer
        elif self.action == 'register':
            return ClientRegistrationSerializer
        return ClientSerializer
    
    def perform_create(self, serializer):
        """
        Set the owner field to the current user if authenticated.
        """
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """
        Soft delete the client instead of hard delete.
        """
        instance.delete()  # Soft delete by default
    
    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        """
        Update client's last_seen timestamp.
        
        POST /api/v1/clients/{id}/heartbeat/
        """
        client = self.get_object()
        client.last_seen = timezone.now()
        client.status = Client.Status.ACTIVE
        
        # Update IP address if provided
        ip = request.META.get('REMOTE_ADDR')
        if ip:
            client.ip_address = ip
        
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_training(self, request, pk=None):
        """
        Mark client as currently training.
        
        POST /api/v1/clients/{id}/start_training/
        """
        client = self.get_object()
        client.status = Client.Status.TRAINING
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def finish_training(self, request, pk=None):
        """
        Mark client training as complete and update statistics.
        
        POST /api/v1/clients/{id}/finish_training/
        Body: {
            "training_time": 120.5,
            "samples_count": 100
        }
        """
        client = self.get_object()
        client.status = Client.Status.ACTIVE
        client.total_training_rounds += 1
        
        # Update statistics if provided
        training_time = request.data.get('training_time', 0)
        samples_count = request.data.get('samples_count', 0)
        
        if training_time > 0:
            # Calculate running average
            total_time = client.average_training_time * (client.total_training_rounds - 1)
            client.average_training_time = (total_time + training_time) / client.total_training_rounds
        
        if samples_count > 0:
            client.total_samples_contributed += samples_count
        
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new federated learning client.
        
        POST /api/v1/clients/register/
        Body: {
            "name": "My iPhone",
            "device_type": "mobile",
            "capabilities": {
                "cpu": "A15 Bionic",
                "ram_gb": 6,
                "storage_gb": 128
            }
        }
        
        Returns: Client details including API key for authentication
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if request.user.is_authenticated:
            serializer.save(owner=request.user)
        else:
            serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall client statistics.
        
        GET /api/v1/clients/statistics/
        """
        clients = self.get_queryset()
        
        stats = {
            'total_clients': clients.count(),
            'active_clients': clients.filter(status=Client.Status.ACTIVE).count(),
            'training_clients': clients.filter(status=Client.Status.TRAINING).count(),
            'inactive_clients': clients.filter(status=Client.Status.INACTIVE).count(),
            'online_clients': sum(1 for c in clients if c.is_online()),
            'total_training_rounds': sum(c.total_training_rounds for c in clients),
            'total_samples_contributed': sum(c.total_samples_contributed for c in clients),
            'clients_by_type': {
                device_type: clients.filter(device_type=device_type).count()
                for device_type, _ in Client.DeviceType.choices
            }
        }
        
        return Response(stats)
