# Template Management System - Implementation Plan

## Overview
This document outlines the implementation plan for expanding the existing template system to support the comprehensive template management requirements from the mobile app.

## Current State Analysis

### What We Already Have ✅
1. **Database Schema**:
   - `document_templates` table with most required fields
   - `business_branding` table for centralized branding
   - Support for multiple document types (estimate, invoice, contract, etc.)
   - System templates support (`is_system_template`)
   - Default template management (`is_default`, unique constraint)
   - Usage tracking (`usage_count`, `last_used_date`)
   - Sections configuration in JSONB format
   - Template versioning (`version` field)

2. **Domain Layer**:
   - `DocumentTemplate` entity with business logic
   - `DocumentTemplateFactory` for creating type-specific templates
   - `BusinessBranding` entity for branding configuration
   - Support for template types (professional, minimal, creative, etc.)

3. **Application Layer**:
   - `ManageDocumentTemplatesUseCase` with CRUD operations
   - Methods for default template management
   - Template cloning functionality
   - Template search and filtering

4. **API Layer**:
   - Basic CRUD endpoints (`GET`, `POST`, `PUT`)
   - Template filtering by document type
   - Separate endpoints for estimates/invoices

5. **Repository Layer**:
   - `DocumentTemplateRepository` interface
   - Implementation for Supabase

## What Needs to Be Added 🚀

### Phase 1: Enhanced Database Schema (Week 1)

#### 1.1 Template Layout Entity
```sql
CREATE TABLE public.template_layouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    header_style VARCHAR(50) CHECK (header_style IN ('standard', 'bold', 'minimal', 'centered', 'split')),
    items_table_style VARCHAR(50) CHECK (items_table_style IN ('standard', 'detailed', 'simple', 'creative', 'service', 'consulting')),
    footer_style VARCHAR(50) CHECK (footer_style IN ('simple', 'detailed', 'none')),
    logo_position VARCHAR(50) CHECK (logo_position IN ('top_left', 'top_center', 'top_right', 'header_left', 'header_right')),
    page_size VARCHAR(20) CHECK (page_size IN ('a4', 'letter', 'legal')),
    section_spacing DECIMAL(5,2),
    margins JSONB DEFAULT '{"top": 20, "left": 20, "right": 20, "bottom": 20}'::JSONB,
    column_widths JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.2 Template Color Scheme Entity
```sql
CREATE TABLE public.template_color_schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    name VARCHAR(100),
    primary_color VARCHAR(7) CHECK (primary_color ~ '^#[0-9A-Fa-f]{6}$'),
    secondary_color VARCHAR(7) CHECK (secondary_color ~ '^#[0-9A-Fa-f]{6}$'),
    accent_color VARCHAR(7) CHECK (accent_color ~ '^#[0-9A-Fa-f]{6}$'),
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    surface_color VARCHAR(7),
    text_primary_color VARCHAR(7) DEFAULT '#000000',
    text_secondary_color VARCHAR(7) DEFAULT '#6B7280',
    border_color VARCHAR(7) DEFAULT '#E5E7EB',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.3 Template Typography Entity
```sql
CREATE TABLE public.template_typography (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    title_font JSONB DEFAULT '{"name": "System", "size": 28, "weight": "bold"}'::JSONB,
    header_font JSONB DEFAULT '{"name": "System", "size": 14, "weight": "semibold"}'::JSONB,
    body_font JSONB DEFAULT '{"name": "System", "size": 11, "weight": "regular"}'::JSONB,
    caption_font JSONB DEFAULT '{"name": "System", "size": 9, "weight": "regular"}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.4 Template Business Rules Entity
```sql
CREATE TABLE public.template_business_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    show_invoice_number BOOLEAN DEFAULT TRUE,
    show_due_date BOOLEAN DEFAULT TRUE,
    show_tax_breakdown BOOLEAN DEFAULT TRUE,
    show_payment_terms BOOLEAN DEFAULT TRUE,
    show_notes BOOLEAN DEFAULT TRUE,
    default_payment_terms VARCHAR(50) CHECK (default_payment_terms IN ('immediate', 'net_15', 'net_30', 'net_60', 'net_90', 'custom')),
    currency_format VARCHAR(10) CHECK (currency_format IN ('usd', 'eur', 'gbp', 'cad', 'aud')),
    date_format VARCHAR(20) CHECK (date_format IN ('mm_dd_yyyy', 'dd_mm_yyyy', 'yyyy_mm_dd', 'month_day_year')),
    tax_calculation VARCHAR(20) CHECK (tax_calculation IN ('inclusive', 'exclusive')),
    rounding_rules JSONB DEFAULT '{"decimal_places": 2, "rounding_mode": "half_up"}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.5 Template Custom Fields Entity
