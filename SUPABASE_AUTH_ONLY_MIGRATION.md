# Hero365 Migration: Remove Local Users Table - Use Supabase Auth Only

## Overview
This document outlines the plan to simplify Hero365's architecture by removing the local `users` table and relying entirely on Supabase Auth for user management.

## Current Architecture Analysis

### ✅ Good News: Already Using Supabase User IDs
- **businesses.owner_id**: `TEXT NOT NULL` (Supabase user ID)
- **business_memberships.user_id**: `TEXT NOT NULL` (Supabase user ID)  
- **business_invitations.invited_by**: `TEXT NOT NULL` (Supabase user ID)
- **departments.manager_id**: `TEXT` (Supabase user ID)

The system is **already designed** to work with Supabase user IDs as strings, not foreign keys to a local users table.

## What Needs to be Removed/Modified

### 1. Database Layer
#### Remove Tables:
- ✅ **users table** - Complete removal
- ✅ **Remove all users table migrations**

#### Remove Alembic References:
- Remove users table creation in migrations
- Remove foreign key constraints to users table (items table)

### 2. Domain Layer  
#### Remove Entities:
- ✅ **User entity** (`backend/app/domain/entities/user.py`)
- ✅ **User value objects** (Email, Phone, Password)

#### Remove Repositories:
- ✅ **UserRepository interface** (`backend/app/domain/repositories/user_repository.py`)
- ✅ **SupabaseUserRepository** (`backend/app/infrastructure/database/repositories/supabase_user_repository.py`)

### 3. Application Layer
#### Remove Use Cases:
- ✅ **CreateUserUseCase**
- ✅ **GetUserUseCase** 
- ✅ **UpdateUserUseCase**
- ✅ **DeleteUserUseCase**
- ✅ **ManageOnboardingUseCase**

#### Remove DTOs:
- ✅ **UserDTO classes** (`backend/app/application/dto/user_dto.py`)

### 4. API Layer
#### Remove Routes:
- ✅ **User management routes** (`backend/app/api/routes/users.py`)
- ✅ **User admin endpoints**

#### Remove Schemas:
- ✅ **User schemas** (`backend/app/api/schemas/user_schemas.py`)

#### Remove Controllers:
- ✅ **User controller logic**

### 5. Infrastructure Layer
#### Update Dependency Injection:
- ✅ **Remove user repository bindings**
- ✅ **Remove user use case bindings**

#### Update Auth Dependencies:
- ✅ **Simplify `get_current_user()` to return Supabase user data directly**
- ✅ **Remove local user creation logic**

## What Stays the Same

### ✅ Business Logic - No Changes Needed!
- **Business creation** - Already uses `owner_id: str` 
- **Business memberships** - Already uses `user_id: str`
- **Team invitations** - Already uses `invited_by: str`
- **All business operations** - Already work with string user IDs

### ✅ Authentication - Simplified!
- **OAuth flow remains the same**
- **JWT validation remains the same** 
- **Supabase Auth integration remains the same**

## Features Lost vs. Gained

### ❌ Features Lost (Minor):
1. **User profile management** - No local full_name, phone storage
2. **User search/listing** - No admin user management 
3. **User roles** - No is_superuser flag
4. **User status** - No is_active flag
5. **User creation tracking** - No local created_at timestamps

### ✅ Features Gained (Major):
1. **Simplified architecture** - 50% less code to maintain
2. **Reduced complexity** - No user sync issues 
3. **Better reliability** - Single source of truth (Supabase)
4. **Faster development** - No dual user management
5. **Better OAuth support** - Native Supabase features

## User Data Available from Supabase Auth

When needed, we can get this data from Supabase Auth:
```python
user_data = {
    "id": "ec64fc30-6375-43da-99c8-71c2c1df70d3",
    "email": "user@example.com", 
    "phone": "+1234567890",
    "user_metadata": {
        "full_name": "John Doe",
        "avatar_url": "https://...",
    },
    "created_at": "2023-11-24T...",
    "last_sign_in_at": "2023-11-25T...",
    "is_active": true
}
```

## Migration Steps

### Phase 1: Remove Dependencies (Safe)
1. Remove user-related use cases  
2. Remove user DTOs and schemas
3. Remove user API routes
4. Update dependency injection

### Phase 2: Simplify Auth (Core Change)
1. Update `get_current_user()` to return Supabase user data
2. Remove local user creation logic
3. Update business controllers to use Supabase user data

### Phase 3: Database Cleanup (Final)
1. Drop users table
2. Remove user migrations
3. Update items table to remove foreign key constraints

## Implementation Priority: HIGH ✅

**Recommendation: Proceed with this migration**

The benefits significantly outweigh the losses:
- **Simpler architecture** 
- **Fewer bugs** (no sync issues)
- **Faster development**
- **Better scalability**

The lost features are minor and can be replaced with Supabase Auth features when needed. 