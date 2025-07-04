# Products and Services Integration API Documentation

This document provides comprehensive API documentation for integrating products and services into the Hero365 mobile app. This covers all endpoints needed for product/service management, inventory tracking, and integration with estimates, invoices, and jobs.

## Overview

The Hero365 system treats both products and services as "products" with different types:
- **Products**: Physical items with inventory tracking
- **Services**: Labor, consulting, or service offerings (typically non-inventory items)

Both share the same API endpoints but have different attributes and behaviors based on their type.

## Authentication & Authorization

All endpoints require:
- **Authentication**: Bearer token in `Authorization` header
- **Business Context**: User must be a member of a business
- **Permissions**:
  - `view_projects` - Read access to products/services
  - `edit_projects` - Write access to products/services
  - `delete_projects` - Delete access to products/services

## Base URL

All endpoints use the base URL: `/api/v1/products`

## Products/Services Management

### Create Product/Service

**Endpoint:** `POST /api/v1/products`

**Description:** Creates a new product or service with comprehensive configuration options.

**Request Schema:**
```json
{
  "sku": "string (required, unique)",
  "name": "string (required)",
  "description": "string (optional)",
  "product_type": "string (required: 'product' | 'service')",
  "status": "string (default: 'active')",
  "category_id": "uuid (optional)",
  
  "pricing_model": "string (default: 'fixed')",
  "unit_price": "decimal (required)",
  "cost_price": "decimal (optional)",
  "markup_percentage": "decimal (optional)",
  "currency": "string (default: 'USD')",
  
  "track_inventory": "boolean (default: true for products, false for services)",
  "unit_of_measure": "string (default: 'each')",
  "initial_quantity": "decimal (default: 0)",
  "reorder_point": "decimal (optional)",
  "reorder_quantity": "decimal (optional)",
  "minimum_quantity": "decimal (optional)",
  "maximum_quantity": "decimal (optional)",
  
  "tax_rate": "decimal (optional)",
  "tax_code": "string (optional)",
  "is_taxable": "boolean (default: true)",
  
  "primary_supplier_id": "uuid (optional)",
  "barcode": "string (optional)",
  "manufacturer": "string (optional)",
  "brand": "string (optional)",
  "image_urls": "array of strings (optional)"
}
```

**Example - Creating a Product:**
```bash
POST /api/v1/products
Content-Type: application/json
Authorization: Bearer {token}

{
  "sku": "PIPE-100",
  "name": "PVC Pipe 4 inch",
  "description": "Heavy duty PVC pipe for plumbing",
  "product_type": "product",
  "unit_price": 25.99,
  "cost_price": 15.00,
  "track_inventory": true,
  "unit_of_measure": "feet",
  "initial_quantity": 500,
  "reorder_point": 50,
  "reorder_quantity": 200,
  "is_taxable": true,
  "weight": 2.5,
  "weight_unit": "lbs"
}
```

**Example - Creating a Service:**
```bash
POST /api/v1/products
Content-Type: application/json
Authorization: Bearer {token}

{
  "sku": "HVAC-INSTALL",
  "name": "HVAC System Installation",
  "description": "Complete HVAC system installation service",
  "product_type": "service",
  "unit_price": 150.00,
  "cost_price": 0.00,
  "track_inventory": false,
  "unit_of_measure": "hour",
  "is_taxable": true
}
```

### Get Product/Service Details

**Endpoint:** `GET /api/v1/products/{product_id}`

**Description:** Retrieves detailed information about a specific product or service.

**Example:**
```bash
GET /api/v1/products/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer {token}
```

### Update Product/Service

**Endpoint:** `PUT /api/v1/products/{product_id}`

**Description:** Updates an existing product or service. All fields are optional.

### Delete Product/Service

**Endpoint:** `DELETE /api/v1/products/{product_id}`

**Description:** Soft deletes a product or service (sets status to inactive).

**Response:**
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

## Search and List Products/Services

### List Products/Services

**Endpoint:** `GET /api/v1/products`

**Description:** Retrieves a paginated list of products and services with optional filtering.

**Query Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100, max: 1000): Maximum number of records to return
- `status` (string, optional): Filter by status ('active', 'inactive', 'discontinued')
- `category_id` (uuid, optional): Filter by category ID
- `supplier_id` (uuid, optional): Filter by supplier ID
- `low_stock_only` (boolean, default: false): Show only low stock items

### Advanced Search

**Endpoint:** `POST /api/v1/products/search`