```sql
CREATE TABLE public.template_custom_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.document_templates(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(20) CHECK (field_type IN ('text', 'number', 'currency', 'date', 'email', 'phone', 'address', 'multiline')),
    default_value TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,
    placeholder TEXT,
    validation_rules JSONB,
    display_order INTEGER,
    is_global BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Phase 2: Built-in Templates Migration (Week 2)

#### 2.1 Create Migration Script for Built-in Templates
- Extract hardcoded templates from mobile app
- Create SQL inserts for 12 built-in templates:
  - Professional (3 templates)
  - Minimal (2 templates)
  - Creative (2 templates)
  - Corporate (1 template)
  - Service (1 template)
  - Consulting (1 template)
  - Modern (1 template)
  - Classic (1 template)

#### 2.2 Template Data Structure
```json
{
  "name": "Classic Professional",
  "category": "professional",
  "colorScheme": {
    "primary": "#2563EB",
    "secondary": "#64748B",
    "accent": "#F1F5F9",
    "background": "#FFFFFF",
    "text": "#1E293B"
  },
  "typography": {
    "titleFont": {"name": "System", "size": 28, "weight": "bold"},
    "headerFont": {"name": "System", "size": 14, "weight": "semibold"},
    "bodyFont": {"name": "System", "size": 11, "weight": "regular"}
  },
  "layout": {
    "headerStyle": "standard",
    "itemsTableStyle": "standard",
    "footerStyle": "detailed",
    "logoPosition": "top_left"
  }
}
```

### Phase 3: Enhanced Domain Entities (Week 2)

#### 3.1 Extend DocumentTemplate Entity
```python
# Add new properties for detailed configuration
class DocumentTemplate(BaseModel):
    # Existing fields...
    
    # New relationships
    layout: Optional[TemplateLayout] = None
    color_scheme: Optional[TemplateColorScheme] = None
    typography: Optional[TemplateTypography] = None
    business_rules: Optional[TemplateBusinessRules] = None
    custom_fields: List[TemplateCustomField] = Field(default_factory=list)
    
    # Enhanced methods
    def apply_branding(self, branding: BusinessBranding) -> 'DocumentTemplate':
        """Apply business branding to template"""
        pass
    
    def generate_preview(self) -> dict:
        """Generate template preview data"""
        pass
    
    def validate_for_document_type(self) -> bool:
        """Validate template is appropriate for its document type"""
        pass
```

#### 3.2 Create New Domain Entities
- `TemplateLayout`
- `TemplateColorScheme`
- `TemplateTypography`
- `TemplateBusinessRules`
- `TemplateCustomField`

### Phase 4: Enhanced Use Cases (Week 3)

#### 4.1 Template Analytics Use Case
```python
class TemplateAnalyticsUseCase:
    async def get_template_usage_stats(self, template_id: UUID) -> TemplateUsageStats
    async def get_popular_templates(self, business_id: UUID) -> List[TemplateWithStats]
    async def get_template_conversion_rate(self, template_id: UUID) -> float
```

#### 4.2 Template Bulk Operations Use Case
```python
class TemplateBulkOperationsUseCase:
    async def duplicate_template(self, template_id: UUID) -> DocumentTemplate
    async def import_templates(self, templates_data: List[dict]) -> List[DocumentTemplate]
    async def export_templates(self, template_ids: List[UUID]) -> dict
```

#### 4.3 Template Preview Use Case
```python
class TemplatePreviewUseCase:
    async def generate_preview(self, template_id: UUID, sample_data: dict) -> PreviewData
    async def generate_pdf_preview(self, template_id: UUID) -> bytes
```

### Phase 5: Enhanced API Endpoints (Week 3)

#### 5.1 New Endpoints
```python
# Template Operations
PUT    /api/v1/templates/{id}/default              # Set as default
GET    /api/v1/templates/default/{document_type}   # Get default template
POST   /api/v1/templates/{id}/duplicate            # Duplicate template
POST   /api/v1/templates/{id}/preview              # Generate preview
GET    /api/v1/templates/categories                # List categories
GET    /api/v1/templates/built-in                  # Get built-in templates

# Template Analytics
GET    /api/v1/templates/{id}/usage                # Usage statistics
GET    /api/v1/templates/analytics                 # Analytics dashboard
GET    /api/v1/templates/popular                   # Most used templates

