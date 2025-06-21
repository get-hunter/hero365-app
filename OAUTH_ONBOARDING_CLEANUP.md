# OAuth Authentication Onboarding Logic Cleanup

## Overview
Removed legacy onboarding metadata handling from OAuth authentication flows since onboarding completion is now determined purely by business membership status.

## Changes Made

### 1. **OAuth Controller Cleanup**
**File**: `backend/app/api/controllers/oauth_controller.py`

#### Removed Logic:
- ❌ Default onboarding metadata setting for new users
- ❌ Onboarding data retrieval from user metadata  
- ❌ Onboarding fields in AuthUserResponse creation

#### Before:
```python
# For new users, ensure onboarding metadata is set to default values
if is_new_user:
    default_onboarding_metadata = {
        "onboarding_completed": False,
        "completed_steps": []
    }
    await self._update_user_metadata_if_needed(user_data.id, default_onboarding_metadata)

onboarding_data = self.auth_facade.get_onboarding_data(user_metadata)

user_response = AuthUserResponse(
    # ... other fields ...
    onboarding_completed=onboarding_data["onboarding_completed"],
    onboarding_completed_at=onboarding_data["onboarding_completed_at"],
    completed_steps=onboarding_data["completed_steps"]
)
```

#### After:
```python
# Get user metadata for basic profile information
auth_service = self.container.get_auth_service()
updated_user_result = await auth_service.get_user_by_id(user_data.id)

user_response = AuthUserResponse(
    # ... other fields ...
    # No onboarding fields - determined by business membership
)
```

### 2. **Auth Schema Cleanup**
**File**: `backend/app/api/schemas/auth_schemas.py`

#### Removed Fields:
```python
# ❌ REMOVED from AuthUserResponse
onboarding_completed: Optional[bool] = None
onboarding_completed_at: Optional[datetime] = None  
completed_steps: Optional[List[str]] = None
```

#### Updated Serialization:
```python
# Before
@field_serializer('last_login', 'onboarding_completed_at')

# After  
@field_serializer('last_login')
```

## Impact on Sign-In Flow

### Apple Sign-In
- **Before**: Sets onboarding metadata, retrieves onboarding data, returns onboarding fields
- **After**: Only handles basic user profile data, no onboarding logic

### Google Sign-In  
- **Before**: Sets onboarding metadata, retrieves onboarding data, returns onboarding fields
- **After**: Only handles basic user profile data, no onboarding logic

## Log Output Changes

### Before (What Was Causing the Issue):
```
🔍 Onboarding data: {'onboarding_completed': False, 'onboarding_completed_at': None, 'completed_steps': []}
📝 Set default onboarding metadata for new user: {'onboarding_completed': False, 'completed_steps': []}
```

### After (Clean):
```
🔍 Is new user: true
🔍 Retrieved user metadata: {'email': 'user@example.com', 'full_name': 'User Name'}
✅ Apple Sign-In successful for Supabase user: uuid
```

## API Response Changes

### OAuth Sign-In Response - AuthUserResponse

#### Before:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "is_superuser": false,
  "supabase_id": "uuid",
  "onboarding_completed": false,
  "onboarding_completed_at": null,
  "completed_steps": []
}
```

#### After:
```json
{
  "id": "uuid", 
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "is_superuser": false,
  "supabase_id": "uuid",
  "last_login": "2025-06-21T14:27:12Z"
}
```

## Onboarding Determination

### How Onboarding Status is Now Determined:
1. **OAuth Sign-In**: Returns basic user data only
2. **Client Gets Profile**: Calls `GET /api/v1/users/me`  
3. **Profile Response**: Includes `needs_onboarding` based on business memberships
4. **Client Decision**: Uses `needs_onboarding` field to show/hide onboarding

### Flow:
```
OAuth Sign-In → Basic User Data
     ↓
GET /users/me → Business Membership Check → needs_onboarding: true/false
     ↓
Client Shows Onboarding (if true) or Main App (if false)
```

## Benefits

### 1. **Simplified Authentication**
- No complex onboarding metadata handling during sign-in
- Faster authentication response
- Cleaner OAuth controller logic

### 2. **Single Source of Truth**  
- Onboarding status determined in one place: `/users/me`
- Based on actual business data, not arbitrary metadata flags
- Self-healing onboarding status

### 3. **Reduced Complexity**
- Fewer fields to manage
- No metadata synchronization issues
- Cleaner API responses

### 4. **Better Reliability**
- No risk of inconsistent onboarding states
- Failed business creation doesn't leave orphaned onboarding flags
- Automatic onboarding completion when joining businesses

## Testing

### Verify Clean Authentication:
1. Sign in with Apple/Google
2. Check logs for absence of onboarding data messages
3. Verify AuthUserResponse doesn't include onboarding fields
4. Confirm `/users/me` still provides `needs_onboarding` status

### Test Cases:
- [ ] New user Apple sign-in (no onboarding metadata set)
- [ ] New user Google sign-in (no onboarding metadata set)
- [ ] Existing user sign-in (no onboarding fields in response)
- [ ] Verify `/users/me` still works for onboarding status 