# Simplified User Management API

## Overview
This document describes the simplified user management API with business-membership-based onboarding completion.

## Core Principle
**A user has completed onboarding if and only if they are associated with at least one active business (either as owner or member).**

## API Endpoint

### Get Current User Profile

**Endpoint**: `GET /api/v1/users/me`

**Description**: Get current user profile with business memberships and onboarding status.

**Authentication**: Required (Bearer token)

**Response**:
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

**Response Fields**:

**Basic User Info**:
- `id`: User's unique identifier
- `email`: User's email address
- `phone`: User's phone number
- `full_name`: User's full name
- `is_active`: User account status
- `is_superuser`: Admin privileges flag
- `supabase_id`: Supabase user ID
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Business Memberships**:
- `business_memberships`: Array of business membership summaries
  - `business_id`: UUID of the business
  - `business_name`: Display name of the business
  - `role`: Human-readable role name (Owner, Manager, Employee, etc.)
  - `is_owner`: Boolean indicating if user is the business owner
  - `is_active`: Boolean indicating if membership is active
  - `joined_date`: Date when user joined the business

**Onboarding Status**:
- `has_businesses`: Boolean indicating if user has any business memberships
- `needs_onboarding`: Boolean indicating if user needs to complete onboarding
  - `true` if user has no active business memberships
  - `false` if user has at least one active business membership

## Onboarding Logic

### Simple Rules
```
needs_onboarding = user has NO active business memberships
```

### User Flow Scenarios

**Scenario 1: New User Creating Business**
1. New user → `needs_onboarding: true`
2. User goes through onboarding flow
3. User creates business → Automatic owner membership created
4. User profile → `needs_onboarding: false`
5. Redirect to main app

**Scenario 2: User Joining Existing Business**
1. New user → `needs_onboarding: true`
2. User receives business invitation
3. User accepts invitation → Membership created
4. User profile → `needs_onboarding: false`
5. Skip onboarding, redirect directly to main app

**Scenario 3: Business Creation Fails**
1. User goes through onboarding
2. Business creation fails → No membership created
3. User profile → `needs_onboarding: true`
4. Show onboarding again until business is successfully created

**Scenario 4: User Leaves All Businesses**
1. User had businesses → `needs_onboarding: false`
2. User leaves/gets removed from all businesses
3. User profile → `needs_onboarding: true`
4. Show onboarding flow again

## Implementation Examples

### Frontend Logic

```javascript
async function checkUserOnboardingStatus() {
  const response = await fetch('/api/v1/users/me', {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  const user = await response.json();
  
  if (user.needs_onboarding) {
    // User needs to create or join a business
    redirectTo('/onboarding');
  } else {
    // User has business membership, go to main app
    redirectTo('/dashboard');
  }
}
```

### Mobile Integration

**iOS Swift**:
```swift
struct UserProfile: Codable {
    let id: String
    let email: String?
    let fullName: String?
    let businessMemberships: [BusinessMembership]
    let hasBusinesses: Bool
    let needsOnboarding: Bool
    
    private enum CodingKeys: String, CodingKey {
        case id, email, businessMemberships, hasBusinesses, needsOnboarding
        case fullName = "full_name"
        case hasBusinesses = "has_businesses"
        case needsOnboarding = "needs_onboarding"
    }
}

func handleUserProfile(_ user: UserProfile) {
    if user.needsOnboarding {
        showOnboardingFlow()
    } else {
        showMainApp()
    }
}
```

**Android Kotlin**:
```kotlin
data class UserProfile(
    val id: String,
    val email: String?,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("business_memberships") val businessMemberships: List<BusinessMembership>,
    @SerializedName("has_businesses") val hasBusinesses: Boolean,
    @SerializedName("needs_onboarding") val needsOnboarding: Boolean
)

fun handleUserProfile(user: UserProfile) {
    if (user.needsOnboarding) {
        showOnboardingFlow()
    } else {
        showMainApp()
    }
}
```

## Business Creation Integration

When a business is created via `POST /api/v1/businesses/`, the system automatically:

1. **Creates Business Entity**: Saves business to database
2. **Creates Owner Membership**: Creates business membership with:
   - Role: `OWNER`
   - Permissions: Full owner permissions
   - Active status: `true`
   - Joined date: Current timestamp
3. **Updates Onboarding Status**: User automatically gets `needs_onboarding: false`

## Business Invitation Integration

When a user accepts a business invitation, the system automatically:

1. **Creates Member Membership**: Creates business membership with appropriate role
2. **Updates Onboarding Status**: User automatically gets `needs_onboarding: false`
3. **Skips Onboarding**: User goes directly to main app

## Benefits of This Approach

### Simplicity
- Single source of truth: business membership status
- No complex metadata management
- No separate onboarding completion tracking

### Flexibility
- Handles both business creation and invitation scenarios
- Automatically handles edge cases (failed business creation, leaving businesses)
- Works for multi-business users

### User Experience
- Users who join existing businesses skip onboarding entirely
- Users who create businesses complete onboarding automatically
- Failed operations don't leave users in inconsistent states

## Error Handling

### Authentication Required (401)
```json
{
  "detail": "Could not validate credentials"
}
```

### Server Error (500)
```json
{
  "detail": "Failed to get user profile: Database connection error"
}
```

## Migration Notes

### Breaking Changes
- Removed `onboarding_completed` field
- Removed `onboarding_completed_at` field  
- Removed `completed_steps` field
- Removed `POST /api/v1/users/me/onboarding-completed` endpoint

### New Fields
- `business_memberships`: Array of business membership summaries
- `has_businesses`: Boolean indicating business membership existence
- `needs_onboarding`: Boolean indicating onboarding requirement

### Client Updates Required
- Update onboarding logic to check `needs_onboarding` field only
- Remove calls to onboarding completion endpoint
- Update UI to handle business membership display 