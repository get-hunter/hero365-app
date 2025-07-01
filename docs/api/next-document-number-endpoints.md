# Next Document Number API Endpoints

This document describes the API endpoints for getting the next available document numbers for estimates, quotes, and invoices.

## Overview

These endpoints allow clients to preview the next document number that will be assigned when creating a new estimate, quote, or invoice, without actually creating the document. This improves user experience by showing users what number their next document will have before they create it.

## Endpoints

### Get Next Estimate Number

**Endpoint:** `GET /api/estimates/next-number`

**Description:** Returns the next available estimate or quote number for the current business.

**Query Parameters:**
- `prefix` (optional, string): The prefix for the document number. Default: "EST"
- `document_type` (optional, string): Type of document - "estimate" or "quote". Default: "estimate"

**Response Schema:**
```json
{
  "next_number": "string",
  "prefix": "string", 
  "document_type": "string"
}
```

**Example Request:**
```bash
GET /api/estimates/next-number?prefix=EST&document_type=estimate
```

**Example Response:**
```json
{
  "next_number": "EST-000001",
  "prefix": "EST",
  "document_type": "estimate"
}
```

**Example Request for Quote:**
```bash
GET /api/estimates/next-number?prefix=QUO&document_type=quote
```

**Example Response:**
```json
{
  "next_number": "QUO-000001",
  "prefix": "QUO",
  "document_type": "quote"
}
```

### Get Next Invoice Number

**Endpoint:** `GET /api/invoices/next-number`

**Description:** Returns the next available invoice number for the current business.

**Query Parameters:**
- `prefix` (optional, string): The prefix for the invoice number. Default: "INV"

**Response Schema:**
```json
{
  "next_number": "string",
  "prefix": "string"
}
```

**Example Request:**
```bash
GET /api/invoices/next-number?prefix=INV
```

**Example Response:**
```json
{
  "next_number": "INV-000001",
  "prefix": "INV"
}
```

## Authentication & Authorization

Both endpoints require:
- Valid authentication token
- Business context (user must be member of a business)
- `view_projects` permission

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Document type must be 'estimate' or 'quote'"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

## Document Number Format

Document numbers follow the pattern: `PREFIX-XXXXXX` where:
- `PREFIX` is the document type prefix (EST, QUO, INV, etc.)
- `XXXXXX` is a 6-digit zero-padded sequential number per business

Examples:
- `EST-000001` (first estimate)
- `QUO-000001` (first quote)
- `INV-000001` (first invoice)
- `EST-000002` (second estimate)

## Usage Examples

### Mobile App Integration

```typescript
// Get next estimate number
const getNextEstimateNumber = async () => {
  const response = await fetch('/api/estimates/next-number', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.next_number; // "EST-000001"
};

// Get next quote number
const getNextQuoteNumber = async () => {
  const response = await fetch('/api/estimates/next-number?prefix=QUO&document_type=quote', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.next_number; // "QUO-000001"
};

// Get next invoice number
const getNextInvoiceNumber = async () => {
  const response = await fetch('/api/invoices/next-number', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.next_number; // "INV-000001"
};
```

### Form Pre-population

These endpoints are particularly useful for:

1. **Form Display**: Show the document number field pre-populated with the next available number
2. **User Confirmation**: Allow users to see what number their document will have before creating it
3. **Numbering Validation**: Ensure users understand the numbering sequence
4. **Preview Mode**: Display document previews with the actual number that will be assigned

## Notes

- Document numbers are generated sequentially per business
- Each business has its own numbering sequence
- Numbers are not reserved by calling these endpoints - they only preview what the next number would be
- The actual number assignment happens when the document is created
- If multiple users are creating documents simultaneously, the actual assigned number may differ from the previewed number
- Numbers are unique within each business and document type combination 