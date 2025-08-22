# Professional Data API Documentation

## Overview

The Professional Data API provides public endpoints for retrieving professional information, services, products, and availability. These endpoints are designed to be consumed by deployed professional websites to display real, dynamic data from the Hero365 platform.

## Base URL

```
/api/v1/public/professional
```

## Authentication

These are **public endpoints** that do not require authentication. They are designed to be called from deployed websites to display professional information to potential customers.

## Endpoints

### 1. Get Professional Profile

**Endpoint:** `GET /api/v1/public/professional/profile/{business_id}`

Retrieves complete professional profile information including business details, contact information, service areas, and credentials.

#### Response

```json
{
  "business_id": "austin-elite-hvac",
  "business_name": "Austin Elite HVAC",
  "trade_type": "hvac",
  "description": "Professional HVAC services in Austin with 25+ years of experience",
  "phone": "(512) 555-COOL",
  "email": "service@austinelitehvac.com",
  "address": "456 Tech Ridge Blvd, Austin, TX 78753",
  "website": "https://austinelitehvac.com",
  "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville", "Georgetown"],
  "emergency_service": true,
  "years_in_business": 25,
  "license_number": "TACLA123456",
  "insurance_verified": true,
  "average_rating": 4.9,
  "total_reviews": 247,
  "certifications": ["NATE Certified", "EPA Certified", "BBB A+ Rating"]
}
```

### 2. Get Professional Services

**Endpoint:** `GET /api/v1/public/professional/services/{business_id}`

Retrieves all services offered by a professional with detailed pricing and availability information.

#### Query Parameters

- `category` (optional): Filter by service category
- `emergency_only` (optional): Show only emergency services (default: false)
- `available_only` (optional): Show only available services (default: true)

#### Response

```json
[
  {
    "id": "emergency-ac-repair",
    "name": "Emergency AC Repair",
    "description": "24/7 emergency air conditioning repair service throughout Austin metro area",
    "category": "HVAC Repair",
    "base_price": 99.0,
    "price_range_min": 99.0,
    "price_range_max": 399.0,
    "pricing_unit": "service call",
    "duration_minutes": 120,
    "is_emergency": true,
    "requires_quote": false,
    "available": true,
    "service_areas": ["Austin", "Round Rock", "Cedar Park"],
    "keywords": ["emergency ac repair", "air conditioning repair", "hvac emergency"],
    "image_url": null
  }
]
```

### 3. Get Professional Products

**Endpoint:** `GET /api/v1/public/professional/products/{business_id}`

Retrieves product catalog with pricing, availability, and specifications.

#### Query Parameters

- `category` (optional): Filter by product category
- `brand` (optional): Filter by brand
- `in_stock_only` (optional): Show only in-stock products (default: true)
- `max_price` (optional): Maximum price filter

#### Response

```json
[
  {
    "id": "trane-xr14-3ton",
    "name": "Trane XR14 3-Ton Heat Pump",
    "description": "Energy-efficient heat pump system with 14.5 SEER rating",
    "category": "Heat Pumps",
    "brand": "Trane",
    "model": "XR14",
    "price": 3299.99,
    "msrp": 3599.99,
    "in_stock": true,
    "stock_quantity": 5,
    "specifications": {
      "capacity": "3 tons",
      "seer": "14.5",
      "refrigerant": "R-410A",
      "sound_level": "69 dB"
    },
    "warranty_years": 10,
    "energy_rating": "14.5 SEER",
    "image_url": null,
    "datasheet_url": null
  }
]
```

### 4. Get Professional Availability

**Endpoint:** `GET /api/v1/public/professional/availability/{business_id}`

Retrieves professional availability for scheduling appointments.

#### Query Parameters

- `start_date` (optional): Start date for availability check (YYYY-MM-DD)
- `end_date` (optional): End date for availability check (YYYY-MM-DD)
- `service_type` (optional): Filter by service type
- `service_area` (optional): Filter by service area

#### Response

```json
{
  "business_id": "austin-elite-hvac",
  "available_dates": ["2024-01-20", "2024-01-21", "2024-01-22"],
  "slots": [
    {
      "date": "2024-01-20",
      "start_time": "09:00",
      "end_time": "11:00",
      "slot_type": "regular",
      "duration_minutes": 120,
      "available": true
    }
  ],
  "emergency_available": true,
  "next_available": "2024-01-20T09:00:00Z",
  "service_areas": [
    {"area": "Austin", "available": true, "response_time": "30 min"},
    {"area": "Round Rock", "available": true, "response_time": "45 min"}
  ]
}
```

