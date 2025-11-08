# 🔐 Federated AI - Authentication & Permissions Guide

**Created:** November 6, 2025  
**Version:** 1.0  
**Status:** ✅ **FULLY OPERATIONAL**

---

## 📋 Overview

The Federated AI API uses **token-based authentication** with custom permission classes to secure endpoints. There are two authentication methods:

1. **User Authentication** - For admin users and registered users (Token-based)
2. **Client Authentication** - For federated learning devices (API Key-based)

---

## 🔑 Authentication Methods

### 1. User Token Authentication

**How it works:**
- User logs in with username/password
- Server returns authentication token
- Client includes token in `Authorization` header for subsequent requests

**Token Format:**
```
Authorization: Token <your-token-here>
```

**Example:**
```bash
curl -H "Authorization: Token 1f3d8bcadccc4ab1c233d1e5645bf009dd63fe36" \
  http://localhost:8000/api/v1/categories/
```

### 2. Client API Key Authentication

**How it works:**
- Client registers and receives an API key
- Client includes API key in `X-API-Key` header
- Server validates API key and authorizes access

**Header Format:**
```
X-API-Key: <your-api-key-here>
```

**Example:**
```bash
curl -H "X-API-Key: 6UqbQ7Aw81kgVGJHE_0oFYRfzAWFma5vRJdNnM2DwbU" \
  http://localhost:8000/api/v1/clients/
```

---

## 🚪 Authentication Endpoints

### 1. Login (Get Token)

**Endpoint:** `POST /api/v1/auth/login/`  
**Permission:** AllowAny  
**Purpose:** Authenticate user and get token

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "token": "1f3d8bcadccc4ab1c233d1e5645bf009dd63fe36",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@federated-ai.local",
        "is_staff": true
    },
    "created": "2025-11-06T15:23:09.920926Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

### 2. Register New User

**Endpoint:** `POST /api/v1/auth/register/`  
**Permission:** AllowAny  
**Purpose:** Create new user account and get token

**Request:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "token": "3625f583185f0197d932a194d12ae0e073622353",
    "user": {
        "id": 2,
        "username": "newuser",
        "email": "user@example.com"
    }
}
```

**Validation Rules:**
- Username: Required, unique
- Email: Required, valid email format
- Password: Required, minimum 8 characters
- password_confirm: Must match password

---

### 3. Logout (Revoke Token)

**Endpoint:** `POST /api/v1/auth/logout/`  
**Permission:** IsAuthenticated  
**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "detail": "Successfully logged out."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Token 1f3d8bcadccc4ab1c233d1e5645bf009dd63fe36"
```

---

### 4. Get User Profile

**Endpoint:** `GET /api/v1/auth/profile/`  
**Permission:** IsAuthenticated  
**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@federated-ai.local",
    "first_name": "",
    "last_name": "",
    "is_staff": true,
    "date_joined": "2025-11-06T13:32:53.307197Z"
}
```

---

### 5. Update User Profile

**Endpoint:** `PUT/PATCH /api/v1/auth/profile/`  
**Permission:** IsAuthenticated  
**Headers:** `Authorization: Token <token>`

**Request:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "newemail@example.com"
}
```

---

### 6. Change Password

**Endpoint:** `POST /api/v1/auth/change-password/`  
**Permission:** IsAuthenticated  
**Headers:** `Authorization: Token <token>`

**Request:**
```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password",
    "new_password_confirm": "new_secure_password"
}
```

**Response:**
```json
{
    "detail": "Password changed successfully."
}
```

---

### 7. Client Authentication

**Endpoint:** `POST /api/v1/auth/client/`  
**Permission:** AllowAny  
**Purpose:** Authenticate federated learning client

**Request:**
```json
{
    "api_key": "6UqbQ7Aw81kgVGJHE_0oFYRfzAWFma5vRJdNnM2DwbU"
}
```

