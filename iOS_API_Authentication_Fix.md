# iOS API Authentication Integration Fix

## 🚨 Issue
The iOS app is making API requests to `/api/v1/businesses/` without including authentication tokens, resulting in `403 Forbidden` errors.

## ✅ Solution
All authenticated API requests must include the Bearer token in the Authorization header.

## 📱 iOS Implementation

### 1. API Service with Authentication

```swift
import Foundation

class APIService {
    static let shared = APIService()
    private let baseURL = "http://localhost:8000/api/v1"  // Update for production
    
    private init() {}
    
    // MARK: - Generic Request Method with Authentication
    private func authenticatedRequest<T: Codable>(
        endpoint: String,
        method: HTTPMethod = .GET,
        body: Data? = nil,
        responseType: T.Type
    ) async throws -> T {
        
        // Get the access token
        guard let accessToken = TokenManager.shared.getAccessToken() else {
            throw APIError.notAuthenticated
        }
        
        // Check if token is expired and refresh if needed
        if TokenManager.shared.isTokenExpired() {
            try await refreshTokenIfNeeded()
        }
        
        // Create the request
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // 🔑 Add Bearer token to Authorization header
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        if let body = body {
            request.httpBody = body
        }
        
        // Log the request for debugging
        print("🌐 API Request: \(method.rawValue) \(endpoint)")
        print("🔑 Authorization: Bearer \(accessToken.prefix(20))...")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        print("📊 API Response: \(httpResponse.statusCode)")
        
        guard 200...299 ~= httpResponse.statusCode else {
            if httpResponse.statusCode == 401 {
                throw APIError.notAuthenticated
            } else if httpResponse.statusCode == 403 {
                throw APIError.forbidden
            }
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        let decodedResponse = try JSONDecoder().decode(responseType, from: data)
        return decodedResponse
    }
    
    // MARK: - Business API Methods
    
    func createBusiness(_ request: CreateBusinessRequest) async throws -> BusinessResponse {
        let body = try JSONEncoder().encode(request)
        return try await authenticatedRequest(
            endpoint: "/businesses/",
            method: .POST,
            body: body,
            responseType: BusinessResponse.self
        )
    }
    
    func getMyBusinesses(skip: Int = 0, limit: Int = 10) async throws -> [UserBusinessSummaryResponse] {
        return try await authenticatedRequest(
            endpoint: "/businesses/me?skip=\(skip)&limit=\(limit)",
            method: .GET,
            responseType: [UserBusinessSummaryResponse].self
        )
    }
    
    func getCurrentUser() async throws -> UserResponse {
        return try await authenticatedRequest(
            endpoint: "/users/me",
            method: .GET,
            responseType: UserResponse.self
        )
    }
    
    // MARK: - Token Refresh
    private func refreshTokenIfNeeded() async throws {
        guard let refreshToken = TokenManager.shared.getRefreshToken() else {
            throw APIError.notAuthenticated
        }
        
        // Implement token refresh logic here
        // This should call your backend's refresh token endpoint
        print("🔄 Refreshing access token...")
        // TODO: Implement refresh token logic
    }
}

enum HTTPMethod: String {
    case GET = "GET"
    case POST = "POST"
    case PUT = "PUT"
    case DELETE = "DELETE"
}

enum APIError: Error, LocalizedError {
    case notAuthenticated
    case forbidden
    case invalidURL
    case invalidResponse
    case serverError(Int)
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .notAuthenticated:
            return "User is not authenticated. Please sign in again."
        case .forbidden:
            return "You don't have permission to perform this action."
        case .invalidURL:
            return "Invalid API URL"
        case .invalidResponse:
            return "Invalid server response"
        case .serverError(let code):
            return "Server error with code: \(code)"
        case .decodingError:
            return "Failed to decode server response"
        }
    }
}
```

### 2. Business Creation Usage

