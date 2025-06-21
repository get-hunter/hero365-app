# Onboarding API Specification

## Overview
This document describes the API changes for the onboarding feature that tracks and manages user onboarding completion status across all authentication methods.

## API Changes

### 1. New Endpoint: Mark Onboarding Completed

**Endpoint**: `POST /users/me/onboarding-completed`

**Description**: Mark the current user's onboarding as completed and optionally store completion steps.

**Authentication**: Required (Bearer token)

**Request Body** (optional):
```json
{
  "completed_steps": ["step1", "step2", "step3"],
  "completion_date": "2024-01-15T10:30:00Z"
}
```

**Request Schema**:
- `completed_steps` (array of strings, optional): List of completed onboarding steps
- `completion_date` (datetime, optional): Custom completion date (defaults to current timestamp)

**Response**:
```json
{
  "success": true,
  "message": "Onboarding marked as completed successfully",
  "onboarding_completed": true,
  "completed_at": "2024-01-15T10:30:00Z"
}
```

**Response Schema**:
- `success` (boolean): Operation success status
- `message` (string): Confirmation message
- `onboarding_completed` (boolean): Onboarding completion status
- `completed_at` (datetime): When onboarding was completed

### 2. Enhanced Authentication Responses

All authentication endpoints now include onboarding status in their responses:

**Affected Endpoints**:
- `POST /auth/signin` (Email/password login)
- `POST /auth/signin/phone` (Phone/password login)  
- `POST /auth/otp/verify` (OTP verification)
- `POST /auth/apple/signin` (Apple Sign-In)
- `POST /auth/google/signin` (Google Sign-In)

**Important Note**: OAuth endpoints (Apple/Google Sign-In) now properly save the `full_name` and other profile information to user metadata in Supabase, ensuring persistence across sessions.

**Enhanced User Object in Auth Responses**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "phone": null,
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false,
    "supabase_id": "550e8400-e29b-41d4-a716-446655440000",
    "onboarding_completed": false,
    "onboarding_completed_at": null,
    "completed_steps": []
  },
  "is_new_user": false
}
```

**New User Fields**:
- `onboarding_completed` (boolean): Whether user has completed onboarding
- `onboarding_completed_at` (datetime|null): When onboarding was completed
- `completed_steps` (array): List of completed onboarding steps

### 3. Enhanced User Profile Response

**Endpoint**: `GET /users/me`

**Enhanced Response**:
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
  "onboarding_completed": true,
  "onboarding_completed_at": "2024-01-02T15:45:00Z",
  "completed_steps": ["profile_setup", "preferences", "verification"]
}
```

## Data Storage

Onboarding data is stored in the user's metadata in Supabase:

```json
{
  "user_metadata": {
    "full_name": "John Doe",
    "onboarding_completed": true,
    "completed_at": "2024-01-02T15:45:00.000Z",
    "completed_steps": ["profile_setup", "preferences", "verification"]
  }
}
```

### OAuth Profile Data Persistence

**Apple Sign-In**: The `full_name` provided in the sign-in request is automatically saved to user metadata.

**Google Sign-In**: Multiple profile fields are saved to user metadata:
- `full_name`: Complete name
- `given_name`: First name  
- `family_name`: Last name
- `picture_url`: Profile picture URL

**Metadata Update Logic**: Profile data is only saved if the field is not already present or is empty, preventing overwrites of existing user-modified data.

## Usage Examples

### 1. Check Onboarding Status After Login

```javascript
// After successful login/signup
const authResponse = await fetch('/auth/signin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password' })
});

const data = await authResponse.json();

if (!data.user.onboarding_completed) {
  // Show onboarding flow
  showOnboarding();
} else {
  // Proceed to main app
  redirectToMainApp();
}
```

### 2. Mark Onboarding as Completed

```javascript
// After user completes onboarding steps
const response = await fetch('/users/me/onboarding-completed', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    completed_steps: ['profile_setup', 'preferences', 'verification']
  })
});

const result = await response.json();
console.log(result.message); // "Onboarding marked as completed successfully"
```

### 3. Get Current User Status

```javascript
// Check user's onboarding status
const response = await fetch('/users/me', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const user = await response.json();

if (user.onboarding_completed) {
  console.log(`Onboarding completed on: ${user.onboarding_completed_at}`);
  console.log(`Completed steps: ${user.completed_steps.join(', ')}`);
}
```

## Migration Notes

- **Backward Compatible**: Existing authentication flows continue to work
- **Default Values**: New users have `onboarding_completed: false` by default
- **Existing Users**: Users without onboarding data will show `onboarding_completed: false`
- **Optional Fields**: All new onboarding fields are optional and nullable

## Error Handling

### POST /users/me/onboarding-completed

**400 Bad Request**:
```json
{
  "detail": "Failed to mark onboarding completed: [error details]"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```

## Security Considerations

- Onboarding data is stored in user metadata, accessible only to the authenticated user
- Completion status cannot be modified by other users
- Only the user themselves can mark their onboarding as completed
- All onboarding endpoints require valid authentication tokens 