**Description:** Advanced search for products and services with comprehensive filtering.

**Example - Search for Services:**
```bash
POST /api/v1/products/search
Content-Type: application/json
Authorization: Bearer {token}

{
  "search_term": "installation",
  "product_type": "service",
  "min_price": 50,
  "max_price": 200,
  "limit": 20,
  "sort_by": "unit_price",
  "sort_order": "asc"
}
```

## Inventory Management (Products Only)

### Adjust Stock

**Endpoint:** `POST /api/v1/products/{product_id}/adjust-stock`

**Description:** Adjusts inventory levels for a product with audit trail.

**Request Schema:**
```json
{
  "product_id": "uuid (required)",
  "quantity_change": "decimal (required)",
  "adjustment_reason": "string (required)",
  "reference_number": "string (optional)",
  "notes": "string (optional)"
}
```

### Reserve Stock

**Endpoint:** `POST /api/v1/products/{product_id}/reserve`

**Description:** Reserves stock for orders, estimates, or jobs.

### Get Reorder Suggestions

**Endpoint:** `GET /api/v1/products/reorder/suggestions`

**Description:** Gets automated reorder suggestions for products that need restocking.

## Mobile App Integration Examples

### Product/Service Selection for Estimates/Invoices

```typescript
// Search products/services for estimate/invoice
const searchProductsServices = async (query: string, type?: 'product' | 'service') => {
  const response = await fetch('/api/v1/products/search', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      search_term: query,
      product_type: type,
      status: 'active',
      limit: 20,
      sort_by: 'name',
      sort_order: 'asc'
    })
  });
  return await response.json();
};

// Check product availability before adding to estimate/invoice
const checkProductAvailability = async (productId: string, quantity: number) => {
  const response = await fetch(`/api/v1/products/${productId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const product = await response.json();
  
  if (product.product_type === 'service') {
    return { available: true, unlimited: true };
  }
  
  return {
    available: product.quantity_available >= quantity,
    availableQuantity: product.quantity_available,
    isLowStock: product.is_low_stock,
    isOutOfStock: product.is_out_of_stock
  };
};
```

### Inventory Management

```typescript
// Adjust inventory levels
const adjustInventory = async (productId: string, quantity: number, reason: string) => {
  const response = await fetch(`/api/v1/products/${productId}/adjust-stock`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product_id: productId,
      quantity_change: quantity,
      adjustment_reason: reason
    })
  });
  return await response.json();
};

// Get low stock alerts
const getLowStockAlerts = async () => {
  const response = await fetch('/api/v1/products?low_stock_only=true&limit=100', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
};
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Validation error: SKU already exists"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions to access products"
}
```

**404 Not Found:**
```json
{
  "detail": "Product not found"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": "Cannot adjust stock for service items"
}
```

## Business Rules

### Product Management Rules
- SKU must be unique within each business
- Product type cannot be changed after creation
- Products with inventory tracking must have valid quantity fields
- Services typically have `track_inventory=false`

### Inventory Rules
- Stock adjustments create audit trail entries
- Reserved quantities are tracked separately from available quantities
- Available quantity = On hand quantity - Reserved quantity
- Low stock alerts trigger when quantity falls below reorder point

### Pricing Rules
- Unit price must be >= 0
- Cost price must be >= 0
- Markup percentage calculated as: (unit_price - cost_price) / cost_price * 100
- Margin percentage calculated as: (unit_price - cost_price) / unit_price * 100

### Integration Rules
- Products can be reserved for estimates, invoices, and jobs
- Services don't require inventory reservation
- Stock movements are automatically created when products are sold
- Products can be associated with multiple suppliers

## Data Validation

### Required Fields
- **sku**: Unique identifier, max 100 characters
- **name**: Product/service name, max 300 characters
- **product_type**: Must be 'product' or 'service'
- **unit_price**: Must be >= 0

### Optional Fields
- **description**: Max 2000 characters
- **category_id**: Valid UUID of existing category
- **cost_price**: Must be >= 0
- **quantities**: Must be >= 0
- **weight**: Must be >= 0
- **tax_rate**: Must be >= 0 and <= 100

### Business Logic Validation
- Products with `track_inventory=true` require inventory-related fields
- Services typically don't need inventory fields
- Reorder quantities must be > 0 if specified
- Maximum quantity must be > minimum quantity if both specified

This API documentation provides comprehensive coverage of all product and service integration endpoints needed for the Hero365 mobile app, with clear examples and error handling patterns.
