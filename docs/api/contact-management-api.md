# Contact Management API Documentation

## Overview

The Contact Management API provides comprehensive functionality for managing business contacts including customers, leads, prospects, vendors, partners, and contractors. This API follows Hero365's business-centric, multi-tenant architecture with role-based access control.

## Authentication & Authorization

All contact endpoints require authentication and proper business context. Users must have appropriate permissions within the business to access contact data.

### Required Permissions

- `view_contacts` - View contact information
- `edit_contacts` - Create and update contacts
- `delete_contacts` - Delete contacts

### Business Context

All contact operations are scoped to a specific business. The business context is automatically extracted from:
- JWT token business context
- Request headers (`X-Business-ID`)
- Query parameters (`business_id`)

## Contact Types

| Type | Description |
|------|-------------|
| `customer` | Existing customers who have purchased services |
| `lead` | Qualified prospects actively being pursued |
| `prospect` | Potential customers identified but not yet qualified |
| `vendor` | Service providers and suppliers |
| `partner` | Business partners and collaborators |
| `contractor` | Independent contractors and freelancers |

## Contact Status

| Status | Description |
|--------|-------------|
| `active` | Contact is active and can be engaged |
| `inactive` | Contact is temporarily inactive |
| `archived` | Contact is archived but not deleted |
| `blocked` | Contact is blocked from communication |

## Contact Priority

| Priority | Description |
|----------|-------------|
| `low` | Low priority contact |
| `medium` | Medium priority contact (default) |
| `high` | High priority contact |
| `urgent` | Urgent priority contact requiring immediate attention |

## Contact Sources

| Source | Description |
|--------|-------------|
| `website` | Contact acquired through website |
| `referral` | Contact from referral |
| `social_media` | Contact from social media |
| `advertising` | Contact from advertising campaigns |
| `cold_outreach` | Contact from cold outreach |
| `event` | Contact from events or trade shows |
| `partner` | Contact from business partners |
| `existing_customer` | Contact from existing customer referral |
| `direct` | Direct contact |
| `other` | Other source |

## API Endpoints

### Core Contact Operations

#### Create Contact
```http
POST /api/v1/contacts/
```

**Request Body:**
```json
{
  "contact_type": "customer",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp",
  "job_title": "CEO",
  "email": "john@acme.com",
  "phone": "+1-555-0123",
  "mobile_phone": "+1-555-0124",
  "website": "https://acme.com",
  "address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "USA"
  },
  "priority": "high",
  "source": "website",
  "tags": ["vip", "enterprise"],
  "notes": "Important client with high potential",
  "estimated_value": 50000.00,
  "currency": "USD",
  "assigned_to": "user-uuid",
  "custom_fields": {
    "industry": "Technology",
    "employees": "100-500"
  }
}
```

**Response:**
```json
{
  "id": "contact-uuid",
  "business_id": "business-uuid",
  "contact_type": "customer",
  "status": "active",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp",
  "job_title": "CEO",
  "email": "john@acme.com",
  "phone": "+1-555-0123",
  "mobile_phone": "+1-555-0124",
  "website": "https://acme.com",
  "address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "USA"
  },
  "priority": "high",
  "source": "website",
  "tags": ["vip", "enterprise"],
  "notes": "Important client with high potential",
  "estimated_value": 50000.00,
  "currency": "USD",
  "assigned_to": "user-uuid",
  "created_by": "user-uuid",
  "custom_fields": {
    "industry": "Technology",
    "employees": "100-500"
  },
  "created_date": "2024-01-15T10:30:00Z",
  "last_modified": "2024-01-15T10:30:00Z",
  "last_contacted": null,
  "display_name": "John Doe (Acme Corp)",
  "primary_contact_method": "john@acme.com",
  "type_display": "Customer",
  "status_display": "Active",
  "priority_display": "High",
  "source_display": "Website"
}
```

#### Get Contact
```http
GET /api/v1/contacts/{contact_id}
```

**Response:** Same as create contact response.

#### Update Contact
```http
PUT /api/v1/contacts/{contact_id}
```

**Request Body:** Same as create contact (all fields optional for updates).

#### Delete Contact
```http
DELETE /api/v1/contacts/{contact_id}
```

