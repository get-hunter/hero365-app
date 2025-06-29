# Cost Estimate Management API Documentation

## Overview
The Cost Estimate Management API provides endpoints for creating, updating, and managing cost estimates as part of the Hero365 job management system. Cost estimates are integral to job records and include labor, materials, equipment, overhead, markup, taxes, and discounts.

## Goals
- **Comprehensive Cost Tracking**: Track all cost components for accurate job pricing
- **Profit Margin Management**: Calculate markup and profit margins automatically
- **Tax & Discount Handling**: Support for regional tax rates and customer discounts
- **Real-time Calculations**: Automatic calculation of subtotals, taxes, and final totals
- **Mobile-First Design**: Optimized for field workers using mobile devices

## Base URL
Cost estimates are managed through the Jobs API at `/api/v1/jobs`

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Business Context
All cost estimate operations automatically use the current user's business context.

## Cost Estimate Data Model

### JobCostEstimate Interface
```typescript
interface JobCostEstimate {
  labor_cost?: number;        // Default: 0, decimal precision, >= 0
  material_cost?: number;     // Default: 0, decimal precision, >= 0
  equipment_cost?: number;    // Default: 0, decimal precision, >= 0
  overhead_cost?: number;     // Default: 0, decimal precision, >= 0
  markup_percentage?: number; // Default: 20, decimal precision, >= 0
  tax_percentage?: number;    // Default: 0, decimal precision, >= 0
  discount_amount?: number;   // Default: 0, decimal precision, >= 0
}
```

### Calculated Values
The system automatically calculates the following values:
- **Subtotal**: `labor_cost + material_cost + equipment_cost + overhead_cost`
- **Markup Amount**: `subtotal * (markup_percentage / 100)`
- **Total Before Tax**: `subtotal + markup_amount - discount_amount`
- **Tax Amount**: `total_before_tax * (tax_percentage / 100)`
- **Final Total**: `total_before_tax + tax_amount`
- **Profit Margin**: `(markup_amount / final_total) * 100` (if final_total > 0)

### Validation Rules
- All cost values must be >= 0
- All values support decimal precision (2 decimal places)
- Markup and tax percentages are whole numbers (20.00 = 20%)
- Discount amount cannot exceed subtotal + markup amount

## API Endpoints

### 1. Create Job with Cost Estimate

**Endpoint**: `POST /api/v1/jobs`

**Description**: Create a new job with an initial cost estimate.

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "HVAC System Installation",
  "description": "Complete HVAC system installation for residential property",
  "job_type": "installation",
  "priority": "high",
  "source": "website",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  },
  "cost_estimate": {
    "labor_cost": "450.00",
    "material_cost": "1200.00",
    "equipment_cost": "150.00",
    "overhead_cost": "200.00",
    "markup_percentage": "25.00",
    "tax_percentage": "8.25",
    "discount_amount": "100.00"
  },
  "scheduled_start": "2024-02-15T09:00:00Z",
  "scheduled_end": "2024-02-15T17:00:00Z",
  "tags": ["hvac", "installation", "residential"]
}
```

**Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "business_id": "550e8400-e29b-41d4-a716-446655440002",
  "job_number": "JOB-2024-001",
  "title": "HVAC System Installation",
  "description": "Complete HVAC system installation for residential property",
  "job_type": "installation",
  "status": "draft",
  "priority": "high",
  "source": "website",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  },
  "cost_estimate": {
    "labor_cost": "450.00",
    "material_cost": "1200.00",
    "equipment_cost": "150.00",
    "overhead_cost": "200.00",
    "markup_percentage": "25.00",
    "tax_percentage": "8.25",
    "discount_amount": "100.00"
  },
  "scheduled_start": "2024-02-15T09:00:00Z",
  "scheduled_end": "2024-02-15T17:00:00Z",
  "assigned_to": [],
  "created_by": "user_12345",
  "tags": ["hvac", "installation", "residential"],
  "created_date": "2024-02-01T10:30:00Z",
  "last_modified": "2024-02-01T10:30:00Z",
  "estimated_revenue": "2275.00",
  "profit_margin": "21.98",
  "is_overdue": false,
  "is_emergency": false,
  "status_display": "Draft",
  "priority_display": "High",
  "type_display": "Installation"
}
```