```swift
class BusinessManager: ObservableObject {
    @Published var businesses: [UserBusinessSummaryResponse] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func createBusiness(name: String, industry: String, description: String? = nil) async {
        DispatchQueue.main.async {
            self.isLoading = true
            self.errorMessage = nil
        }
        
        do {
            let request = CreateBusinessRequest(
                name: name,
                industry: industry,
                description: description
            )
            
            let business = try await APIService.shared.createBusiness(request)
            
            DispatchQueue.main.async {
                self.isLoading = false
                print("✅ Business created successfully: \(business.name)")
                // Refresh the business list
                Task {
                    await self.loadMyBusinesses()
                }
            }
            
        } catch {
            DispatchQueue.main.async {
                self.isLoading = false
                self.errorMessage = error.localizedDescription
                print("❌ Business creation failed: \(error.localizedDescription)")
            }
        }
    }
    
    func loadMyBusinesses() async {
        do {
            let businesses = try await APIService.shared.getMyBusinesses()
            DispatchQueue.main.async {
                self.businesses = businesses
            }
        } catch {
            DispatchQueue.main.async {
                self.errorMessage = error.localizedDescription
            }
        }
    }
}
```

### 3. Updated TokenManager (if not already implemented)

```swift
import KeychainAccess

class TokenManager {
    static let shared = TokenManager()
    private let keychain = Keychain(service: "com.hero365.app")
        .accessibility(.whenUnlockedThisDeviceOnly)
    
    private init() {}
    
    func storeTokens(_ response: OAuthSignInResponse) {
        keychain["hero365_access_token"] = response.access_token
        keychain["hero365_refresh_token"] = response.refresh_token
        
        // Store expiry time
        let expiryDate = Date().addingTimeInterval(TimeInterval(response.expires_in))
        let expiryData = try? JSONEncoder().encode(expiryDate)
        keychain["hero365_token_expiry"] = expiryData?.base64EncodedString()
        
        print("✅ Tokens stored successfully")
    }
    
    func getAccessToken() -> String? {
        let token = keychain["hero365_access_token"]
        if token == nil {
            print("❌ No access token found in keychain")
        }
        return token
    }
    
    func getRefreshToken() -> String? {
        return keychain["hero365_refresh_token"]
    }
    
    func clearTokens() {
        keychain["hero365_access_token"] = nil
        keychain["hero365_refresh_token"] = nil
        keychain["hero365_token_expiry"] = nil
        print("🗑️ All tokens cleared")
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

### 4. Data Models

```swift
// Request Models
struct CreateBusinessRequest: Codable {
    let name: String
    let industry: String
    let description: String?
}

// Response Models
struct BusinessResponse: Codable {
    let id: String
    let name: String
    let industry: String
    let description: String?
    let created_at: String
    let owner_id: String
}

struct UserBusinessSummaryResponse: Codable {
    let business: BusinessResponse
    let membership: BusinessMembershipResponse
}

struct BusinessMembershipResponse: Codable {
    let id: String
    let business_id: String
    let user_id: String
    let role: String
    let permissions: [String]
    let is_active: Bool
    let joined_at: String
}

struct UserResponse: Codable {
    let id: String
    let email: String?
    let phone: String?
    let user_metadata: [String: Any]?
    let created_at: String
    let is_onboarded: Bool
}

struct OAuthSignInResponse: Codable {
    let access_token: String
    let refresh_token: String
    let expires_in: Int
    let user: UserResponse
    let is_new_user: Bool
}
```

## 🔍 Debugging Steps

1. **Check if tokens are stored after sign-in:**
   ```swift
   print("Access token: \(TokenManager.shared.getAccessToken() ?? "nil")")
   ```

2. **Verify API requests include Authorization header:**
   ```swift
   // Add this to your request logging
   print("🔑 Authorization header: \(request.value(forHTTPHeaderField: "Authorization") ?? "missing")")
   ```

3. **Test authentication flow:**
   ```swift
   // After successful sign-in, test API call immediately
   Task {
       do {
           let user = try await APIService.shared.getCurrentUser()
           print("✅ Authentication working: \(user.email ?? "Unknown")")
       } catch {
           print("❌ Authentication failed: \(error)")
       }
   }
   ```

## ✅ Checklist

- [ ] Authentication tokens are stored after successful sign-in
- [ ] All API requests include `Authorization: Bearer <token>` header
- [ ] Token expiry is checked before API calls
- [ ] Error handling for 401/403 responses
- [ ] Debug logging shows token presence in requests
- [ ] Test business creation with valid authentication

## 🚨 Common Issues

1. **Still getting 403?** → Token not being sent or is invalid
2. **401 Unauthorized?** → Token has expired, implement refresh logic
3. **No token in keychain?** → Sign-in flow not storing tokens correctly

The core fix is ensuring **every authenticated API request includes the Bearer token** in the Authorization header. 