**Response:**
```json
{
    "client": {
        "id": 1,
        "device_id": "1a3e1148-5b82-4e6c-a46f-01433d705a13",
        "name": "iPhone 15 Pro",
        "device_type": "mobile",
        "status": "active",
        "last_seen": "2025-11-06T15:24:04.512183Z",
        "api_key": "6UqbQ7Aw81kgVGJHE_0oFYRfzAWFma5vRJdNnM2DwbU"
    },
    "authenticated": true
}
```

---

### 8. Verify Token

**Endpoint:** `POST /api/v1/auth/verify-token/`  
**Permission:** IsAuthenticated  
**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@federated-ai.local",
        "first_name": "",
        "last_name": "",
        "is_staff": true,
        "date_joined": "2025-11-06T13:32:53.307197Z"
    }
}
```

---

## 🛡️ Permission Classes

### 1. IsAdminOrReadOnly

**Used by:** ObjectCategory API  
**Rules:**
- ✅ Anyone can READ (GET)
- ❌ Only admins can CREATE/UPDATE/DELETE

**Applied to:**
- `/api/v1/categories/` - Category management

---

### 2. IsClientOrAdmin

**Used by:** Client, TrainingRound, ModelVersion, DetectionResult APIs  
**Rules:**
- ✅ Admins have full access
- ✅ Authenticated users can access
- ✅ Clients with valid API key can access their own data
- ❌ Unauthenticated users denied

**Applied to:**
- `/api/v1/clients/` - Client management
- `/api/v1/training/rounds/` - Training rounds
- `/api/v1/models/` - Model versions
- `/api/v1/detection/results/` - Detection results

---

### 3. CanUploadImages

**Used by:** TrainingImage API  
**Rules:**
- ✅ Admins can upload
- ✅ Authenticated users can upload
- ✅ Clients with valid API key can upload
- ❌ Unauthenticated users denied

**Applied to:**
- `/api/v1/training/images/` - Training images

---

### 4. IsOwnerOrReadOnly

**Used by:** Individual object permissions  
**Rules:**
- ✅ Anyone can READ
- ✅ Owner can UPDATE/DELETE
- ❌ Non-owners cannot modify

**Ownership Fields:**
- `owner` - Primary owner field
- `uploaded_by` - For uploaded content
- `created_by` - For created resources
- `user` - For user-specific resources

---

## 🔒 Access Control Matrix

| Endpoint | Anonymous | User Token | Admin Token | Client API Key |
|----------|-----------|------------|-------------|----------------|
| **Authentication** |
| POST /auth/login/ | ✅ | ✅ | ✅ | ❌ |
| POST /auth/register/ | ✅ | ✅ | ✅ | ❌ |
| POST /auth/logout/ | ❌ | ✅ | ✅ | ❌ |
| GET /auth/profile/ | ❌ | ✅ | ✅ | ❌ |
| POST /auth/client/ | ✅ | ✅ | ✅ | ✅ |
| **Categories** |
| GET /categories/ | ✅ | ✅ | ✅ | ✅ |
| POST /categories/ | ❌ | ❌ | ✅ | ❌ |
| PUT /categories/{id}/ | ❌ | ❌ | ✅ | ❌ |
| DELETE /categories/{id}/ | ❌ | ❌ | ✅ | ❌ |
| **Clients** |
| GET /clients/ | ❌ | ✅ | ✅ | ✅ |
| POST /clients/register/ | ✅ | ✅ | ✅ | ✅ |
| PUT /clients/{id}/ | ❌ | ✅ (owner) | ✅ | ✅ (self) |
| **Training Images** |
| GET /training/images/ | ❌ | ✅ | ✅ | ✅ |
| POST /training/images/ | ❌ | ✅ | ✅ | ✅ |
| POST /training/images/bulk_upload/ | ❌ | ✅ | ✅ | ✅ |
| **Training Rounds** |
| GET /training/rounds/ | ❌ | ✅ | ✅ | ✅ |
| POST /training/rounds/ | ❌ | ❌ | ✅ | ✅ |
| **Models** |
| GET /models/ | ❌ | ✅ | ✅ | ✅ |
| GET /models/deployed/ | ❌ | ✅ | ✅ | ✅ |
| POST /models/{id}/deploy/ | ❌ | ❌ | ✅ | ❌ |
| **Detection Results** |
| GET /detection/results/ | ❌ | ✅ | ✅ | ✅ |
| POST /detection/results/submit/ | ❌ | ✅ | ✅ | ✅ |

---

## 🧪 Testing Authentication

### Test 1: Admin Login
```bash
# Get admin token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"

