# Website Context API Documentation

## Overview

The Website Context API provides a single, optimized endpoint that aggregates all data needed for website generation. This replaces multiple API calls with one comprehensive request, improving performance and reducing complexity for website builders.

## Base URL

```
GET /api/v1/public/contractors/website/context/{business_id}
```

## Authentication

**Public Endpoint** - No authentication required. This endpoint is designed for website builders and public consumption.

## Endpoints

### 1. Get Complete Website Context

**Endpoint:** `GET /api/v1/public/contractors/website/context/{business_id}`

**Description:** Returns complete website context including business info, activities, service templates, and trade information.

**Parameters:**
- `business_id` (path, required): Business UUID
- `include_templates` (query, optional): Include service templates (default: true)
- `include_trades` (query, optional): Include trade information (default: true)
- `activity_limit` (query, optional): Limit number of activities (1-100)
- `template_limit` (query, optional): Limit number of templates (1-100)

**Response Example:**
```json
{
  "business": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Austin HVAC Pros",
    "description": "Professional HVAC services in Austin, TX",
    "phone": "(512) 555-0123",
    "email": "info@austinhvacpros.com",
    "address": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "postal_code": "78701",
    "website": "https://austinhvacpros.com",
    "primary_trade_slug": "hvac",
    "service_areas": ["Austin", "Round Rock", "Cedar Park"]
  },
  "activities": [
    {
      "slug": "ac-installation",
      "name": "AC Installation",
      "trade_slug": "hvac",
      "trade_name": "HVAC",
      "synonyms": ["air conditioning installation", "ac install"],
      "tags": ["installation", "cooling"],
      "default_booking_fields": [
        {
          "key": "system_type",
          "type": "select",
          "label": "System Type",
          "options": ["Central Air", "Ductless Mini-Split", "Window Unit"],
          "required": false
        }
      ],
      "required_booking_fields": [
        {
          "key": "problem_description",
          "type": "textarea",
          "label": "Installation Requirements",
          "required": true
        }
      ]
    }
  ],
  "service_templates": [
    {
      "template_slug": "ac-installation-standard",
      "name": "Standard AC Installation",
      "description": "Professional air conditioning installation",
      "pricing_model": "fixed",
      "pricing_config": {
        "base_price": 3500,
        "currency": "USD"
      },
      "unit_of_measure": "complete system",
      "is_emergency": false,
      "activity_slug": "ac-installation"
    }
  ],
  "trades": [
    {
      "slug": "hvac",
      "name": "HVAC",
      "description": "Heating, ventilation, and air conditioning services",
      "segments": "both",
      "icon": "snowflake"
    }
  ],
  "metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "total_activities": 4,
    "total_templates": 8,
    "total_trades": 1,
    "primary_trade": "hvac"
  }
}
```

### 2. Get Activities Only (Lightweight)

**Endpoint:** `GET /api/v1/public/contractors/website/context/{business_id}/activities`

**Description:** Returns only activity information without full context data.

**Parameters:**
- `business_id` (path, required): Business UUID
- `limit` (query, optional): Limit number of activities (1-100)

**Response Example:**
```json
{
  "business_id": "550e8400-e29b-41d4-a716-446655440000",
  "activities": [
    {
      "slug": "ac-installation",
      "name": "AC Installation",
      "trade_slug": "hvac",
      "trade_name": "HVAC",
      "synonyms": ["air conditioning installation"],
      "tags": ["installation", "cooling"],
      "default_booking_fields": [...],
      "required_booking_fields": [...]
    }
  ],
  "total_activities": 4
}
```

### 3. Get Website Summary

**Endpoint:** `GET /api/v1/public/contractors/website/context/{business_id}/summary`

**Description:** Returns basic business information and metadata counts.

**Response Example:**
```json
{
  "business": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Austin HVAC Pros",
    "description": "Professional HVAC services in Austin, TX",
    "phone": "(512) 555-0123",
    "email": "info@austinhvacpros.com",
    "city": "Austin",
    "state": "TX",
    "service_areas": ["Austin", "Round Rock"]
  },
  "metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "total_activities": 4,
    "total_templates": 8,
    "total_trades": 1,
    "primary_trade": "hvac"
  }
}
```

## Data Models

