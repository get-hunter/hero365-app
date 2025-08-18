# Invoice Update API - Date Field Handling

## Overview

The Invoice Update API (`PUT /api/v1/invoices/{invoice_id}`) now properly handles date fields sent as datetime strings from the mobile app.

## Changes Made

### Added Fields
- **`issue_date`**: Optional date field for custom issue date (previously missing from update schema)

### Enhanced Date Parsing
Both `issue_date` and `due_date` fields now accept:
- ISO 8601 date strings: `"2025-08-18"`
- ISO 8601 datetime strings: `"2025-08-18T10:59:38Z"`
- Date objects (for internal use)

The API automatically converts datetime strings to date objects by extracting only the date portion.

## API Schema

### Request Body
```json
{
  "title": "Sink Repair & Faucet Replacement",
  "description": "Kitchen sink repair with new faucet installation",
  "issue_date": "2025-08-18T10:59:38Z",  // Now supported
  "due_date": "2025-12-31T10:59:38Z",    // Now supports datetime strings
  "line_items": [...],
  "currency": "USD",
  "tax_rate": 0.0825,
  // ... other fields
}
```

### Response
Date fields are returned as ISO date strings:
```json
{
  "issue_date": "2025-08-18",
  "due_date": "2025-12-31",
  // ... other fields
}
```

## Validation Rules

### Issue Date
- Cannot be in the future
- Accepts datetime strings (time portion is ignored)

### Due Date  
- Must be greater than or equal to issue_date (if provided)
- Accepts datetime strings (time portion is ignored)
- **Note**: For updates, due dates in the past are allowed to support template updates on existing invoices

## Implementation Details

### Date Converter
Added `SupabaseConverter.parse_date()` method that:
1. Handles `datetime.date` objects directly
2. Converts `datetime.datetime` objects to dates
3. Parses ISO date strings (`"2025-08-18"`)
4. Parses ISO datetime strings (`"2025-08-18T10:59:38Z"`) and extracts date

### Schema Updates
- Added `issue_date` field to `UpdateInvoiceSchema`
- Added field validator for both date fields using `@field_validator` with `mode='before'`
- Updated corresponding DTO and route handler

## Error Handling

Invalid date formats will return a 422 validation error with details:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "due_date"],
      "msg": "Failed to parse date: invalid-date-string"
    }
  ]
}
```

## Mobile App Integration

The mobile app can now send date fields in any of these formats:
- `"2025-08-18"` (ISO date string)
- `"2025-08-18T10:59:38Z"` (ISO datetime string)
- `"2025-08-18T10:59:38.123Z"` (ISO datetime with milliseconds)

All formats will be automatically converted to the appropriate date object for processing.