### 5. Search Professionals

**Endpoint:** `GET /api/v1/public/professional/search`

Search for professionals by various criteria.

#### Query Parameters

- `trade_type` (optional): Filter by trade type (hvac, plumbing, electrical, etc.)
- `location` (optional): Search by location/service area
- `service` (optional): Search by service type
- `emergency_only` (optional): Show only emergency service providers (default: false)
- `radius_miles` (optional): Search radius in miles (default: 25)

#### Response

```json
{
  "results": [
    {
      "business_id": "austin-elite-hvac",
      "business_name": "Austin Elite HVAC",
      "trade_type": "hvac",
      "phone": "(512) 555-COOL",
      "service_areas": ["Austin", "Round Rock", "Cedar Park"],
      "emergency_service": true,
      "average_rating": 4.9,
      "total_reviews": 247,
      "distance_miles": 5.2
    }
  ],
  "total_count": 1,
  "search_criteria": {
    "trade_type": "hvac",
    "location": "Austin",
    "service": null,
    "emergency_only": false,
    "radius_miles": 25
  }
}
```

## Data Integration Service

The `ProfessionalDataService` class provides methods to fetch and format professional data for website consumption:

```python
from app.application.services.professional_data_service import ProfessionalDataService

# Initialize service
data_service = ProfessionalDataService(base_url="https://api.hero365.com")

# Fetch complete professional data
data = await data_service.get_complete_professional_data("business-123")

# Format services for website display
formatted_services = data_service.format_services_for_website(data["services"])

# Format products for website display  
formatted_products = data_service.format_products_for_website(data["products"])
```

## Website Integration

### JavaScript/TypeScript Example

```typescript
// Fetch professional data for website
async function loadProfessionalData(businessId: string) {
  const baseUrl = 'https://api.hero365.com';
  
  try {
    // Fetch profile
    const profile = await fetch(`${baseUrl}/api/v1/public/professional/profile/${businessId}`);
    const profileData = await profile.json();
    
    // Fetch services
    const services = await fetch(`${baseUrl}/api/v1/public/professional/services/${businessId}`);
    const servicesData = await services.json();
    
    // Fetch products
    const products = await fetch(`${baseUrl}/api/v1/public/professional/products/${businessId}`);
    const productsData = await products.json();
    
    // Update website content
    updateWebsiteContent({
      profile: profileData,
      services: servicesData,
      products: productsData
    });
    
  } catch (error) {
    console.error('Failed to load professional data:', error);
    // Fallback to static content
  }
}
```

### React Component Example

```tsx
import React, { useEffect, useState } from 'react';

interface ProfessionalData {
  profile: any;
  services: any[];
  products: any[];
}

export function ProfessionalWebsite({ businessId }: { businessId: string }) {
  const [data, setData] = useState<ProfessionalData | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadData() {
      try {
        const response = await fetch(`/api/v1/public/professional/profile/${businessId}`);
        const profile = await response.json();
        
        const servicesResponse = await fetch(`/api/v1/public/professional/services/${businessId}`);
        const services = await servicesResponse.json();
        
        setData({ profile, services, products: [] });
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, [businessId]);
  
  if (loading) return <div>Loading...</div>;
  if (!data) return <div>Failed to load professional data</div>;
  
  return (
    <div>
      <h1>{data.profile.business_name}</h1>
      <p>{data.profile.description}</p>
      
      <div className="services">
        {data.services.map(service => (
          <div key={service.id} className="service-card">
            <h3>{service.name}</h3>
            <p>{service.description}</p>
            <span className="price">From ${service.base_price}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `404 Not Found`: Professional or resource not found
- `500 Internal Server Error`: Server error

Error responses include a `detail` field with error information:

```json
{
  "detail": "Professional not found"
}
```

## Fallback Data

The service includes fallback data mechanisms:

- If the API is unavailable, fallback data is returned
- Fallback data includes basic professional information
- The `fallback_used` flag indicates when fallback data is returned

## Performance Considerations

- All endpoints are optimized for fast response times
- Data is cached where appropriate
- Parallel requests are supported for fetching multiple data types
- Graceful degradation when services are unavailable

## Rate Limits

- No rate limits on public endpoints
- Designed for high-volume website traffic
- Monitoring and alerting in place for performance

## Support

For API support:
- Documentation: https://docs.hero365.com/api/professional-data
- Support: api-support@hero365.com
