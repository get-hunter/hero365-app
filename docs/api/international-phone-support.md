# International Phone Number Support

## Overview

Hero365 now supports international phone numbers using the E.164 standard format, making the platform ready for global expansion. The system automatically normalizes, validates, and formats phone numbers for different countries.

## Database Schema

### Phone Number Fields

Each table with phone numbers now has these fields:

```sql
phone VARCHAR(20) NOT NULL,     -- E.164 format: +1234567890 (primary storage)
phone_country_code VARCHAR(3),  -- Country code: 1, 44, 49, etc.
phone_display VARCHAR(30)       -- Formatted display: +1 (555) 123-4567
```

### Automatic Normalization

When you insert or update a phone number:

```sql
-- Input: Any format
INSERT INTO businesses (name, phone) VALUES ('Test Co', '(555) 123-4567');

-- Automatically creates:
-- phone = '+15551234567'          (E.164 format)
-- phone_country_code = '1'
-- phone_display = '+1 (555) 123-4567'
```

## Supported Formats

### Input Formats (All Normalized Automatically)

- `(555) 123-4567` → `+15551234567`
- `555-123-4567` → `+15551234567`
- `+1 555 123 4567` → `+15551234567`
- `15551234567` → `+15551234567`
- `+44 20 7123 4567` → `+442071234567`
- `+49 30 12345678` → `+493012345678`

### Display Formats (Country-Specific)

- **US/Canada**: `+1 (555) 123-4567`
- **UK**: `+44 20 7123 4567`
- **Germany**: `+49 30 12345678`
- **France**: `+33 1 23 45 67 89`
- **Default**: `+CC XXXXXXXXX`

## Backend Usage

### Pydantic Value Object

```python
from app.domain.value_objects.phone_number import PhoneNumber

# Create from user input
phone = PhoneNumber.from_input("(555) 123-4567", default_country_code="1")

# Access different formats
print(phone.e164)        # +15551234567
print(phone.display)     # +1 (555) 123-4567
print(phone.country_code) # 1

# Validation
print(phone.is_valid())  # True
print(phone.is_country("1"))  # True

# For different use cases
sms_number = phone.for_sms()      # +15551234567 (E.164)
display_text = phone.for_display() # +1 (555) 123-4567
storage_value = phone.for_storage() # +15551234567 (E.164)
```

### Convenience Functions

```python
from app.domain.value_objects.phone_number import (
    normalize_phone, 
    is_valid_phone, 
    format_phone_for_display,
    get_phone_e164
)

# Quick validation
if is_valid_phone("555-123-4567"):
    print("Valid phone number")

# Quick formatting
display = format_phone_for_display("5551234567")  # +1 (555) 123-4567

# Quick E.164 conversion
e164 = get_phone_e164("(555) 123-4567")  # +15551234567
```

## Database Functions

### Validation

```sql
SELECT is_valid_e164_phone('+15551234567'); -- Returns true
SELECT is_valid_e164_phone('555-123-4567'); -- Returns false
```

### Normalization

```sql
SELECT normalize_phone_to_e164('(555) 123-4567', '1'); -- Returns '+15551234567'
SELECT normalize_phone_to_e164('020 7123 4567', '44'); -- Returns '+442071234567'
```

### Country Code Extraction

```sql
SELECT extract_country_code('+15551234567'); -- Returns '1'
SELECT extract_country_code('+442071234567'); -- Returns '44'
```

### Display Formatting

```sql
SELECT format_phone_display('+15551234567'); -- Returns '+1 (555) 123-4567'
SELECT format_phone_display('+442071234567'); -- Returns '+44 20 7123 4567'
```

## API Integration

### Input Handling

The API accepts phone numbers in any format:

```json
{
  "name": "Test Business",
  "phone": "(555) 123-4567"
}
```

### Output Format

APIs return the display format for better UX:

```json
{
  "business_id": "123",
  "name": "Test Business", 
  "phone": "+1 (555) 123-4567",
  "phone_country": "1"
}
```

### SMS/Calling Integration

Use the E.164 format for external services:

```python
# For Twilio, AWS SNS, etc.
sms_service.send(
    to=business.phone_e164,  # +15551234567
    message="Your appointment is confirmed"
)
```

## Country Support

### Currently Supported Countries

| Country | Code | Example Format |
|---------|------|----------------|
| United States | 1 | +1 (555) 123-4567 |
| Canada | 1 | +1 (555) 123-4567 |
| United Kingdom | 44 | +44 20 7123 4567 |
| Germany | 49 | +49 30 12345678 |
| France | 33 | +33 1 23 45 67 89 |
| Spain | 34 | +34 91 123 45 67 |
| Italy | 39 | +39 06 1234 5678 |
| Mexico | 52 | +52 55 1234 5678 |
| Brazil | 55 | +55 11 1234 5678 |
| China | 86 | +86 10 1234 5678 |
| India | 91 | +91 11 1234 5678 |

### Adding New Countries

To add support for a new country:

1. Update the `extract_country_code()` function
2. Add formatting rules to `format_phone_display()`
3. Add country to the documentation

## Migration Strategy

### Clean Architecture

Since Hero365 is still in development, we've implemented a clean, modern approach:

- **Single Source of Truth**: `phone` field stores E.164 format directly
- **Automatic Validation**: Invalid phone numbers are rejected at insert/update
- **Country-Specific Formatting**: Display format generated automatically
- **No Legacy Baggage**: Clean schema optimized for international use

### Implementation Benefits

1. **Simplified Schema**: Only necessary fields, no legacy compatibility
2. **Automatic Validation**: Database-level phone number validation
3. **International Ready**: E.164 standard from day one
4. **Performance Optimized**: Direct E.164 storage and indexing

## Benefits for International Expansion

### Technical Benefits

- **Standardized Storage**: E.164 format ensures consistency
- **Validation**: Prevents invalid phone numbers
- **SMS/Call Ready**: Direct integration with communication services
- **Search Optimization**: Indexed E.164 format for fast lookups
- **Country Filtering**: Easy to filter by country code

### User Experience Benefits

- **Familiar Formatting**: Numbers displayed in local format
- **Input Flexibility**: Accepts any common input format
- **International Ready**: Supports global phone number patterns
- **Validation Feedback**: Real-time validation for better UX

### Business Benefits

- **Global Expansion Ready**: No technical barriers for new markets
- **Communication Services**: Easy integration with SMS/voice providers
- **Data Quality**: Consistent, validated phone number data
- **Compliance**: Follows international standards (E.164)

## Examples

### US Business
```
Input: (512) 555-0100
Storage: +15125550100
Display: +1 (512) 555-0100
Country: 1
```

### UK Business
```
Input: 020 7123 4567
Storage: +442071234567
Display: +44 20 7123 4567
Country: 44
```

### German Business
```
Input: 030 12345678
Storage: +493012345678
Display: +49 30 12345678
Country: 49
```

This system ensures Hero365 is ready for global expansion while maintaining backward compatibility and providing excellent user experience across all markets.