### 2. Update Job Cost Estimate

**Endpoint**: `PUT /api/v1/jobs/{job_id}`

**Description**: Update an existing job's cost estimate. You can provide partial updates - only the fields you specify will be updated.

**Path Parameters**:
- `job_id` (UUID): The ID of the job to update

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body** (Partial update example):
```json
{
  "cost_estimate": {
    "labor_cost": "500.00",
    "material_cost": "1350.00",
    "markup_percentage": "22.00",
    "tax_percentage": "8.75"
  }
}
```

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "business_id": "550e8400-e29b-41d4-a716-446655440002",
  "job_number": "JOB-2024-001",
  "title": "HVAC System Installation",
  "cost_estimate": {
    "labor_cost": "500.00",
    "material_cost": "1350.00",
    "equipment_cost": "150.00",
    "overhead_cost": "200.00",
    "markup_percentage": "22.00",
    "tax_percentage": "8.75",
    "discount_amount": "100.00"
  },
  "last_modified": "2024-02-01T14:30:00Z",
  "estimated_revenue": "2484.50",
  "profit_margin": "19.35"
}
```

### 3. Get Job with Cost Estimate

**Endpoint**: `GET /api/v1/jobs/{job_id}`

**Description**: Retrieve a job with its complete cost estimate details.

**Path Parameters**:
- `job_id` (UUID): The ID of the job to retrieve

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "cost_estimate": {
    "labor_cost": "500.00",
    "material_cost": "1350.00",
    "equipment_cost": "150.00",
    "overhead_cost": "200.00",
    "markup_percentage": "22.00",
    "tax_percentage": "8.75",
    "discount_amount": "100.00"
  },
  "estimated_revenue": "2484.50",
  "profit_margin": "19.35"
}
```

## Cost Calculation Examples

### Example 1: Basic Service Call
```json
{
  "cost_estimate": {
    "labor_cost": "150.00",
    "material_cost": "25.00",
    "equipment_cost": "0.00",
    "overhead_cost": "15.00",
    "markup_percentage": "20.00",
    "tax_percentage": "8.25",
    "discount_amount": "0.00"
  }
}
```

**Calculations**:
- Subtotal: $150.00 + $25.00 + $0.00 + $15.00 = $190.00
- Markup: $190.00 × 20% = $38.00
- Total Before Tax: $190.00 + $38.00 - $0.00 = $228.00
- Tax: $228.00 × 8.25% = $18.81
- **Final Total: $246.81**
- Profit Margin: ($38.00 ÷ $246.81) × 100 = 15.40%

### Example 2: Large Project with Discount
```json
{
  "cost_estimate": {
    "labor_cost": "2000.00",
    "material_cost": "5000.00",
    "equipment_cost": "800.00",
    "overhead_cost": "500.00",
    "markup_percentage": "15.00",
    "tax_percentage": "7.50",
    "discount_amount": "500.00"
  }
}
```

**Calculations**:
- Subtotal: $2000.00 + $5000.00 + $800.00 + $500.00 = $8,300.00
- Markup: $8,300.00 × 15% = $1,245.00
- Total Before Tax: $8,300.00 + $1,245.00 - $500.00 = $9,045.00
- Tax: $9,045.00 × 7.50% = $678.38
- **Final Total: $9,723.38**
- Profit Margin: ($1,245.00 ÷ $9,723.38) × 100 = 12.81%

## Error Handling

### Validation Errors
**Status Code**: `400 Bad Request`

```json
{
  "error": "ValidationError",
  "message": "Invalid cost estimate data",
  "details": {
    "field": "labor_cost",
    "error": "Labor cost cannot be negative"
  }
}
```

