# Business Creation 403 Debugging Guide

## Issue Description
Business creation is failing with a 403 Forbidden HTTP status code. The logs show:
```
INFO:     37.223.245.13:0 - "POST /api/v1/businesses/ HTTP/1.1" 403 Forbidden
INFO:httpx:HTTP Request: GET https://xflkldekhpqjpdrpeupg.supabase.co/auth/v1/user "HTTP/2 200 OK"
INFO:httpx:HTTP Request: GET https://xflkldekhpqjpdrpeupg.supabase.co/auth/v1/user "HTTP/2 200 OK"
INFO:httpx:HTTP Request: PUT https://xflkldekhpqjpdrpeupg.supabase.co/auth/v1/admin/users/3eb19c13-4347-4c8b-8eb8-bf18747e8946 "HTTP/2 200 OK"
```

## Debugging Changes Made

### 1. Enhanced Authentication Debugging (`backend/app/api/deps.py`)
- Added comprehensive logging to `get_current_user()` function
- Track token validation and user data extraction
- Log authentication failures with detailed error messages
- Debug business controller dependency injection

### 2. Business Route Debugging (`backend/app/api/routes/businesses.py`)
- Added logging to the business creation endpoint
- Track incoming requests, user data, and controller instances
- Log successful business creation and catch exceptions

### 3. Business Controller Debugging (`backend/app/api/controllers/business_controller.py`)
- Enhanced logging in `create_business()` method
- Track DTO conversion, use case execution, and response generation
- Categorize exceptions (ValidationError, BusinessLogicError, ApplicationError)

### 4. Repository Debugging (`backend/app/infrastructure/database/repositories/supabase_business_repository.py`)
- Added logging to Supabase business creation operations
- Track database requests and responses
- Monitor potential RLS (Row Level Security) issues

### 5. Use Case Debugging (`backend/app/application/use_cases/business/create_business.py`)
- Comprehensive logging throughout the business creation flow
- Track validation, uniqueness checks, entity creation, and membership creation
- Enhanced error handling and reporting

### 6. Auth Middleware Debugging (`backend/app/api/middleware/auth_handler.py`)
- Enhanced request processing logging
- Track token extraction and validation
- Monitor authentication state and response status codes

## Potential Root Causes

### 1. Authentication Issues
- **Token Validation**: The JWT token might be invalid or expired
- **User Context**: Current user data might not be properly extracted
- **Supabase Auth**: Issues with Supabase authentication validation

### 2. Authorization Issues
- **RLS Policies**: Supabase Row Level Security might be blocking the insert
- **Business Logic**: Permission checks in the business creation flow
- **Middleware**: Authentication middleware might be rejecting the request

### 3. Database Issues
- **Connection**: Supabase client connection problems
- **Schema**: Table permissions or schema mismatches
- **Constraints**: Database constraint violations

### 4. Application Logic Issues
- **Dependency Injection**: Problems with use case or repository instantiation
- **Error Handling**: Incorrect error mapping or response codes
- **Configuration**: Missing or incorrect configuration values

## Testing Instructions

### 1. Enable Debug Logging
Ensure your logging configuration includes DEBUG level:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 2. Test Business Creation
Make a POST request to create a business and monitor logs:
```bash
curl -X POST "http://localhost:8000/api/v1/businesses/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Business",
    "industry": "technology",
    "company_size": "small"
  }'
```

### 3. Monitor Logs
Watch for these key log messages in sequence:

#### Authentication Flow:
1. `AuthMiddleware processing request: POST /api/v1/businesses/`
2. `get_current_user called with token: ...`
3. `Successfully authenticated user: [user_id], email: [email]`

#### Business Creation Flow:
4. `get_business_controller called`
5. `create_business endpoint called`
6. `create_business called for user: [user_id]`
7. `execute() called with business name: [name], owner: [owner_id]`
8. `Business created successfully: [business_id]`

### 4. Error Analysis
If the flow breaks at any point, the logs will show:
- **Authentication errors**: Look for token validation failures
- **Controller errors**: Check dependency injection issues
- **Use case errors**: Monitor validation or business logic failures
- **Repository errors**: Watch for database/Supabase errors

## Expected Log Output (Success Case)
```
INFO:AuthMiddleware processing request: POST /api/v1/businesses/
INFO:Token extracted: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
INFO:get_current_user called with token: eyJ0eXAiOiJKV1Q...
INFO:Successfully authenticated user: 3eb19c13-4347-4c8b-8eb8-bf18747e8946, email: user@example.com
INFO:get_business_controller called
INFO:BusinessController initialized successfully
INFO:create_business endpoint called
INFO:create_business called for user: 3eb19c13-4347-4c8b-8eb8-bf18747e8946
INFO:execute() called with business name: Test Business, owner: 3eb19c13-4347-4c8b-8eb8-bf18747e8946
INFO:Business created successfully: [business_id]
```

## Troubleshooting Steps

### If 403 occurs before authentication logs:
- Check middleware configuration
- Verify API route registration
- Review CORS settings

### If 403 occurs after authentication but before business creation:
- Check authorization middleware
- Verify user permissions
- Review business controller dependencies

### If 403 occurs during business creation:
- Check Supabase RLS policies
- Verify database permissions
- Review business validation logic

### If 403 occurs during database operations:
- Check Supabase client configuration
- Verify table permissions
- Review RLS policies for businesses table

## Next Steps
1. Run the business creation request with the enhanced logging
2. Share the complete log output from the request
3. We'll analyze the exact point where the 403 error occurs
4. Implement targeted fixes based on the root cause identified

## RLS Policy Check
Verify your Supabase RLS policies for the `businesses` table:
```sql
-- Check existing policies
SELECT * FROM pg_policies WHERE tablename = 'businesses';

-- Ensure INSERT policy exists for authenticated users
CREATE POLICY "Users can create businesses" ON businesses
  FOR INSERT WITH CHECK (auth.uid()::text = owner_id);
``` 