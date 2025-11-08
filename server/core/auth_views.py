"""
Authentication views for the Federated AI API.
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .auth_serializers import (
    LoginSerializer,
    TokenSerializer,
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ClientAuthSerializer
)

User = get_user_model()


class LoginView(APIView):
    """
    User login endpoint.
    
    POST /api/v1/auth/login/
    Body: {
        "username": "admin",
        "password": "password"
    }
    
    Returns: {
        "token": "authentication-token",
        "user": {...}
    }
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    @extend_schema(
        summary="User login",
        description="Authenticate a user with username and password. Returns an authentication token.",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'user': {'type': 'object'}
                }
            }
        }
    )
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        token_serializer = TokenSerializer(token)
        
        return Response({
            'token': token.key,
            'user': token_serializer.data['user'],
            'created': token_serializer.data['created']
        })


class LogoutView(APIView):
    """
    User logout endpoint.
    
    POST /api/v1/auth/logout/
    Headers: Authorization: Token <token>
    
    Deletes the user's authentication token.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="User logout",
        description="Logout the current user by deleting their authentication token.",
        tags=["Authentication"],
        responses={200: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}}
    )
    def post(self, request):
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    User registration endpoint.
    
    POST /api/v1/auth/register/
    Body: {
        "username": "newuser",
        "email": "user@example.com",
        "password": "secure_password",
        "password_confirm": "secure_password"
    }
    
    Returns: {
        "token": "authentication-token",
        "user": {...}
    }
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    @extend_schema(
        summary="User registration",
        description="Create a new user account and return an authentication token.",
        tags=["Authentication"],
        request=RegisterSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'user': {'type': 'object'}
                }
            }
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        token = Token.objects.create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the authenticated user's profile.
    
    GET /api/v1/auth/profile/
    PUT/PATCH /api/v1/auth/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    
    POST /api/v1/auth/change-password/
    Body: {
        "old_password": "current_password",
        "new_password": "new_password",
        "new_password_confirm": "new_password"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'detail': 'Password changed successfully.'})


class ClientAuthView(APIView):
    """
    Client authentication endpoint using API key.
    
    POST /api/v1/auth/client/
    Body: {
        "api_key": "client-api-key"
    }
    
    Returns: {
        "client": {...}
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ClientAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        client = serializer.get_client()
        
        # Update last_seen
        from django.utils import timezone
        client.last_seen = timezone.now()
        client.save()
        
        from clients.serializers import ClientDetailSerializer
        client_serializer = ClientDetailSerializer(client, context={'request': request})
        
        return Response({
            'client': client_serializer.data,
            'authenticated': True
        })


class VerifyTokenView(APIView):
    """
    Verify if a token is valid.
    
    POST /api/v1/auth/verify-token/
    Headers: Authorization: Token <token>
    
    Returns: {
        "valid": true,
        "user": {...}
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_serializer = UserSerializer(request.user)
        return Response({
            'valid': True,
            'user': user_serializer.data
        })
