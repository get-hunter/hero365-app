# Contact API Fixes and Field Mapping

## Issues Resolved

### 1. Contact Source Field Mapping

**Issue**: iOS client was looking for `originalSource` field but API returns `source`

**Solution**: 
- API correctly uses `source` field (not `originalSource`)
- Updated OpenAPI specification to reflect current API structure
- Generated new client types with correct field mappings

**Client Changes Required**:
```swift
// Change from:
struct Contact {
    let originalSource: String?  // ❌ Wrong field name
}

// To:
struct Contact {
    let source: String?          // ✅ Correct field name
}
```

### 2. Contact Creation Failures

**Issue**: Contact creation was failing with 400 Bad Request due to missing database fields

**Root Cause**: 
- Contact entity includes `relationship_status` and `lifecycle_stage` fields
- Database table was missing these columns
- Repository was not mapping these fields correctly

**Solution**:
- Added missing fields to repository mapping
- Updated DTOs to include relationship and lifecycle tracking
- Enhanced API response schema with new fields

### Current API Response Structure

```json
{
  "id": "contact-uuid",
  "business_id": "business-uuid",
  "contact_type": "customer",
  "status": "active",
  "relationship_status": "active_client",
  "lifecycle_stage": "customer", 
  "source": "website",
  "priority": "high",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "created_date": "2024-01-15T10:30:00Z",
  "display_name": "John Doe",
  "type_display": "Customer",
  "status_display": "Active",
  "priority_display": "High",
  "source_display": "Website",
  "relationship_status_display": "Active Client",
  "lifecycle_stage_display": "Customer"
}
```

### New Fields Added

| Field | Type | Description | Values |
|-------|------|-------------|---------|
| `relationship_status` | `string` | Sales relationship status | `prospect`, `qualified_lead`, `opportunity`, `active_client`, `past_client`, `lost_lead`, `inactive` |
| `lifecycle_stage` | `string` | Customer lifecycle stage | `awareness`, `interest`, `consideration`, `decision`, `retention`, `customer` |
| `relationship_status_display` | `string` | Human-readable relationship status | "Active Client", "Prospect", etc. |
| `lifecycle_stage_display` | `string` | Human-readable lifecycle stage | "Customer", "Awareness", etc. |

### Source Field Values

The `source` field accepts these standardized values:

- `website`
- `google_ads` 
- `social_media`
- `referral`
- `phone_call`
- `walk_in`
- `email_marketing`
- `trade_show`
- `direct_mail`
- `yellow_pages`
- `partner`
- `existing_customer`
- `cold_outreach`
- `event`
- `direct`
- `other`

## Client Implementation

### 1. Update Contact Model

```swift
struct Contact: Codable {
    let id: String
    let businessId: String
    let contactType: String
    let status: String
    let relationshipStatus: String
    let lifecycleStage: String
    let source: String?  // ← Use 'source', not 'originalSource'
    let priority: String
    let firstName: String?
    let lastName: String?
    let email: String?
    let phone: String?
    let createdDate: String?
    let displayName: String
    let typeDisplay: String
    let statusDisplay: String
    let priorityDisplay: String
    let sourceDisplay: String
    let relationshipStatusDisplay: String
    let lifecycleStageDisplay: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case businessId = "business_id"
        case contactType = "contact_type"
        case status
        case relationshipStatus = "relationship_status"
        case lifecycleStage = "lifecycle_stage"
        case source      // ← Map to 'source' field
        case priority
        case firstName = "first_name"
        case lastName = "last_name"
        case email
        case phone
        case createdDate = "created_date"
        case displayName = "display_name"
        case typeDisplay = "type_display"
        case statusDisplay = "status_display"
        case priorityDisplay = "priority_display"
        case sourceDisplay = "source_display"
        case relationshipStatusDisplay = "relationship_status_display"
        case lifecycleStageDisplay = "lifecycle_stage_display"
    }
}
```

### 2. Update Source Enum

```swift
enum ContactSource: String, CaseIterable {
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

### 3. Handle Source Field Properly

```swift
extension Contact {
    var originalSource: ContactSource {
        // Use the 'source' field (not 'originalSource')
        guard let sourceValue = source,
              let contactSource = ContactSource(rawValue: sourceValue) else {
            return .other
        }
        return contactSource
    }
}
```

## Testing

### 1. Verify Field Mapping

```bash
# Test contact creation
curl -X POST "https://api.hero365.com/api/v1/contacts/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_type": "customer",
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "source": "website"
  }'
```

Expected response should include:
- `source: "website"`
- `relationship_status: "active_client"`
- `lifecycle_stage: "customer"`

### 2. Verify Client Parsing

```swift
// This should no longer show debug messages about missing originalSource
let contacts = try ContactService.getContacts()
print("Loaded \(contacts.count) contacts successfully")
```

## Summary

- ✅ **API field name**: `source` (correct)
- ❌ **Previous client expectation**: `originalSource` (incorrect)
- ✅ **Solution**: Updated client to use `source` field
- ✅ **Enhanced tracking**: Added relationship status and lifecycle stage
- ✅ **Generated client**: Updated OpenAPI spec and client types

The debug messages about missing `originalSource` field should no longer appear once the client is updated to use the correct field names. 