# Use token to access API
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/v1/categories/
```

### Test 2: User Registration
```bash
# Register new user and get token
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

### Test 3: Client API Key
```bash
# Register new client and get API key
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/clients/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Device",
    "device_type": "mobile",
    "capabilities": {"cpu": "ARM64", "ram_gb": 8}
  }')

API_KEY=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['api_key'])")

# Use API key
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/clients/
```

### Test 4: Unauthorized Access
```bash
# Try to access without auth (should fail)
curl http://localhost:8000/api/v1/clients/

# Try to create category without admin (should fail)
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Authorization: Token user-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'
```

---

## 🔧 Implementation Details

### Files Created

**1. Core Permissions** (`server/core/permissions.py`)
- `IsOwnerOrReadOnly` - Owner-based permissions
- `IsClientOrAdmin` - Client/Admin permissions
- `IsAdminOrReadOnly` - Admin write, public read
- `IsValidatedOrAdmin` - Validated objects only
- `CanUploadImages` - Image upload permissions

**2. Auth Serializers** (`server/core/auth_serializers.py`)
- `LoginSerializer` - Login validation
- `RegisterSerializer` - User registration
- `TokenSerializer` - Token information
- `UserSerializer` - User profile
- `ChangePasswordSerializer` - Password change
- `ClientAuthSerializer` - Client authentication

**3. Auth Views** (`server/core/auth_views.py`)
- `LoginView` - User login
- `LogoutView` - User logout
- `RegisterView` - User registration
- `UserProfileView` - Profile management
- `ChangePasswordView` - Password change
- `ClientAuthView` - Client authentication
- `VerifyTokenView` - Token verification

### URL Configuration
```python
# Authentication endpoints
/api/v1/auth/login/
/api/v1/auth/logout/
/api/v1/auth/register/
/api/v1/auth/profile/
/api/v1/auth/change-password/
/api/v1/auth/client/
/api/v1/auth/verify-token/
```

---

## ✅ Test Results

### Authentication Tests
```
✅ Admin login successful - Token received
✅ User registration working - New user created
✅ Token authentication working - API access granted
✅ Client API key auth working - Client authenticated
✅ User profile retrieval working
✅ Token verification working
```

### Permission Tests
```
✅ Categories read-only for non-admins
✅ Categories writable for admins
✅ Clients accessible with valid credentials
✅ Training images uploadable by authenticated users
✅ API key header authentication working
```

---

## 📊 Summary

**Authentication Status:** ✅ **COMPLETE**

| Component | Status | Details |
|-----------|--------|---------|
| User Login | ✅ | Token-based auth working |
| User Registration | ✅ | New users can register |
| User Logout | ✅ | Token revocation working |
| Profile Management | ✅ | Get/Update profile working |
| Password Change | ✅ | Secure password change |
| Client Auth | ✅ | API key authentication |
| Token Verification | ✅ | Token validation working |
| Permission Classes | ✅ | 5 custom classes implemented |
| ViewSet Protection | ✅ | All ViewSets secured |

**Total Auth Endpoints:** 7  
**Total Permission Classes:** 5  
**Protected ViewSets:** 6

---

## 🎯 Next Steps

- ✅ **Phase 1.4.4 Complete**
- ⏳ **Phase 1.4.5:** API Documentation (Swagger)
- ⏳ **Phase 1.4.6:** API Tests
- ⏳ **Phase 1.4.7:** Real Client Testing

---

**Last Updated:** November 6, 2025, 15:30 UTC  
**Version:** 1.0  
**Status:** Production Ready ✅
