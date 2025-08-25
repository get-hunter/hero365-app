# Service Template Data Model

## Overview
New data model to support service templates and business customizations, eliminating the need for each professional to manually create common services.

## Key Concepts

1. **Service Templates**: Pre-defined industry-standard services
2. **Business Services**: Business instances with customizations  
3. **Service Categories**: Standardized categories by trade
4. **Trade-Specific Catalogs**: Different service sets per trade type

## New Tables

### 1. service_categories
Standardized service categories across trades.

```sql
CREATE TABLE service_categories (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(100) NOT NULL,
    description text,
    slug varchar(100) NOT NULL,
    trade_types text[] NOT NULL, -- ['hvac', 'plumbing', 'electrical']
    category_type varchar(50) NOT NULL CHECK (category_type IN ('equipment', 'service_type', 'specialization')),
    icon varchar(100), -- Icon name for UI
    parent_id uuid REFERENCES service_categories(id),
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Example categories:
-- Air Conditioning (hvac)
-- Heating (hvac) 
-- Installation (hvac, plumbing, electrical)
-- Maintenance (hvac, plumbing, electrical)
-- Emergency Service (hvac, plumbing, electrical)
```

### 2. service_templates  
Pre-defined industry services that businesses can adopt.

```sql
CREATE TABLE service_templates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id uuid NOT NULL REFERENCES service_categories(id),
    name varchar(200) NOT NULL,
    description text NOT NULL,
    trade_types text[] NOT NULL, -- Which trades offer this service
    service_type varchar(50) NOT NULL CHECK (service_type IN ('product', 'service', 'maintenance_plan')),
    pricing_model varchar(50) NOT NULL CHECK (pricing_model IN ('fixed', 'hourly', 'per_unit', 'quote_required')),
    default_unit_price numeric(10,2),
    unit_of_measure varchar(50) DEFAULT 'service',
    estimated_duration_hours numeric(4,2),
    tags text[], -- ['emergency', 'seasonal', 'diagnostic', 'installation']
    is_common boolean DEFAULT false, -- Most businesses offer this
    is_emergency boolean DEFAULT false,
    prerequisites text[], -- Other services that should be offered first
    upsell_templates uuid[], -- Related services to suggest
    metadata jsonb DEFAULT '{}',
    usage_count integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Example templates:
-- "AC Repair & Diagnostics" - hvac, quote_required, emergency
-- "Furnace Installation" - hvac, quote_required  
-- "24/7 Emergency Service" - hvac/plumbing/electrical, hourly, emergency
-- "Annual HVAC Maintenance" - hvac, fixed, maintenance_plan
```

### 3. business_services
Business instances of services (from templates or custom).

```sql  
CREATE TABLE business_services (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES businesses(id),
    template_id uuid REFERENCES service_templates(id), -- null for custom services
    category_id uuid NOT NULL REFERENCES service_categories(id),
    name varchar(200) NOT NULL,
    description text,
    pricing_model varchar(50) NOT NULL,
    unit_price numeric(10,2),
    minimum_price numeric(10,2),
    unit_of_measure varchar(50) DEFAULT 'service',
    estimated_duration_hours numeric(4,2),
    is_active boolean DEFAULT true,
    is_featured boolean DEFAULT false,
    is_emergency boolean DEFAULT false,
    availability_schedule jsonb, -- When this service is available
    service_areas text[], -- Geographic areas for this service
    custom_fields jsonb DEFAULT '{}',
    booking_settings jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);
```

### 4. business_service_bundles
Group related services into packages.

```sql
CREATE TABLE business_service_bundles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id uuid NOT NULL REFERENCES businesses(id),
    name varchar(200) NOT NULL,
    description text,
    service_ids uuid[] NOT NULL, -- References to business_services
    bundle_price numeric(10,2),
    discount_amount numeric(10,2),
    discount_percentage numeric(5,2),
    is_active boolean DEFAULT true,
    is_seasonal boolean DEFAULT false,
    valid_from date,
    valid_until date,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);
```

## Migration Strategy

### Phase 1: Create New Tables
1. Create service_categories with standard categories
2. Create service_templates with common services  
3. Create business_services table
4. Seed with industry-standard data

### Phase 2: Data Migration
1. Map existing products to service templates where possible
2. Create business_services records from existing products
3. Preserve custom pricing and descriptions
4. Mark truly custom services (template_id = null)

### Phase 3: Update APIs & Logic
1. Modify service creation to use templates
2. Update website generation to use standardized categories
3. Add business onboarding with template selection
4. Build service template management UI

## Benefits

1. **Faster Onboarding**: New businesses get pre-populated services for their trade
2. **Consistent Categories**: Standardized service organization for website generation
3. **Easy Customization**: Templates can be customized per business
4. **Better Analytics**: Track popular services across platform
5. **Upselling Opportunities**: Template system suggests related services
6. **Maintenance Efficiency**: Update service descriptions across all businesses

## Business Logic Examples

### New Business Onboarding
```python
# When a new HVAC business signs up
hvac_templates = get_service_templates_by_trade('hvac', is_common=True)
for template in hvac_templates:
    create_business_service(
        business_id=new_business.id,
        template_id=template.id,
        # Use template defaults, business can customize later
        unit_price=template.default_unit_price
    )
```

### Website Service Categories
```python
# Generate navigation for professional website
def get_service_categories_for_business(business_id):
    return ServiceCategory.query.join(
        BusinessService.category_id == ServiceCategory.id
    ).filter(
        BusinessService.business_id == business_id,
        BusinessService.is_active == True
    ).distinct().all()
```
