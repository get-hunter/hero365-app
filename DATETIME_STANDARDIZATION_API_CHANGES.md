# API Datetime Format Standardization

## Overview
All datetime fields in API responses have been standardized to use UTC format without microseconds and with "Z" suffix across the entire API.

## Changes Made

### Datetime Format Standardization
- **Previous Format**: `2025-06-21T14:27:12.211371+00:00` (with microseconds and timezone offset)
- **New Format**: `2025-06-21T14:27:12Z` (without microseconds, UTC with "Z" suffix)

### Affected Schemas

#### Business Management APIs
**BusinessResponse**
- `created_date`: Optional[datetime]
- `last_modified`: Optional[datetime] 
- `onboarding_completed_date`: Optional[datetime]

**BusinessSummaryResponse**
- `created_date`: Optional[datetime]

**BusinessMembershipResponse**
- `joined_date`: datetime
- `invited_date`: Optional[datetime]

**BusinessInvitationResponse**
- `invitation_date`: datetime
- `expiry_date`: datetime
- `accepted_date`: Optional[datetime]
- `declined_date`: Optional[datetime]

#### Authentication APIs
**AuthUserResponse**
- `last_login`: Optional[datetime]
- `onboarding_completed_at`: Optional[datetime]

**AuthSessionResponse**
- `created_at`: datetime
- `expires_at`: datetime
- `last_activity`: datetime

## Implementation Details

### Common Utility Function
The datetime formatter has been centralized in `backend/app/utils.py` for reuse across all API schemas:

```python
def format_datetime_utc(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to standardized UTC format without microseconds."""
    if dt is None:
        return None
    # Ensure datetime is in UTC and format without microseconds
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        # Convert to UTC if not already
        utc_dt = dt.utctimetuple()
        return datetime(*utc_dt[:6]).strftime("%Y-%m-%dT%H:%M:%SZ")
```

### Schema Configuration
Each response schema now includes:
- Import: `from ...utils import format_datetime_utc`
- `model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})`
- `@field_serializer` decorators for datetime fields

### Files Updated
- `backend/app/utils.py` - Added common datetime formatter
- `backend/app/api/schemas/business_schemas.py` - Updated all business-related schemas
- `backend/app/api/schemas/auth_schemas.py` - Updated authentication schemas
- `backend/app/api/schemas/common_schemas.py` - Updated common schemas

## Example Response

### Business Creation Response
```json
{
  "id": "432d5e86-3883-413f-9783-290bc021fb42",
  "name": "Hunter Apps, Inc",
  "industry": "Digital Freelancer",
  "company_size": "just_me",
  "owner_id": "d13d3df3-d84a-4143-8573-51c71c90be4c",
  "created_date": "2025-06-21T14:27:12Z",
  "last_modified": "2025-06-21T14:27:12Z",
  "onboarding_completed_date": null,
  "is_active": true,
  "onboarding_completed": false
}
```

## Client Implementation Notes

### Parsing the New Format
```javascript
// JavaScript
const createdDate = new Date("2025-06-21T14:27:12Z");

// Swift
let formatter = ISO8601DateFormatter()
let createdDate = formatter.date(from: "2025-06-21T14:27:12Z")

// Python
from datetime import datetime
created_date = datetime.fromisoformat("2025-06-21T14:27:12Z".replace("Z", "+00:00"))
```

### Benefits
1. **Consistency**: All datetime fields use the same format
2. **Readability**: Cleaner format without microseconds
3. **Standard Compliance**: ISO 8601 format with UTC indicator
4. **Client-Friendly**: Easier to parse in mobile applications

## Migration Notes
- No breaking changes for clients that properly parse ISO 8601 datetime strings
- Clients hardcoding microsecond parsing may need updates
- All dates are guaranteed to be in UTC timezone

## Testing
Test the new format with sample business creation:
```bash
curl -X POST "/api/v1/businesses" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Business", "industry": "Technology", "company_size": "just_me"}'
```

Expected datetime format in response: `"created_date": "2025-06-21T14:27:12Z"` 