**Response:**
```json
{
  "message": "Contact deleted successfully",
  "success": true
}
```

### Contact Listing & Search

#### List Contacts
```http
GET /api/v1/contacts/?skip=0&limit=100
```

**Query Parameters:**
- `skip` (integer): Number of records to skip (default: 0)
- `limit` (integer): Maximum records to return (default: 100, max: 1000)

**Response:**
```json
{
  "contacts": [
    {
      // Contact objects (same as create response)
    }
  ],
  "total_count": 150,
  "page": 1,
  "per_page": 100,
  "has_next": true,
  "has_previous": false
}
```

#### Search Contacts
```http
POST /api/v1/contacts/search
```

**Request Body:**
```json
{
  "search_term": "john",
  "contact_type": "customer",
  "status": "active",
  "priority": "high",
  "source": "website",
  "assigned_to": "user-uuid",
  "tags": ["vip"],
  "has_email": true,
  "has_phone": true,
  "min_estimated_value": 1000.00,
  "max_estimated_value": 100000.00,
  "created_after": "2024-01-01T00:00:00Z",
  "created_before": "2024-12-31T23:59:59Z",
  "last_contacted_after": "2024-01-01T00:00:00Z",
  "last_contacted_before": "2024-12-31T23:59:59Z",
  "never_contacted": false,
  "skip": 0,
  "limit": 100,
  "sort_by": "created_date",
  "sort_order": "desc"
}
```

**Response:** Same as list contacts response.

### Bulk Operations

#### Bulk Update Contacts
```http
POST /api/v1/contacts/bulk-update
```

**Request Body:**
```json
{
  "contact_ids": ["contact-uuid-1", "contact-uuid-2"],
  "status": "active",
  "priority": "high",
  "assigned_to": "user-uuid",
  "tags_to_add": ["important"],
  "tags_to_remove": ["old"],
  "custom_fields": {
    "bulk_updated": "2024-01-15"
  }
}
```

**Response:**
```json
{
  "updated_count": 2,
  "success": true,
  "message": "Successfully updated 2 contacts"
}
```

#### Assign Contacts
```http
POST /api/v1/contacts/assign
```

**Request Body:**
```json
{
  "contact_ids": ["contact-uuid-1", "contact-uuid-2"],
  "assigned_to": "user-uuid",
  "notes": "Assigned for follow-up"
}
```

**Response:**
```json
{
  "updated_count": 2,
  "success": true,
  "message": "Successfully assigned 2 contacts"
}
```

### Contact Management

#### Convert Contact Type
```http
POST /api/v1/contacts/{contact_id}/convert
```

**Request Body:**
```json
{
  "to_type": "customer",
  "notes": "Converted from lead after successful sale"
}
```

**Response:** Updated contact object.

#### Mark Contact as Contacted
```http
POST /api/v1/contacts/{contact_id}/mark-contacted
```

**Response:** Updated contact object with `last_contacted` timestamp.

### Tag Management

#### Manage Contact Tags
```http
POST /api/v1/contacts/tags
```

**Request Body:**
```json
{
  "contact_ids": ["contact-uuid-1", "contact-uuid-2"],
  "tags": ["important", "follow-up"],
  "operation": "add"  // "add", "remove", "replace"
}
```

**Response:**
```json
{
  "updated_count": 2,
  "success": true,
  "message": "Successfully added tags on 2 contacts"
}
```

### Analytics & Statistics

#### Get Contact Statistics
```http
GET /api/v1/contacts/statistics/overview
```

**Response:**
```json
{
  "total_contacts": 150,
  "active_contacts": 140,
  "inactive_contacts": 5,
  "archived_contacts": 3,
  "blocked_contacts": 2,
  "customers": 50,
  "leads": 60,
  "prospects": 30,
  "vendors": 5,
  "partners": 3,
  "contractors": 2,
  "high_priority": 20,
  "medium_priority": 100,
  "low_priority": 25,
  "urgent_priority": 5,
  "with_email": 145,
  "with_phone": 130,
  "assigned_contacts": 120,
  "unassigned_contacts": 30,
  "never_contacted": 40,
  "recently_contacted": 80,
  "high_value_contacts": 25,
  "total_estimated_value": 2500000.00,
  "average_estimated_value": 16666.67
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions",
  "details": {
    "required_permission": "edit_contacts"
  }
}
```

