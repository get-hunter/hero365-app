# Inventory Management API Documentation

This document describes the comprehensive API endpoints for the Hero365 inventory management system, including products, suppliers, and purchase order management.

## Overview

The inventory management system provides complete functionality for:

- **Product Management**: Create, update, and manage products with comprehensive inventory tracking
- **Stock Management**: Track inventory levels, movements, and automated reorder suggestions
- **Supplier Management**: Manage supplier relationships with performance tracking
- **Purchase Order Workflow**: Complete procurement workflow from creation to receiving
- **Cost Management**: Multiple costing methods (FIFO, LIFO, Weighted Average)
- **Multi-location Support**: Track inventory across multiple business locations

## Authentication & Authorization

All endpoints require:
- Valid authentication token in `Authorization: Bearer {token}` header
- Business context (user must be member of a business)
- Appropriate permissions:
  - `view_projects` - Read access to inventory data
  - `edit_projects` - Write access to inventory operations

## Products API

### Create Product

**Endpoint:** `POST /api/products`

**Description:** Creates a new product with comprehensive inventory settings.

**Request Schema:**
```json
{
  "sku": "string (required, unique)",
  "name": "string (required)",
  "description": "string (optional)",
  "category_id": "uuid (optional)",
  "unit_price": "decimal (required)",
  "cost": "decimal (optional)",
  "unit_of_measure": "string (required)",
  "track_inventory": "boolean (default: true)",
  "initial_quantity": "decimal (optional, default: 0)",
  "reorder_point": "decimal (optional)",
  "reorder_quantity": "decimal (optional)",
  "max_stock_level": "decimal (optional)",
  "barcode": "string (optional)",
  "tax_rate": "decimal (optional)",
  "is_active": "boolean (default: true)",
  "notes": "string (optional)"
}
```

**Response Schema:**
```json
{
  "product": {
    "id": "uuid",
    "sku": "string",
    "name": "string",
    "description": "string",
    "unit_price": "decimal",
    "cost": "decimal",
    "quantity_on_hand": "decimal",
    "quantity_available": "decimal",
    "is_low_stock": "boolean",
    "is_out_of_stock": "boolean",
    "created_at": "datetime",
    "last_modified": "datetime"
  },
  "success": true
}
```

**Example Request:**
```bash
POST /api/products
Content-Type: application/json
Authorization: Bearer {token}

{
  "sku": "WIDGET-001",
  "name": "Premium Widget",
  "description": "High-quality widget for professional use",
  "unit_price": 29.99,
  "cost": 15.00,
  "unit_of_measure": "EACH",
  "track_inventory": true,
  "initial_quantity": 100,
  "reorder_point": 20,
  "reorder_quantity": 50,
  "barcode": "1234567890123"
}
```

### Get Product

**Endpoint:** `GET /api/products/{product_id}`

**Description:** Retrieves detailed product information including current inventory levels.

**Response Schema:**
```json
{
  "product": {
    "id": "uuid",
    "sku": "string",
    "name": "string",
    "description": "string",
    "unit_price": "decimal",
    "cost": "decimal",
    "quantity_on_hand": "decimal",
    "quantity_reserved": "decimal",
    "quantity_available": "decimal",
    "reorder_point": "decimal",
    "reorder_quantity": "decimal",
    "is_low_stock": "boolean",
    "is_out_of_stock": "boolean",
    "last_cost": "decimal",
    "average_cost": "decimal",
    "created_at": "datetime",
    "last_modified": "datetime"
  },
  "success": true
}
```

### Search Products

**Endpoint:** `GET /api/products/search`

**Description:** Search and filter products with comprehensive criteria.

**Query Parameters:**
- `query` (optional): Text search across SKU, name, and description
- `category_id` (optional): Filter by product category
- `barcode` (optional): Search by barcode
- `status` (optional): Filter by status (active, inactive, discontinued)
- `low_stock_only` (optional): Show only low stock products
- `out_of_stock_only` (optional): Show only out of stock products
- `track_inventory` (optional): Filter by inventory tracking
- `page` (optional, default: 1): Page number for pagination
- `limit` (optional, default: 50): Items per page

