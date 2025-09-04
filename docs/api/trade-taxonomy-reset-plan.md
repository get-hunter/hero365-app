# Trade Taxonomy Reset Plan - 10x Implementation

## Core Philosophy
Profile-first, Activity-driven. Everything else (services, booking forms, website pages) derives from Activities chosen under a Trade Profile. No duplicate trade enums, no branching logic per market.

## Data Model (Clean & Scalable)

### Trade Profiles
```sql
trade_profiles (
  slug text PRIMARY KEY,
  name text NOT NULL,
  synonyms text[],
  segments text CHECK (segments IN ('residential','commercial','both')),
  icon text,
  description text
)
```

### Activities  
```sql
trade_activities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  trade_slug text REFERENCES trade_profiles(slug),
  slug text UNIQUE NOT NULL,
  name text NOT NULL,
  synonyms text[],
  tags text[],
  default_booking_fields jsonb DEFAULT '[]',
  required_booking_fields jsonb DEFAULT '[]'
)
```

### Service Templates (Enhanced)
```sql
service_templates (
  -- Add columns:
  template_slug text UNIQUE NOT NULL,
  activity_slug text REFERENCES trade_activities(slug),
  pricing_config jsonb DEFAULT '{}',
  default_booking_fields jsonb DEFAULT '[]',
  required_booking_fields jsonb DEFAULT '[]',
  status text DEFAULT 'active' CHECK (status IN ('active','draft','deprecated')),
  version int DEFAULT 1,
  is_common bool DEFAULT false,
  is_emergency bool DEFAULT false
)
```

### Business (Simplified)
```sql
businesses (
  -- Add:
  primary_trade_slug text REFERENCES trade_profiles(slug),
  -- Remove: commercial_trades, residential_trades, commercial_services, residential_services
)
```

### Business Services (Enhanced)
```sql
business_services (
  -- Add:
  adopted_from_slug text,
  template_version int,
  pricing_config jsonb DEFAULT '{}'
)
```

## Onboarding Flow (Fast & Unambiguous)
1. Select `primary_trade_slug` (synonyms-supported search)
2. Pick 3–10 `trade_activities` for that profile  
3. Confirm business basics + service areas
4. Auto-adopt mapped `service_templates` for chosen activities
5. Done → website and booking-ready

## API Surface
### New Endpoints
- `GET /taxonomy/trades`
- `GET /taxonomy/trades/{slug}/activities`
- `POST /onboarding/start`
- `POST /onboarding/select-activities`
- `POST /services/adopt-template/by-slug`
- `POST /services/bulk-adopt-by-slug`
- `GET /onboarding/state`
- `POST /onboarding/complete`

### Keep Existing
- `GET /services/categories-with-services` (for website)
- `POST /services/custom` (for long-tail offers)

## Implementation Order
1. ✅ Save plan
2. 🔄 Create migrations + seeds
3. Update Business entity 
4. Create taxonomy repositories
5. Update service repositories
6. Create taxonomy routes
7. Create onboarding routes
8. Add adopt-by-slug endpoints
9. Regenerate OpenAPI
10. Test core flows

## Benefits
- Single source of truth for booking fields, templates, tech skills
- Versioned templates with safe evolution
- Idempotent onboarding (rerunnable)
- Clean website/booking integration
- No enum synchronization complexity
