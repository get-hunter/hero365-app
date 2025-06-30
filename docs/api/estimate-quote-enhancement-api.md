# Estimate vs Quote Document Type Enhancement API

## Overview

The Hero365 platform now supports distinguishing between **Estimates** and **Quotes** as different document types. This enhancement addresses the business need for contractors to provide both preliminary pricing (estimates) and firm offers (quotes) to their clients.

## Business Context

### Estimates vs Quotes

| Aspect | Estimate | Quote |
|--------|----------|-------|
| **Purpose** | Rough approximation of costs | Formal offer to provide specific services |
| **Legal Status** | Non-binding, subject to change | Binding commitment when accepted |
| **Precision** | Generally within a range (±10-20%) | Exact pricing for defined scope |
| **Usage** | Initial discussions, budgeting, feasibility | Final negotiations, contract basis |
| **Client Expectation** | Understand ballpark costs | Firm commitment to pricing |
| **Flexibility** | Can be revised as project details evolve | Changes require formal amendments |

### When Clients Request Each Type

**Clients Request Estimates When:**
- Exploring project feasibility  
- Need rough costs for financial planning
- Comparison shopping with multiple contractors
- Project details aren't fully defined
- Seeking internal management approval

**Clients Request Quotes When:**
- Ready to commit with well-defined scope
- Formal procurement processes require quotes
- Need binding pricing for agreements
- Legal/organizational requirements
- Ready to select a contractor

## API Changes

### New Document Type Field

All estimate-related endpoints now support a `document_type` field:

```typescript
interface DocumentType {
  estimate: "estimate"  // Preliminary pricing, non-binding
  quote: "quote"       // Firm offer, binding when accepted
}
```

### Enhanced Estimate Creation

**Endpoint**: `POST /api/v1/estimates`

**New Request Body Structure**:
```json
{
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Kitchen Renovation Project", 
  "document_type": "estimate",  // NEW FIELD
  "description": "Complete kitchen renovation including cabinets and appliances",
  "line_items": [
    {
      "description": "Kitchen cabinet installation",
      "quantity": 1,
      "unit_price": 5000.00,
      "unit": "project"
    }
  ],
  "currency": "USD",
  "tax_rate": 8.5,
  "valid_until": "2024-03-15T00:00:00Z"
}
```

**Enhanced Response Structure**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "business_id": "550e8400-e29b-41d4-a716-446655440005",
  "estimate_number": "EST-000001",  // or "QUO-000001" for quotes
  "document_type": "estimate",       // NEW FIELD
  "document_type_display": "Estimate",  // NEW FIELD
  "status": "draft",
  "title": "Kitchen Renovation Project",
  "total_amount": 5425.00,
  "created_at": "2024-02-01T10:00:00Z"
}
```

### Document Number Prefixes

The system automatically generates appropriate prefixes based on document type:

- **Estimates**: `EST-XXXXXX` (e.g., EST-000001)
- **Quotes**: `QUO-XXXXXX` (e.g., QUO-000001)

Each document type maintains its own sequential numbering within each business.

### Search and Filtering

**Enhanced Search Endpoint**: `POST /api/v1/estimates/search`

```json
{
  "document_type": "quote",  // NEW FILTER
  "status": "sent",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "min_amount": 1000.00,
  "max_amount": 10000.00,
  "created_from": "2024-01-01T00:00:00Z",
  "created_to": "2024-12-31T23:59:59Z"
}
```

**List Endpoint**: `GET /api/v1/estimates`

New query parameter:
```
GET /api/v1/estimates?document_type=quote&status=sent&limit=50
```

### Status Management

Status transitions apply to both document types but may have different business implications:

**Estimate Status Flow**:
```
draft → sent → viewed → (approved/rejected/expired)
```

**Quote Status Flow**:
```
draft → sent → viewed → (approved/rejected/expired) → converted
```

**Note**: When a quote is approved, it typically becomes a binding agreement and should be converted to an invoice promptly.

## Templates and Branding

### Document-Specific Templates

The template system supports different styling and content based on document type:

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440003",
  "document_type": "quote",
  "template_variables": {
    "disclaimer_text": "This quote is valid for 30 days and constitutes a binding offer upon acceptance.",
    "terms_emphasis": "high"
  }
}
```

