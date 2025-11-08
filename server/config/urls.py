"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from objects.views import ObjectCategoryViewSet, download_model, model_metadata
from clients.views import ClientViewSet
from training.views import TrainingImageViewSet, TrainingRoundViewSet, ModelVersionViewSet
from detection.views import DetectionResultViewSet
from core.auth_views import (
    LoginView,
    LogoutView,
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    ClientAuthView,
    VerifyTokenView
)

# Create API router
router = routers.DefaultRouter()

# Objects app
router.register(r'categories', ObjectCategoryViewSet, basename='category')

# Clients app
router.register(r'clients', ClientViewSet, basename='client')

# Training app
router.register(r'training/images', TrainingImageViewSet, basename='trainingimage')
router.register(r'training/rounds', TrainingRoundViewSet, basename='traininground')
router.register(r'models', ModelVersionViewSet, basename='modelversion')

# Detection app
router.register(r'detection/results', DetectionResultViewSet, basename='detectionresult')

# Authentication URLs
auth_patterns = [
    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('profile/', UserProfileView.as_view(), name='auth_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('client/', ClientAuthView.as_view(), name='auth_client'),
    path('verify-token/', VerifyTokenView.as_view(), name='auth_verify_token'),
]

# Model serving URLs
model_patterns = [
    path('download/', download_model, name='model_download'),
    path('metadata/', model_metadata, name='model_metadata'),
]

# Import custom admin dashboard
from core.admin_dashboard import dashboard_view

urlpatterns = [
    path('admin/dashboard/', dashboard_view, name='admin_dashboard'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include(auth_patterns)),
    path('api/v1/model/', include(model_patterns)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
