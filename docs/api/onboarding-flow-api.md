# Onboarding Flow API Documentation

## Overview

The Hero365 onboarding API provides a comprehensive, profile-first, activity-driven flow for creating new businesses. This API is designed specifically for mobile applications and follows a step-by-step approach to guide users through business setup.

## Base URL

```
Production: https://hero365-backend-production.up.railway.app/api/v1/onboarding
Development: http://localhost:8000/api/v1/onboarding
```

## Authentication

All endpoints except session management require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Onboarding Flow Steps

The onboarding process follows these steps:

1. **Session Start** - Initialize onboarding session
2. **Profile Selection** - Choose primary trade profile
3. **Activity Selection** - Select specific activities within the trade
4. **Business Details** - Provide business information
5. **Service Templates** - Auto-adopt or select service templates
6. **Completion** - Create business and finalize setup

---

## API Endpoints

### 1. Session Management

#### Start Onboarding Session

**POST** `/session/start`

Initialize a new onboarding session for tracking and analytics.

**Request Body:**
```json
{
  "user_agent": "Hero365-iOS/1.0.0",
  "referral_source": "web_search",
  "utm_parameters": {
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "contractor_signup"
  }
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires_at": "2025-01-03T12:00:00Z",
  "current_step": "profile_selection",
  "available_profiles_count": 24,
  "estimated_completion_time": "5-10 minutes",
  "analytics_enabled": true
}
```

---

### 2. Profile Selection

#### Get All Profiles

**GET** `/profiles`

Retrieve all available trade profiles with enhanced onboarding data.

**Query Parameters:**
- `search` (optional): Search term for profile names/synonyms
- `segments` (optional): Filter by market segments (`residential`, `commercial`, `both`)
- `popular_only` (optional): Show only popular profiles (boolean)

**Response:**
```json
{
  "profiles": [
    {
      "slug": "hvac",
      "name": "HVAC",
      "synonyms": ["heating", "ventilation", "air conditioning", "mechanical"],
      "segments": "residential",
      "icon": "thermometer",
      "description": "Heating, ventilation, and air conditioning systems",
      "activity_count": 4,
      "is_popular": true,
      "estimated_setup_time": "10 minutes"
    }
  ],
  "total_count": 24,
  "popular_count": 7,
  "stats": {
    "total_profiles": 24,
    "popular_profiles": [...],
    "total_activities": 50,
    "emergency_activities": 15,
    "total_templates": 100,
    "popular_templates": 25,
    "average_completion_time": "7 minutes",
    "completion_rate": 0.85
  }
}
```

#### Get Popular Profiles

**GET** `/profiles/popular`

Quick access to the most popular trade profiles.

**Response:** Same structure as `/profiles` but filtered for popular profiles only.

#### Search Profiles

**GET** `/profiles/search?q={search_term}`

Search profiles by name or synonyms.

**Query Parameters:**
- `q` (required): Search term

---

### 3. Activity Selection

#### Get Activities for Trade

**GET** `/profiles/{trade_slug}/activities`

Retrieve activities available for a specific trade profile.

**Path Parameters:**
- `trade_slug`: Trade profile slug (e.g., "hvac", "plumbing")

**Query Parameters:**
- `search` (optional): Search term for activity names
- `emergency_only` (optional): Show only emergency activities
- `popular_only` (optional): Show only popular activities

**Response:**
```json
{
  "activities": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "slug": "ac-repair",
      "name": "AC Repair",
      "description": "Professional ac repair services",
      "synonyms": ["air conditioning repair", "ac fix"],
      "tags": ["repair", "cooling", "emergency"],
      "is_popular": true,
      "is_emergency": false,
      "template_count": 3,
      "estimated_revenue": "$150-800"
    }
  ],
  "total_count": 4,
  "emergency_count": 1,
  "trade_profile": {
    "slug": "hvac",
    "name": "HVAC",
    "activity_count": 4,
    "is_popular": true
  }
}
```

#### Get Popular Activities

**GET** `/profiles/{trade_slug}/activities/popular`

Get only popular activities for a trade.

#### Get Emergency Activities

**GET** `/profiles/{trade_slug}/activities/emergency`

Get only emergency activities for a trade.

#### Search Activities

**GET** `/profiles/{trade_slug}/activities/search?q={search_term}`

Search activities within a specific trade.

---

### 4. Validation Endpoints

#### Validate Profile Selection

**POST** `/validate/profile`

Validate a selected trade profile.

**Request Body:**
```json
{
  "profile_slug": "hvac"
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "suggestions": [
    "Popular choice! This trade has high demand in most markets"
  ]
}
```

#### Validate Activity Selections

