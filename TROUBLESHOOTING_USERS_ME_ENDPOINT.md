# Troubleshooting Guide: `/api/v1/users/me` Endpoint

This guide helps you resolve issues with the `/api/v1/users/me` endpoint in the Hero365 API backend.

## Table of Contents

- [Overview](#overview)
- [Simplified Architecture](#simplified-architecture)
- [Authentication Requirements](#authentication-requirements)
- [How the Endpoint Works](#how-the-endpoint-works)
- [Making Valid Requests](#making-valid-requests)
- [Obtaining Valid Tokens](#obtaining-valid-tokens)
- [Common Failure Scenarios](#common-failure-scenarios)
- [Testing Examples](#testing-examples)
- [Mobile App Integration](#mobile-app-integration)
- [Debugging Checklist](#debugging-checklist)

## Overview

The `/api/v1/users/me` endpoint returns information about the currently authenticated user **directly from Supabase**. 

**Key Features:**
- ✅ **No local database dependency** - gets data directly from Supabase token
- ✅ **Pure Supabase integration** - single source of truth
- ✅ **Supports all auth methods** - email, phone, OAuth, OTP
- ✅ **Fast response** - no database queries needed

**Endpoint:** `GET /api/v1/users/me`

**Authentication:** Required (Supabase JWT token)

## Simplified Architecture

### How It Works Now

```
Client Request → FastAPI Backend → Supabase Token Verification → User Data Response
```

**No database involved!** The endpoint:
1. **Extracts token** from Authorization header
2. **Verifies with Supabase** using `supabase.auth.get_user(token)`
3. **Returns user data** directly from Supabase token payload

### What Changed

❌ **Old (Complex):**
- Hybrid Supabase + Local PostgreSQL
- Database connection required
- User data duplicated locally
- Connection failures

✅ **New (Simple):**
- Pure Supabase integration
- No database connections
- Single source of truth
- No connection issues

## Authentication Requirements

### Required Header

```
Authorization: Bearer {supabase_access_token}
```

### Supported Token Types

**Primary: Supabase JWT Tokens**
- From any Supabase auth method (email, phone, OAuth, OTP)
- Verified directly with Supabase service
- Contains all user data in token payload

**Legacy: App JWT Tokens** (backward compatibility)
- From `/api/v1/login/access-token` endpoint
- Verified with app SECRET_KEY
- Limited to email/password authentication

## How the Endpoint Works

### Token Verification Process

1. **Extract token** from `Authorization: Bearer {token}` header
2. **Call Supabase** `supabase.auth.get_user(token)`
3. **Return user data** from Supabase response:

```python
# Backend code (simplified)
def get_current_user(token: str) -> dict:
    supabase_user_data = supabase_service.verify_token(token)
    if supabase_user_data:
        return supabase_user_data  # Direct return from Supabase
    # No database lookups needed!
```

### Response Format

**Success Response:**
```json
{
  "id": "12345678-1234-1234-1234-123456789abc",
  "email": "user@example.com",
  "phone": "+1234567890",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

**Data Sources:**
- `id`: Supabase user ID
- `email`/`phone`: From Supabase auth
- `full_name`: From `user_metadata.full_name`
- `is_superuser`: From `app_metadata.is_superuser`
- `is_active`: Always `true` (Supabase users are active)

## Making Valid Requests

### Basic Request

```http
GET /api/v1/users/me HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### cURL Example

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN" \
  -H "Content-Type: application/json"
```

## Obtaining Valid Tokens

### Method 1: Email/Password Authentication

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-here",
    "email": "user@example.com"
  }
}
```

### Method 2: Phone/Password Authentication

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signin/phone" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "password": "SecurePassword123!"
  }'
```

### Method 3: Phone OTP Authentication

**Step 1 - Send OTP:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/otp/send" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

**Step 2 - Verify OTP:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/otp/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "token": "123456"
  }'
```

### Method 4: OAuth Authentication

**Get OAuth URL:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/oauth/google"
```

**Response:**
```json
{
  "url": "https://accounts.google.com/oauth/authorize?..."
}
```

Then redirect user to the URL and handle the callback.

## Common Failure Scenarios

### 1. Missing Authorization Header

**Error:**
```json
{
  "detail": "Not authenticated"
}
```

**Status:** `401 Unauthorized`

**Solution:** Add `Authorization: Bearer {token}` header

### 2. Invalid or Expired Supabase Token

**Error:**
```json
{
  "detail": "Could not validate credentials"
}
```

**Status:** `401 Unauthorized`

**Causes:**
- Token expired (check `exp` claim)
- Invalid token format
- Token revoked in Supabase

**Solutions:**
- Use refresh token to get new access token
- Re-authenticate user
- Check token format in jwt.io

### 3. Malformed Authorization Header

**Common Issues:**
```
❌ Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...     # Missing "Bearer "
❌ Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Lowercase "bearer"
❌ Authorization: Bearer  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # Double space
```

**Correct:**
```
✅ Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Supabase Service Issues

**Error:**
```json
{
  "detail": "Could not validate credentials: Supabase error message"
}
```

**Causes:**
- Supabase service down
- Invalid Supabase configuration
- Network connectivity issues

**Solutions:**
- Check Supabase dashboard status
- Verify `SUPABASE_URL` and `SUPABASE_KEY` environment variables
- Test Supabase connection directly

### 5. Token Verification Failures

**Common Token Issues:**
- **Expired tokens:** Check `exp` claim in JWT
- **Wrong audience:** Token for different Supabase project
- **Invalid signature:** Token tampered with or wrong key

**Debug Token:**
1. Go to [jwt.io](https://jwt.io)
2. Paste your token
3. Check payload and expiration
4. Verify `iss` (issuer) matches your Supabase URL

## Testing Examples

### Complete Test Flow

```bash
# 1. Authenticate to get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | grep -o '"access_token":"[^"]*"' \
  | cut -d'"' -f4)

# 2. Use token to get user info
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Postman Collection

**1. Login Request:**
```
POST {{base_url}}/api/v1/auth/signin
Headers: Content-Type: application/json
Body: {"email": "user@example.com", "password": "password123"}

Test Script:
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.access_token);
}
```

**2. Get User Request:**
```
GET {{base_url}}/api/v1/users/me
Headers: Authorization: Bearer {{access_token}}
```

### JavaScript/TypeScript

```typescript
interface UserResponse {
  id: string;
  email?: string;
  phone?: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

async function getCurrentUser(token: string): Promise<UserResponse> {
  const response = await fetch('/api/v1/users/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required');
    }
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return await response.json();
}
```

## Mobile App Integration

### iOS Swift

```swift
struct User: Codable {
    let id: String
    let email: String?
    let phone: String?
    let fullName: String?
    let isActive: Bool
    let isSuperuser: Bool
    
    private enum CodingKeys: String, CodingKey {
        case id, email, phone, isActive, isSuperuser
        case fullName = "full_name"
        case isActive = "is_active"
        case isSuperuser = "is_superuser"
    }
}

func getCurrentUser() async throws -> User {
    guard let token = getStoredToken() else {
        throw AuthError.noToken
    }
    
    var request = URLRequest(url: URL(string: "http://localhost:8000/api/v1/users/me")!)
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse else {
        throw NetworkError.invalidResponse
    }
    
    switch httpResponse.statusCode {
    case 200:
        return try JSONDecoder().decode(User.self, from: data)
    case 401:
        clearStoredToken()
        throw AuthError.invalidToken
    default:
        throw NetworkError.httpError(httpResponse.statusCode)
    }
}
```

### Android Kotlin

```kotlin
data class User(
    val id: String,
    val email: String?,
    val phone: String?,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("is_superuser") val isSuperuser: Boolean
)

suspend fun getCurrentUser(): Result<User> = withContext(Dispatchers.IO) {
    try {
        val token = getStoredToken() ?: return@withContext Result.failure(
            Exception("No authentication token")
        )
        
        val request = Request.Builder()
            .url("http://localhost:8000/api/v1/users/me")
            .addHeader("Authorization", "Bearer $token")
            .addHeader("Content-Type", "application/json")
            .build()
        
        val response = okHttpClient.newCall(request).execute()
        
        when (response.code) {
            200 -> {
                val json = response.body?.string() ?: ""
                val user = gson.fromJson(json, User::class.java)
                Result.success(user)
            }
            401 -> {
                clearStoredToken()
                Result.failure(Exception("Authentication required"))
            }
            else -> Result.failure(Exception("HTTP ${response.code}"))
        }
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

## Debugging Checklist

### Backend Status

- [ ] **Server running:** `curl http://localhost:8000/health` 
- [ ] **API docs accessible:** Visit `http://localhost:8000/docs`
- [ ] **Supabase config:** Check `SUPABASE_URL` and `SUPABASE_KEY` env vars
- [ ] **No database errors:** No PostgreSQL connection needed anymore!

### Token Issues

- [ ] **Token format:** Must start with `Bearer ` (note space)
- [ ] **Token validity:** Use jwt.io to decode and check expiration
- [ ] **Token source:** Must be from Supabase auth endpoints
- [ ] **Token scope:** Verify `aud` (audience) matches your Supabase project

### Request Format

- [ ] **Authorization header:** `Authorization: Bearer {token}`
- [ ] **Content-Type:** `application/json` (recommended)
- [ ] **Method:** `GET` request to `/api/v1/users/me`
- [ ] **Encoding:** UTF-8 encoding for special characters

### Network & Connectivity

- [ ] **Backend reachable:** `curl http://localhost:8000/docs`
- [ ] **Supabase reachable:** Check Supabase dashboard
- [ ] **CORS settings:** Verify CORS for web/mobile clients
- [ ] **Firewall/Proxy:** Check network restrictions

### Quick Debug Commands

```bash
# Check if backend is running
curl -I http://localhost:8000/docs

# Test authentication endpoint
curl -X POST "http://localhost:8000/api/v1/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -v

# Test with verbose output
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -v
```

## Key Advantages of New Architecture

### ✅ Simplified

- **No database setup** required for user management
- **Single source of truth** - Supabase handles everything
- **Fewer failure points** - no database connection issues

### ✅ Performance  

- **Faster responses** - no database queries
- **Scalable** - leverages Supabase infrastructure
- **Reliable** - reduced complexity means fewer bugs

### ✅ Features

- **All auth methods** - email, phone, OAuth, OTP supported
- **Rich user data** - metadata from Supabase
- **Real-time updates** - data always current

---

**Architecture:** Pure Supabase Integration  
**Last Updated:** December 2024  
**No Database Required:** ✅ 