# Simplified Onboarding - Client Implementation Guide

## Overview

This document provides step-by-step instructions for implementing the simplified business-membership-based onboarding system in the Hero365 mobile app.

## Key Changes Summary

### What Changed
- **Simplified Logic**: Onboarding completion is now determined solely by business membership status
- **Removed Fields**: No more `onboarding_completed`, `onboarding_completed_at`, `completed_steps`
- **Removed Endpoints**: No more `POST /users/me/onboarding-completed`
- **New Logic**: `needs_onboarding = user has NO active business memberships`

### What This Means
- Users who create businesses automatically complete onboarding
- Users who join existing businesses skip onboarding entirely
- Failed business creation keeps users in onboarding flow
- No manual onboarding completion tracking needed

## API Changes

### Updated User Profile Response

**Endpoint**: `GET /api/v1/users/me`

**Old Response** (Remove these fields):
```json
{
  "onboarding_completed": true,
  "onboarding_completed_at": "2024-01-02T15:45:00Z",
  "completed_steps": ["profile_setup", "preferences"]
}
```

**New Response** (Use these fields):
```json
{
  "id": "user-id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "business_memberships": [
    {
      "business_id": "business-uuid",
      "business_name": "Acme Services",
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

### Removed Endpoint
**DELETE**: `POST /api/v1/users/me/onboarding-completed` - No longer needed

## Implementation Steps

### Step 1: Update Data Models

**iOS (Swift)**:
```swift
// Update UserProfile model
struct UserProfile: Codable {
    let id: String
    let email: String?
    let fullName: String?
    let businessMemberships: [BusinessMembership]
    let hasBusinesses: Bool
    let needsOnboarding: Bool
    
    // Remove these old fields:
    // let onboardingCompleted: Bool
    // let onboardingCompletedAt: Date?
    // let completedSteps: [String]
    
    private enum CodingKeys: String, CodingKey {
        case id, email, businessMemberships, hasBusinesses, needsOnboarding
        case fullName = "full_name"
        case hasBusinesses = "has_businesses"
        case needsOnboarding = "needs_onboarding"
    }
}

struct BusinessMembership: Codable {
    let businessId: String
    let businessName: String
    let role: String
    let isOwner: Bool
    let isActive: Bool
    let joinedDate: Date
    
    private enum CodingKeys: String, CodingKey {
        case businessId = "business_id"
        case businessName = "business_name"
        case role
        case isOwner = "is_owner"
        case isActive = "is_active"
        case joinedDate = "joined_date"
    }
}
```

**Android (Kotlin)**:
```kotlin
// Update UserProfile data class
data class UserProfile(
    val id: String,
    val email: String?,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("business_memberships") val businessMemberships: List<BusinessMembership>,
    @SerializedName("has_businesses") val hasBusinesses: Boolean,
    @SerializedName("needs_onboarding") val needsOnboarding: Boolean
    
    // Remove these old fields:
    // @SerializedName("onboarding_completed") val onboardingCompleted: Boolean,
    // @SerializedName("onboarding_completed_at") val onboardingCompletedAt: Date?,
    // @SerializedName("completed_steps") val completedSteps: List<String>
)

data class BusinessMembership(
    @SerializedName("business_id") val businessId: String,
    @SerializedName("business_name") val businessName: String,
    val role: String,
    @SerializedName("is_owner") val isOwner: Boolean,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("joined_date") val joinedDate: Date
)
```

### Step 2: Update Onboarding Logic

**iOS (Swift)**:
```swift
class OnboardingManager {
    
    // REMOVE: Old complex onboarding logic
    // func markOnboardingCompleted() { ... }
    // func checkOnboardingSteps() { ... }
    
    // NEW: Simple business-based logic
    func checkOnboardingStatus() async throws -> OnboardingStatus {
        let userProfile = try await UserService.getCurrentUser()
        
        if userProfile.needsOnboarding {
            return .needsOnboarding
        } else {
            return .completed
        }
    }
    
    func handleOnboardingFlow() async {
        do {
            let status = try await checkOnboardingStatus()
            
            switch status {
            case .needsOnboarding:
                // Show onboarding flow
                await MainActor.run {
                    showOnboardingViewController()
                }
            case .completed:
                // Go to main app
                await MainActor.run {
                    showMainTabBarController()
                }
            }
        } catch {
            // Handle error - default to onboarding
            await MainActor.run {
                showOnboardingViewController()
            }
        }
    }
}

enum OnboardingStatus {
    case needsOnboarding
    case completed
}
```

**Android (Kotlin)**:
```kotlin
class OnboardingManager {
    
    // REMOVE: Old complex onboarding logic
    // fun markOnboardingCompleted() { ... }
    // fun checkOnboardingSteps() { ... }
    