**POST** `/validate/activities`

Validate selected activities for a trade.

**Request Body:**
```json
{
  "trade_slug": "hvac",
  "activity_slugs": ["ac-repair", "furnace-repair", "hvac-maintenance"]
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "suggestions": [
    "Great selection! All chosen activities are in high demand"
  ]
}
```

#### Validate Business Details

**POST** `/validate/business-details`

Validate business information before creation.

**Request Body:**
```json
{
  "name": "Elite HVAC Services",
  "description": "Professional HVAC services for residential customers",
  "phone_number": "+1-555-123-4567",
  "business_email": "contact@elitehvac.com",
  "website": "https://elitehvac.com",
  "address": "123 Main St",
  "city": "Austin",
  "state": "TX",
  "zip_code": "78701",
  "company_size": "small",
  "market_focus": "residential",
  "business_registration_number": "TX123456789",
  "tax_id": "12-3456789",
  "business_license": "HVAC-TX-2024-001",
  "insurance_number": "INS-123456",
  "referral_source": "web_search",
  "primary_goals": ["increase_revenue", "grow_customer_base"]
}
```

#### Validate Complete Request

**POST** `/validate/complete`

Validate the entire onboarding request before processing.

**Request Body:** Complete onboarding request (see completion section)

---

### 5. Completion

#### Complete Onboarding

**POST** `/complete`

Complete the entire onboarding process and create the business.

**Request Body:**
```json
{
  "primary_trade_slug": "hvac",
  "selected_activity_slugs": ["ac-repair", "furnace-repair", "hvac-maintenance"],
  "business_details": {
    "name": "Elite HVAC Services",
    "description": "Professional HVAC services",
    "phone_number": "+1-555-123-4567",
    "business_email": "contact@elitehvac.com",
    "city": "Austin",
    "state": "TX",
    "postal_code": "78701",
    "company_size": "small",
    "market_focus": "residential"
  },
  "template_selections": {
    "activity_slugs": ["ac-repair", "furnace-repair", "hvac-maintenance"],
    "template_slugs": [],
    "auto_adopt_popular": true
  },
  "onboarding_session_id": "550e8400-e29b-41d4-a716-446655440000",
  "completion_time_seconds": 420
}
```

**Response:**
```json
{
  "business_id": "550e8400-e29b-41d4-a716-446655440010",
  "business_name": "Elite HVAC Services",
  "primary_trade": {
    "slug": "hvac",
    "name": "HVAC",
    "is_popular": true,
    "activity_count": 3
  },
  "selected_activities": [
    {
      "slug": "ac-repair",
      "name": "AC Repair",
      "is_popular": true,
      "is_emergency": false,
      "estimated_revenue": "$150-800"
    }
  ],
  "adopted_templates": [
    "hvac-ac-repair-emergency",
    "hvac-furnace-repair-standard",
    "hvac-maintenance-annual"
  ],
  "created_services": 3,
  "recommended_next_steps": [
    "Set up your service areas and pricing",
    "Upload your business logo and photos",
    "Configure your booking availability",
    "Create your first customer estimate"
  ],
  "onboarding_completion_time": "420 seconds",
  "setup_completion_percentage": 75.0,
  "estimated_revenue_potential": "$100K-300K annually"
}
```

---

## Mobile Implementation Guide

### 1. Onboarding Flow Implementation

```swift
// 1. Start Session
let sessionRequest = OnboardingSessionRequest(
    userAgent: "Hero365-iOS/1.0.0",
    referralSource: .webSearch
)
let session = await onboardingAPI.startSession(sessionRequest)

// 2. Get Profiles
let profiles = await onboardingAPI.getProfiles(popularOnly: true)

// 3. Validate Profile Selection
let profileValidation = await onboardingAPI.validateProfile("hvac")

// 4. Get Activities
let activities = await onboardingAPI.getActivities(
    tradeSlug: "hvac", 
    popularOnly: true
)

// 5. Validate Activities
let activityValidation = await onboardingAPI.validateActivities(
    tradeSlug: "hvac",
    activitySlugs: ["ac-repair", "furnace-repair"]
)

// 6. Complete Onboarding
let completionRequest = CompleteOnboardingRequest(
    primaryTradeSlug: "hvac",
    selectedActivitySlugs: ["ac-repair", "furnace-repair"],
    businessDetails: businessDetails,
    templateSelections: templateSelections
)
let completion = await onboardingAPI.complete(completionRequest)
```

### 2. Error Handling

