# Lead Source Standardization API

## Overview

This document outlines the standardized lead source system for Hero365, ensuring consistency between the mobile app and backend API. The lead sources have been unified across Contact and Job entities to provide a comprehensive set of acquisition channels.

## Standardized Lead Sources

The following lead sources are now available across both contacts and jobs:

| API Value | Display Name | Description |
|-----------|--------------|-------------|
| `website` | Website | Contact from company website |
| `google_ads` | Google Ads | Contact from Google advertising campaigns |
| `social_media` | Social Media | Contact from social media platforms |
| `referral` | Referral | Contact from customer/partner referrals |
| `phone_call` | Phone Call | Contact initiated through phone calls |
| `walk_in` | Walk-In | Contact from walk-in customers |
| `email_marketing` | Email Marketing | Contact from email marketing campaigns |
| `trade_show` | Trade Show | Contact from trade shows and exhibitions |
| `direct_mail` | Direct Mail | Contact from direct mail campaigns |
| `yellow_pages` | Yellow Pages | Contact from Yellow Pages listings |
| `partner` | Partner | Contact from business partners |
| `existing_customer` | Existing Customer | Contact from existing customer referrals |
| `cold_outreach` | Cold Outreach | Contact from cold calling/outreach |
| `event` | Event | Contact from events and conferences |
| `direct` | Direct | Direct contact without specific channel |
| `other` | Other | Other unlisted sources |

## Additional Job-Specific Sources

For jobs, the following additional sources are available:

| API Value | Display Name | Description |
|-----------|--------------|-------------|
| `repeat_customer` | Repeat Customer | Job from existing customer |
| `emergency_call` | Emergency Call | Job from emergency service calls |

## Mobile App Integration

### Swift Enum Mapping

Your current Swift enum should be updated to use the API values:

```swift
enum LeadSource: String, CaseIterable {
    case website = "website"
    case googleAds = "google_ads"
    case socialMedia = "social_media"
    case referral = "referral"
    case phoneCall = "phone_call"
    case walkIn = "walk_in"
    case emailMarketing = "email_marketing"
    case tradeShow = "trade_show"
    case directMail = "direct_mail"
    case yellowPages = "yellow_pages"
    case partner = "partner"
    case existingCustomer = "existing_customer"
    case coldOutreach = "cold_outreach"
    case event = "event"
    case direct = "direct"
    case other = "other"
    
    var displayName: String {
        switch self {
        case .website: return "Website"
        case .googleAds: return "Google Ads"
        case .socialMedia: return "Social Media"
        case .referral: return "Referral"
        case .phoneCall: return "Phone Call"
        case .walkIn: return "Walk-In"
        case .emailMarketing: return "Email Marketing"
        case .tradeShow: return "Trade Show"
        case .directMail: return "Direct Mail"
        case .yellowPages: return "Yellow Pages"
        case .partner: return "Partner"
        case .existingCustomer: return "Existing Customer"
        case .coldOutreach: return "Cold Outreach"
        case .event: return "Event"
        case .direct: return "Direct"
        case .other: return "Other"
        }
    }
}
```

### Job-Specific Sources (if needed)

```swift
enum JobSource: String, CaseIterable {
    // All LeadSource cases plus:
    case repeatCustomer = "repeat_customer"
    case emergencyCall = "emergency_call"
    
    var displayName: String {
        switch self {
        case .repeatCustomer: return "Repeat Customer"
        case .emergencyCall: return "Emergency Call"
        // Include all LeadSource display names...
        }
    }
}
```

## API Usage

### Creating a Contact with Source

```http
POST /api/v1/contacts/
```

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "source": "google_ads",
    "contact_type": "lead",
    "business_id": "business-uuid"
}
```

### Creating a Job with Source

```http
POST /api/v1/jobs/
```

```json
{
    "title": "HVAC Repair",
    "job_type": "repair",
    "source": "phone_call",
    "contact_id": "contact-uuid",
    "business_id": "business-uuid"
}
```

### Filtering by Source

```http
GET /api/v1/contacts/?source=google_ads
GET /api/v1/jobs/?source=referral
```

## Migration Notes

### Database Changes

- The `source` column in both `contacts` and `jobs` tables now supports the expanded enum values
- Existing data with old source values will continue to work
- New values are available immediately

### Backward Compatibility

- Old source values are still supported but deprecated
- Mapping from old to new values:
  - `advertising` → `google_ads` (for most cases)
  - `cold_call` → `phone_call` or `cold_outreach`
  - `marketing` → `email_marketing` or `social_media`

### Frontend TypeScript Types

The TypeScript client has been automatically updated with the new source types:

```typescript
export type ContactSourceSchema = 
  | "website"
  | "google_ads"
  | "social_media"
  | "referral"
  | "phone_call"
  | "walk_in"
  | "email_marketing"
  | "trade_show"
  | "direct_mail"
  | "yellow_pages"
  | "partner"
  | "existing_customer"
  | "cold_outreach"
  | "event"
  | "direct"
  | "other";
```

## Benefits

1. **Consistency**: Same lead sources across web and mobile apps
2. **Comprehensive**: Covers all major acquisition channels
3. **Future-proof**: Easy to add new sources as needed
4. **Analytics**: Better tracking and reporting capabilities
5. **User Experience**: Consistent terminology across platforms

## Analytics & Reporting

With standardized lead sources, you can now:

- Track lead conversion rates by source
- Identify most effective marketing channels
- Calculate ROI for different acquisition methods
- Generate consistent reports across platforms
- Segment customers by acquisition channel

## Next Steps

1. Update your mobile app's lead source enum to match the API values
2. Test the integration with sample data
3. Update any analytics or reporting code to use the new values
4. Consider adding source-specific validation or business rules as needed 