### 404 Not Found
```json
{
  "error": "Contact not found"
}
```

### 409 Conflict
```json
{
  "error": "Contact with this email already exists"
}
```

## Business Rules

### Contact Creation
- At least one name field (first_name, last_name, or company_name) is required
- At least one contact method (email, phone, or mobile_phone) is required
- Email addresses must be unique within a business
- Phone numbers must be unique within a business

### Contact Updates
- Cannot change contact to a duplicate email/phone within the business
- Status changes follow business logic (e.g., cannot unarchive blocked contacts)

### Contact Type Conversions
- Prospects can be converted to leads
- Leads and prospects can be converted to customers
- Other conversions are allowed but may not follow specific business rules

### Permissions
- Users need `view_contacts` to read contact data
- Users need `edit_contacts` to create, update, assign, or convert contacts
- Users need `delete_contacts` to delete contacts
- All operations are scoped to businesses where the user has membership

## Integration Examples

### JavaScript/TypeScript
```typescript
// Create a contact
const contact = await fetch('/api/v1/contacts/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'X-Business-ID': businessId
  },
  body: JSON.stringify({
    contact_type: 'lead',
    first_name: 'Jane',
    last_name: 'Smith',
    email: 'jane@example.com',
    phone: '+1-555-0199'
  })
});

// Search contacts
const searchResults = await fetch('/api/v1/contacts/search', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'X-Business-ID': businessId
  },
  body: JSON.stringify({
    search_term: 'jane',
    contact_type: 'lead',
    limit: 50
  })
});
```

### Python
```python
import requests

# Headers for all requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'X-Business-ID': business_id
}

# Create a contact
contact_data = {
    'contact_type': 'customer',
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com'
}

response = requests.post(
    'https://api.hero365.com/api/v1/contacts/',
    headers=headers,
    json=contact_data
)

# Get contact statistics
stats = requests.get(
    'https://api.hero365.com/api/v1/contacts/statistics/overview',
    headers=headers
)
```

## Rate Limiting

- Contact creation: 100 requests per minute per business
- Contact updates: 200 requests per minute per business
- Contact searches: 500 requests per minute per business
- Bulk operations: 10 requests per minute per business

## Webhooks

Contact events can trigger webhooks:

- `contact.created`
- `contact.updated`
- `contact.deleted`
- `contact.converted`
- `contact.assigned`
- `contact.contacted`

Webhook payload example:
```json
{
  "event": "contact.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "business_id": "business-uuid",
  "data": {
    "contact_id": "contact-uuid",
    "contact": {
      // Full contact object
    },
    "created_by": "user-uuid"
  }
}
```

## Data Export/Import

### Export Contacts
```http
GET /api/v1/contacts/export?format=csv&filters=...
```

### Import Contacts
```http
POST /api/v1/contacts/import
Content-Type: multipart/form-data

file: contacts.csv
mapping: {"Name": "first_name", "Email": "email"}
```

## Custom Fields

Contacts support custom fields stored as JSON:

```json
{
  "custom_fields": {
    "industry": "Technology",
    "company_size": "100-500",
    "lead_score": 85,
    "last_interaction": "2024-01-15",
    "preferences": {
      "communication": "email",
      "frequency": "weekly"
    }
  }
}
```

Custom fields are:
- Flexible and schema-less
- Searchable (limited)
- Included in exports
- Preserved during updates

## Best Practices

1. **Data Quality**: Always validate email and phone formats
2. **Deduplication**: Check for existing contacts before creating new ones
3. **Tags**: Use consistent tag naming conventions
4. **Assignment**: Assign contacts to team members for accountability
5. **Activity Tracking**: Use the mark-contacted endpoint to track interactions
6. **Custom Fields**: Use structured custom fields for business-specific data
7. **Bulk Operations**: Use bulk endpoints for efficiency when updating multiple contacts
8. **Search**: Use specific search criteria to improve performance
9. **Permissions**: Ensure users have appropriate permissions before operations
10. **Error Handling**: Implement proper error handling for all API calls 