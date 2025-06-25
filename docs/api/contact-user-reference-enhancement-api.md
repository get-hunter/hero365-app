# Contact User Reference Enhancement API

## Overview
This document outlines the enhancement for handling user references (`assigned_to` and `created_by`) in contact responses, providing embedded user information to eliminate N+1 queries.

## Current State
Currently, contacts return user references as simple string IDs:
```json
{
  "assigned_to": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## Enhanced Approach: Embedded User Objects

### 1. Default Response (Basic User Info)
By default, contacts will return embedded user objects with essential information:

```json
{
  "assigned_to": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "display_name": "John Doe",
    "email": "john.doe@example.com"
  },
  "created_by": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "display_name": "Jane Smith", 
    "email": "jane.smith@example.com"
  }
}
```

### 2. Expanded Response (Full User Info)
When `?include_user_details=full` is specified, additional user information is included:

```json
{
  "assigned_to": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "display_name": "John Doe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "role": "manager",
    "department": "Sales",
    "is_active": true
  },
  "created_by": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "display_name": "Jane Smith",
    "email": "jane.smith@example.com", 
    "full_name": "Jane Smith",
    "phone": "+1987654321",
    "role": "admin",
    "department": "Operations",
    "is_active": true
  }
}
```

### 3. Minimal Response
When `?include_user_details=none` is specified, only user IDs are returned:

```json
{
  "assigned_to": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

## API Endpoints Enhancement

### GET /contacts
**Query Parameters:**
- `include_user_details`: `none`, `basic` (default), `full`

### GET /contacts/{contact_id}
**Query Parameters:**
- `include_user_details`: `none`, `basic` (default), `full`

### POST /contacts/search
**Request Body Enhancement:**
```json
{
  "search_term": "customer name",
  "include_user_details": "basic"
}
```

## Schema Changes

### New User Reference Schemas

```python
class UserReferenceBasic(BaseModel):
    """Basic user reference information."""
    id: str = Field(..., description="User ID")
    display_name: str = Field(..., description="User display name")
    email: Optional[str] = Field(None, description="User email")

class UserReferenceFull(BaseModel):
    """Full user reference information."""
    id: str = Field(..., description="User ID")
    display_name: str = Field(..., description="User display name")
    email: Optional[str] = Field(None, description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: Optional[str] = Field(None, description="Business role")
    department: Optional[str] = Field(None, description="Department")
    is_active: bool = Field(True, description="Active status")

# Enum for user detail inclusion levels
class UserDetailLevel(str, Enum):
    """User detail inclusion levels."""
    NONE = "none"
    BASIC = "basic" 
    FULL = "full"
```

### Enhanced Contact Response Schema

```python
class ContactResponse(BaseModel):
    # ... existing fields ...
    
    # Enhanced user reference fields (conditional based on include_user_details)
    assigned_to: Optional[Union[str, UserReferenceBasic, UserReferenceFull]] = Field(None, description="Assigned user (ID or object based on include_user_details)")
    created_by: Optional[Union[str, UserReferenceBasic, UserReferenceFull]] = Field(None, description="Creator user (ID or object based on include_user_details)")
```

### Enhanced Request Schemas

```python
class ContactSearchRequest(BaseModel):
    # ... existing fields ...
    include_user_details: UserDetailLevel = Field(UserDetailLevel.BASIC, description="Level of user detail to include")
```

## Benefits

### Performance
1. **Eliminated N+1 Queries**: No separate user lookup requests needed
2. **Optimized Database Queries**: Single query with LEFT JOINs for user data
3. **Flexible Loading**: Choose appropriate detail level based on use case

### User Experience
1. **Immediate Display**: User names available for immediate UI rendering
2. **Progressive Enhancement**: Basic info by default, detailed info on demand
3. **Reduced Loading States**: No secondary loading for user information

### Development
1. **Type Safety**: Strongly typed user reference objects
2. **Cleaner API**: No need to manage separate user ID fields
3. **Consistent Pattern**: Same approach can be applied to other entities

## Implementation Strategy

### Phase 1: Schema Enhancement
1. Add new user reference schemas and enums
2. Update ContactResponse with Union types for user fields
3. Add `include_user_details` parameter to request schemas

### Phase 2: Repository Enhancement
1. Modify contact repository to optionally JOIN user data from auth.users
2. Implement query parameter handling for user detail levels
3. Add user data transformation logic

### Phase 3: API Enhancement
1. Update contact endpoints with new query parameters
2. Implement conditional user detail inclusion logic
3. Update response transformation methods

### Phase 4: Frontend Adaptation
1. Update client SDK with new response types
2. Modify UI components to use embedded user data
3. Remove separate user API calls from contact views

## Database Query Optimization

### Basic User Details Query
```sql
SELECT 
    c.*,
    json_build_object(
        'id', au.id,
        'display_name', COALESCE(au.full_name, au.email),
        'email', au.email
    ) as assigned_user_data,
    json_build_object(
        'id', cu.id,
        'display_name', COALESCE(cu.full_name, cu.email), 
        'email', cu.email
    ) as creator_user_data
FROM contacts c
LEFT JOIN auth.users au ON c.assigned_to = au.id
LEFT JOIN auth.users cu ON c.created_by = cu.id
WHERE c.business_id = $1;
```

### Full User Details Query
```sql
SELECT 
    c.*,
    json_build_object(
        'id', au.id,
        'display_name', COALESCE(au.full_name, au.email),
        'email', au.email,
        'full_name', au.full_name,
        'phone', au.phone,
        'role', bm_a.role,
        'department', bm_a.job_title,
        'is_active', au.is_active
    ) as assigned_user_data,
    json_build_object(
        'id', cu.id,
        'display_name', COALESCE(cu.full_name, cu.email),
        'email', cu.email,
        'full_name', cu.full_name,
        'phone', cu.phone,
        'role', bm_c.role,
        'department', bm_c.job_title,
        'is_active', cu.is_active
    ) as creator_user_data
FROM contacts c
LEFT JOIN auth.users au ON c.assigned_to = au.id
LEFT JOIN auth.users cu ON c.created_by = cu.id
LEFT JOIN business_memberships bm_a ON au.id = bm_a.user_id AND bm_a.business_id = c.business_id
LEFT JOIN business_memberships bm_c ON cu.id = bm_c.user_id AND bm_c.business_id = c.business_id
WHERE c.business_id = $1;
```

## Migration Guide

### For API Consumers
```typescript
// Before
const contact = await api.contacts.getContact(contactId);
const assignedUserId = contact.assigned_to; // string ID
const assignedUser = await api.users.getUser(assignedUserId);

// After
const contact = await api.contacts.getContact(contactId); // basic user info by default
const assignedUser = contact.assigned_to; // UserReferenceBasic object

// For full user details
const contactWithFullUserInfo = await api.contacts.getContact(contactId, { 
  include_user_details: 'full' 
});
const assignedUser = contactWithFullUserInfo.assigned_to; // UserReferenceFull object

// For minimal response (ID only)
const contactMinimal = await api.contacts.getContact(contactId, { 
  include_user_details: 'none' 
});
const assignedUserId = contactMinimal.assigned_to; // string ID
```

## Security Considerations

1. **Permission-Based Filtering**: User details only shown based on requester's permissions within the business
2. **Business Context**: Only show user details for users within the same business context
3. **Data Minimization**: Sensitive user data (like personal phone) only included in full detail mode
4. **Privacy Compliance**: User email and phone excluded if user privacy settings restrict it

## Conclusion

This streamlined approach provides:
- **Performance**: Eliminates N+1 queries for user data
- **Flexibility**: Three levels of user detail inclusion
- **Simplicity**: Clean API without legacy compatibility concerns
- **User Experience**: Immediate access to user information for UI rendering
- **Consistency**: Uniform pattern for user references across the application

The implementation can be done incrementally, starting with the schema changes and moving through repository, API, and frontend updates. 