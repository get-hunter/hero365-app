# Native Apple/Google Sign-In Integration Guide for Swift

This guide explains how to integrate native Apple and Google Sign-In with your Swift iOS app using your **Hero365 backend as a proxy to Supabase Auth**.

> **🏗️ Architecture**: iOS App → Your Backend → Supabase Auth (consistent with email/phone auth)

## 🏗️ Architecture Overview

```
iOS App → Hero365 Backend → Supabase Auth
```

**Benefits of this approach:**
- ✅ Consistent with your existing email/phone authentication flow
- ✅ Centralized authentication logic in your backend
- ✅ Your backend handles all Supabase integration
- ✅ iOS app only needs to handle native OAuth and send ID tokens
- ✅ No need for Supabase iOS SDK

## 📱 iOS Implementation

### 1. Apple Sign-In Implementation

```swift
import AuthenticationServices

class AppleSignInManager: NSObject, ObservableObject {
    @Published var isSignedIn = false
    @Published var errorMessage: String?
    
    private let apiBaseURL = "http://localhost:8000/api/v1"  // Update for production
    
    func signInWithApple() {
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]
        
        let authorizationController = ASAuthorizationController(authorizationRequests: [request])
        authorizationController.delegate = self
        authorizationController.performRequests()
    }
}

extension AppleSignInManager: ASAuthorizationControllerDelegate {
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            
            guard let identityToken = appleIDCredential.identityToken,
                  let idTokenString = String(data: identityToken, encoding: .utf8) else {
                self.errorMessage = "Failed to get ID token from Apple"
                return
            }
            
            let email = appleIDCredential.email
            let fullName = appleIDCredential.fullName?.formatted()
            
            Task {
                await sendAppleTokenToBackend(
                    idToken: idTokenString,
                    userIdentifier: appleIDCredential.user,
                    email: email,
                    fullName: fullName
                )
            }
        }
    }
    
    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        self.errorMessage = "Apple Sign-In failed: \(error.localizedDescription)"
    }
    
    private func sendAppleTokenToBackend(
        idToken: String,
        userIdentifier: String,
        email: String?,
        fullName: String?
    ) async {
        let requestBody = AppleSignInRequest(
            id_token: idToken,
            user_identifier: userIdentifier,
            email: email,
            full_name: fullName
        )
        
        do {
            let url = URL(string: "\(apiBaseURL)/auth/apple/signin")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONEncoder().encode(requestBody)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                throw AuthError.invalidResponse
            }
            
            let authResponse = try JSONDecoder().decode(OAuthSignInResponse.self, from: data)
            
            DispatchQueue.main.async {
                self.handleSuccessfulAuth(authResponse)
            }
            
        } catch {
            DispatchQueue.main.async {
                self.errorMessage = "Apple Sign-In failed: \(error.localizedDescription)"
            }
        }
    }
    
    private func handleSuccessfulAuth(_ response: OAuthSignInResponse) {
        // Store tokens securely
        TokenManager.shared.storeTokens(response)
        
        // Update UI
        self.isSignedIn = true
        self.errorMessage = nil
        
        print("Apple Sign-In successful for user: \(response.user.email ?? "Unknown")")
        print("Is new user: \(response.is_new_user)")
    }
}

// Helper extension for PersonNameComponents
extension PersonNameComponents {
    func formatted() -> String {
        var parts: [String] = []
        if let givenName = givenName { parts.append(givenName) }
        if let familyName = familyName { parts.append(familyName) }
        return parts.joined(separator: " ")
    }
}
```

### 2. Google Sign-In Implementation

First, add Google Sign-In SDK to your project:

```
https://github.com/google/GoogleSignIn-iOS
```

