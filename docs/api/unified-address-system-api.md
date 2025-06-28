# Unified Address System API Documentation

## Overview

Hero365 now uses a **unified JSONB address storage system** across all entities (contacts, jobs, etc.) for consistency, flexibility, and enhanced field service capabilities.

## Key Changes

### ✅ What's New
- **Unified Address Value Object**: Single `Address` class for all entities
- **JSONB Storage**: All addresses stored as JSONB for flexibility
- **Rich Address Data**: Support for geocoding, access notes, Google Places integration
- **Consistent APIs**: Same address structure across all endpoints

### ⚠️ Breaking Changes
- **Contacts**: Address fields migrated from individual columns to JSONB `address` field
- **Address Structure**: Enhanced with new optional fields for geocoding and field service

## Address Data Structure

### Core Address Fields (Required)
```json
{
  "street_address": "123 Main Street",
  "city": "Anytown", 
  "state": "CA",
  "postal_code": "12345",
  "country": "US"
}
```

### Extended Address Fields (Optional)
```json
{
  "street_address": "123 Main Street",
  "city": "Anytown",
  "state": "CA", 
  "postal_code": "12345",
  "country": "US",
  
  // Geocoding Data
  "latitude": 37.7749,
  "longitude": -122.4194,
  
  // Field Service
  "access_notes": "Gate code: 1234. Ring doorbell twice.",
  
  // External Integration
  "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
  "formatted_address": "123 Main Street, Anytown, CA 12345, USA",
  
  // Metadata
  "address_type": "residential"
}
```

## API Endpoints

### Contact Address APIs

#### Get Contact List
```http
GET /api/v1/contacts/
```

**Response** (Address in JSONB format):
```json
{
  "contacts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "business_id": "550e8400-e29b-41d4-a716-446655440001",
      "contact_type": "customer",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1-555-123-4567",
      "address": {
        "street_address": "123 Main Street",
        "city": "Anytown", 
        "state": "CA",
        "postal_code": "12345",
        "country": "US",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "access_notes": "Ring doorbell twice"
      }
    }
  ]
}
```

#### Get Single Contact
```http
GET /api/v1/contacts/{contact_id}
```

**Response**: Same address structure as contact list.

#### Create/Update Contact
```http
POST /api/v1/contacts/
PUT /api/v1/contacts/{contact_id}
```

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",
  "address": {
    "street_address": "123 Main Street",
    "city": "Anytown",
    "state": "CA", 
    "postal_code": "12345",
    "country": "US",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "access_notes": "Ring doorbell twice",
    "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
    "formatted_address": "123 Main Street, Anytown, CA 12345, USA",
    "address_type": "residential"
  }
}
```

### Job Address APIs

#### Get Job List
```http
GET /api/v1/jobs/
```

**Response** (job_address in JSONB format):
```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "business_id": "550e8400-e29b-41d4-a716-446655440001", 
      "job_number": "JOB-001",
      "title": "Kitchen Remodel",
      "job_address": {
        "street_address": "456 Oak Avenue",
        "city": "Somewhere",
        "state": "TX",
        "postal_code": "78901",
        "country": "US",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "access_notes": "Key under mat. Dog in backyard.",
        "address_type": "residential"
      }
    }
  ]
}
```

#### Create Job  
```http
POST /api/v1/jobs/
```

**Request Body**:
```json
{
  "title": "Kitchen Remodel",
  "description": "Complete kitchen renovation",
  "job_type": "installation",
  "priority": "medium",
  "source": "website",
  "job_address": {
    "street_address": "456 Oak Avenue",
    "city": "Somewhere",
    "state": "TX",
    "postal_code": "78901", 
    "country": "US",
    "latitude": 30.2672,
    "longitude": -97.7431,
    "access_notes": "Key under mat. Dog in backyard.",
    "address_type": "residential"
  }
}
```

## Address Validation Rules

### Required Fields
- `street_address`: Must not be empty
- `city`: Must not be empty  
- `state`: Must not be empty
- `postal_code`: Must not be empty

### Optional Fields
- `country`: Defaults to "US"
- `latitude`: Must be between -90 and 90
- `longitude`: Must be between -180 and 180
- `access_notes`: Free text for field service notes
- `place_id`: Google Places ID for geocoding integration
- `formatted_address`: Full formatted address from geocoding service
- `address_type`: Category like "residential", "commercial", etc.

## Database Schema Changes

### Migration Applied: `20250130000000_unify_address_storage_jsonb.sql`

#### Contacts Table
```sql
-- BEFORE (Individual Columns)
ALTER TABLE contacts DROP COLUMN street_address;
ALTER TABLE contacts DROP COLUMN city;
ALTER TABLE contacts DROP COLUMN state;
ALTER TABLE contacts DROP COLUMN postal_code; 
ALTER TABLE contacts DROP COLUMN country;

