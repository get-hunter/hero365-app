# Permission System Enhancement API Documentation

## Overview

This document describes the enhancements made to the Hero365 permission system to fix contact access issues and improve the overall authorization architecture.

## Changes Made

### 1. Added Missing Permission Decorators

**Problem**: Contact API endpoints were missing permission decorators, causing permission checks to be bypassed.

**Solution**: Added appropriate permission decorators to all contact endpoints:

```python
# View operations require view_contacts permission
@require_view_contacts
async def list_contacts(...):
    pass

@require_view_contacts  
async def get_contact(...):
    pass

@require_view_contacts
async def search_contacts(...):
    pass

# Edit operations require edit_contacts permission
@require_edit_contacts
async def create_contact(...):
    pass

@require_edit_contacts
async def update_contact(...):
    pass

# Delete operations require delete_contacts permission
@require_delete_contacts
async def delete_contact(...):
    pass
```

### 2. Enhanced Permission Assignment System

**Problem**: Business memberships were created with empty permission arrays, violating the database constraint and causing permission denials.

**Solution**: 
- Created database functions to automatically assign default permissions based on user roles
- Added triggers to ensure permissions are always assigned when memberships are created or updated
- Fixed existing memberships with empty permission arrays

### 3. Simplified Owner Permissions

**Problem**: Owners had to be manually granted each individual permission, making the system inflexible for new permissions.

**Solution**: Introduced wildcard permission system:
- Owners now get a special `"*"` permission that grants access to everything
- Permission checking logic updated to handle wildcard permissions
- Future-proof system that automatically includes new permissions for owners

## Permission System Architecture

### Role Hierarchy

1. **Owner** (Level 5) - Wildcard permissions (`"*"`) - All current and future permissions
2. **Admin** (Level 4) - Most business operations except business profile editing
3. **Manager** (Level 3) - Team leadership and project management
4. **Employee** (Level 2) - Day-to-day operational tasks
5. **Contractor** (Level 1) - Limited project access
6. **Viewer** (Level 0) - Read-only access

### Default Permission Sets

#### Owner Role
```json
{
  "permissions": [
    "view_contacts", "create_contacts", "edit_contacts", "delete_contacts",
    "view_jobs", "create_jobs", "edit_jobs", "delete_jobs",
    "view_projects", "create_projects", "edit_projects", "delete_projects", 
    "edit_business_profile", "view_business_settings", "edit_business_settings",
    "invite_team_members", "edit_team_members", "remove_team_members",
    "view_invoices", "create_invoices", "edit_invoices", "delete_invoices",
    "view_estimates", "create_estimates", "edit_estimates", "delete_estimates",
    "view_reports", "edit_reports", "view_accounting", "edit_accounting",
    "*"
  ]
}
```

#### Admin Role
```json
{
  "permissions": [
    "view_contacts", "create_contacts", "edit_contacts", "delete_contacts",
    "view_jobs", "create_jobs", "edit_jobs", "delete_jobs",
    "view_projects", "create_projects", "edit_projects", "delete_projects",
    "view_business_settings", "invite_team_members", "edit_team_members",
    "view_invoices", "create_invoices", "edit_invoices", "delete_invoices",
    "view_estimates", "create_estimates", "edit_estimates", "delete_estimates",
    "view_reports", "edit_reports", "view_accounting", "edit_accounting"
  ]
}
```

#### Manager Role  
```json
{
  "permissions": [
    "view_contacts", "create_contacts", "edit_contacts",
    "view_jobs", "create_jobs", "edit_jobs",
    "view_projects", "create_projects", "edit_projects",
    "view_invoices", "create_invoices", "edit_invoices",
    "view_estimates", "create_estimates", "edit_estimates",
    "invite_team_members", "view_reports"
  ]
}
```

#### Employee Role
```json
{
  "permissions": [
    "view_contacts", "create_contacts", "edit_contacts",
    "view_jobs", "create_jobs", "edit_jobs", 
    "view_projects", "create_projects", "edit_projects",
    "view_invoices", "view_estimates"
  ]
}
```

#### Contractor Role
```json
{
  "permissions": [
    "view_contacts", "view_jobs", "view_projects"
  ]
}
```

#### Viewer Role
```json
{
  "permissions": [
    "view_contacts", "view_jobs", "view_projects"
  ]
}
```

## API Endpoints Affected

### Contact Management

All contact endpoints now properly enforce permissions:

#### GET `/api/v1/contacts/` - List Contacts
- **Permission Required**: `view_contacts`
- **Decorator**: `@require_view_contacts`

#### GET `/api/v1/contacts/{contact_id}` - Get Contact
- **Permission Required**: `view_contacts` 
- **Decorator**: `@require_view_contacts`

#### POST `/api/v1/contacts/` - Create Contact
- **Permission Required**: `edit_contacts`
- **Decorator**: `@require_edit_contacts`