# Template Bulk Operations
POST   /api/v1/templates/bulk/import               # Import templates
POST   /api/v1/templates/bulk/export               # Export templates
```

#### 5.2 Enhanced Existing Endpoints
- Add pagination to list endpoints
- Add search and filtering capabilities
- Add sorting options (by usage, date, name)

### Phase 6: Repository Implementation (Week 4)

#### 6.1 Enhanced Repository Methods
```python
class SupabaseDocumentTemplateRepository:
    # Template Layout Methods
    async def get_template_layout(self, template_id: UUID) -> TemplateLayout
    async def update_template_layout(self, template_id: UUID, layout: TemplateLayout) -> TemplateLayout
    
    # Color Scheme Methods
    async def get_template_color_scheme(self, template_id: UUID) -> TemplateColorScheme
    async def update_template_color_scheme(self, template_id: UUID, scheme: TemplateColorScheme) -> TemplateColorScheme
    
    # Typography Methods
    async def get_template_typography(self, template_id: UUID) -> TemplateTypography
    async def update_template_typography(self, template_id: UUID, typography: TemplateTypography) -> TemplateTypography
    
    # Business Rules Methods
    async def get_template_business_rules(self, template_id: UUID) -> TemplateBusinessRules
    async def update_template_business_rules(self, template_id: UUID, rules: TemplateBusinessRules) -> TemplateBusinessRules
    
    # Custom Fields Methods
    async def get_template_custom_fields(self, template_id: UUID) -> List[TemplateCustomField]
    async def add_template_custom_field(self, template_id: UUID, field: TemplateCustomField) -> TemplateCustomField
    async def update_template_custom_field(self, field_id: UUID, field: TemplateCustomField) -> TemplateCustomField
    async def delete_template_custom_field(self, field_id: UUID) -> bool
```

### Phase 7: Mobile App Integration (Week 4)

#### 7.1 API Documentation
- Create comprehensive API documentation for mobile app
- Document response formats and data structures
- Provide example requests and responses

#### 7.2 Sync Strategy
```python
# Template sync endpoint for mobile app
GET /api/v1/templates/sync?last_sync={timestamp}
# Returns templates modified since last sync

# Template cache validation
HEAD /api/v1/templates/{id}/version
# Returns ETag for cache validation
```

### Phase 8: Testing & Validation (Week 5)

#### 8.1 Unit Tests
- Test template creation with all configurations
- Test default template management
- Test template inheritance from branding
- Test template validation rules

#### 8.2 Integration Tests
- Test complete template lifecycle
- Test template usage in document creation
- Test template analytics tracking
- Test mobile app sync scenarios

#### 8.3 Performance Tests
- Test template listing with pagination
- Test template search performance
- Test bulk operations performance

## Implementation Order

### Week 1: Database Schema
1. Create migration for new template tables
2. Update existing `document_templates` table if needed
3. Create indexes for performance
4. Set up foreign key constraints

### Week 2: Domain & Entities
1. Create new domain entities
2. Extend existing DocumentTemplate entity
3. Implement business logic methods
4. Create factory methods for built-in templates

### Week 3: Use Cases & Business Logic
1. Implement template analytics use case
2. Implement bulk operations use case
3. Implement preview generation use case
4. Extend existing use cases

### Week 4: API & Repository
1. Implement new API endpoints
2. Enhance existing endpoints
3. Implement repository methods
4. Create API documentation

### Week 5: Testing & Deployment
1. Write comprehensive tests
2. Performance optimization
3. Load built-in templates
4. Deploy to production

## Migration Strategy

### Step 1: Prepare Database
```sql
-- Run migrations to create new tables
-- This won't affect existing functionality
```

### Step 2: Load Built-in Templates
```sql
-- Insert built-in templates
-- Set "Classic Professional" as default
```

### Step 3: Migrate Existing Data
```sql
-- Update existing templates to new structure
-- Ensure backward compatibility
```

### Step 4: Update Application Code
- Deploy new domain entities
- Deploy new use cases
- Deploy new API endpoints

### Step 5: Mobile App Updates
- Update mobile app to use new API
- Implement template caching
- Add offline fallback

## Success Criteria

1. ✅ All 12 built-in templates loaded and accessible
2. ✅ Default template management working correctly
3. ✅ Template inheritance from branding functional
4. ✅ Mobile app successfully using backend templates
5. ✅ Template analytics tracking usage
6. ✅ Performance meets requirements (< 100ms response time)
7. ✅ All tests passing
8. ✅ Documentation complete

## Risk Mitigation

1. **Data Migration Risk**: Keep backup of existing templates
2. **Performance Risk**: Implement caching at multiple levels
3. **Mobile App Risk**: Maintain fallback to local templates
4. **Compatibility Risk**: Version API endpoints properly

## Next Steps

1. Review and approve implementation plan
2. Set up development environment
3. Begin Phase 1: Database Schema
4. Create detailed technical specifications for each phase
