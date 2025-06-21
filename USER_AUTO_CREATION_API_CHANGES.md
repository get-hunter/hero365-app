# User Auto-Creation API Changes

## Overview
This document describes the API changes made to fix the issue where users authenticated via Supabase Auth (OAuth) could not create businesses because they didn't exist in the local users table.

## Problem Description
- Users could successfully authenticate with Supabase Auth (OAuth providers like Google, Apple)
- Authentication tokens were valid and passed verification
- When trying to create a business, the API returned `403 Forbidden`
- Root cause: User existed in Supabase Auth but not in the local `users` table

## Solution Implemented

### Modified Endpoint
**Endpoint:** All authenticated endpoints (via `get_current_user` dependency)
**Change:** Automatic user creation when user exists in Supabase Auth but not locally

### Implementation Details

#### 1. Modified `get_current_user` Dependency
**File:** `backend/app/api/deps.py`

The dependency now includes an additional step:
1. Verifies token with Supabase Auth
2. **NEW:** Checks if user exists in local users table
3. **NEW:** Automatically creates user in local table if missing
4. Returns user data

#### 2. User Auto-Creation Logic
When a user is authenticated via Supabase but doesn't exist locally:

```python
# Extract user info from Supabase Auth
create_user_dto = CreateUserDTO(
    email=supabase_user_data.get("email"),
    phone=supabase_user_data.get("phone"), 
    full_name=user_metadata.get("full_name"),
    is_active=True,
    is_superuser=False,
    supabase_id=supabase_id
)

# Create user using OAuth registration method
await create_user_use_case.execute_oauth_registration(create_user_dto)
```

#### 3. Error Handling
- If user creation fails, authentication still succeeds
- Error is logged but doesn't block the request
- User remains authenticated via Supabase Auth

## API Behavior Changes

### Before Fix
1. User authenticates with OAuth → ✅ Success
2. User tries to create business → ❌ 403 Forbidden
3. Error: User not found in local database

### After Fix  
1. User authenticates with OAuth → ✅ Success
2. **NEW:** System auto-creates user in local database → ✅ Success
3. User tries to create business → ✅ Success

## Client Impact

### No Breaking Changes
- Existing API endpoints remain unchanged
- Response formats are identical
- No client code changes required

### Improved User Experience
- OAuth users can immediately use business creation features
- No manual user registration required
- Seamless authentication experience

## Technical Details

### Database Changes
- No schema changes required
- Uses existing `users` table structure
- Leverages existing `execute_oauth_registration` method

### Security Considerations
- User creation only happens for verified Supabase Auth tokens
- Users are created with `is_superuser=false` by default
- Supabase ID is preserved for future lookups

### Performance Impact
- Minimal overhead: One additional database lookup per authentication
- User creation only happens once per user
- Subsequent requests use existing user record

## Testing Recommendations

### Test Scenarios
1. **New OAuth User**: First-time OAuth login should create local user
2. **Existing OAuth User**: Subsequent logins should not create duplicate users  
3. **Business Creation**: OAuth users should be able to create businesses immediately
4. **Error Resilience**: Failed user creation should not block authentication

### Verification Steps
1. Authenticate with OAuth provider
2. Check that user exists in local `users` table
3. Verify business creation works without 403 error
4. Confirm user has correct `supabase_id` mapping

## Migration Notes

### Deployment Steps
1. Deploy code changes
2. No database migrations required
3. Existing OAuth users will be auto-created on next login

### Rollback Plan
- Remove auto-creation logic from `get_current_user`
- Existing created users will remain in database
- Business creation may fail again for OAuth-only users

## Related Files Changed
- `backend/app/api/deps.py` - Modified `get_current_user` dependency
- `backend/app/application/dto/user_dto.py` - Added `is_active` field to `CreateUserDTO`

## Issue Resolution
This change resolves the following error pattern:
```
INFO:     37.223.245.13:0 - "POST /api/v1/businesses/ HTTP/1.1" 403 Forbidden
INFO:httpx:HTTP Request: GET https://xflkldekhpqjpdrpeupg.supabase.co/auth/v1/user "HTTP/2 200 OK"
INFO:httpx:HTTP Request: GET https://xflkldekhpqjpdrpeupg.supabase.co/rest/v1/users?select=%2A&id=eq.ec64fc30-6375-43da-99c8-71c2c1df70d3 "HTTP/2 404 Not Found"
```

After fix:
- Supabase Auth verification: ✅ 200 OK
- Local user lookup: ✅ User auto-created if missing
- Business creation: ✅ 201 Created 