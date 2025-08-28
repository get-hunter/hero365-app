# Mobile Website Deployment API

## Overview

The Mobile Website Deployment API enables mobile app users to deploy websites by submitting business data (name, address, service areas, services, products, team, hours, subdomain) and triggering a background deployment process to Cloudflare Pages.

## Base URL

```
POST /api/v1/mobile/website/deploy
GET  /api/v1/mobile/website/deployments/{deployment_id}
GET  /api/v1/mobile/website/deployments
POST /api/v1/mobile/website/deployments/{deployment_id}/cancel
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

The business context is automatically resolved from the authenticated user's business membership.

## Endpoints

### 1. Deploy Website

**POST** `/api/v1/mobile/website/deploy`

Initiates a website deployment from mobile app with collected business data.

#### Request Body

```json
{
  "subdomain": "austin-elite",
  "service_areas": [
    {
      "postal_code": "78701",
      "country_code": "US",
      "city": "Austin",
      "region": "TX",
      "emergency_services_available": true,
      "regular_services_available": true
    }
  ],
  "services": [
    {
      "name": "HVAC Repair",
      "description": "Professional HVAC repair and maintenance",
      "pricing_model": "hourly",
      "unit_price": 125.0,
      "estimated_duration_hours": 2.0,
      "is_emergency": true,
      "is_featured": true
    }
  ],
  "products": [
    {
      "name": "Air Filter",
      "sku": "AF-001",
      "description": "High-efficiency air filter",
      "unit_price": 25.99,
      "is_featured": false
    }
  ],
  "locations": [
    {
      "name": "Main Office",
      "address": "123 Main St",
      "city": "Austin",
      "state": "TX",
      "postal_code": "78701",
      "is_primary": true
    }
  ],
  "hours": [
    {
      "day_of_week": 1,
      "is_open": true,
      "open_time": "08:00:00",
      "close_time": "17:00:00",
      "is_emergency_only": false
    },
    {
      "day_of_week": 2,
      "is_open": true,
      "open_time": "08:00:00",
      "close_time": "17:00:00",
      "is_emergency_only": false
    }
  ],
  "branding": {
    "primary_color": "#3B82F6",
    "secondary_color": "#10B981",
    "logo_url": "https://example.com/logo.png"
  },
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response

**Success (201 Created)**

```json
{
  "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "status_url": "/api/v1/mobile/website/deployments/123e4567-e89b-12d3-a456-426614174000",
  "estimated_completion_minutes": 3,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**

- **400 Bad Request**: Invalid request data or subdomain not available
- **409 Conflict**: Active deployment already in progress
- **404 Not Found**: Business not found
- **500 Internal Server Error**: Deployment initiation failed

### 2. Get Deployment Status

**GET** `/api/v1/mobile/website/deployments/{deployment_id}`

Retrieves the current status of a deployment for mobile app polling.

#### Response

**Success (200 OK)**

```json
{
  "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 100,
  "current_step": "Deployment completed successfully",
  "website_url": "https://austin-elite.hero365-websites.pages.dev",
  "error_message": null,
  "build_logs": [
    "2024-01-15T10:32:15Z: Starting website build",
    "2024-01-15T10:32:45Z: Build completed successfully",
    "2024-01-15T10:33:00Z: Deploying to Cloudflare Pages"
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:33:15Z"
}
```

**Error Responses**

- **404 Not Found**: Deployment not found
- **403 Forbidden**: Access denied to deployment
- **500 Internal Server Error**: Status retrieval failed

### 3. List Deployments

**GET** `/api/v1/mobile/website/deployments`

Lists recent deployments for the current business.

#### Query Parameters

- `limit` (optional): Maximum number of deployments to return (default: 10)
- `skip` (optional): Number of deployments to skip for pagination (default: 0)

#### Response

**Success (200 OK)**

```json
{
  "deployments": [
    {
      "deployment_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "progress": 100,
      "current_step": "Deployment completed successfully",
      "website_url": "https://austin-elite.hero365-websites.pages.dev",
      "error_message": null,
      "build_logs": ["..."],
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:33:15Z"
    }
  ],
  "total_count": 5
}
```

### 4. Cancel Deployment

**POST** `/api/v1/mobile/website/deployments/{deployment_id}/cancel`

Cancels a pending or in-progress deployment.

#### Response

**Success (200 OK)**

```json
{
  "message": "Deployment cancelled successfully"
}
```

**Error Responses**

- **404 Not Found**: Deployment not found
- **403 Forbidden**: Access denied to deployment
- **400 Bad Request**: Cannot cancel deployment in current status
- **500 Internal Server Error**: Cancellation failed

## Data Models

### Business Hours

```json
{
  "day_of_week": 1,           // 1=Monday, 7=Sunday
  "is_open": true,
  "open_time": "08:00:00",    // HH:MM:SS format
  "close_time": "17:00:00",
  "lunch_start": "12:00:00",  // Optional
  "lunch_end": "13:00:00",    // Optional
  "is_emergency_only": false
}
```

### Service Area

```json
{
  "postal_code": "78701",
  "country_code": "US",       // 2-letter country code
  "city": "Austin",           // Optional
  "region": "TX",             // Optional state/province
  "emergency_services_available": true,
  "regular_services_available": true
}
```

### Business Service

```json
{
  "name": "HVAC Repair",
  "description": "Professional HVAC repair and maintenance",
  "pricing_model": "hourly",  // fixed, hourly, per_unit, tiered, custom
  "unit_price": 125.0,        // Optional
  "estimated_duration_hours": 2.0,  // Optional
  "is_emergency": true,
  "is_featured": true
}
```

### Business Product

```json
{
  "name": "Air Filter",
  "sku": "AF-001",           // Optional
  "description": "High-efficiency air filter",
  "unit_price": 25.99,      // Optional
  "is_featured": false
}
```

### Business Location

```json
{
  "name": "Main Office",     // Optional
  "address": "123 Main St",  // Optional
  "city": "Austin",
  "state": "TX",
  "postal_code": "78701",    // Optional
  "is_primary": true
}
```

### Branding

```json
{
  "primary_color": "#3B82F6",    // Hex color code
  "secondary_color": "#10B981",  // Hex color code
  "logo_url": "https://example.com/logo.png"  // Optional
}
```

## Deployment Status Flow

1. **pending** → Initial status when deployment is created
2. **building** → Website content generation and build in progress
3. **deploying** → Deployment to Cloudflare Pages in progress
4. **completed** → Deployment successful, website is live
5. **failed** → Deployment failed, check error_message
6. **cancelled** → Deployment was cancelled by user

## Validation Rules

### Subdomain

- Lowercase alphanumeric characters and hyphens only
- 1-58 characters in length
- No leading or trailing hyphens
- Reserved names are not allowed (www, api, admin, etc.)
- Must be unique across all businesses

### Business Hours

- At least Monday-Friday hours must be provided
- Close time must be after open time
- Lunch break times are optional

### Service Areas

- At least one service area is required
- Postal code is required (3-20 characters)
- Country code defaults to "US"

### Services

- At least one service is required
- Service name is required
- Valid pricing models: fixed, hourly, per_unit, tiered, custom

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": {
    "type": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "subdomain",
        "message": "Subdomain 'www' is reserved",
        "type": "value_error",
        "input": "www"
      }
    ]
  }
}
```

## Rate Limiting

- Only one active deployment per business at a time
- Subsequent deployment requests will return 409 Conflict until the active deployment completes

## Idempotency

Use the `idempotency_key` field to prevent duplicate deployments. If a deployment with the same idempotency key exists for the business, the existing deployment will be returned instead of creating a new one.

## Mobile App Integration

### Recommended Flow

1. Collect all business data in the mobile app
2. Submit deployment request with `idempotency_key`
3. Poll deployment status every 2-3 seconds using the `status_url`
4. Display progress and current step to user
5. Show website URL when status becomes "completed"
6. Handle errors gracefully and allow retry

### Example Mobile Implementation

```javascript
// Submit deployment
const response = await fetch('/api/v1/mobile/website/deploy', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    subdomain: 'austin-elite',
    // ... other data
    idempotency_key: generateUUID()
  })
});

const deployment = await response.json();

// Poll status
const pollStatus = async () => {
  const statusResponse = await fetch(deployment.status_url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    // Show success with website URL
    showSuccess(status.website_url);
  } else if (status.status === 'failed') {
    // Show error
    showError(status.error_message);
  } else {
    // Update progress and continue polling
    updateProgress(status.progress, status.current_step);
    setTimeout(pollStatus, 2000);
  }
};

pollStatus();
```

## Database Schema

The API persists data to the following Supabase tables:

- `business_websites` - Website configuration per business
- `website_deployments` - Individual deployment runs
- `service_areas` - Business service coverage areas
- `business_services` - Services offered by the business
- `products` - Products offered by the business (optional)
- `business_locations` - Business locations
- `business_hours` - Operating hours per location/day
- `business_branding` - Branding preferences (optional)

All tables include RLS (Row Level Security) policies to ensure data isolation between businesses.
