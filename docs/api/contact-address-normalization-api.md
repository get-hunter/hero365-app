# Contact Address Field Normalization API Changes

## Overview
The contact address storage has been normalized from a single JSON field to individual database columns for better query performance, data integrity, and location-based functionality.

## Database Schema Changes

### Before (JSON Address Field)
```sql
"address" TEXT  -- Stored as JSON string: {"street_address": "123 Main St", "city": "Boston", ...}
```

### After (Individual Address Fields)
```sql
"street_address" VARCHAR(200)  -- Street address line
"city" VARCHAR(100)           -- City name  
"state" VARCHAR(100)          -- State/province/region
"postal_code" VARCHAR(20)     -- ZIP/postal code
"country" VARCHAR(100)        -- Country name or code
```

## API Schema Changes

### Contact Address Schema (No Changes)
The `ContactAddressSchema` remains the same for API compatibility:

```typescript
export type ContactAddressSchema = {
  street_address?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
  country?: string | null
}
```

### Request/Response Handling
- **API Input**: Still accepts `ContactAddressSchema` object in `address` field
- **API Output**: Still returns `ContactAddressSchema` object in `address` field
- **Database Storage**: Now stores components in individual columns instead of JSON

## Benefits of This Change

### 1. Enhanced Query Capabilities
```sql
-- Now possible: Filter contacts by city
SELECT * FROM contacts WHERE city = 'Boston';

-- Now possible: Geographic grouping
SELECT city, COUNT(*) FROM contacts GROUP BY city;

-- Now possible: State-based reporting
SELECT state, AVG(estimated_value) FROM contacts GROUP BY state;
```

### 2. Better Performance
- Indexed individual fields for faster location-based queries
- No JSON parsing overhead for address filtering
- More efficient sorting and grouping operations

### 3. Data Integrity
- Field-level validation and constraints
- Proper data types for each address component
- Better normalization and consistency

### 4. Integration Benefits
- Easier integration with mapping services (Google Maps, etc.)
- Better support for geographic analysis
- Simplified address validation logic

## Migration Process

### 1. Data Migration
```sql
-- Existing JSON address data is migrated to individual fields
UPDATE contacts SET 
  street_address = (address::jsonb->>'street_address'),
  city = COALESCE((address::jsonb->>'city'), city),
  state = COALESCE((address::jsonb->>'state'), state),
  postal_code = COALESCE((address::jsonb->>'postal_code'), postal_code),
  country = COALESCE((address::jsonb->>'country'), country)
WHERE address IS NOT NULL;
```

### 2. Schema Updates
```sql
-- Add new street_address field
ALTER TABLE contacts ADD COLUMN street_address VARCHAR(200);

-- Drop old JSON address field
ALTER TABLE contacts DROP COLUMN address;

-- Add performance indexes
CREATE INDEX idx_contacts_city ON contacts(city);
CREATE INDEX idx_contacts_state ON contacts(state);
CREATE INDEX idx_contacts_country ON contacts(country);
CREATE INDEX idx_contacts_postal_code ON contacts(postal_code);
```

## Frontend Impact

### No Breaking Changes
The frontend API remains unchanged:
- Still send/receive `address` object in contact requests/responses
- Address validation logic remains the same
- Form handling stays identical

### Enhanced Capabilities
Once migrated, the frontend can leverage:
- Faster location-based filtering
- Better address autocomplete performance
- Geographic reporting features
- Location-based contact grouping

## Backend Changes

### Repository Layer
- Updated `_contact_to_dict()` to map individual fields
- Updated `_dict_to_contact()` to build address from individual fields
- Improved error handling for address data parsing

### Database Queries
- More efficient location-based queries
- Better performance for contact filtering by location
- Enhanced reporting capabilities

## Testing Considerations

### 1. Data Integrity Tests
- Verify all existing address data migrated correctly
- Ensure no data loss during migration
- Validate address field mappings

### 2. API Compatibility Tests
- Confirm existing API contracts still work
- Test address object serialization/deserialization
- Verify frontend integration remains functional

### 3. Performance Tests
- Measure query performance improvements
- Test location-based filtering speed
- Validate index effectiveness

## Rollback Plan

If issues arise, the migration can be reversed:

```sql
-- Add back JSON address field
ALTER TABLE contacts ADD COLUMN address TEXT;

-- Rebuild JSON from individual fields
UPDATE contacts SET address = json_build_object(
  'street_address', street_address,
  'city', city,
  'state', state,
  'postal_code', postal_code,
  'country', country
)::text
WHERE street_address IS NOT NULL OR city IS NOT NULL 
   OR state IS NOT NULL OR postal_code IS NOT NULL 
   OR country IS NOT NULL;

-- Remove individual fields
ALTER TABLE contacts 
DROP COLUMN street_address,
DROP COLUMN city,
DROP COLUMN state, 
DROP COLUMN postal_code,
DROP COLUMN country;
```

## Next Steps

1. **Clean existing JSON data** in address field (as mentioned)
2. **Apply migration** using `supabase db push`
3. **Test API endpoints** to ensure compatibility
4. **Update frontend** if any location-based features are desired
5. **Monitor performance** improvements in location queries

This change provides a solid foundation for future location-based features while maintaining full API compatibility. 