**Response Schema:**
```json
{
  "products": [
    {
      "id": "uuid",
      "sku": "string",
      "name": "string",
      "unit_price": "decimal",
      "quantity_available": "decimal",
      "is_low_stock": "boolean",
      "is_out_of_stock": "boolean"
    }
  ],
  "pagination": {
    "page": "integer",
    "limit": "integer",
    "total_count": "integer",
    "total_pages": "integer"
  },
  "success": true
}
```

### Stock Adjustment

**Endpoint:** `POST /api/products/{product_id}/stock-adjustment`

**Description:** Adjust product inventory levels with audit trail.

**Request Schema:**
```json
{
  "adjustment_type": "string (INCREASE|DECREASE|SET)",
  "quantity": "decimal (required)",
  "reason": "string (required)",
  "cost_per_unit": "decimal (optional)",
  "location_id": "uuid (optional)",
  "notes": "string (optional)"
}
```

**Example Request:**
```bash
POST /api/products/123e4567-e89b-12d3-a456-426614174000/stock-adjustment
Content-Type: application/json

{
  "adjustment_type": "INCREASE",
  "quantity": 25,
  "reason": "Physical count adjustment",
  "cost_per_unit": 15.50,
  "notes": "Quarterly inventory count adjustment"
}
```

### Get Reorder Suggestions

**Endpoint:** `GET /api/products/reorder-suggestions`

**Description:** Get automated reorder suggestions based on current stock levels and reorder points.

**Response Schema:**
```json
{
  "suggestions": [
    {
      "product_id": "uuid",
      "sku": "string",
      "name": "string",
      "current_quantity": "decimal",
      "reorder_point": "decimal",
      "suggested_quantity": "decimal",
      "estimated_cost": "decimal",
      "supplier_id": "uuid",
      "supplier_name": "string",
      "days_of_stock_remaining": "integer",
      "priority": "string (HIGH|MEDIUM|LOW)"
    }
  ],
  "total_estimated_cost": "decimal",
  "success": true
}
```

## Suppliers API

### Create Supplier

**Endpoint:** `POST /api/suppliers`

**Description:** Creates a new supplier with comprehensive contact and terms information.

**Request Schema:**
```json
{
  "name": "string (required)",
  "supplier_code": "string (optional, unique)",
  "contact_person": "string (optional)",
  "email": "string (optional)",
  "phone": "string (optional)",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "postal_code": "string",
    "country": "string"
  },
  "payment_terms": {
    "net_days": "integer (default: 30)",
    "discount_percentage": "decimal (optional)",
    "discount_days": "integer (optional)"
  },
  "tax_id": "string (optional)",
  "website": "string (optional)",
  "notes": "string (optional)",
  "is_active": "boolean (default: true)"
}
```

**Example Request:**
```bash
POST /api/suppliers
Content-Type: application/json

{
  "name": "ABC Supply Company",
  "supplier_code": "ABC001",
  "contact_person": "John Smith",
  "email": "orders@abcsupply.com",
  "phone": "+1-555-123-4567",
  "address": {
    "street": "123 Industrial Way",
    "city": "Supply City",
    "state": "CA",
    "postal_code": "90210",
    "country": "US"
  },
  "payment_terms": {
    "net_days": 30,
    "discount_percentage": 2.0,
    "discount_days": 10
  }
}
```

### Get Supplier Performance

**Endpoint:** `GET /api/suppliers/{supplier_id}/performance`

**Description:** Retrieves comprehensive supplier performance metrics.