### Recommended Template Differences

**Estimate Templates Should Include**:
- "This is a preliminary estimate"
- "Final pricing may vary based on actual conditions"
- "Not a binding commitment"
- Ranges or "approximately" language

**Quote Templates Should Include**:
- "This quote constitutes a firm offer"
- "Valid until [date]"
- "Binding upon acceptance"
- Precise pricing and terms

## Conversion Workflows

### Estimate to Quote Conversion

**Endpoint**: `POST /api/v1/estimates/{estimate_id}/convert-to-quote`

```json
{
  "title": "Updated title if needed",
  "valid_until": "2024-03-15T00:00:00Z",
  "notes": "Converted from preliminary estimate after scope clarification"
}
```

**Response**: Creates a new quote document with the same line items but updated terms and disclaimers.

### Quote to Invoice Conversion

**Endpoint**: `POST /api/v1/estimates/{quote_id}/convert-to-invoice`

```json
{
  "advance_payment_amount": 2500.00,
  "due_date": "2024-04-15T00:00:00Z",
  "payment_terms": "Net 30"
}
```

## Analytics and Reporting

### Enhanced Analytics

**Endpoint**: `GET /api/v1/estimates/analytics/overview`

**Enhanced Response**:
```json
{
  "estimates": {
    "total_count": 45,
    "total_value": 125000.00,
    "average_value": 2777.78,
    "conversion_rate_to_quotes": 65.5
  },
  "quotes": {
    "total_count": 28,
    "total_value": 98500.00,
    "average_value": 3517.86,
    "acceptance_rate": 78.6,
    "conversion_rate_to_invoices": 85.2
  },
  "overall_metrics": {
    "estimate_to_invoice_conversion": 55.4,
    "pipeline_health": "strong"
  }
}
```

### Document Type Breakdown

**Endpoint**: `GET /api/v1/estimates/analytics/by-document-type`

```json
{
  "date_range": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-12-31T23:59:59Z"
  },
  "breakdown": {
    "estimate": {
      "count": 156,
      "total_value": 450000.00,
      "avg_value": 2884.62,
      "conversion_to_quotes": 42,
      "conversion_to_invoices": 18
    },
    "quote": {
      "count": 89,
      "total_value": 387500.00,
      "avg_value": 4352.81,
      "acceptance_rate": 76.4,
      "conversion_to_invoices": 68
    }
  }
}
```

## Mobile App Implementation

### UI/UX Considerations

**Document Type Selection**:
```swift
// iOS Swift Example
enum DocumentType: String, CaseIterable {
    case estimate = "estimate"
    case quote = "quote"
    
    var displayName: String {
        switch self {
        case .estimate: return "Estimate"
        case .quote: return "Quote"
        }
    }
    
    var description: String {
        switch self {
        case .estimate: return "Preliminary pricing, subject to change"
        case .quote: return "Firm offer, binding when accepted"
        }
    }
}
```

**Visual Distinctions**:
- **Estimates**: Blue theme, "PRELIMINARY" watermark
- **Quotes**: Green theme, "FIRM OFFER" watermark
- Different icons in lists and cards
- Status badges reflect document type context

### Document Creation Flow

```swift
struct DocumentTypeSelectionView: View {
    var body: some View {
        VStack(spacing: 20) {
            DocumentTypeCard(
                type: .estimate,
                title: "Create Estimate",
                subtitle: "Preliminary pricing for planning",
                icon: "doc.text.below.ecg"
            )
            
            DocumentTypeCard(
                type: .quote,
                title: "Create Quote", 
                subtitle: "Firm offer ready for acceptance",
                icon: "doc.text.fill"
            )
        }
    }
}
```

## Business Logic Examples

### Validation Rules

**Document Type Specific Validations**:

```typescript
interface DocumentValidation {
  estimate: {
    // More flexible validation
    line_items: { min: 1 }
    valid_until: { required: false }
    terms: { binding_language: "forbidden" }
  }
  quote: {
    // Stricter validation
    line_items: { min: 1, detailed_descriptions: true }
    valid_until: { required: true, min_days: 7 }
    terms: { binding_language: "required" }
  }
}
```

### Status Transition Rules