```swift
import GoogleSignIn

class GoogleSignInManager: NSObject, ObservableObject {
    @Published var isSignedIn = false
    @Published var errorMessage: String?
    
    private let apiBaseURL = "http://localhost:8000/api/v1"  // Update for production
    
    func signInWithGoogle() {
        guard let presentingViewController = UIApplication.shared.windows.first?.rootViewController else {
            return
        }
        
        GIDSignIn.sharedInstance.signIn(withPresenting: presentingViewController) { [weak self] result, error in
            
            if let error = error {
                self?.errorMessage = "Google Sign-In failed: \(error.localizedDescription)"
                return
            }
            
            guard let user = result?.user,
                  let idToken = user.idToken?.tokenString else {
                self?.errorMessage = "Failed to get ID token from Google"
                return
            }
            
            Task {
                await self?.sendGoogleTokenToBackend(
                    idToken: idToken,
                    accessToken: user.accessToken.tokenString,
                    email: user.profile?.email,
                    fullName: user.profile?.name,
                    givenName: user.profile?.givenName,
                    familyName: user.profile?.familyName,
                    pictureURL: user.profile?.imageURL(withDimension: 200)?.absoluteString
                )
            }
        }
    }
    
    private func sendGoogleTokenToBackend(
        idToken: String,
        accessToken: String,
        email: String?,
        fullName: String?,
        givenName: String?,
        familyName: String?,
        pictureURL: String?
    ) async {
        let requestBody = GoogleSignInRequest(
            id_token: idToken,
            access_token: accessToken,
            email: email,
            full_name: fullName,
            given_name: givenName,
            family_name: familyName,
            picture_url: pictureURL
        )
        
        do {
            let url = URL(string: "\(apiBaseURL)/auth/google/signin")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONEncoder().encode(requestBody)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                throw AuthError.invalidResponse
            }
            
            let authResponse = try JSONDecoder().decode(OAuthSignInResponse.self, from: data)
            
            DispatchQueue.main.async {
                self.handleSuccessfulAuth(authResponse)
            }
            
        } catch {
            DispatchQueue.main.async {
                self.errorMessage = "Google Sign-In failed: \(error.localizedDescription)"
            }
        }
    }
    
    private func handleSuccessfulAuth(_ response: OAuthSignInResponse) {
        // Store tokens securely
        TokenManager.shared.storeTokens(response)
        
        // Update UI
        self.isSignedIn = true
        self.errorMessage = nil
        
        print("Google Sign-In successful for user: \(response.user.email ?? "Unknown")")
        print("Is new user: \(response.is_new_user)")
    }
}
```

### 3. Data Models

```swift
// Request Models
struct AppleSignInRequest: Codable {
    let id_token: String
    let user_identifier: String
    let email: String?
    let full_name: String?
}

struct GoogleSignInRequest: Codable {
    let id_token: String
    let access_token: String?
    let email: String?
    let full_name: String?
    let given_name: String?
    let family_name: String?
    let picture_url: String?
}

// Response Models
struct OAuthSignInResponse: Codable {
    let access_token: String
    let refresh_token: String
    let expires_in: Int
    let token_type: String
    let user: User
    let is_new_user: Bool
}

struct User: Codable {
    let id: String
    let email: String?
    let phone: String?
    let full_name: String?
    let is_active: Bool
    let is_superuser: Bool
    let supabase_id: String?
}

enum AuthError: Error {
    case invalidResponse
    case missingIdToken
    case networkError
    case decodingError
}
```

### 4. SwiftUI Integration

```swift
import SwiftUI

struct LoginView: View {
    @StateObject private var appleSignIn = AppleSignInManager()
    @StateObject private var googleSignIn = GoogleSignInManager()
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Welcome to Hero365")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            // Apple Sign-In Button
            SignInWithAppleButton(
                onRequest: { request in
                    request.requestedScopes = [.fullName, .email]
                }
            ) { result in
                appleSignIn.signInWithApple()
            }
            .frame(height: 50)
            .signInWithAppleButtonStyle(.black)
            
            // Google Sign-In Button
            Button("Sign in with Google") {
                googleSignIn.signInWithGoogle()
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
            
            if let error = appleSignIn.errorMessage ?? googleSignIn.errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .font(.caption)
            }
        }
        .padding()
        .onChange(of: appleSignIn.isSignedIn) { isSignedIn in
            if isSignedIn {
                // Navigate to main app
            }
        }
        .onChange(of: googleSignIn.isSignedIn) { isSignedIn in
            if isSignedIn {
                // Navigate to main app
            }
        }
    }
}
```

### 5. Token Management

```swift
import KeychainAccess

class TokenManager {
    static let shared = TokenManager()
    private let keychain = Keychain(service: "com.yourapp.hero365")
        .accessibility(.whenUnlockedThisDeviceOnly)
    
    private init() {}
    
    func storeTokens(_ response: OAuthSignInResponse) {
        keychain["hero365_access_token"] = response.access_token
        keychain["hero365_refresh_token"] = response.refresh_token
        
        // Store expiry time
        let expiryDate = Date().addingTimeInterval(TimeInterval(response.expires_in))
        let expiryData = try? JSONEncoder().encode(expiryDate)
        keychain["hero365_token_expiry"] = expiryData?.base64EncodedString()
    }
    
    func getAccessToken() -> String? {
        return keychain["hero365_access_token"]
    }
    
    func getRefreshToken() -> String? {
        return keychain["hero365_refresh_token"]
    }
    
    func clearTokens() {
        keychain["hero365_access_token"] = nil
        keychain["hero365_refresh_token"] = nil
        keychain["hero365_token_expiry"] = nil
    }
    
    func isTokenExpired() -> Bool {
        guard let expiryString = keychain["hero365_token_expiry"],
              let expiryData = Data(base64Encoded: expiryString),
              let expiryDate = try? JSONDecoder().decode(Date.self, from: expiryData) else {
            return true
        }
        
        return Date() >= expiryDate
    }
}
```

## 🔧 Backend Configuration

