# Mobile App Client Requirements - Project Creation API

## Overview
This document outlines the requirements for the mobile app client when integrating with the Hero365 project creation API. These requirements are based on the current server-side validation rules and address structure.

## API Endpoint
```
POST /api/v1/projects
```

## Authentication Requirements
- **Authorization Header**: Required
- **Format**: `Authorization: Bearer <jwt_token>`
- **Business Context**: Must be included in request headers for business validation

## Request Body Requirements

### Required Fields
```typescript
{
  name: string,                    // 1-200 characters
  description: string,             // 1-1000 characters  
  project_type: ProjectType,       // enum: "maintenance" | "installation" | "renovation" | "repair" | "inspection"
  status: ProjectStatus,           // enum: "planning" | "active" | "on_hold" | "completed" | "cancelled"
  priority: ProjectPriority,       // enum: "low" | "medium" | "high" | "critical"
  start_date: string              // ISO 8601 format: "2025-06-29T12:10:40.788Z"
}
```

### Optional Fields
```typescript
{
  project_number?: string | null,        // Auto-generated if not provided, max 50 chars
  contact_id?: string | null,           // UUID of existing contact
  client_name?: string | null,          // Max 200 characters
  client_email?: string | null,         // Max 200 characters, valid email format
  client_phone?: string | null,         // Max 50 characters
  address?: ContactAddressSchema | null, // See address requirements below
  end_date?: string | null,             // ISO 8601 format, must be after start_date
  estimated_hours?: number | null,      // Non-negative decimal
  actual_hours?: number | null,         // Non-negative decimal  
  budget_amount?: number | null,        // Non-negative decimal with 2 decimal places
  actual_cost?: number | null,          // Non-negative decimal with 2 decimal places
  manager_id?: string | null,           // UUID of manager user
  team_members?: string[] | null,       // Array of user IDs, max 20 items
  tags?: string[] | null,               // Array of strings, max 50 items
  notes?: string | null                 // Max 2000 characters
}
```

## Address Requirements (ContactAddressSchema)

### Critical Validation Rules
⚠️ **IMPORTANT**: If you include an `address` object, the `street_address` field is **REQUIRED** and cannot be empty.

### Address Schema Structure
```typescript
type ContactAddressSchema = {
  street_address: string,      // REQUIRED if address object is provided
  city: string,               // REQUIRED if address object is provided  
  state: string,              // REQUIRED if address object is provided
  postal_code: string,        // REQUIRED if address object is provided
  country?: string,           // Optional, defaults to "US"
  latitude?: number | null,   // Optional, for geocoding
  longitude?: number | null,  // Optional, for geocoding
  access_notes?: string | null, // Optional, max 500 chars
  place_id?: string | null,   // Optional, Google Places ID
  formatted_address?: string | null, // Optional, full formatted address
  address_type?: string | null // Optional, e.g., "residential", "commercial"
}
```

### Address Validation Rules
1. **If `address` is provided, ALL of these fields must be non-empty strings:**
   - `street_address`
   - `city` 
   - `state`
   - `postal_code`

2. **If you cannot provide a complete address, set `address` to `null` instead of providing partial data**

3. **Country defaults to "US" if not specified**

## Mobile App Implementation Requirements

### 1. Address Input Validation

#### Option A: Complete Address Required
```swift
struct ProjectAddress {
    let streetAddress: String
    let city: String
    let state: String
    let postalCode: String
    let country: String = "US"
    
    var isValid: Bool {
        return !streetAddress.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !city.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !state.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !postalCode.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
}
```

#### Option B: Optional Address (Recommended)
```swift
struct ProjectCreationForm {
    // ... other fields
    
    // Address fields - all optional, but if any is provided, all required fields must be filled
    @State private var hasAddress: Bool = false
    @State private var streetAddress: String = ""
    @State private var city: String = ""
    @State private var state: String = ""
    @State private var postalCode: String = ""
    
    var addressIsValid: Bool {
        if !hasAddress {
            return true // No address is valid
        }
        // If hasAddress is true, all required fields must be filled
        return !streetAddress.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !city.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !state.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !postalCode.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
}
```

### 2. Request Construction

#### Valid Request Examples

