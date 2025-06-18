# Hero365 API Integration Guide for Swift Apps

This guide provides comprehensive documentation for integrating Hero365 backend authentication APIs into your Swift iOS application. The API supports multiple authentication methods including email/password, phone number, and OAuth providers (Google, Apple).

## Table of Contents

- [Base Configuration](#base-configuration)
- [Authentication Methods](#authentication-methods)
- [API Endpoints](#api-endpoints)
- [Authentication Flows](#authentication-flows)
- [Error Handling](#error-handling)
- [Token Management](#token-management)
- [Best Practices](#best-practices)
- [Testing](#testing)

## Base Configuration

### API Base URL

```
Development: http://localhost:8000
Production: https://your-api-domain.com
```

### API Version

All authentication endpoints are prefixed with `/api/v1`

### Content Type

All requests should use `Content-Type: application/json`

### Headers

```
Content-Type: application/json
Authorization: Bearer {access_token}  # For protected endpoints
```

## Authentication Methods

The Hero365 API supports the following authentication methods:

1. **Email & Password** - Traditional authentication
2. **Phone & Password** - Phone number with password
3. **Phone & OTP** - Passwordless phone authentication via SMS
4. **Google OAuth** - Sign in with Google
5. **Apple OAuth** - Sign in with Apple ID

## API Endpoints

### 1. Email & Password Authentication

#### Sign Up with Email

**Endpoint:** `POST /api/v1/auth/signup`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"  // Optional
}
```

**Response:**
```json
{
  "message": "User created successfully. Please check your email for verification."
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request data
- `503` - Supabase not configured

#### Sign In with Email

**Endpoint:** `POST /api/v1/auth/signin`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-here",
    "email": "user@example.com",
    "user_metadata": {
      "full_name": "John Doe"
    }
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `503` - Supabase not configured

### 2. Phone Number Authentication

#### Sign Up with Phone

**Endpoint:** `POST /api/v1/auth/signup/phone`

**Request Body:**
```json
{
  "phone": "+1234567890",
  "password": "SecurePassword123!",
  "full_name": "John Doe"  // Optional
}
```

**Response:**
```json
{
  "message": "User created successfully. Please verify your phone number."
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request data
- `503` - Supabase not configured

#### Sign In with Phone

**Endpoint:** `POST /api/v1/auth/signin/phone`

**Request Body:**
```json
{
  "phone": "+1234567890",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-here",
    "phone": "+1234567890",
    "user_metadata": {
      "full_name": "John Doe"
    }
  }
}
```

### 3. Phone OTP Authentication

#### Send OTP

**Endpoint:** `POST /api/v1/auth/otp/send`

**Request Body:**
```json
{
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully to your phone number."
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid phone number or SMS sending failed
- `503` - Supabase not configured

#### Verify OTP

**Endpoint:** `POST /api/v1/auth/otp/verify`

**Request Body:**
```json
{
  "phone": "+1234567890",
  "token": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-here",
    "phone": "+1234567890",
    "user_metadata": {}
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid OTP
- `503` - Supabase not configured

### 4. OAuth Authentication

#### Get OAuth URL

**Endpoint:** `GET /api/v1/auth/oauth/{provider}`

**Supported Providers:** `google`, `apple`, `github`

**Example:** `GET /api/v1/auth/oauth/google`

**Response:**
```json
{
  "url": "https://your-project.supabase.co/auth/v1/authorize?provider=google",
  "provider": "google"
}
```

**Status Codes:**
- `200` - Success
- `400` - Unsupported OAuth provider
- `503` - Supabase not configured

### 5. Utility Endpoints

#### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Password Recovery

**Endpoint:** `POST /api/v1/auth/password-recovery`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password recovery email sent"
}
```

#### Get Current User

**Endpoint:** `GET /api/v1/users/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "user-uuid-here",
  "email": "user@example.com",
  "phone": "+1234567890",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

#### Sign Out

**Endpoint:** `POST /api/v1/auth/signout`

**Response:**
```json
{
  "message": "Sign out should be handled by the frontend Supabase client"
}
```

**Note:** Sign out should be handled locally by clearing stored tokens.

## Authentication Flows

### 1. Email/Password Flow

```
1. User enters email and password
2. App sends POST to /api/v1/auth/signin
3. Backend validates credentials via Supabase
4. Backend returns access_token and refresh_token
5. App stores tokens securely (Keychain)
6. App includes access_token in Authorization header for protected requests
```

### 2. Phone/Password Flow

```
1. User enters phone number and password
2. App sends POST to /api/v1/auth/signin/phone
3. Backend validates credentials via Supabase
4. Backend returns access_token and refresh_token
5. App stores tokens securely
```

### 3. Phone/OTP Flow

```
1. User enters phone number
2. App sends POST to /api/v1/auth/otp/send
3. Backend sends SMS via configured provider
4. User receives SMS with 6-digit code
5. User enters OTP code
6. App sends POST to /api/v1/auth/otp/verify with phone and token
7. Backend validates OTP via Supabase
8. Backend returns access_token and refresh_token
```

### 4. OAuth Flow (Google/Apple)

```
1. App calls GET /api/v1/auth/oauth/{provider} to get OAuth URL
2. App opens OAuth URL in web view or external browser
3. User completes OAuth flow with provider
4. Provider redirects to callback URL with authorization code
5. Supabase handles token exchange automatically
6. App receives authentication result via deep link or URL monitoring
7. App extracts tokens from callback URL parameters
```

### 5. Apple Sign In (Native)

For native Apple Sign In, you can skip the OAuth URL and use Apple's native SDK:

```
1. Use Apple's AuthenticationServices framework
2. Get authorization code from Apple
3. Exchange code with Supabase directly (via web view or backend call)
4. Extract tokens from response
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid data, validation errors)
- `401` - Unauthorized (invalid credentials, expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (endpoint doesn't exist)
- `503` - Service Unavailable (Supabase not configured)

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Messages

- `"Invalid credentials"` - Wrong email/password or phone/password
- `"Invalid OTP"` - Wrong OTP code or expired
- `"Invalid refresh token"` - Refresh token is expired or invalid
- `"Supabase authentication is not configured"` - Backend configuration issue
- `"Failed to send OTP: [reason]"` - SMS sending failed
- `"Unsupported OAuth provider"` - Invalid provider name

### Recommended Error Handling

1. **Network Errors**: Check internet connectivity, retry with exponential backoff
2. **401 Unauthorized**: Clear stored tokens, redirect to login
3. **400 Bad Request**: Show user-friendly validation errors
4. **503 Service Unavailable**: Show maintenance message, retry later

## Token Management

### Token Storage

**Recommended**: Use iOS Keychain for secure token storage

```
- Store access_token with key: "hero365_access_token"
- Store refresh_token with key: "hero365_refresh_token"
- Set accessibility: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
```

### Token Lifecycle

1. **Access Token**: Short-lived (default: 8 days), used for API requests
2. **Refresh Token**: Long-lived, used to get new access tokens
3. **Automatic Refresh**: Check token expiry before requests, refresh if needed

### Token Refresh Strategy

```
1. Before each API request, check if access_token is expired
2. If expired, use refresh_token to get new tokens via /api/v1/auth/refresh
3. Update stored tokens with new values
4. Retry original request with new access_token
5. If refresh fails (401), clear tokens and redirect to login
```

### Token Validation

Access tokens are JWT tokens. You can decode them to check:
- `exp` (expiry time)
- `sub` (subject/user ID)
- `email` or `phone` (user identifier)

## Best Practices

### Security

1. **Always use HTTPS** in production
2. **Store tokens in Keychain**, never in UserDefaults
3. **Validate SSL certificates** to prevent man-in-the-middle attacks
4. **Implement certificate pinning** for production apps
5. **Clear tokens on app uninstall** or user logout

### User Experience

1. **Phone Number Formatting**: Format phone numbers with country code (+1234567890)
2. **OTP Input**: Provide easy 6-digit OTP input with auto-detection from SMS
3. **Loading States**: Show loading indicators during authentication
4. **Error Messages**: Display user-friendly error messages
5. **Auto-retry**: Implement automatic retry for network failures

### Performance

1. **Token Caching**: Cache valid tokens to avoid unnecessary requests
2. **Background Refresh**: Refresh tokens in background before expiry
3. **Request Timeout**: Set appropriate timeouts (30 seconds for auth requests)
4. **Connection Pooling**: Reuse HTTP connections where possible

### OAuth Integration

#### Google Sign In

1. Configure Google Sign-In SDK
2. Get authorization code from Google
3. Use Supabase OAuth flow or exchange code manually
4. Handle both success and cancellation cases

#### Apple Sign In

1. Use AuthenticationServices framework
2. Handle both Sign In with Apple button and programmatic calls
3. Support biometric authentication where available
4. Handle account deletion requirements

### Phone Number Validation

```
Valid formats:
- "+1234567890" (recommended)
- "+1 (234) 567-8900" (will be normalized)
- International format with country code

Invalid formats:
- "234-567-8900" (missing country code)
- "1234567890" (missing + prefix)
```

### OTP Best Practices

1. **Auto-detection**: Use SMS auto-detection for better UX
2. **Resend Logic**: Allow OTP resend after 30-60 seconds
3. **Expiry Handling**: Show countdown timer for OTP expiry
4. **Rate Limiting**: Implement client-side rate limiting for OTP requests

## Testing

### Development Environment

```
Base URL: http://localhost:8000
Supabase: Development project
SMS: Test mode (no actual SMS sent)
```

### Test Accounts

For development testing, you can create test accounts:

```json
{
  "email": "test@example.com",
  "phone": "+1234567890",
  "password": "TestPassword123!"
}
```

### Postman Collection

Import the following collection for API testing:

```
POST {{base_url}}/api/v1/auth/signup
POST {{base_url}}/api/v1/auth/signin
POST {{base_url}}/api/v1/auth/signup/phone
POST {{base_url}}/api/v1/auth/signin/phone
POST {{base_url}}/api/v1/auth/otp/send
POST {{base_url}}/api/v1/auth/otp/verify
GET {{base_url}}/api/v1/auth/oauth/google
GET {{base_url}}/api/v1/auth/oauth/apple
POST {{base_url}}/api/v1/auth/refresh
GET {{base_url}}/api/v1/users/me
```

### Testing OAuth

For OAuth testing in development:
1. Use web view or external browser
2. Monitor callback URLs
3. Test both success and cancellation flows
4. Verify token extraction from callback

## Support and Resources

### Documentation
- Supabase Auth: https://supabase.com/docs/guides/auth
- Apple Sign In: https://developer.apple.com/sign-in-with-apple/
- Google Sign In: https://developers.google.com/identity

### Common Issues

1. **CORS Errors**: Ensure your app's bundle ID is configured in backend CORS settings
2. **SSL Errors**: Use proper certificates in production
3. **Token Expiry**: Implement proper token refresh logic
4. **Phone Format**: Always use international format with country code
5. **OAuth Redirect**: Ensure proper URL schemes are configured

### Contact

For API-specific issues:
- Check API documentation: `{base_url}/docs`
- Review server logs for detailed error messages
- Test endpoints using the interactive API docs

---

**Note**: This API uses Supabase for authentication. Ensure your backend is properly configured with Supabase credentials and OAuth providers before implementing authentication in your Swift app. 