### WebsiteBusinessInfo
- `id`: Business UUID
- `name`: Business name
- `description`: Business description
- `phone`: Contact phone number
- `email`: Contact email
- `address`: Street address
- `city`: City
- `state`: State/province
- `postal_code`: Postal/ZIP code
- `website`: Website URL
- `primary_trade_slug`: Primary trade identifier
- `service_areas`: Array of service area names

### WebsiteActivityInfo
- `slug`: Activity identifier
- `name`: Activity display name
- `trade_slug`: Associated trade identifier
- `trade_name`: Trade display name
- `synonyms`: Alternative names for the activity
- `tags`: Activity tags/categories
- `default_booking_fields`: Optional booking form fields
- `required_booking_fields`: Required booking form fields

### WebsiteBookingField
- `key`: Field identifier
- `type`: Field type (text, select, textarea, number, date, email, tel)
- `label`: Display label
- `options`: Available options (for select/radio fields)
- `required`: Whether field is required
- `placeholder`: Placeholder text
- `help_text`: Help text for the field

### WebsiteServiceTemplate
- `template_slug`: Template identifier
- `name`: Template name
- `description`: Template description
- `pricing_model`: Pricing model (fixed, hourly, per_unit, tiered, quote)
- `pricing_config`: Pricing configuration object
- `unit_of_measure`: Unit of measurement
- `is_emergency`: Emergency service flag
- `activity_slug`: Associated activity

### WebsiteTradeInfo
- `slug`: Trade identifier
- `name`: Trade display name
- `description`: Trade description
- `segments`: Market segments (residential, commercial, both)
- `icon`: Trade icon identifier

## Error Responses

### 404 Not Found
```json
{
  "detail": "Website context not found for business: {business_id}"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error retrieving website context: {error_message}"
}
```

## Caching

The API includes caching headers for optimal performance:

- `Cache-Control: public, max-age=3600` (1 hour cache)
- `ETag` based on business ID and last modified time
- `Vary: Accept-Encoding` for compression support

## Usage Examples

### Website Builder Integration

```javascript
// Fetch complete website context
const response = await fetch(`/api/v1/public/contractors/website/context/${businessId}`);
const context = await response.json();

// Use business info for header
const { business, activities, service_templates } = context;

// Generate navigation from activities
const navigation = activities.map(activity => ({
  name: activity.name,
  href: `/services/${activity.slug}`
}));

// Create service pages
activities.forEach(activity => {
  generateServicePage(activity, business);
});
```

### Activity-Specific Booking Forms

```javascript
// Get activity with booking fields
const activity = context.activities.find(a => a.slug === 'ac-installation');

// Render booking form
const bookingFields = [
  ...activity.required_booking_fields.map(f => ({ ...f, required: true })),
  ...activity.default_booking_fields.map(f => ({ ...f, required: false }))
];

renderBookingForm(bookingFields);
```

### SEO Optimization

```javascript
// Generate page metadata
const activity = context.activities[0];
const business = context.business;

const pageTitle = `${activity.name} - ${business.name} in ${business.city}`;
const pageDescription = `Professional ${activity.name.toLowerCase()} services in ${business.city}. Contact ${business.name} at ${business.phone}.`;

// Use activity tags for keywords
const keywords = [...activity.tags, business.city, activity.trade_name];
```

## Performance Considerations

1. **Single Request**: Replaces 3-5 individual API calls
2. **Selective Loading**: Use query parameters to limit data
3. **Caching**: Responses are cached for 1 hour
4. **Lightweight Endpoints**: Use `/activities` or `/summary` for specific needs
5. **Pagination**: Use `limit` parameters for large datasets

## Integration with Activity Content Packs

This API works seamlessly with the Activity Content Pack system:

```javascript
// Get website context
const context = await getWebsiteContext(businessId);

// For each activity, get content pack
for (const activity of context.activities) {
  const contentPack = await fetch(`/api/v1/activity-content/public/content-packs/${activity.slug}`);
  const content = await contentPack.json();
  
  // Generate activity page with context + content
  generateActivityPage(activity, content, context.business);
}
```

## Rate Limiting

- Public endpoints are rate-limited to prevent abuse
- Recommended: Cache responses on the client side
- Use appropriate cache headers for CDN integration

## Support

For questions about the Website Context API:
- Check the OpenAPI documentation at `/docs`
- Review the implementation in `backend/app/api/public/routes/contractors/website_context.py`
- See usage examples in the website-builder components