**Project with Complete Address:**
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
  "budget_amount": 8000.0,
  "tags": ["hvac", "installation"]
}
```

**Project without Address:**
```json
{
  "name": "HVAC Installation", 
  "description": "Installation of new HVAC system",
  "project_type": "installation",
  "status": "planning",
  "priority": "medium", 
  "contact_id": "ED4294EA-D4CF-429A-AE23-5F7EEF4A7280",
  "client_name": "John Appleseed",
  "address": null,
  "start_date": "2025-06-29T12:10:40.788Z",
  "budget_amount": 8000.0,
  "tags": ["hvac", "installation"]
}
```

#### Swift Implementation Example
```swift
func createProjectRequest() -> ProjectCreateRequest {
    let address: ContactAddressSchema? = hasAddress && addressIsValid ? 
        ContactAddressSchema(
            street_address: streetAddress,
            city: city,
            state: state, 
            postal_code: postalCode,
            country: "US"
        ) : nil
    
    return ProjectCreateRequest(
        name: projectName,
        description: projectDescription,
        project_type: projectType,
        status: .planning,
        priority: priority,
        contact_id: selectedContactId,
        client_name: clientName,
        address: address,  // Either complete address or nil
        start_date: startDate.iso8601String,
        budget_amount: budgetAmount
    )
}
```

### 3. Error Handling Requirements

#### Address Validation Errors
```swift
enum ProjectCreationError: Error {
    case incompleteAddress
    case invalidDateRange
    case networkError(String)
    case validationError([String])
}

func handleValidationResponse(_ response: ErrorResponse) {
    if response.message.contains("Street address is required") {
        // Show user: "Please provide a complete address or leave address fields empty"
        showAlert(
            title: "Incomplete Address",
            message: "Please fill in all address fields (street, city, state, postal code) or leave the address section empty."
        )
    }
}
```

#### Common Server Errors
```swift
// Handle these specific error messages:
- "Street address is required"
- "City is required" 
- "State is required"
- "Postal code is required"
- "End date must be after start date"
- "Project number 'XXX' already exists"
```

### 4. User Interface Requirements

#### Address Section Design
```swift
Section("Project Address (Optional)") {
    Toggle("Include Address", isOn: $hasAddress)
    
    if hasAddress {
        TextField("Street Address", text: $streetAddress)
            .textFieldStyle(RoundedBorderTextFieldStyle())
        
        TextField("City", text: $city)
            .textFieldStyle(RoundedBorderTextFieldStyle())
        
        TextField("State", text: $state)
            .textFieldStyle(RoundedBorderTextFieldStyle())
        
        TextField("Postal Code", text: $postalCode)
            .textFieldStyle(RoundedBorderTextFieldStyle())
    }
}
.footer(Text(hasAddress ? "All address fields are required if you choose to include an address" : ""))
```

#### Form Validation
```swift
var isFormValid: Bool {
    return !projectName.isEmpty &&
           !projectDescription.isEmpty &&
           addressIsValid &&
           (endDate == nil || endDate! > startDate)
}
```

### 5. Testing Requirements

#### Test Cases to Implement
1. **Complete Valid Address**
   - All required address fields filled
   - Should succeed

2. **No Address**  
   - `address` field set to `null`
   - Should succeed

3. **Incomplete Address** 
   - Missing `street_address` or other required fields
   - Should fail with validation error

4. **Empty String in Required Address Fields**
   - `street_address: ""`
   - Should fail with validation error

5. **Whitespace-only Address Fields**
   - `street_address: "   "`
   - Should fail with validation error

#### Swift Unit Tests Example
```swift
func testProjectCreationWithCompleteAddress() {
    let request = ProjectCreateRequest(
        name: "Test Project",
        description: "Test Description", 
        project_type: .installation,
        status: .planning,
        priority: .medium,
        address: ContactAddressSchema(
            street_address: "123 Main St",
            city: "Austin",
            state: "TX", 
            postal_code: "78701",
            country: "US"
        ),
        start_date: Date().iso8601String
    )
    
    // This should succeed
    XCTAssertNoThrow(try validateRequest(request))
}

func testProjectCreationWithoutAddress() {
    let request = ProjectCreateRequest(
        name: "Test Project",
        description: "Test Description",
        project_type: .installation, 
        status: .planning,
        priority: .medium,
        address: nil,  // No address provided
        start_date: Date().iso8601String
    )
    
    // This should succeed
    XCTAssertNoThrow(try validateRequest(request))
}
```

## Key Takeaways for Mobile App

1. **Address is Optional**: Don't provide an address object if you don't have complete information
2. **All-or-Nothing**: If providing address, ALL required fields must be non-empty
3. **Validation First**: Always validate client-side before sending to server
4. **Clear UI**: Make it clear to users that address is optional but if provided, must be complete
5. **Error Handling**: Provide clear feedback when address validation fails
6. **Auto-Generation**: Project numbers are auto-generated if not provided
7. **Date Validation**: End date must be after start date if provided

This approach ensures compatibility with the current server validation while providing a good user experience. 