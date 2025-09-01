# Service Management API Documentation

## Overview

The Service Management API provides endpoints for managing business services with an intelligent default assignment system. This API enables contractors to easily configure their service offerings with minimal setup, improving the onboarding experience.

## Key Features

- **Auto-Assignment**: Automatically assigns default services based on primary trade and market focus
- **Market Focus**: Supports residential, commercial, or both market segments
- **Comprehensive Service Catalog**: 81 residential services and 77 commercial services across all trades
- **Easy Management**: Simple APIs to add, remove, and update services
- **Preview Mode**: Preview services before applying changes

## Base URL

```
/api/v1/services
```

## Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Get Default Services

**GET** `/default`

Returns all available services organized by trade categories.

**Response:**
```json
{
  "residential_services": {
    "hvac": [
      {
        "key": "ac_installation",
        "display_name": "AC Installation",
        "trade_category": "hvac"
      },
      {
        "key": "furnace_repair",
        "display_name": "Furnace Repair", 
        "trade_category": "hvac"
      }
    ]
  },
  "commercial_services": {
    "mechanical": [
      {
        "key": "hvac_installation",
        "display_name": "HVAC Installation",
        "trade_category": "mechanical"
      }
    ]
  }
}
```

### 2. Preview Services for Trades

**POST** `/preview`

Preview what services would be auto-assigned for given trades and market focus.

**Request Body:**
```json
{
  "primary_trade": "hvac",
  "secondary_trades": ["plumbing"],
  "market_focus": "both"
}
```

**Response:**
```json
{
  "primary_trade": "hvac",
  "secondary_trades": ["plumbing"],
  "market_focus": "both",
  "residential_services": ["hvac", "plumbing"],
  "commercial_services": ["mechanical", "plumbing"],
  "service_details": {
    "hvac": {
      "key": "hvac",
      "display_name": "HVAC",
      "trade_category": "auto-assigned"
    }
  }
}
```

### 3. Get Business Services

**GET** `/business/{business_id}`

Get current services for a business along with all available options.

**Parameters:**
- `business_id` (path): Business UUID

**Response:**
```json
{
  "business_id": "550e8400-e29b-41d4-a716-446655440010",
  "market_focus": "both",
  "residential_services": ["hvac", "plumbing"],
  "commercial_services": ["mechanical", "plumbing"],
  "available_residential_services": {
    "hvac": [
      {
        "key": "ac_installation",
        "display_name": "AC Installation",
        "trade_category": "hvac"
      }
    ]
  },
  "available_commercial_services": {
    "mechanical": [
      {
        "key": "hvac_installation", 
        "display_name": "HVAC Installation",
        "trade_category": "mechanical"
      }
    ]
  }
}
```

### 4. Update Business Services

**PUT** `/business/{business_id}`

Update services for a business. Users can select/unselect services.

**Parameters:**
- `business_id` (path): Business UUID

**Request Body:**
```json
{
  "residential_services": ["hvac", "plumbing", "electrical"],
  "commercial_services": ["mechanical", "plumbing"]
}
```

**Response:** Same as Get Business Services

### 5. Auto-Assign Services

**POST** `/business/{business_id}/auto-assign`

Auto-assign default services based on primary and secondary trades.

**Parameters:**
- `business_id` (path): Business UUID

**Request Body:**
```json
{
  "primary_trade": "hvac",
  "secondary_trades": ["plumbing"],
  "market_focus": "both"
}
```

**Response:** Same as Get Business Services

## Market Focus Options

- `residential`: Serves residential customers only
- `commercial`: Serves commercial customers only  
- `both`: Serves both residential and commercial customers

## Trade Categories

### Residential Trades
- `hvac` - HVAC systems
- `plumbing` - Plumbing services
- `electrical` - Electrical work
- `chimney` - Chimney services
- `roofing` - Roofing services
- `garage_door` - Garage door services
- `septic` - Septic systems
- `pest_control` - Pest control
- `irrigation` - Irrigation systems
- `painting` - Painting services

### Commercial Trades
- `mechanical` - Mechanical systems
- `refrigeration` - Commercial refrigeration
- `plumbing` - Commercial plumbing
- `electrical` - Commercial electrical
- `security_systems` - Security systems
- `landscaping` - Commercial landscaping
- `roofing` - Commercial roofing
- `kitchen_equipment` - Kitchen equipment
- `water_treatment` - Water treatment
- `pool_spa` - Pool and spa services

## Auto-Assignment Logic

The system intelligently determines market focus based on the primary trade:

### Residential-Only Trades
- HVAC, Chimney, Garage Door, Septic, Pest Control, Irrigation, Painting

### Commercial-Only Trades  
- Refrigeration, Kitchen Equipment, Water Treatment, Security Systems

### Both Markets
- Plumbing, Electrical, Roofing, Landscaping, Mechanical, Pool & Spa

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid business ID format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Business not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to get business services: <error_message>"
}
```

## Usage Examples

### Mobile App Onboarding Flow

1. **Get Available Services**: Call `/default` to show all service options
2. **Preview Auto-Assignment**: Call `/preview` with user's trade selection
3. **Create Business**: Business creation automatically assigns default services
4. **Allow Customization**: User can call `/business/{id}` to see assigned services and modify them

### Service Management Flow

1. **Get Current Services**: Call `/business/{id}` to see current configuration
2. **Update Services**: Call `PUT /business/{id}` to modify service selection
3. **Re-assign Defaults**: Call `/business/{id}/auto-assign` if trade focus changes

## Benefits for Mobile App

- **Faster Onboarding**: Users get pre-selected services instead of empty lists
- **Better UX**: Smart defaults reduce decision fatigue
- **Easy Customization**: Simple toggle interface for service selection
- **Market-Aware**: Services automatically match the contractor's market focus
- **Comprehensive Coverage**: 158 total services across all trade categories

This API enables a smooth, intelligent onboarding experience while maintaining full flexibility for service customization.
