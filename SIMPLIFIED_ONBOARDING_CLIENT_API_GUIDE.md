# Simplified Onboarding - Client API Integration Guide

## Overview

This document outlines the API changes for implementing the simplified business-membership-based onboarding system in the Hero365 mobile app client.

## Key API Changes

### What Changed
- **Simplified Logic**: Onboarding completion determined solely by business membership status
- **Removed Fields**: `onboarding_completed`, `onboarding_completed_at`, `completed_steps`
- **Removed Endpoint**: `POST /api/v1/users/me/onboarding-completed`
- **New Logic**: `needs_onboarding = user has NO active business memberships`

## Updated API Endpoint

### GET /api/v1/users/me

**Purpose**: Get current user profile with simplified onboarding status

**Authentication**: Required (Bearer token)

**Response Changes**:

#### REMOVED Fields (Stop Using):
```json
{
  "onboarding_completed": true,           // ❌ REMOVE
  "onboarding_completed_at": "2024-01-02T15:45:00Z",  // ❌ REMOVE  
  "completed_steps": ["profile_setup", "preferences"]  // ❌ REMOVE
}
```

#### NEW Fields (Start Using):
```json
{
  "business_memberships": [
    {
      "business_id": "123e4567-e89b-12d3-a456-426614174000",
      "business_name": "Acme Home Services",
      "role": "Owner",
      "is_owner": true,
      "is_active": true,
      "joined_date": "2024-01-02T16:00:00Z"
    }
  ],
  "has_businesses": true,
  "needs_onboarding": false
}
```

#### Complete New Response Structure:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": null,
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "supabase_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "business_memberships": [
    {
      "business_id": "123e4567-e89b-12d3-a456-426614174000",
      "business_name": "Acme Home Services",
      "role": "Owner",
      "is_owner": true,
      "is_active": true,
      "joined_date": "2024-01-02T16:00:00Z"
    }
  ],
  "has_businesses": true,
  "needs_onboarding": false
}
```

## Field Definitions

### business_memberships (Array)
Array of user's business membership summaries.

**Fields**:
- `business_id` (string): UUID of the business
- `business_name` (string): Display name of the business  
- `role` (string): Human-readable role name (Owner, Manager, Employee, etc.)
- `is_owner` (boolean): True if user is the business owner
- `is_active` (boolean): True if membership is active
- `joined_date` (string): ISO 8601 timestamp when user joined the business

### has_businesses (Boolean)
- `true`: User has at least one business membership
- `false`: User has no business memberships

### needs_onboarding (Boolean)
**Primary field for onboarding logic**:
- `true`: User needs to complete onboarding (has no active business memberships)
- `false`: User has completed onboarding (has at least one active business membership)

## Removed API Endpoint

### ❌ POST /api/v1/users/me/onboarding-completed

**Status**: REMOVED - No longer needed

**Previous Purpose**: Manually mark onboarding as completed

**Why Removed**: Onboarding completion is now automatic when user creates or joins a business

## Onboarding Logic Flow

### Simple Rule
```
if (user.needs_onboarding === true) {
  // Show onboarding flow
} else {
  // Go to main app
}
```

### Automatic Completion Triggers

**Business Creation**:
- User creates business via `POST /api/v1/businesses/`
- System automatically creates owner membership
- Next `/users/me` call returns `needs_onboarding: false`

**Business Invitation Acceptance**:
- User accepts invitation via business invitation endpoint
- System automatically creates member membership  
- Next `/users/me` call returns `needs_onboarding: false`

## Integration Scenarios

### Scenario 1: New User Creating Business

1. **Initial State**: `GET /users/me` → `needs_onboarding: true`
2. **Action**: Show onboarding flow
3. **Business Creation**: `POST /api/v1/businesses/` (creates owner membership)
4. **Updated State**: `GET /users/me` → `needs_onboarding: false`
5. **Result**: Redirect to main app

### Scenario 2: User Joining Existing Business

1. **Initial State**: `GET /users/me` → `needs_onboarding: true`
2. **Action**: User receives and accepts business invitation
3. **Invitation Acceptance**: Creates member membership
4. **Updated State**: `GET /users/me` → `needs_onboarding: false`
5. **Result**: Skip onboarding, go directly to main app

### Scenario 3: Business Creation Fails

1. **State**: `GET /users/me` → `needs_onboarding: true`
2. **Action**: User attempts business creation
3. **Failure**: `POST /api/v1/businesses/` fails (no membership created)
4. **Unchanged State**: `GET /users/me` → `needs_onboarding: true`
5. **Result**: Stay in onboarding flow

### Scenario 4: User Leaves All Businesses

1. **Previous State**: `GET /users/me` → `needs_onboarding: false`
2. **Action**: User leaves/removed from all businesses
3. **Updated State**: `GET /users/me` → `needs_onboarding: true`
4. **Result**: Show onboarding on next app launch

## Error Handling

### Authentication Errors
**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```
**Action**: Redirect to login

