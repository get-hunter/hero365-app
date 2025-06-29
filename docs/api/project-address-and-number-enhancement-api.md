# Project Address and Number Enhancement API Changes

## Overview
The project creation API has been enhanced to support structured address handling and automatic project number generation. These changes ensure consistency with the unified address system and provide better project management capabilities.

## Database Schema Changes

### New Project Table Columns
```sql
-- Added project_number column
"project_number" VARCHAR(50) NOT NULL -- Auto-generated if not provided

-- Updated address storage to JSONB for structured data
"address" JSONB DEFAULT '{}' -- Replaces simple text field
```

### Migration Applied
- Added `project_number` column with unique constraint per business
- Migrated existing projects to auto-generated project numbers
- Updated `address` field to use JSONB for structured address storage
- Added database indexes for performance optimization

## API Schema Changes

### Project Creation Request Schema
The `ProjectCreateRequest` now includes enhanced address support:

```typescript
export type ProjectCreateRequest = {
  project_number?: string | null  // NEW: Optional, auto-generated if not provided
  name: string
  description: string
  project_type: ProjectType
  status: ProjectStatus
  priority: ProjectPriority
  contact_id?: string | null
  client_name?: string | null
  client_email?: string | null
  client_phone?: string | null
  address?: ContactAddressSchema | null  // UPDATED: Now structured address
  start_date: string
  end_date?: string | null
  estimated_hours?: number | string | null
  actual_hours?: number | string | null
  budget_amount?: number | string | null
  actual_cost?: number | string | null
  manager_id?: string | null
  team_members?: Array<string> | null
  tags?: Array<string> | null
  notes?: string | null
}
```

### Address Schema (ContactAddressSchema)
```typescript
export type ContactAddressSchema = {
  street_address?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
  country?: string | null
  latitude?: number | null
  longitude?: number | null
  access_notes?: string | null
  place_id?: string | null
  formatted_address?: string | null
  address_type?: string | null
}
```

## Breaking Changes

### 1. Address Field Structure
**Before:**
```json
{
  "address": "123 Main St, Austin, TX 78701"
}
```

**After:**
```json
{
  "address": {
    "street_address": "123 Main St",
    "city": "Austin", 
    "state": "TX",
    "postal_code": "78701",
    "country": "US"
  }
}
```

### 2. Project Number Field
**New field available:**
```json
{
  "project_number": "PROJ-2025-001"  // Auto-generated if not provided
}
```

## Mobile App Implementation Guide

### 1. Update Project Creation Form

#### Address Input
Replace single address text field with structured address form:
```swift
// Before
@State private var address: String = ""

// After  
@State private var streetAddress: String = ""
@State private var city: String = ""
@State private var state: String = ""
@State private var postalCode: String = ""
@State private var country: String = "US"
```

#### Project Number Input
Add optional project number field:
```swift
@State private var projectNumber: String = ""
// Note: Leave empty for auto-generation
```

### 2. API Request Construction

#### Updated Project Creation Request
```swift
let projectRequest = ProjectCreateRequest(
    project_number: projectNumber.isEmpty ? nil : projectNumber,
    name: projectName,
    description: projectDescription,
    project_type: projectType,
    status: .planning,
    priority: priority,
    contact_id: selectedContactId,
    client_name: clientName,
    address: address.isEmpty ? nil : ContactAddressSchema(
        street_address: streetAddress,
        city: city,
        state: state,
        postal_code: postalCode,
        country: country
    ),
    start_date: startDate.iso8601,
    // ... other fields
)
```

### 3. Address Validation

#### Client-Side Validation
```swift
func validateAddress() -> Bool {
    // At minimum, require street address and city
    return !streetAddress.isEmpty && !city.isEmpty && !state.isEmpty
}
```

#### Server Response Handling
```swift
// The server will return validation errors for invalid addresses
if let error = response.error {
    if error.contains("Street address is required") {
        // Handle address validation error
    }
}
```

### 4. Response Handling

#### Project Creation Response
```swift
struct ProjectResponse {
    let id: String
    let project_number: String  // Always present in response
    let name: String
    let address: ContactAddressSchema?  // Structured address
    // ... other fields
}
```

