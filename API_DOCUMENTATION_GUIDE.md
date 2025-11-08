# API Documentation Guide

## Overview

The Federated Learning Object Detection API now includes interactive OpenAPI/Swagger documentation powered by drf-spectacular. This provides a user-friendly interface to explore and test all API endpoints.

## Documentation URLs

### Swagger UI (Interactive)
- **URL:** http://localhost:8000/api/docs/
- **Features:**
  - Interactive API explorer
  - Try out requests directly in the browser
  - View request/response schemas
  - Authentication support

### ReDoc (Read-Only)
- **URL:** http://localhost:8000/api/redoc/
- **Features:**
  - Clean, responsive documentation
  - Searchable endpoint list
  - Detailed schema descriptions
  - Better for reference documentation

### OpenAPI Schema
- **URL:** http://localhost:8000/api/schema/
- **Format:** YAML (default) or JSON (?format=openapi-json)
- **Purpose:** Machine-readable API specification
- **Use Cases:**
  - Import into Postman/Insomnia
  - Generate client SDKs
  - CI/CD validation

## Configuration

### settings.py

```python
INSTALLED_APPS = [
    ...
    'drf_spectacular',
    ...
]

REST_FRAMEWORK = {
    ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Federated Learning Object Detection API',
    'DESCRIPTION': 'REST API for federated learning-based object detection system...',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
    ],
}
```

### urls.py

```python
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

## Enhanced Documentation with Decorators

We've added `@extend_schema` decorators to key ViewSets to provide better documentation:

### Object Categories

```python
@extend_schema_view(
    list=extend_schema(
        summary="List object categories",
        description="Get a paginated list of all object categories...",
        tags=["Object Categories"],
    ),
    ...
)
class ObjectCategoryViewSet(viewsets.ModelViewSet):
    ...
    
    @extend_schema(
        summary="Activate category",
        description="Mark a category as active...",
        tags=["Object Categories"],
        responses={200: ObjectCategorySerializer},
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        ...
```

### Authentication

```python
class LoginView(APIView):
    @extend_schema(
        summary="User login",
        description="Authenticate a user with username and password...",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={200: {...}},
    )
    def post(self, request):
        ...
```

## API Endpoints

### Summary

The API includes the following endpoint groups:

1. **Object Categories** (`/api/v1/categories/`)
   - List, create, retrieve, update, delete categories
   - Custom actions: activate, deactivate, statistics

2. **Clients** (`/api/v1/clients/`)
   - Manage federated learning clients
   - Custom actions: heartbeat, register, start/finish training

3. **Training Images** (`/api/v1/training/images/`)
   - Upload and manage training images
   - Custom actions: validate, invalidate, bulk_upload

4. **Training Rounds** (`/api/v1/training/rounds/`)
   - Coordinate training rounds
   - Custom actions: start, complete

5. **Model Versions** (`/api/v1/models/`)
   - Track model versions and metrics
   - Custom actions: deploy, undeploy, deployed

6. **Detection Results** (`/api/v1/detection/results/`)
   - Submit and review detection results
   - Custom actions: submit, feedback, statistics

7. **Authentication** (`/api/v1/auth/`)
   - login, logout, register
   - profile, change-password
   - client (API key auth), verify-token

## Using the Swagger UI

### 1. Authentication

To test protected endpoints:

1. Click the **Authorize** button (top right)
2. Enter your token: `Token <your-token-here>`
3. Example: `Token 1f3d8bcadccc4ab1c233d1e5645bf009dd63fe36`
4. Click **Authorize** then **Close**

### 2. Testing Endpoints

1. Expand an endpoint (e.g., `GET /api/v1/categories/`)
2. Click **Try it out**
3. Modify parameters if needed
4. Click **Execute**
5. View the response below

### 3. Viewing Schemas

Each endpoint shows:
- **Request Body:** Required fields and data types
- **Responses:** Possible status codes and response shapes
- **Parameters:** Query params, path params, headers

## Improvements Made

### Bug Fixes

1. **Fixed ModelVersion field names:**
   - Changed `is_deployed` → `is_production`
   - Added `deployed_at` field
   - Removed non-existent fields: `model_architecture`, `total_parameters`, `performance_metrics`
   - Used actual model fields: `accuracy`, `precision`, `recall`, `f1_score`, `model_size_mb`

2. **Updated ViewSet filters:**
   - Changed `filterset_fields = ['is_deployed']` → `['is_production']`

3. **Fixed deploy/undeploy actions:**
   - Now properly sets `is_production` and `deployed_at`
   - Uses `timezone.now()` for timestamps

### Documentation Enhancements

1. **Added tags** for logical grouping:
   - "Object Categories"
   - "Authentication"
   - (Can add more: "Clients", "Training", "Detection", "Models")

2. **Added summaries** for quick overview

3. **Added descriptions** for detailed explanations

4. **Defined response schemas** for complex responses

## Next Steps

### Phase 1.4.6: Write API Tests
- Create test files for each app
- Test CRUD operations
- Test authentication and permissions
- Test filtering and pagination
- Test file uploads
- Aim for 80%+ code coverage

### Phase 1.4.7: Verify with Real Client
- Create Postman collection
- Test complete workflows
- Document any issues
- Create example requests/responses

## Import into Postman

1. Open Postman
2. Click **Import**
3. Select **Link** tab
4. Enter: `http://localhost:8000/api/schema/?format=openapi-json`
5. Click **Continue** → **Import**

Your entire API will be imported with all endpoints, schemas, and examples!

## Troubleshooting

### Schema Generation Issues

If you see warnings about:
- "unable to guess serializer" → Add `serializer_class` to APIView
- "unable to resolve type hint" → Add `@extend_schema_field` to SerializerMethodField

These are warnings, not errors. The schema will still generate.

### Authentication in Swagger

Make sure to use the format: `Token <key>` not just `<key>`

### CORS Issues

If accessing from a different domain:
- Update `CORS_ALLOWED_ORIGINS` in settings.py
- Or set `CORS_ALLOW_ALL_ORIGINS = True` (development only!)

## Resources

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://github.com/Redocly/redoc)