-- AFTER (JSONB Column)
ALTER TABLE contacts ADD COLUMN address JSONB DEFAULT '{}';
CREATE INDEX idx_contacts_address ON contacts USING GIN (address);
```

#### Jobs Table  
```sql
-- Jobs already used JSONB job_address, now enhanced with new fields
COMMENT ON COLUMN jobs.job_address IS 'JSONB address object: {street_address, city, state, postal_code, country, latitude?, longitude?, access_notes?, place_id?, formatted_address?, address_type?}';
```

## Error Handling

### Address Parsing Errors
When address JSONB cannot be parsed, the system will:
- Log a warning message
- Return `null` for the address field
- Continue processing other contact/job data

### Validation Errors
Invalid address data will result in:
```json
{
  "error": "ValidationError",
  "message": "Street address is required",
  "field": "address.street_address"
}
```

## Migration Guide

### For API Clients

#### Before (Individual Fields)
```json
{
  "street_address": "123 Main St",
  "city": "Anytown",
  "state": "CA", 
  "postal_code": "12345",
  "country": "US"
}
```

#### After (JSONB Object)
```json
{
  "address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345", 
    "country": "US"
  }
}
```

### Enhanced Capabilities
You can now include additional address data:
```json
{
  "address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "access_notes": "Ring doorbell twice",
    "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
    "address_type": "residential"
  }
}
```

## Address Utility Functions

The system provides shared utilities for address handling:

### Parsing JSONB
```python
from app.application.utils.address_utils import AddressUtils

# Parse JSONB to Address value object
address = AddressUtils.parse_address_from_jsonb(jsonb_data)

# Parse JSONB to Contact DTO
contact_address = AddressUtils.parse_address_to_contact_dto(jsonb_data)

# Parse JSONB to Job DTO  
job_address = AddressUtils.parse_address_to_job_dto(jsonb_data)
```

### Creating Addresses
```python
# Minimal address
address = AddressUtils.create_minimal_address(
    street_address="123 Main St",
    city="Anytown", 
    state="CA",
    postal_code="12345"
)

# Geocoded address
address = AddressUtils.create_geocoded_address(
    street_address="123 Main St",
    city="Anytown",
    state="CA", 
    postal_code="12345",
    latitude=37.7749,
    longitude=-122.4194,
    access_notes="Ring doorbell twice"
)
```

### Address Validation
```python
# Check completeness
is_complete = AddressUtils.validate_address_completeness(address)

# Check geocoding
has_coords = AddressUtils.validate_address_geocoding(address)

# Get display formats
formats = AddressUtils.get_address_display_formats(address)
# Returns: {"full": "...", "short": "...", "street_city": "...", etc.}
```

## Benefits of Unified System

### ✅ Consistency
- Same address structure across all entities
- Unified validation and parsing logic
- Consistent API responses

### ✅ Flexibility  
- Easy to add new address fields without schema changes
- Support for international address formats
- Rich metadata storage

### ✅ Field Service Ready
- Geocoding coordinates for routing
- Access notes for technicians  
- Google Places integration

### ✅ Performance
- GIN indexes on JSONB for fast queries
- Efficient storage of sparse data
- Single source of truth for address logic

## Next Steps

1. **Test Migration**: Verify all existing address data migrated correctly
2. **Update Client Apps**: Modify mobile app to use new address structure
3. **Enable Geocoding**: Integrate with Google Places API for automatic geocoding
4. **Field Service Features**: Build routing and access note features for technicians 