    // NEW: Simple business-based logic
    suspend fun checkOnboardingStatus(): OnboardingStatus {
        return try {
            val userProfile = UserService.getCurrentUser()
            
            if (userProfile.needsOnboarding) {
                OnboardingStatus.NEEDS_ONBOARDING
            } else {
                OnboardingStatus.COMPLETED
            }
        } catch (e: Exception) {
            // Default to onboarding on error
            OnboardingStatus.NEEDS_ONBOARDING
        }
    }
    
    suspend fun handleOnboardingFlow() {
        val status = checkOnboardingStatus()
        
        when (status) {
            OnboardingStatus.NEEDS_ONBOARDING -> {
                // Show onboarding flow
                withContext(Dispatchers.Main) {
                    showOnboardingActivity()
                }
            }
            OnboardingStatus.COMPLETED -> {
                // Go to main app
                withContext(Dispatchers.Main) {
                    showMainActivity()
                }
            }
        }
    }
}

enum class OnboardingStatus {
    NEEDS_ONBOARDING,
    COMPLETED
}
```

### Step 3: Update App Launch Flow

**iOS (Swift)**:
```swift
// In AppDelegate or SceneDelegate
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    func applicationDidFinishLaunching(_ application: UIApplication) -> Bool {
        
        // Check authentication first
        if AuthManager.shared.isAuthenticated {
            // User is authenticated, check onboarding
            Task {
                await OnboardingManager.shared.handleOnboardingFlow()
            }
        } else {
            // Show login
            showLoginViewController()
        }
        
        return true
    }
}

// Update your main navigation logic
extension AppDelegate {
    
    func showOnboardingViewController() {
        let onboardingVC = OnboardingViewController()
        window?.rootViewController = UINavigationController(rootViewController: onboardingVC)
    }
    
    func showMainTabBarController() {
        let mainTabBar = MainTabBarController()
        window?.rootViewController = mainTabBar
    }
}
```

**Android (Kotlin)**:
```kotlin
// In MainActivity or SplashActivity
class SplashActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        lifecycleScope.launch {
            // Check authentication first
            if (AuthManager.isAuthenticated()) {
                // User is authenticated, check onboarding
                OnboardingManager.handleOnboardingFlow()
            } else {
                // Show login
                showLoginActivity()
            }
        }
    }
    
    private fun showOnboardingActivity() {
        val intent = Intent(this, OnboardingActivity::class.java)
        startActivity(intent)
        finish()
    }
    
    private fun showMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
    
    private fun showLoginActivity() {
        val intent = Intent(this, LoginActivity::class.java)
        startActivity(intent)
        finish()
    }
}
```

### Step 4: Update Business Creation Flow

**iOS (Swift)**:
```swift
class BusinessCreationViewController: UIViewController {
    
    @IBAction func createBusinessTapped(_ sender: UIButton) {
        Task {
            do {
                // Create business
                let business = try await BusinessService.createBusiness(
                    name: businessNameTextField.text!,
                    industry: selectedIndustry,
                    companySize: selectedSize
                )
                
                // Business creation automatically creates owner membership
                // No need to manually mark onboarding complete
                
                // Check user status and navigate
                await OnboardingManager.shared.handleOnboardingFlow()
                
            } catch {
                // Handle business creation error
                showErrorAlert("Failed to create business: \(error.localizedDescription)")
                // User stays in onboarding flow automatically
            }
        }
    }
}
```

**Android (Kotlin)**:
```kotlin
class BusinessCreationActivity : AppCompatActivity() {
    
    private fun createBusiness() {
        lifecycleScope.launch {
            try {
                // Create business
                val business = BusinessService.createBusiness(
                    name = businessNameEditText.text.toString(),
                    industry = selectedIndustry,
                    companySize = selectedSize
                )
                
                // Business creation automatically creates owner membership
                // No need to manually mark onboarding complete
                
                // Check user status and navigate
                OnboardingManager.handleOnboardingFlow()
                
            } catch (e: Exception) {
                // Handle business creation error
                showErrorDialog("Failed to create business: ${e.message}")
                // User stays in onboarding flow automatically
            }
        }
    }
}
```

### Step 5: Update Business Invitation Flow

**iOS (Swift)**:
```swift
class InvitationViewController: UIViewController {
    
    @IBAction func acceptInvitationTapped(_ sender: UIButton) {
        Task {
            do {
                // Accept invitation
                try await BusinessService.acceptInvitation(invitationId: invitation.id)
                
                // Invitation acceptance automatically creates membership
                // No need to manually mark onboarding complete
                
                // Check user status and navigate
                await OnboardingManager.shared.handleOnboardingFlow()
                
            } catch {
                showErrorAlert("Failed to accept invitation: \(error.localizedDescription)")
            }
        }
    }
}
```

**Android (Kotlin)**:
```kotlin
class InvitationActivity : AppCompatActivity() {
    