```typescript
const statusTransitions = {
  estimate: {
    draft: ["sent", "cancelled"],
    sent: ["viewed", "cancelled"],
    viewed: ["approved", "rejected", "expired"],
    approved: ["converted"], // Can convert to quote or invoice
    rejected: ["draft"], // Can revise
    expired: ["draft"] // Can revise
  },
  quote: {
    draft: ["sent", "cancelled"],
    sent: ["viewed", "cancelled"], 
    viewed: ["approved", "rejected", "expired"],
    approved: ["converted"], // Should convert to invoice
    rejected: [], // Final state
    expired: [] // Final state
  }
}
```

## Error Handling

### Document Type Validation Errors

```json
{
  "error": "ValidationError",
  "message": "Invalid document configuration",
  "details": {
    "document_type": "quote",
    "violations": [
      {
        "field": "valid_until",
        "error": "Quotes must have a valid until date"
      },
      {
        "field": "terms",
        "error": "Quotes must include binding language in terms"
      }
    ]
  }
}
```

### Business Rule Violations

```json
{
  "error": "BusinessRuleViolation", 
  "message": "Cannot convert expired quote",
  "details": {
    "document_type": "quote",
    "status": "expired",
    "rule": "Expired quotes cannot be converted to invoices"
  }
}
```

## Migration Guide

### Existing Data

All existing estimates will automatically be assigned `document_type: "estimate"` during the migration. No data loss will occur.

### API Compatibility

- **Backward Compatible**: Existing API calls without `document_type` will default to "estimate"
- **Optional Field**: `document_type` is optional in creation requests
- **Response Enhancement**: All responses now include `document_type` and `document_type_display`

### Client Updates Required

1. **Update Models**: Add `document_type` field to estimate models
2. **UI Updates**: Implement document type selection and visual distinctions
3. **Validation**: Update client-side validation for document-specific rules
4. **Analytics**: Update analytics dashboards to show document type breakdown

## Best Practices

### When to Use Each Type

**Use Estimates For**:
- Initial client inquiries
- Project feasibility discussions  
- Budget planning conversations
- Scope definition phases
- Competitive bidding early stages

**Use Quotes For**:
- Final pricing presentations
- Formal proposals
- Contract negotiations
- Well-defined project scopes
- Ready-to-proceed situations

### Workflow Recommendations

1. **Start with Estimates**: Begin client relationships with estimates for initial discussions
2. **Convert to Quotes**: Once scope is defined, convert estimates to quotes
3. **Set Clear Expectations**: Communicate document type implications to clients
4. **Use Appropriate Templates**: Ensure legal disclaimers match document type
5. **Track Conversions**: Monitor estimate→quote→invoice conversion rates

## Support and Testing

### Testing Endpoints

Use the development environment to test document type functionality:

```bash
# Create estimate
curl -X POST https://api-dev.hero365.com/v1/estimates \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_type": "estimate", "title": "Test Estimate", "contact_id": "..."}'

# Create quote  
curl -X POST https://api-dev.hero365.com/v1/estimates \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_type": "quote", "title": "Test Quote", "contact_id": "..."}'
```

### Common Questions

**Q: Can I change an estimate to a quote?**
A: Use the conversion endpoint to create a new quote from an estimate rather than updating the document type directly.

**Q: Do estimates and quotes share the same numbering sequence?**  
A: No, each document type maintains its own sequential numbering (EST-XXXXXX vs QUO-XXXXXX).

**Q: What happens to existing estimates?**
A: All existing estimates retain their functionality and are automatically assigned `document_type: "estimate"`.

**Q: Can I filter analytics by document type?**
A: Yes, all analytics endpoints support filtering and breakdown by document type.

## Implementation Timeline

This enhancement is available immediately in:
- ✅ Backend API (all endpoints updated)
- ✅ Database schema (migration applied)
- ✅ Documentation (this document)

**Mobile App Updates Required**:
- Update estimate models to include `document_type`
- Implement document type selection UI
- Add visual distinctions for estimates vs quotes
- Update validation logic

**Recommended Rollout**:
1. **Phase 1**: Backend deployment (complete)
2. **Phase 2**: Mobile app updates (estimate: 1-2 weeks)
3. **Phase 3**: User training and documentation
4. **Phase 4**: Analytics dashboard enhancements 