## API Endpoints

### POST /api/v1/projects
**Create a new project**

**Request Body:**
```json
{
  "name": "HVAC Installation",
  "description": "Installation of new HVAC system",
  "project_type": "installation",
  "status": "planning",
  "priority": "medium",
  "contact_id": "ED4294EA-D4CF-429A-AE23-5F7EEF4A7280",
  "client_name": "John Appleseed",
  "address": {
    "street_address": "3494 Kuhl Avenue",
    "city": "Elberton",
    "state": "GA", 
    "postal_code": "30635",
    "country": "US"
  },
  "start_date": "2025-06-29T12:10:40.788Z",
  "budget_amount": "8000.0",
  "tags": ["hvac", "installation"]
}
```

**Response (201 Created):**
```json
{
  "id": "pj0e8400-e29b-41d4-a716-446655440001",
  "project_number": "PROJ-2025-001",
  "name": "HVAC Installation",
  "description": "Installation of new HVAC system",
  "address": {
    "street_address": "3494 Kuhl Avenue",
    "city": "Elberton",
    "state": "GA",
    "postal_code": "30635",
    "country": "US"
  },
  "project_type": "installation",
  "status": "planning",
  "priority": "medium",
  // ... other fields
}
```

## Validation Rules

### Project Number
- Must be unique within the business
- Maximum 50 characters
- Auto-generated format: `PROJ-YYYY-###` (e.g., `PROJ-2025-001`)
- If provided, cannot conflict with existing project numbers

### Address
- All fields are optional, but at least `street_address` is recommended
- `country` defaults to "US" if not provided
- Coordinates (`latitude`, `longitude`) are optional for geocoding

## Error Handling

### Common Validation Errors
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Project validation failed",
  "details": [
    {
      "field": "address.street_address",
      "message": "Street address is required"
    },
    {
      "field": "project_number", 
      "message": "Project number 'PROJ-2025-001' already exists"
    }
  ]
}
```

### Database Errors
```json
{
  "error": "PROJECT_NUMBER_CONFLICT",
  "message": "Project number already exists for this business",
  "details": {
    "project_number": "PROJ-2025-001"
  }
}
```

## Testing Recommendations

### 1. Address Input Testing
- Test with various address formats
- Test with minimal address data (street + city)
- Test with full address including coordinates
- Test with international addresses

### 2. Project Number Testing
- Test auto-generation (leave field empty)
- Test custom project numbers
- Test duplicate project number handling
- Test project number validation

### 3. Integration Testing
- Create projects with various address combinations
- Verify project numbers are sequential and unique
- Test project creation with existing contacts
- Verify address geocoding if implemented

## Migration Notes for Existing Apps

### 1. Update Existing Screens
- Replace single address input with structured form
- Add optional project number field
- Update validation logic for new address structure

### 2. Data Model Updates
```swift
// Update Project model
struct Project {
    let projectNumber: String  // New field
    let address: ContactAddress?  // Changed from String to structured type
    // ... existing fields
}

struct ContactAddress {
    let streetAddress: String?
    let city: String?
    let state: String?
    let postalCode: String? 
    let country: String?
    // ... additional fields
}
```

### 3. Backward Compatibility
- The API maintains backward compatibility for reading existing projects
- All existing projects have been migrated to include project numbers
- Address data has been preserved during migration

## Performance Considerations

### 1. Address Validation
- Client-side validation reduces server round trips
- Server-side validation ensures data integrity
- Consider debounced address validation for better UX

### 2. Project Number Generation
- Auto-generation is handled server-side for uniqueness
- Consider caching latest project number for offline scenarios

## Security Considerations

### 1. Address Data
- Address information may be sensitive (customer locations)
- Ensure proper access controls for project viewing
- Consider field-level permissions for sensitive address data

### 2. Project Numbers
- Project numbers should not be predictable if business-sensitive
- Consider custom numbering schemes for different project types

This enhancement provides a more robust and scalable foundation for project management with proper address handling and automated project numbering. 