    private fun acceptInvitation() {
        lifecycleScope.launch {
            try {
                // Accept invitation
                BusinessService.acceptInvitation(invitation.id)
                
                // Invitation acceptance automatically creates membership
                // No need to manually mark onboarding complete
                
                // Check user status and navigate
                OnboardingManager.handleOnboardingFlow()
                
            } catch (e: Exception) {
                showErrorDialog("Failed to accept invitation: ${e.message}")
            }
        }
    }
}
```

### Step 6: Update Settings/Profile Screen

**iOS (Swift)**:
```swift
class ProfileViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        loadUserProfile()
    }
    
    private func loadUserProfile() {
        Task {
            do {
                let userProfile = try await UserService.getCurrentUser()
                
                await MainActor.run {
                    // Update UI with user info
                    nameLabel.text = userProfile.fullName
                    emailLabel.text = userProfile.email
                    
                    // Show business memberships
                    updateBusinessMemberships(userProfile.businessMemberships)
                    
                    // Show onboarding status (optional)
                    onboardingStatusLabel.text = userProfile.needsOnboarding ? 
                        "Complete your setup" : "Setup complete"
                }
            } catch {
                // Handle error
                showErrorAlert("Failed to load profile")
            }
        }
    }
    
    private func updateBusinessMemberships(_ memberships: [BusinessMembership]) {
        // Update UI to show user's businesses
        businessTableView.reloadData()
    }
}
```

**Android (Kotlin)**:
```kotlin
class ProfileFragment : Fragment() {
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        loadUserProfile()
    }
    
    private fun loadUserProfile() {
        lifecycleScope.launch {
            try {
                val userProfile = UserService.getCurrentUser()
                
                withContext(Dispatchers.Main) {
                    // Update UI with user info
                    nameTextView.text = userProfile.fullName
                    emailTextView.text = userProfile.email
                    
                    // Show business memberships
                    updateBusinessMemberships(userProfile.businessMemberships)
                    
                    // Show onboarding status (optional)
                    onboardingStatusTextView.text = if (userProfile.needsOnboarding) {
                        "Complete your setup"
                    } else {
                        "Setup complete"
                    }
                }
            } catch (e: Exception) {
                // Handle error
                showErrorDialog("Failed to load profile")
            }
        }
    }
    
    private fun updateBusinessMemberships(memberships: List<BusinessMembership>) {
        // Update UI to show user's businesses
        businessAdapter.updateMemberships(memberships)
    }
}
```

## Code Removal Checklist

### Remove These Files/Classes:
- [ ] `OnboardingCompletionRequest` model
- [ ] `OnboardingCompletionResponse` model
- [ ] Any `markOnboardingCompleted()` API calls
- [ ] Any `completedSteps` tracking logic
- [ ] Any manual onboarding state management

### Remove These API Calls:
- [ ] `POST /api/v1/users/me/onboarding-completed`
- [ ] Any manual onboarding completion tracking

### Remove These Fields from User Models:
- [ ] `onboarding_completed`
- [ ] `onboarding_completed_at`
- [ ] `completed_steps`

### Update These Fields in User Models:
- [ ] Add `business_memberships: [BusinessMembership]`
- [ ] Add `has_businesses: Bool`
- [ ] Add `needs_onboarding: Bool`

## Testing Scenarios

### Test Case 1: New User Creates Business
1. **Setup**: New user account, no businesses
2. **Expected**: `needs_onboarding: true`
3. **Action**: Go through onboarding, create business
4. **Expected**: `needs_onboarding: false`, redirect to main app

### Test Case 2: New User Joins Business
1. **Setup**: New user account, receives invitation
2. **Expected**: `needs_onboarding: true`
3. **Action**: Accept business invitation
4. **Expected**: `needs_onboarding: false`, skip onboarding, go to main app

### Test Case 3: Business Creation Fails
1. **Setup**: User in onboarding flow
2. **Action**: Attempt to create business, fails
3. **Expected**: `needs_onboarding: true`, stay in onboarding

### Test Case 4: User Leaves All Businesses
1. **Setup**: User with businesses, `needs_onboarding: false`
2. **Action**: User leaves/gets removed from all businesses
3. **Expected**: `needs_onboarding: true`, show onboarding on next app launch

### Test Case 5: Multiple Businesses
1. **Setup**: User with multiple business memberships
2. **Expected**: `needs_onboarding: false`, show all businesses in profile

## Migration Notes

### For Existing Users
- Users with existing businesses will automatically have `needs_onboarding: false`
- Users without businesses will have `needs_onboarding: true` and see onboarding
- No data migration needed on client side

### For Development
- Update all API integration tests
- Update UI tests for onboarding flow
- Test business creation and invitation flows
- Verify error handling scenarios

## Support

If you encounter issues during implementation:

1. **Check API Response**: Verify the `/users/me` endpoint returns the new fields
2. **Test Business Creation**: Ensure business creation creates owner membership
3. **Test Invitations**: Ensure invitation acceptance creates member membership
4. **Check Error Handling**: Verify failed operations don't leave users in inconsistent states

The simplified system should make onboarding much more reliable and easier to maintain! 