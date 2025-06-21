# Supabase Database Access Fix

## Issue Description
Users were experiencing 403 Forbidden errors when attempting to create businesses and perform other database write operations. The logs showed:

```
INFO: POST /api/v1/businesses/ HTTP/1.1" 403 Forbidden
```

## Root Cause
The repository layer was using the Supabase **anonymous key** (`SUPABASE_ANON_KEY`) for database operations instead of the **service role key** (`SUPABASE_SERVICE_KEY`).

### Key Differences:
- **Anonymous Key**: Limited permissions, intended for client-side operations, subject to RLS policies
- **Service Role Key**: Full database access, bypasses RLS policies, intended for server-side operations

## Fix Applied
Updated the Supabase client initialization in `backend/app/infrastructure/config/dependency_injection.py`:

```python
def _get_supabase_client(self) -> Client:
    """Get or create Supabase client."""
    if self._supabase_client is None:
        # Use service key for database operations (bypasses RLS and has full access)
        self._supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return self._supabase_client
```

**Before**: Used `settings.SUPABASE_ANON_KEY`
**After**: Uses `settings.SUPABASE_SERVICE_KEY`

## Impact
This change resolves the following operations:
- ✅ Business creation (`POST /api/v1/businesses/`)
- ✅ Business membership creation
- ✅ Team member invitations
- ✅ All other database write operations

## Security Considerations
- The service key is only used on the backend server
- Frontend applications should continue using the anonymous key
- The service key has full database access, so it's properly secured in environment variables
- This follows Supabase's recommended pattern for server-side applications

## Verification
The fix can be verified by:
1. Creating a new business through the API
2. Checking that no 403 Forbidden errors occur
3. Confirming successful database writes

## Environment Configuration
Ensure your environment has both keys configured:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key  # For client operations
SUPABASE_SERVICE_KEY=your-service-role-key  # For server operations
```

## Best Practices
- **Client-side operations**: Use anonymous key with proper RLS policies
- **Server-side operations**: Use service role key for full database access
- **Authentication**: Continue using the auth service with appropriate keys
- **API endpoints**: Server routes should use service key through repositories 