#### PUT `/api/v1/contacts/{contact_id}` - Update Contact
- **Permission Required**: `edit_contacts`
- **Decorator**: `@require_edit_contacts`

#### DELETE `/api/v1/contacts/{contact_id}` - Delete Contact
- **Permission Required**: `delete_contacts`
- **Decorator**: `@require_delete_contacts`

#### POST `/api/v1/contacts/search` - Search Contacts
- **Permission Required**: `view_contacts`
- **Decorator**: `@require_view_contacts`

#### POST `/api/v1/contacts/bulk-update` - Bulk Update Contacts
- **Permission Required**: `edit_contacts`
- **Decorator**: `@require_edit_contacts`

#### GET `/api/v1/contacts/statistics/overview` - Contact Statistics
- **Permission Required**: `view_contacts`
- **Decorator**: `@require_view_contacts`

## Database Changes

### New Functions

#### `get_default_permissions_for_role(role_name text) -> jsonb`
Returns default permissions for a given role, with special handling for owners.

#### `assign_default_permissions() -> TRIGGER`
Trigger function that automatically assigns default permissions when memberships are created or updated with empty permission arrays.

#### `user_has_permission(user_permissions jsonb, required_permission text) -> boolean`
Helper function that checks if a user has a specific permission, handling the wildcard `"*"` permission for owners.

### New Views

#### `business_membership_permissions`
Provides a clear view of business membership permissions with special indicators for owners:

```sql
SELECT * FROM business_membership_permissions;
```

**Sample Output**:
```
id         | business_id | user_id | role    | permission_summary | has_all_permissions
-----------|-------------|---------|---------|-------------------|-------------------
uuid-123   | bus-456     | usr-789 | owner   | ALL_PERMISSIONS   | true
uuid-124   | bus-456     | usr-790 | manager | 17 specific perms | false
```

## Permission Checking Logic

### Backend Implementation

The permission system now supports:

1. **Explicit Permission Checking**: Direct lookup of specific permissions
2. **Wildcard Permission Support**: Owners with `"*"` permission have access to everything
3. **Fallback Handling**: Graceful degradation when permission data is missing

```python
# Example permission check
async def check_user_business_permissions(user_id: str, business_id: str, required_permissions: List[str]) -> bool:
    # Get user's permissions for the business
    user_permissions = get_user_permissions(user_id, business_id)
    
    # Special case: wildcard permission grants everything
    if "*" in user_permissions:
        return True
    
    # Check each required permission
    for permission in required_permissions:
        if permission not in user_permissions:
            return False
    
    return True
```

## Error Handling

### Common Permission Errors

#### Insufficient Permissions (403)
```json
{
  "detail": "Insufficient permissions: view_contacts required"
}
```

#### Missing Business Context (400)
```json
{
  "detail": "Business context required for this operation"
}
```

#### User Not Member (403)
```json
{
  "detail": "User is not a member of this business"
}
```

#### Inactive Membership (403)
```json
{
  "detail": "User membership is inactive"
}
```

## Implementation Notes

### Owner Permissions
- Owners automatically receive all current and future permissions via the `"*"` wildcard
- When new permissions are added to the system, owners will automatically have access
- No need to manually update owner permissions when expanding the permission system

### Permission Inheritance
- Permissions are role-based but can be customized per user
- Default permissions are assigned automatically based on role
- Custom permissions can be added or removed as needed

### Future Extensibility
- New permissions can be added to the system without affecting existing users
- Owners will automatically have access to new permissions
- Other roles can be updated via migration or manual assignment

## Migration History

1. **20250623140000_fix_business_membership_permissions.sql**
   - Added default permission assignment functions
   - Fixed existing memberships with empty permission arrays
   - Added permission assignment triggers

2. **20250623140209_simplify_owner_permissions.sql**
   - Introduced wildcard permission system for owners
   - Added helper functions for permission checking
   - Created business_membership_permissions view

## Testing

To test the permission system:

1. **Create a test user with different roles**
2. **Attempt to access contact endpoints**
3. **Verify appropriate permissions are enforced**
4. **Test owner wildcard permissions work for new features**

## Security Considerations

- All API endpoints now properly enforce permissions
- Wildcard permissions are restricted to owners only
- Permission checks happen at multiple layers (middleware, use cases)
- Database constraints ensure permissions are always assigned
- Inactive memberships are properly handled

## Client Integration

The frontend can now rely on proper permission enforcement. The client should:

1. **Handle 403 permission errors gracefully**
2. **Check user permissions before showing UI elements**
3. **Provide clear feedback when users lack permissions**
4. **Support different permission levels in the UI**

## Performance Impact

- Permission checks are optimized with proper indexing
- Wildcard permission checking is fast (simple array lookup)
- Database views provide efficient permission summaries
- Caching can be added at the application layer if needed 