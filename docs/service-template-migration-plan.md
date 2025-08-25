# Service Template System Migration Plan

## Overview
Migration plan to implement the new service template system that eliminates the need for each business to manually create common services.

## Migration Phases

### Phase 1: Database Schema & Seeding ✅
**Status**: Complete
- [x] Create service_categories table 
- [x] Create service_templates table
- [x] Create business_services table  
- [x] Create business_service_bundles table
- [x] Create service_template_adoptions table
- [x] Seed with common industry services (60+ templates)
- [x] Add proper indexes and RLS policies

**Files Created**:
- `supabase/migrations/20250125160000_create_service_templates.sql`
- `supabase/migrations/20250125170000_seed_service_templates.sql`

### Phase 2: Data Migration Script
**Status**: Pending

Create migration script to move existing data:

```sql
-- Migration script: 20250125180000_migrate_existing_products.sql
-- Move existing products table data to new business_services

-- 1. Map existing products to service templates where possible
WITH template_matches AS (
    SELECT 
        p.id as product_id,
        p.business_id,
        p.name,
        p.description,
        p.unit_price,
        p.is_service,
        p.category_id as old_category_id,
        -- Try to match to service templates by name similarity
        (SELECT st.id 
         FROM service_templates st 
         WHERE similarity(LOWER(p.name), LOWER(st.name)) > 0.6 
         ORDER BY similarity(LOWER(p.name), LOWER(st.name)) DESC 
         LIMIT 1) as template_id,
        -- Map to new categories based on business trade
        (SELECT sc.id 
         FROM service_categories sc 
         JOIN businesses b ON b.id = p.business_id
         WHERE sc.trade_types && COALESCE(b.residential_trades, b.commercial_trades)
         ORDER BY array_length(sc.trade_types, 1) DESC 
         LIMIT 1) as new_category_id
    FROM products p
    WHERE p.is_service = true OR p.product_type = 'service'
)
INSERT INTO business_services (
    business_id, template_id, category_id, name, description, 
    pricing_model, unit_price, is_active, is_featured, created_at
)
SELECT 
    tm.business_id,
    tm.template_id,
    COALESCE(tm.new_category_id, (SELECT id FROM service_categories WHERE slug = 'consultation' LIMIT 1)),
    tm.name,
    COALESCE(tm.description, 'Migrated from products table'),
    CASE 
        WHEN tm.unit_price = 0 THEN 'quote_required'
        ELSE 'fixed'
    END,
    tm.unit_price,
    true,
    false,
    now()
FROM template_matches tm;

-- 2. Track template adoptions
INSERT INTO service_template_adoptions (template_id, business_id, business_service_id, customizations)
SELECT 
    bs.template_id,
    bs.business_id,
    bs.id,
    jsonb_build_object(
        'custom_pricing', bs.unit_price != st.default_unit_price,
        'custom_description', bs.description != st.description,
        'migrated_from_products', true
    )
FROM business_services bs
JOIN service_templates st ON bs.template_id = st.id
WHERE bs.template_id IS NOT NULL;

-- 3. Create fallback category for unmapped services
INSERT INTO service_categories (name, slug, trade_types, category_type, description, sort_order)
VALUES ('Custom Services', 'custom-services', ARRAY['hvac', 'plumbing', 'electrical'], 'service_type', 'Business-specific custom services', 999)
ON CONFLICT (slug) DO NOTHING;
```

### Phase 3: API Development  
**Status**: Pending

Create new API endpoints:

#### Backend API Endpoints Needed:
1. **Service Template APIs**
   - `GET /api/v1/service-templates` - List templates by trade
   - `GET /api/v1/service-templates/{id}` - Get template details
   - `GET /api/v1/service-categories` - List categories

2. **Business Service APIs**  
   - `GET /api/v1/business/{id}/services` - List business services
   - `POST /api/v1/business/{id}/services/from-template` - Adopt template
   - `POST /api/v1/business/{id}/services/custom` - Create custom service
   - `PUT /api/v1/business/{id}/services/{service_id}` - Update service
   - `DELETE /api/v1/business/{id}/services/{service_id}` - Remove service

3. **Business Onboarding APIs**
   - `POST /api/v1/business/{id}/services/bulk-adopt` - Adopt multiple templates
   - `GET /api/v1/onboarding/recommended-services?trades=hvac,plumbing` - Get recommended services

#### Pydantic Models Needed:
```python
# app/domain/service_templates/models.py
class ServiceCategory(BaseModel):
    id: UUID
    name: str
    slug: str
    trade_types: List[str]
    category_type: str
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = 0

class ServiceTemplate(BaseModel):
    id: UUID
    category_id: UUID
    name: str
    description: str
    trade_types: List[str]
    service_type: str
    pricing_model: str
    default_unit_price: Optional[Decimal] = None
    price_range_min: Optional[Decimal] = None
    price_range_max: Optional[Decimal] = None
    unit_of_measure: str = "service"
    estimated_duration_hours: Optional[Decimal] = None
    tags: List[str] = []
    is_common: bool = False
    is_emergency: bool = False
    requires_license: bool = False
    skill_level: Optional[str] = None
    seasonal_demand: Optional[Dict] = None
    upsell_templates: List[UUID] = []

class BusinessService(BaseModel):
    id: UUID
    business_id: UUID
    template_id: Optional[UUID] = None
    category_id: UUID
    name: str
    description: Optional[str] = None
    pricing_model: str
    unit_price: Optional[Decimal] = None
    minimum_price: Optional[Decimal] = None
    unit_of_measure: str = "service"
    estimated_duration_hours: Optional[Decimal] = None
    is_active: bool = True
    is_featured: bool = False
    is_emergency: bool = False
    availability_schedule: Optional[Dict] = None
    service_areas: List[str] = []
    custom_fields: Dict = {}
    booking_settings: Dict = {}
```