**Response Schema:**
```json
{
  "performance": {
    "supplier_id": "uuid",
    "supplier_name": "string",
    "overall_score": "decimal",
    "performance_grade": "string (A|B|C|D|F)",
    "metrics": {
      "on_time_delivery_rate": "decimal",
      "quality_score": "decimal",
      "total_orders": "integer",
      "total_value": "decimal",
      "average_order_value": "decimal",
      "late_deliveries": "integer",
      "cancelled_orders": "integer"
    },
    "recent_orders": [
      {
        "po_number": "string",
        "order_date": "date",
        "total_amount": "decimal",
        "status": "string",
        "delivered_on_time": "boolean"
      }
    ]
  },
  "success": true
}
```

## Purchase Orders API

### Create Purchase Order

**Endpoint:** `POST /api/purchase-orders`

**Description:** Creates a new purchase order with line items.

**Request Schema:**
```json
{
  "supplier_id": "uuid (required)",
  "expected_delivery_date": "date (optional)",
  "reference_number": "string (optional)",
  "notes": "string (optional)",
  "line_items": [
    {
      "product_id": "uuid (required)",
      "quantity": "decimal (required)",
      "unit_cost": "decimal (required)",
      "notes": "string (optional)"
    }
  ]
}
```

**Response Schema:**
```json
{
  "purchase_order": {
    "id": "uuid",
    "po_number": "string",
    "supplier_name": "string",
    "status": "string",
    "total_amount": "decimal",
    "order_date": "date",
    "expected_delivery_date": "date",
    "line_items_count": "integer",
    "created_by": "string"
  },
  "success": true
}
```

### Approve Purchase Order

**Endpoint:** `POST /api/purchase-orders/{purchase_order_id}/approve`

**Description:** Approves a purchase order, moving it to approved status.

**Request Schema:**
```json
{
  "notes": "string (optional)"
}
```

### Send Purchase Order

**Endpoint:** `POST /api/purchase-orders/{purchase_order_id}/send`

**Description:** Sends an approved purchase order to the supplier.

**Request Schema:**
```json
{
  "send_method": "string (EMAIL|FAX|PORTAL)",
  "recipient_email": "string (optional)",
  "message": "string (optional)"
}
```

### Receive Purchase Order

**Endpoint:** `POST /api/purchase-orders/{purchase_order_id}/receive`

**Description:** Records receipt of purchase order items with quantity verification.

**Request Schema:**
```json
{
  "received_items": [
    {
      "line_item_id": "uuid (required)",
      "received_quantity": "decimal (required)",
      "actual_cost": "decimal (optional)",
      "notes": "string (optional)"
    }
  ],
  "received_date": "date (optional, defaults to today)",
  "delivery_notes": "string (optional)"
}
```

### Get Purchase Order Status

**Endpoint:** `GET /api/purchase-orders/{purchase_order_id}/status`

**Description:** Gets current status and workflow information for a purchase order.

**Response Schema:**
```json
{
  "purchase_order": {
    "id": "uuid",
    "po_number": "string",
    "status": "string",
    "workflow_status": {
      "can_approve": "boolean",
      "can_send": "boolean",
      "can_receive": "boolean",
      "can_cancel": "boolean"
    },
    "approval_history": [
      {
        "approved_by": "string",
        "approved_at": "datetime",
        "notes": "string"
      }
    ],
    "receiving_history": [
      {
        "received_date": "date",
        "received_by": "string",
        "items_received": "integer"
      }
    ]
  },
  "success": true
}
```

## Stock Movements API

### Get Stock Movement History

**Endpoint:** `GET /api/products/{product_id}/stock-movements`

**Description:** Retrieves complete audit trail of stock movements for a product.

**Query Parameters:**
- `start_date` (optional): Filter movements from this date
- `end_date` (optional): Filter movements until this date
- `movement_type` (optional): Filter by movement type
- `page` (optional, default: 1): Page number
- `limit` (optional, default: 50): Items per page

