# Business Creation API Fix

## Issue Summary
The business creation API was failing due to two critical issues:
1. **Authentication Token Loss**: 307 redirects were stripping Authorization headers
2. **Database Type Mismatch**: JSONB permissions were being sent as JSON strings instead of arrays

## Fixes Applied

### 1. Authentication Token Loss Fix

**Problem**: iOS app called `/api/v1/businesses` but route required `/api/v1/businesses/` (trailing slash). FastAPI automatically redirected with 307, causing Authorization header loss.

**Solution**: 
- Added `redirect_slashes=False` to FastAPI configuration in `backend/app/main.py`
- Added route handler for exact path without trailing slash in `backend/app/api/routes/businesses.py`

```python
# backend/app/main.py
application = FastAPI(
    # ...
    redirect_slashes=False,  # Prevent automatic redirects that strip auth headers
)

# backend/app/api/routes/businesses.py  
@router.post("", response_model=BusinessResponse, status_code=201)  # Handles /businesses
@router.post("/", response_model=BusinessResponse, status_code=201) # Handles /businesses/
```

### 2. Database JSONB Type Fix

**Problem**: Database expected JSONB array for `permissions` field, but repositories were sending JSON strings using `json.dumps()`. This caused PostgreSQL error: "cannot get array length of a scalar" (code 22023).

**Solution**: Send permissions as list directly to Supabase, not as JSON string.

**Files Fixed**:
- `backend/app/infrastructure/database/repositories/supabase_business_membership_repository.py`
- `backend/app/infrastructure/database/repositories/supabase_business_invitation_repository.py`

```python
# Before (broken)
"permissions": json.dumps(membership.permissions),
permissions=json.loads(data["permissions"]),

# After (fixed)  
"permissions": membership.permissions,  # Send as list directly
permissions=data["permissions"],        # Already a list from JSONB
```

## Result
Business creation now works successfully:
- ✅ Authentication token properly received and validated
- ✅ Business entity created in database
- ✅ Owner membership created without JSONB errors
- ✅ Complete business setup process functional

## Client Implementation
iOS app should continue using the exact URL path: `POST /api/v1/businesses` (without trailing slash). 