### Phase 4: Business Logic Implementation
**Status**: Pending

#### Key Business Logic:
1. **Template Adoption**
   ```python
   def adopt_service_template(business_id: UUID, template_id: UUID, customizations: Dict = None):
       template = get_service_template(template_id)
       
       # Check if business already has this service
       existing = get_business_service_by_template(business_id, template_id)
       if existing:
           raise ValueError("Service already exists")
       
       # Create business service from template
       service_data = {
           'business_id': business_id,
           'template_id': template_id,
           'category_id': template.category_id,
           'name': customizations.get('name', template.name),
           'description': customizations.get('description', template.description),
           'pricing_model': template.pricing_model,
           'unit_price': customizations.get('unit_price', template.default_unit_price),
           'is_emergency': template.is_emergency,
           # Apply other customizations
       }
       
       business_service = create_business_service(service_data)
       
       # Track adoption
       track_template_adoption(template_id, business_id, business_service.id, customizations)
       
       return business_service
   ```

2. **Business Onboarding**
   ```python
   def setup_business_services(business_id: UUID, trade_types: List[str]):
       # Get common services for business trades
       common_templates = get_common_service_templates(trade_types)
       
       adopted_services = []
       for template in common_templates:
           if template.is_common:
               service = adopt_service_template(business_id, template.id)
               adopted_services.append(service)
       
       return adopted_services
   ```

3. **Website Service Categories**
   ```python
   def get_website_service_categories(business_id: UUID) -> List[ServiceCategory]:
       # Get categories that have active business services
       return (
           ServiceCategory.query
           .join(BusinessService, BusinessService.category_id == ServiceCategory.id)
           .filter(
               BusinessService.business_id == business_id,
               BusinessService.is_active == True
           )
           .distinct()
           .order_by(ServiceCategory.sort_order)
           .all()
       )
   ```

### Phase 5: Frontend Integration
**Status**: Pending  

#### Mobile App Changes:
1. **Onboarding Flow**
   - Show pre-selected common services for business trade
   - Allow customization of pricing and descriptions
   - Option to add custom services

2. **Service Management**
   - Browse service template catalog
   - One-click adopt templates with customizations
   - Manage active services and pricing

3. **Service Categories**
   - Use standardized categories for organization
   - Consistent icons and naming across businesses

### Phase 6: Website Generation Updates
**Status**: Pending

#### Dynamic Navigation:
```typescript
// Update professional-homepage.tsx to use standardized categories
function categorizeServices(services: Service[]) {
  // Use database categories instead of hardcoded logic
  return services.reduce((categories, service) => {
    const category = service.category;
    if (!categories[category.slug]) {
      categories[category.slug] = {
        name: category.name,
        slug: category.slug,
        icon: category.icon,
        services: []
      };
    }
    categories[category.slug].services.push(service);
    return categories;
  }, {});
}
```

#### Website Builder Integration:
- Use `business_services` table instead of `products`
- Generate navigation based on `service_categories`
- Show services grouped by standardized categories
- Support emergency services highlighting

### Phase 7: Testing & Validation
**Status**: Pending

#### Test Cases:
1. **Template System**
   - [ ] Service templates load correctly by trade
   - [ ] Template adoption creates business services
   - [ ] Customizations are preserved
   - [ ] Upsell recommendations work

2. **Business Onboarding**  
   - [ ] New HVAC business gets common HVAC services
   - [ ] Multi-trade business gets services for all trades
   - [ ] Custom services can be added
   - [ ] Pricing can be customized

3. **Website Generation**
   - [ ] Service categories appear in navigation
   - [ ] Services are grouped correctly
   - [ ] Emergency services are highlighted
   - [ ] Custom services appear properly

4. **Data Migration**
   - [ ] Existing products are mapped correctly
   - [ ] No data loss during migration
   - [ ] Service categories are assigned properly
   - [ ] Template matching works accurately

### Phase 8: Deployment Strategy
**Status**: Pending

#### Rollout Plan:
1. **Staging Deployment**
   - Deploy to staging environment
   - Run data migration on test data
   - Validate all functionality

2. **Production Migration**
   - Schedule maintenance window
   - Run database migrations
   - Deploy API changes
   - Update mobile app

3. **Gradual Rollout**
   - Enable for new businesses first
   - Migrate existing businesses in batches
   - Monitor for issues and performance

4. **Cleanup**
   - Remove old product-based logic
   - Update documentation
   - Train customer support

## Expected Benefits

### For Businesses:
- **5x Faster Onboarding**: Pre-populated services instead of manual creation
- **Consistent Branding**: Professional service descriptions and naming
- **Better Pricing**: Industry-standard pricing guidance
- **Upselling**: Automatic related service suggestions

### For Platform:
- **Better Analytics**: Track popular services across trades  
- **Easier Website Generation**: Standardized categories for navigation
- **Reduced Support**: Less confusion about service setup
- **Scalability**: Easy to add new trades and services

### For Customers:
- **Consistent Experience**: Similar services have similar names/descriptions
- **Better Discovery**: Standardized categorization helps find services
- **Professional Quality**: Higher quality service descriptions

## Success Metrics

1. **Onboarding Speed**: Reduce new business service setup from 2+ hours to <30 minutes
2. **Service Adoption**: 80%+ of new businesses use template services
3. **Website Quality**: 90%+ of websites have proper service categorization  
4. **Customer Satisfaction**: Reduce service-related support tickets by 50%
5. **Business Growth**: Increase average services per business by 40%

## Rollback Plan

If issues arise:
1. Disable new service template APIs
2. Fall back to original products table
3. Restore from database backup if necessary
4. Re-enable old business onboarding flow

The migration is designed to be backward-compatible during transition period.