**Response Schema:**
```json
{
  "movements": [
    {
      "id": "uuid",
      "movement_type": "string",
      "quantity_change": "decimal",
      "quantity_before": "decimal",
      "quantity_after": "decimal",
      "cost_per_unit": "decimal",
      "total_cost": "decimal",
      "reason": "string",
      "reference_number": "string",
      "created_by": "string",
      "created_at": "datetime"
    }
  ],
  "pagination": {
    "page": "integer",
    "limit": "integer",
    "total_count": "integer"
  },
  "success": true
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: [specific validation message]"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to access inventory data"
}
```

### 404 Not Found
```json
{
  "detail": "Product/Supplier/Purchase Order not found"
}
```

### 409 Conflict
```json
{
  "detail": "SKU already exists"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "Business rule violation: [specific business rule]"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

## Mobile App Integration Examples

### Product Search and Selection

```typescript
// Search products for estimate/invoice
const searchProducts = async (query: string) => {
  const response = await fetch(`/api/products/search?query=${query}&limit=20`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
};

// Check product availability
const checkAvailability = async (productId: string, quantity: number) => {
  const product = await fetch(`/api/products/${productId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());
  
  return {
    available: product.product.quantity_available >= quantity,
    availableQuantity: product.product.quantity_available,
    isLowStock: product.product.is_low_stock
  };
};
```

### Inventory Management

```typescript
// Adjust stock levels
const adjustStock = async (productId: string, adjustment: any) => {
  const response = await fetch(`/api/products/${productId}/stock-adjustment`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(adjustment)
  });
  return await response.json();
};

// Get reorder suggestions
const getReorderSuggestions = async () => {
  const response = await fetch('/api/products/reorder-suggestions', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
};
```

### Purchase Order Workflow

```typescript
// Create purchase order
const createPurchaseOrder = async (orderData: any) => {
  const response = await fetch('/api/purchase-orders', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  });
  return await response.json();
};

// Approve purchase order
const approvePurchaseOrder = async (poId: string, notes?: string) => {
  const response = await fetch(`/api/purchase-orders/${poId}/approve`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ notes })
  });
  return await response.json();
};
```

## Business Rules and Workflows

### Product Management Rules
- SKU must be unique within each business
- Products with `track_inventory=true` must have quantity tracking
- Negative inventory is allowed but generates low stock warnings
- Product deletion is soft delete - sets `is_active=false`

### Inventory Tracking Rules
- All stock movements create audit trail entries
- Reserved quantities are tracked separately from available quantities
- Available quantity = On hand quantity - Reserved quantity
- Low stock alerts trigger when quantity falls below reorder point

### Purchase Order Workflow
1. **Draft**: Initial creation, can be modified
2. **Pending Approval**: Awaiting management approval
3. **Approved**: Ready to send to supplier
4. **Sent**: Transmitted to supplier
5. **Confirmed**: Supplier has confirmed receipt
6. **Partially Received**: Some items received
7. **Received**: All items received
8. **Closed**: Purchase order completed

### Supplier Performance Tracking
- On-time delivery rate calculated automatically
- Quality scores can be manually updated
- Overall performance grade based on weighted metrics
- Historical performance data maintained for reporting

## Integration with Other Systems

### Estimates and Invoices
- Product availability checked during estimate/invoice creation
- Inventory reserved when estimates are converted to invoices
- Stock deducted when invoices are marked as delivered/completed

### Cost Management
- Supports FIFO, LIFO, and Weighted Average costing methods
- Landed costs can be allocated across purchase order items
- Cost basis updated automatically upon receiving inventory

### Multi-location Support
- Products can be tracked across multiple business locations
- Stock movements can specify source and destination locations
- Location-specific reorder points and max levels supported

## Notes

- All decimal values support up to 6 decimal places for precision
- Dates are in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- Currency amounts are stored as decimal values without currency symbols
- All endpoints support standard HTTP caching headers
- Rate limiting may apply based on subscription tier
- Bulk operations are available for high-volume data management 