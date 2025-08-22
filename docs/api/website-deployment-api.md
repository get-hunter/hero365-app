# Website Deployment API Documentation

## Overview

The Website Deployment API provides endpoints for creating, building, and deploying professional websites using AI-generated content and Next.js templates. This API enables the mobile app to offer one-click website creation for Hero365 professionals.

## Base URL

```
POST /api/v1/website-deployment
```

## Authentication

All endpoints require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Deploy Website

**Endpoint:** `POST /api/v1/website-deployment/deploy`

Creates and deploys a complete professional website with AI-generated content.

#### Request Body

```json
{
  "business_name": "Austin Elite HVAC",
  "trade_type": "hvac",
  "location": "Austin, TX",
  "phone_number": "(512) 555-COOL",
  "email": "service@austinelitehvac.com",
  "address": "456 Tech Ridge Blvd, Austin, TX 78753",
  "custom_domain": "austinelitehvac.com",
  "template_variant": "professional",
  "target_keywords": ["hvac austin", "ac repair austin", "heating repair"],
  "service_areas": ["Round Rock", "Cedar Park", "Pflugerville"],
  "primary_color": "#3B82F6",
  "secondary_color": "#10B981",
  "logo_url": "https://example.com/logo.png",
  "include_reviews": true,
  "include_service_areas": true,
  "include_about": true,
  "emergency_service": true
}
```

#### Response

```json
{
  "deployment_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "website_url": null,
  "preview_url": null,
  "build_time": null,
  "pages_generated": null,
  "seo_score": null,
  "content_sections": 6,
  "keywords_optimized": null,
  "created_at": "2024-01-15T10:30:00Z",
  "deployed_at": null,
  "error_message": null
}
```

### 2. Get Deployment Status

**Endpoint:** `GET /api/v1/website-deployment/status/{deployment_id}`

Retrieves the current status of a website deployment.

#### Response

```json
{
  "deployment_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "building",
  "progress": 75,
  "current_step": "Deploying to Cloudflare Pages",
  "website_url": null,
  "error_message": null
}
```

#### Status Values

- `pending` - Deployment queued
- `building` - Generating content and building website
- `deploying` - Deploying to hosting platform
- `completed` - Successfully deployed
- `failed` - Deployment failed
- `cancelled` - Deployment cancelled

### 3. List Deployments

**Endpoint:** `GET /api/v1/website-deployment/deployments?limit=10`

Lists recent website deployments for the current user.

#### Response

```json
[
  {
    "deployment_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "current_step": "Deployment completed successfully",
    "website_url": "https://abc123.hero365-websites.pages.dev",
    "error_message": null
  }
]
```

### 4. Preview Website

**Endpoint:** `POST /api/v1/website-deployment/preview`

Generates a preview of the website content without deploying.

#### Request Body

Same as deploy endpoint but without deployment.

#### Response

```json
{
  "preview_id": "preview-123",
  "content": {
    "business": {
      "name": "Austin Elite HVAC",
      "phone": "(512) 555-COOL",
      "description": "Professional HVAC services..."
    },
    "hero": {
      "headline": "Austin's Most Trusted HVAC Experts",
      "subtitle": "24/7 Emergency Service..."
    },
    "services": [...],
    "seo": {
      "title": "Austin Elite HVAC - Professional HVAC Services",
      "keywords": [...]
    }
  },
  "template_info": {
    "trade_type": "hvac",
    "location": "Austin, TX",
    "sections": ["hero", "services", "about", "reviews"],
    "seo_keywords": ["hvac austin", "ac repair austin"],
    "estimated_pages": 4
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 5. Cancel Deployment

**Endpoint:** `DELETE /api/v1/website-deployment/deployments/{deployment_id}`

Cancels a pending or in-progress deployment.

#### Response

```json
{
  "message": "Deployment cancelled successfully"
}
```

## Trade Types Supported

- `hvac` - Heating, Ventilation, Air Conditioning
- `plumbing` - Plumbing services
- `electrical` - Electrical services
- `roofing` - Roofing services
- `landscaping` - Landscaping services
- `security_systems` - Security system installation
- `pool_spa` - Pool and spa services
- `water_treatment` - Water treatment systems
- `kitchen_equipment` - Commercial kitchen equipment
- `mechanical` - Mechanical services
- `refrigeration` - Refrigeration services

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid trade type specified"
}
```

### 404 Not Found

```json
{
  "detail": "Deployment not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to start website deployment: Build process failed"
}
```

## Features Included

### AI-Generated Content
- Trade-specific headlines and descriptions
- SEO-optimized meta tags and content
- Local business schema markup
- Professional service descriptions
- Customer reviews and testimonials

### Professional Components
- Responsive navigation header
- Hero section with call-to-action buttons
- Services grid with pricing
- About us section with certifications
- Customer reviews and ratings
- Service areas with response times
- Contact forms with lead capture
- Booking widgets for scheduling
- Emergency service banners

### SEO Optimization
- Comprehensive meta tags
- JSON-LD structured data
- XML sitemap generation
- Robots.txt configuration
- Local business optimization
- Mobile-responsive design
- Fast loading times
- Core Web Vitals optimization

### Deployment Features
- Automatic Cloudflare Pages deployment
- SSL certificate provisioning
- CDN distribution
- Custom domain support (coming soon)
- Real-time deployment tracking
- Error handling and retry logic

## Usage Examples

### Mobile App Integration

```swift
// Swift example for mobile app
struct WebsiteDeploymentService {
    func deployWebsite(businessData: BusinessData) async throws -> DeploymentResponse {
        let request = WebsiteDeploymentRequest(
            businessName: businessData.name,
            tradeType: businessData.tradeType,
            location: businessData.location,
            phoneNumber: businessData.phone,
            email: businessData.email,
            address: businessData.address
        )
        
        return try await apiClient.post("/api/v1/website-deployment/deploy", body: request)
    }
    
    func checkDeploymentStatus(deploymentId: String) async throws -> DeploymentStatus {
        return try await apiClient.get("/api/v1/website-deployment/status/\(deploymentId)")
    }
}
```

### JavaScript/TypeScript

```typescript
// TypeScript example
interface WebsiteDeploymentRequest {
  business_name: string;
  trade_type: string;
  location: string;
  phone_number: string;
  email: string;
  address: string;
  // ... other fields
}

async function deployWebsite(data: WebsiteDeploymentRequest): Promise<DeploymentResponse> {
  const response = await fetch('/api/v1/website-deployment/deploy', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  
  return response.json();
}
```

## Rate Limits

- Deploy Website: 5 requests per hour per user
- Status Check: 100 requests per minute per user
- Preview: 20 requests per hour per user

## Best Practices

1. **Always check deployment status** after initiating deployment
2. **Use preview endpoint** to validate content before deploying
3. **Provide comprehensive business information** for better AI content generation
4. **Include target keywords** for SEO optimization
5. **Specify service areas** for local SEO benefits
6. **Use custom domains** for professional branding (when available)

## Support

For API support and questions:
- Email: api-support@hero365.com
- Documentation: https://docs.hero365.com/api/website-deployment
- Status Page: https://status.hero365.com