### Supabase Dashboard Setup

1. Go to your **Supabase Dashboard**
2. Navigate to **Authentication > Providers**
3. **Enable Apple Sign-In:**
   - Toggle on Apple
   - Add your Apple Client ID
   - Add your Apple Team ID
   - Upload your Apple Private Key
4. **Enable Google Sign-In:**
   - Toggle on Google
   - Add your Google Client ID
   - Add your Google Client Secret

### Your Backend Endpoints

Your backend now provides these OAuth endpoints:

```http
# OAuth Endpoints (your backend)
POST /api/v1/auth/apple/signin   # Apple Sign-In with ID token
POST /api/v1/auth/google/signin  # Google Sign-In with ID token

# Standard Auth Endpoints
POST /api/v1/auth/signup         # Email/password signup
POST /api/v1/auth/signin         # Email/password signin
POST /api/v1/auth/otp/send       # Send SMS OTP
POST /api/v1/auth/otp/verify     # Verify SMS OTP

# User Endpoints
GET /api/v1/users/me             # Get current user (requires auth)
```

## 🔄 Authentication Flow

### Apple Sign-In Flow
```
1. User taps "Sign in with Apple" button
2. iOS shows native Apple Sign-In UI
3. User authenticates with Face ID/Touch ID/Passcode
4. iOS app receives ID token from Apple
5. App sends POST to /api/v1/auth/apple/signin with ID token
6. Backend validates ID token with Supabase
7. Backend returns access_token + refresh_token
8. App stores tokens securely in Keychain
```

### Google Sign-In Flow
```
1. User taps "Sign in with Google" button
2. iOS shows Google Sign-In UI
3. User authenticates with Google account
4. iOS app receives ID token from Google
5. App sends POST to /api/v1/auth/google/signin with ID token
6. Backend validates ID token with Supabase
7. Backend returns access_token + refresh_token
8. App stores tokens securely in Keychain
```

## 🧪 Testing

### Test Apple Sign-In
```bash
curl -X POST http://localhost:8000/api/v1/auth/apple/signin \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_identifier": "000123.abc456def789.1234",
    "email": "test@privaterelay.appleid.com",
    "full_name": "Test User"
  }'
```

### Test Google Sign-In
```bash
curl -X POST http://localhost:8000/api/v1/auth/google/signin \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access_token": "ya29.a0ARrdaM...",
    "email": "test@gmail.com",
    "full_name": "Test User"
  }'
```

## 🚨 Troubleshooting

### Common Issues

**1. 422 Unprocessable Entity:**
- Check that all required fields are included in the request
- Verify JSON format is correct
- Ensure `id_token` and `user_identifier` are provided for Apple
- Ensure `id_token` is provided for Google

**2. ID Token validation failed:**
- Ensure your Supabase project has Apple/Google OAuth properly configured
- Check that the ID token is being sent correctly from iOS
- Verify the token hasn't expired (Apple ID tokens expire after 10 minutes)
- Error: "Unable to detect issuer in ID token" means invalid/test token

**3. Backend returning 401:**
- Check Supabase logs in your dashboard
- Ensure OAuth providers are enabled in Supabase
- Verify your iOS app is configured correctly with Apple/Google
- Make sure you're using real ID tokens, not test strings

**4. iOS app not getting ID token:**
- For Apple: Ensure you're testing on a physical device
- For Google: Check GoogleService-Info.plist configuration
- Verify OAuth client IDs are correct

### Debug Logging

Your backend now includes detailed logging. Watch for these messages:

```
🍎 Apple Sign-In attempt for user: [user_identifier]
📧 Email: [email]
👤 Full name: [full_name]
🔑 ID token length: [length] chars
✅ Apple Sign-In successful for Supabase user: [user_id]
❌ Apple Sign-In error: [error_details]
```

### Testing with Real Tokens

**Important**: The endpoints require real ID tokens from Apple/Google:

- ❌ Test strings like `"test_token"` will fail with validation errors
- ✅ Real ID tokens from iOS Sign-In will work properly
- 🔍 Use the debug logging to verify token format and length

## 📚 Additional Resources

- [Apple Sign-In Documentation](https://developer.apple.com/sign-in-with-apple/)
- [Google Sign-In for iOS](https://developers.google.com/identity/sign-in/ios)
- [Supabase Auth Guide](https://supabase.com/docs/guides/auth)

## ✅ Summary

This approach maintains your existing architecture pattern:

- **✅ Consistent Flow**: iOS App → Backend → Supabase (same as email/phone)
- **✅ Centralized Logic**: All authentication logic in your backend
- **✅ Simple iOS Integration**: Just handle native OAuth and send ID tokens
- **✅ Secure**: ID tokens are validated server-side by Supabase
- **✅ No Additional Dependencies**: No need for Supabase iOS SDK
- **✅ Debug Logging**: Detailed logs help troubleshoot issues 