### Server Errors
**500 Internal Server Error**:
```json
{
  "detail": "Failed to get user profile: Database connection error"
}
```
**Action**: Show error message, retry, or default to onboarding

### Network Errors
**Action**: 
- Show offline message
- Cache last known onboarding status
- Default to onboarding if no cached data

## Client Implementation Checklist

### Data Model Updates
- [ ] Add `business_memberships` array field
- [ ] Add `has_businesses` boolean field  
- [ ] Add `needs_onboarding` boolean field
- [ ] Remove `onboarding_completed` field
- [ ] Remove `onboarding_completed_at` field
- [ ] Remove `completed_steps` field

### API Integration Updates
- [ ] Update `/users/me` response parsing
- [ ] Remove `POST /users/me/onboarding-completed` calls
- [ ] Update onboarding logic to use `needs_onboarding` field only
- [ ] Handle business membership display in profile screens

### Business Flow Integration
- [ ] After business creation, refresh user profile
- [ ] After invitation acceptance, refresh user profile
- [ ] Handle business creation failures gracefully
- [ ] Update app launch flow to check `needs_onboarding`

### UI Updates
- [ ] Update profile screens to show business memberships
- [ ] Remove manual onboarding completion buttons/flows
- [ ] Update onboarding completion messaging
- [ ] Handle multiple business memberships display

## Testing Requirements

### API Response Testing
- [ ] Verify new fields are present in `/users/me` response
- [ ] Verify old fields are not used in client logic
- [ ] Test with users who have no businesses
- [ ] Test with users who have multiple businesses

### Flow Testing
- [ ] Test business creation completing onboarding
- [ ] Test invitation acceptance completing onboarding  
- [ ] Test business creation failure keeping onboarding
- [ ] Test user leaving all businesses requiring onboarding

### Error Handling Testing
- [ ] Test API failures during onboarding check
- [ ] Test network errors during profile loading
- [ ] Test authentication failures

## Migration Notes

### For Existing Apps
- **Breaking Changes**: Yes - old onboarding fields removed
- **Backward Compatibility**: None - must update to new API
- **Data Migration**: Not required - server handles logic change

### For Existing Users
- Users with businesses: `needs_onboarding: false` (no action needed)
- Users without businesses: `needs_onboarding: true` (will see onboarding)

### Deployment Considerations
- Update client before deploying server changes
- Test thoroughly in staging environment
- Monitor onboarding completion rates after deployment
- Have rollback plan for critical issues

## Benefits

### Simplified Logic
- Single source of truth: business membership status
- No complex state management
- Automatic onboarding completion

### Better User Experience  
- Users joining businesses skip onboarding entirely
- Failed business creation doesn't leave inconsistent state
- Clear business membership visibility

### Reduced Maintenance
- No manual onboarding state tracking
- Fewer API endpoints to maintain
- Self-healing onboarding status 