```swift
enum OnboardingError: Error {
    case validationFailed([String])
    case networkError(String)
    case serverError(String)
}

func handleOnboardingError(_ error: Error) {
    switch error {
    case OnboardingError.validationFailed(let errors):
        // Show validation errors to user
        showValidationErrors(errors)
    case OnboardingError.networkError(let message):
        // Handle network connectivity issues
        showNetworkError(message)
    case OnboardingError.serverError(let message):
        // Handle server errors
        showServerError(message)
    }
}
```

### 3. Progress Tracking

```swift
struct OnboardingProgress {
    let currentStep: OnboardingStep
    let completedSteps: [OnboardingStep]
    let progressPercentage: Double
    
    var canProceed: Bool {
        // Implement validation logic
    }
}

// Update progress based on current step
func updateProgress() {
    let progress = OnboardingProgress(
        currentStep: .activitySelection,
        completedSteps: [.profileSelection],
        progressPercentage: 40.0
    )
    
    progressView.setProgress(progress.progressPercentage / 100.0)
}
```

### 4. Caching Strategy

```swift
class OnboardingCache {
    private let cache = NSCache<NSString, AnyObject>()
    
    func cacheProfiles(_ profiles: [OnboardingProfile]) {
        cache.setObject(profiles as AnyObject, forKey: "profiles")
    }
    
    func getCachedProfiles() -> [OnboardingProfile]? {
        return cache.object(forKey: "profiles") as? [OnboardingProfile]
    }
}
```

---

## Data Models

### Core Models

```typescript
interface OnboardingProfile {
  slug: string;
  name: string;
  synonyms: string[];
  segments: 'residential' | 'commercial' | 'both';
  icon?: string;
  description?: string;
  activity_count: number;
  is_popular: boolean;
  estimated_setup_time?: string;
}

interface OnboardingActivity {
  id: string;
  slug: string;
  name: string;
  description?: string;
  synonyms: string[];
  tags: string[];
  is_popular: boolean;
  is_emergency: boolean;
  template_count: number;
  estimated_revenue?: string;
}

interface BusinessDetails {
  name: string;
  description?: string;
  phone_number?: string;
  business_email?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  company_size: 'just_me' | 'small' | 'medium' | 'large' | 'enterprise';
  market_focus: 'residential' | 'commercial' | 'both';
  business_registration_number?: string;
  tax_id?: string;
  business_license?: string;
  insurance_number?: string;
  referral_source?: string;
  primary_goals: string[];
}
```

---

## Best Practices

### 1. User Experience

- **Progressive Disclosure**: Show popular options first, allow expansion to full lists
- **Smart Defaults**: Pre-select popular activities based on trade selection
- **Validation Feedback**: Show real-time validation with helpful suggestions
- **Progress Indication**: Clear progress bar and step indicators

### 2. Performance

- **Caching**: Cache profiles and activities for offline browsing
- **Lazy Loading**: Load activities only when trade is selected
- **Batch Validation**: Validate complete flow before submission
- **Optimistic UI**: Show immediate feedback while API calls are in progress

### 3. Error Handling

- **Graceful Degradation**: Handle network errors gracefully
- **Retry Logic**: Implement exponential backoff for failed requests
- **Offline Support**: Cache essential data for offline onboarding
- **User Feedback**: Provide clear, actionable error messages

### 4. Analytics

- **Step Tracking**: Track completion of each onboarding step
- **Drop-off Analysis**: Identify where users abandon the flow
- **Performance Metrics**: Monitor API response times and error rates
- **A/B Testing**: Test different onboarding flows and measure conversion

---

## Testing

### Sample Test Data

```json
{
  "test_profiles": [
    {
      "slug": "hvac",
      "name": "HVAC",
      "is_popular": true,
      "activity_count": 4
    }
  ],
  "test_activities": [
    {
      "slug": "ac-repair",
      "name": "AC Repair",
      "trade_slug": "hvac",
      "is_popular": true
    }
  ]
}
```

### Integration Tests

1. **Complete Flow Test**: Test entire onboarding from start to completion
2. **Validation Tests**: Test all validation scenarios
3. **Error Handling**: Test network failures and server errors
4. **Performance Tests**: Measure API response times
5. **Offline Tests**: Test cached data functionality

---

## Support

For technical support or questions about the onboarding API:

- **Documentation**: This document and OpenAPI spec
- **API Status**: Monitor endpoint health and performance
- **Error Codes**: Reference error code documentation
- **Contact**: Backend team for integration support

---

## Changelog

### Version 2.0.0 (Current)
- Complete rewrite with profile-first, activity-driven flow
- Enhanced validation and suggestions
- Automatic service template adoption
- Comprehensive mobile-optimized responses
- Session management and progress tracking

### Version 1.0.0 (Legacy)
- Basic profile and activity selection
- Simple business creation
- Limited validation