### Common Validation Errors:
- `labor_cost`: "Labor cost cannot be negative"
- `material_cost`: "Material cost cannot be negative"
- `equipment_cost`: "Equipment cost cannot be negative"
- `overhead_cost`: "Overhead cost cannot be negative"
- `markup_percentage`: "Markup percentage cannot be negative"
- `tax_percentage`: "Tax percentage cannot be negative"
- `discount_amount`: "Discount amount cannot be negative"

### Job Not Found
**Status Code**: `404 Not Found`

```json
{
  "error": "NotFoundError",
  "message": "Job not found"
}
```

### Permission Denied
**Status Code**: `403 Forbidden`

```json
{
  "error": "PermissionDeniedError",
  "message": "You don't have permission to access this job"
}
```

## Mobile App Implementation Guidelines

### 1. Cost Input Form Design
- Use numeric keypads for all cost inputs
- Format numbers to 2 decimal places automatically
- Show real-time calculations as user inputs values
- Validate negative values before submission

### 2. Currency Formatting
- Display all currency values formatted to 2 decimal places
- Use locale-appropriate currency formatting
- Show currency symbol ($) consistently

### 3. Calculation Display
```swift
// Example iOS implementation
struct CostEstimateCalculator {
    func calculateTotals(from estimate: CostEstimate) -> CostSummary {
        let subtotal = estimate.laborCost + estimate.materialCost + 
                      estimate.equipmentCost + estimate.overheadCost
        let markupAmount = subtotal * (estimate.markupPercentage / 100)
        let totalBeforeTax = subtotal + markupAmount - estimate.discountAmount
        let taxAmount = totalBeforeTax * (estimate.taxPercentage / 100)
        let finalTotal = totalBeforeTax + taxAmount
        let profitMargin = finalTotal > 0 ? (markupAmount / finalTotal) * 100 : 0
        
        return CostSummary(
            subtotal: subtotal,
            markupAmount: markupAmount,
            totalBeforeTax: totalBeforeTax,
            taxAmount: taxAmount,
            finalTotal: finalTotal,
            profitMargin: profitMargin
        )
    }
}
```

### 4. API Integration
- Always include cost_estimate in job creation requests
- Use PUT requests for cost estimate updates (supports partial updates)
- Handle validation errors gracefully with user-friendly messages
- Show loading states during API calls

### 5. Offline Support
- Cache cost estimates locally when offline
- Sync changes when connection is restored
- Show "unsaved changes" indicators appropriately

## Best Practices

### 1. Data Entry Validation
- Validate numeric inputs client-side before API calls
- Use decimal number types to avoid floating-point precision issues
- Prevent submission of empty or invalid cost data

### 2. User Experience
- Show breakdown of calculations clearly
- Provide tooltips or help text for markup percentage
- Allow quick templates for common cost structures
- Enable copying cost estimates between similar jobs

### 3. Performance
- Cache calculated values to avoid repeated API calls
- Use debounced input for real-time calculations
- Batch multiple cost estimate updates when possible

### 4. Security
- Always validate cost estimates server-side
- Ensure business context is properly enforced
- Log significant cost estimate changes for audit purposes

## Testing Scenarios

### 1. Basic Cost Estimate Creation
1. Create job with all cost fields populated
2. Verify calculations are correct
3. Confirm estimated_revenue and profit_margin are calculated

### 2. Partial Cost Updates
1. Update only labor_cost in existing job
2. Verify other fields remain unchanged
3. Confirm recalculated totals are correct

### 3. Edge Cases
1. Zero values for all cost components
2. Very large cost values
3. High markup percentages (>100%)
4. High tax rates (>20%)
5. Discount amount larger than subtotal

### 4. Validation Testing
1. Negative cost values
2. Invalid decimal precision
3. Missing required fields
4. Malformed JSON requests

## Rate Limits
- Standard API rate limits apply: 1000 requests per hour per user
- Cost estimate calculations are performed server-side
- No additional rate limits for cost estimate operations

## Support
For technical support or questions about cost estimate implementation:
- Check the Jobs Management API documentation
- Review error responses for detailed validation information
- Use the API testing endpoints for development 