# Enhanced Authentication API Documentation

## Overview

Hero365's enhanced authentication system provides JWT tokens with built-in business context and multi-tenant permissions. This system supports seamless business switching while maintaining secure access control.

## Authentication Flow

### 1. Standard Authentication
Users authenticate using existing Supabase OAuth or email/phone authentication. Upon successful authentication, the system generates enhanced JWT tokens containing business membership information.

### 2. Enhanced JWT Token Structure
```json
{
  "sub": "user_id",
  "user_id": "user_id", 
  "current_business_id": "business_uuid",
  "business_memberships": [
    {
      "business_id": "business_uuid",
      "role": "owner|admin|manager|employee|contractor|viewer",
      "permissions": ["array_of_permissions"],
      "role_level": 5
    }
  ],
  "iat": "timestamp",
  "exp": "timestamp"
}
```

### 3. Business Context Validation
All business-scoped API calls automatically validate:
- User is authenticated
- User is a member of the target business
- User has required permissions for the operation

## API Endpoints

### Business Context Management

#### GET /api/v1/business-context/current
Get current business context information.

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response (200):**
```json
{
  "current_business_id": "123e4567-e89b-12d3-a456-426614174000",
  "available_businesses": [
    {
      "business_id": "123e4567-e89b-12d3-a456-426614174000",
      "business_name": "Demo Plumbing Services",
      "role": "owner",
      "permissions": ["view_contacts", "edit_contacts", ...],
      "role_level": 5
    }
  ],
  "user_id": "user_123"
}
```

#### POST /api/v1/business-context/switch
Switch user's current business context.

**Headers:**
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "business_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response (200):**
```json
{
  "current_business_id": "123e4567-e89b-12d3-a456-426614174000",
  "available_businesses": [...],
  "user_id": "user_123",
  "new_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid business ID format
- `403 Forbidden`: User is not a member of the target business
- `500 Internal Server Error`: Server error during context switch

#### GET /api/v1/business-context/available-businesses
Get detailed list of businesses the current user can access.

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response (200):**
```json
[
  {
    "business_id": "123e4567-e89b-12d3-a456-426614174000",
    "business_name": "Demo Plumbing Services",
    "industry": "plumbing",
    "company_size": "small",
    "role": "owner",
    "permissions": ["view_contacts", "edit_contacts", ...],
    "role_level": 5,
    "team_member_count": 5,
    "is_active": true,
    "created_date": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /api/v1/business-context/refresh-token
Refresh the current JWT token with updated business context.

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "current_business_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user_123"
}
```

## Permission System

### Role Hierarchy
1. **Owner** (Level 5) - Full business control
2. **Admin** (Level 4) - Business management, team management  
3. **Manager** (Level 3) - Project management, team oversight
4. **Employee** (Level 2) - Assigned work management
5. **Contractor** (Level 1) - Limited project access
6. **Viewer** (Level 0) - Read-only access

### Permission Types
- **Data Management**: `view_contacts`, `edit_contacts`, `delete_contacts`, `view_projects`, `edit_projects`, etc.
- **Business Management**: `edit_business_profile`, `view_business_settings`, `edit_business_settings`
- **Team Management**: `invite_team_members`, `edit_team_members`, `remove_team_members`
- **Financial**: `view_reports`, `edit_reports`, `view_accounting`, `edit_accounting`

### Business Context Headers
For business-scoped operations, you can specify business context using:

**Header Method:**
```
X-Business-ID: 123e4567-e89b-12d3-a456-426614174000
```

**Path Parameter Method:**
```
/api/v1/businesses/{business_id}/contacts
```

**Query Parameter Method:**
```
/api/v1/contacts?business_id=123e4567-e89b-12d3-a456-426614174000
```

## Middleware Processing Order

1. **Error Handler Middleware** - Catches and formats all errors
2. **CORS Middleware** - Handles cross-origin requests
3. **Business Context Middleware** - Validates business access
4. **Authentication Middleware** - Validates JWT tokens

## Security Features

### Token Validation
- Enhanced JWT tokens are validated for signature, expiration, and business membership
- Fallback to Supabase token validation for backwards compatibility
- Business memberships are refreshed on each token validation

### Business Isolation
- All business data queries include business_id filtering
- Users can only access businesses they are members of
- Permission validation on every business-scoped operation

### Permission Enforcement
- Route-level permission requirements
- Middleware-level permission checking
- Business context validation on every request

## Integration Examples

### Frontend Usage
```javascript
// Get current business context
const context = await fetch('/api/v1/business-context/current', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Switch business context
const switchResponse = await fetch('/api/v1/business-context/switch', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ business_id: 'new_business_id' })
});

// Use new token for subsequent requests
const { new_token } = await switchResponse.json();
localStorage.setItem('access_token', new_token);
```

### Backend Usage
```python
from fastapi import Request, Depends
from app.api.middleware.auth_handler import require_business_permission

@app.get("/api/v1/businesses/{business_id}/contacts")
async def get_contacts(request: Request, business_id: str):
    # Business context automatically validated by middleware
    require_business_permission(request, "view_contacts")
    # ... implementation
```

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "error": {
    "type": "authentication_failed",
    "message": "Authentication required",
    "code": "UNAUTHORIZED"
  }
}
```

#### 403 Forbidden
```json
{
  "error": {
    "type": "authorization_failed", 
    "message": "Access denied to business context",
    "code": "FORBIDDEN"
  }
}
```

#### 400 Bad Request
```json
{
  "error": {
    "type": "validation_error",
    "message": "Business context required for this operation",
    "code": "VALIDATION_ERROR"
  }
}
```

## Migration from Legacy Tokens

The system supports both enhanced JWT tokens and legacy Supabase tokens:

1. **Legacy Token Support**: Existing Supabase tokens continue to work
2. **Automatic Enhancement**: Legacy tokens are enhanced with business context during validation
3. **Gradual Migration**: Frontend can gradually adopt enhanced tokens
4. **Backwards Compatibility**: No breaking changes to existing authentication flow

This enhanced authentication system provides a solid foundation for Hero365's multi-tenant architecture while maintaining security and user experience. 