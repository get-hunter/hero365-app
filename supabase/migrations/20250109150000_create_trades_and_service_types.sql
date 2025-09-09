-- =============================================
-- TRADES AND SERVICE TYPES NORMALIZATION
-- =============================================
-- Create canonical trades table and service types
-- Improve business_services with proper foreign keys
-- Normalize service_areas schema

-- =============================================
-- TRADES TABLE (Canonical Trade Categories)
-- =============================================

CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Trade Identity
    slug VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    
    -- Classification
    market_type VARCHAR(20) NOT NULL CHECK (market_type IN ('residential', 'commercial', 'both')),
    
    -- Display Properties
    description TEXT,
    icon VARCHAR(50), -- Icon identifier for UI
    color VARCHAR(7), -- Hex color code
    display_order INTEGER DEFAULT 0,
    
    -- SEO Properties
    meta_title VARCHAR(200),
    meta_description VARCHAR(300),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- SERVICE TYPES TABLE (Install, Repair, etc.)
-- =============================================

CREATE TABLE service_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Type Identity
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    
    -- Properties
    description TEXT,
    is_emergency BOOLEAN DEFAULT FALSE,
    typical_duration_hours DECIMAL(4,2) DEFAULT 2.0,
    
    -- Display
    display_order INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- INSERT CANONICAL TRADES
-- =============================================

INSERT INTO trades (slug, name, display_name, market_type, description, icon, color, display_order) VALUES
-- Residential Trades
('hvac', 'hvac', 'HVAC', 'residential', 'Heating, ventilation, and air conditioning services', 'thermometer', '#3B82F6', 1),
('plumbing', 'plumbing', 'Plumbing', 'both', 'Plumbing installation, repair, and maintenance', 'wrench', '#0EA5E9', 2),
('electrical', 'electrical', 'Electrical', 'both', 'Electrical installation, repair, and maintenance', 'zap', '#F59E0B', 3),
('roofing', 'roofing', 'Roofing', 'both', 'Roof installation, repair, and maintenance', 'home', '#EF4444', 4),
('chimney', 'chimney', 'Chimney', 'residential', 'Chimney cleaning, repair, and maintenance', 'flame', '#DC2626', 5),
('garage-door', 'garage-door', 'Garage Door', 'residential', 'Garage door installation and repair', 'square', '#6B7280', 6),
('septic', 'septic', 'Septic', 'residential', 'Septic system installation and maintenance', 'droplets', '#059669', 7),
('pest-control', 'pest-control', 'Pest Control', 'both', 'Pest control and extermination services', 'bug', '#7C2D12', 8),
('irrigation', 'irrigation', 'Irrigation', 'both', 'Irrigation system installation and maintenance', 'droplets', '#0891B2', 9),
('painting', 'painting', 'Painting', 'both', 'Interior and exterior painting services', 'paintbrush', '#8B5CF6', 10),

-- Commercial Trades
('mechanical', 'mechanical', 'Mechanical', 'commercial', 'Commercial mechanical systems', 'cog', '#374151', 11),
('refrigeration', 'refrigeration', 'Refrigeration', 'commercial', 'Commercial refrigeration systems', 'snowflake', '#06B6D4', 12),
('security-systems', 'security-systems', 'Security Systems', 'both', 'Security system installation and monitoring', 'shield', '#DC2626', 13),
('landscaping', 'landscaping', 'Landscaping', 'both', 'Landscaping and grounds maintenance', 'tree-pine', '#059669', 14),
('kitchen-equipment', 'kitchen-equipment', 'Kitchen Equipment', 'commercial', 'Commercial kitchen equipment service', 'chef-hat', '#F97316', 15),
('water-treatment', 'water-treatment', 'Water Treatment', 'both', 'Water treatment and filtration systems', 'droplets', '#0284C7', 16),
('pool-spa', 'pool-spa', 'Pool & Spa', 'both', 'Pool and spa installation and maintenance', 'waves', '#0EA5E9', 17),

-- General
('general-contractor', 'general-contractor', 'General', 'both', 'General contracting and construction services', 'hammer', '#6B7280', 18);

-- =============================================
-- INSERT SERVICE TYPES
-- =============================================

INSERT INTO service_types (code, name, display_name, description, is_emergency, typical_duration_hours, display_order) VALUES
('INSTALL', 'install', 'Installation', 'New installation or setup of equipment/systems', FALSE, 4.0, 1),
('REPAIR', 'repair', 'Repair', 'Fix or restore existing equipment/systems', FALSE, 2.0, 2),
('MAINTENANCE', 'maintenance', 'Maintenance', 'Regular maintenance and tune-ups', FALSE, 1.5, 3),
('INSPECTION', 'inspection', 'Inspection', 'Safety and performance inspections', FALSE, 1.0, 4),
('EMERGENCY', 'emergency', 'Emergency Service', 'Urgent repair or emergency response', TRUE, 2.0, 5),
('REPLACEMENT', 'replacement', 'Replacement', 'Complete replacement of equipment/systems', FALSE, 6.0, 6),
('UPGRADE', 'upgrade', 'Upgrade', 'System upgrades and improvements', FALSE, 3.0, 7),
('CONSULTATION', 'consultation', 'Consultation', 'Professional consultation and assessment', FALSE, 1.0, 8);

-- =============================================
-- ALTER BUSINESS_SERVICES TABLE
-- =============================================

-- Add new columns for normalized structure (trade_slug already exists)
ALTER TABLE business_services 
ADD COLUMN IF NOT EXISTS trade_id UUID REFERENCES trades(id),
ADD COLUMN IF NOT EXISTS service_type_id UUID REFERENCES service_types(id),
ADD COLUMN IF NOT EXISTS is_bookable BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS estimated_duration_minutes INTEGER DEFAULT 120,
ADD COLUMN IF NOT EXISTS base_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS service_type_code VARCHAR(20); -- Denormalized for performance

-- =============================================
-- BACKFILL TRADE AND SERVICE TYPE MAPPING
-- =============================================

-- Create a function to map existing categories to trades
CREATE OR REPLACE FUNCTION map_category_to_trade_slug(category_text TEXT, service_name_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Normalize input
    category_text := LOWER(COALESCE(category_text, ''));
    service_name_text := LOWER(COALESCE(service_name_text, ''));
    
    -- Direct category matches
    IF category_text LIKE '%hvac%' OR service_name_text LIKE '%hvac%' OR 
       service_name_text LIKE '%heating%' OR service_name_text LIKE '%cooling%' OR
       service_name_text LIKE '%air condition%' OR service_name_text LIKE '%furnace%' THEN
        RETURN 'hvac';
    END IF;
    
    IF category_text LIKE '%plumb%' OR service_name_text LIKE '%plumb%' OR
       service_name_text LIKE '%drain%' OR service_name_text LIKE '%pipe%' OR
       service_name_text LIKE '%faucet%' OR service_name_text LIKE '%toilet%' THEN
        RETURN 'plumbing';
    END IF;
    
    IF category_text LIKE '%electric%' OR service_name_text LIKE '%electric%' OR
       service_name_text LIKE '%wiring%' OR service_name_text LIKE '%outlet%' OR
       service_name_text LIKE '%panel%' OR service_name_text LIKE '%breaker%' THEN
        RETURN 'electrical';
    END IF;
    
    IF category_text LIKE '%roof%' OR service_name_text LIKE '%roof%' OR
       service_name_text LIKE '%gutter%' OR service_name_text LIKE '%shingle%' THEN
        RETURN 'roofing';
    END IF;
    
    IF category_text LIKE '%chimney%' OR service_name_text LIKE '%chimney%' OR
       service_name_text LIKE '%fireplace%' THEN
        RETURN 'chimney';
    END IF;
    
    IF category_text LIKE '%garage%' OR service_name_text LIKE '%garage%' THEN
        RETURN 'garage-door';
    END IF;
    
    IF category_text LIKE '%septic%' OR service_name_text LIKE '%septic%' THEN
        RETURN 'septic';
    END IF;
    
    IF category_text LIKE '%pest%' OR service_name_text LIKE '%pest%' OR
       service_name_text LIKE '%extermina%' OR service_name_text LIKE '%bug%' THEN
        RETURN 'pest-control';
    END IF;
    
    IF category_text LIKE '%irrigat%' OR service_name_text LIKE '%irrigat%' OR
       service_name_text LIKE '%sprinkler%' THEN
        RETURN 'irrigation';
    END IF;
    
    IF category_text LIKE '%paint%' OR service_name_text LIKE '%paint%' THEN
        RETURN 'painting';
    END IF;
    
    IF category_text LIKE '%mechanical%' OR service_name_text LIKE '%mechanical%' THEN
        RETURN 'mechanical';
    END IF;
    
    IF category_text LIKE '%refrigerat%' OR service_name_text LIKE '%refrigerat%' OR
       service_name_text LIKE '%cooler%' OR service_name_text LIKE '%freezer%' THEN
        RETURN 'refrigeration';
    END IF;
    
    IF category_text LIKE '%security%' OR service_name_text LIKE '%security%' OR
       service_name_text LIKE '%alarm%' OR service_name_text LIKE '%camera%' THEN
        RETURN 'security-systems';
    END IF;
    
    IF category_text LIKE '%landscape%' OR service_name_text LIKE '%landscape%' OR
       service_name_text LIKE '%lawn%' OR service_name_text LIKE '%garden%' THEN
        RETURN 'landscaping';
    END IF;
    
    IF category_text LIKE '%kitchen%' OR service_name_text LIKE '%kitchen%' OR
       service_name_text LIKE '%commercial equipment%' THEN
        RETURN 'kitchen-equipment';
    END IF;
    
    IF category_text LIKE '%water%' OR service_name_text LIKE '%water treatment%' OR
       service_name_text LIKE '%filtration%' OR service_name_text LIKE '%softener%' THEN
        RETURN 'water-treatment';
    END IF;
    
    IF category_text LIKE '%pool%' OR service_name_text LIKE '%pool%' OR
       service_name_text LIKE '%spa%' OR service_name_text LIKE '%hot tub%' THEN
        RETURN 'pool-spa';
    END IF;
    
    -- Default to general contractor
    RETURN 'general-contractor';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create a function to map service names to service types
CREATE OR REPLACE FUNCTION map_service_to_type_code(service_name_text TEXT, is_emergency_service BOOLEAN)
RETURNS TEXT AS $$
BEGIN
    service_name_text := LOWER(COALESCE(service_name_text, ''));
    
    -- Emergency services first
    IF is_emergency_service OR service_name_text LIKE '%emergency%' OR service_name_text LIKE '%urgent%' THEN
        RETURN 'EMERGENCY';
    END IF;
    
    -- Installation services
    IF service_name_text LIKE '%install%' OR service_name_text LIKE '%new%' OR 
       service_name_text LIKE '%setup%' THEN
        RETURN 'INSTALL';
    END IF;
    
    -- Replacement services
    IF service_name_text LIKE '%replac%' OR service_name_text LIKE '%new unit%' THEN
        RETURN 'REPLACEMENT';
    END IF;
    
    -- Repair services
    IF service_name_text LIKE '%repair%' OR service_name_text LIKE '%fix%' OR
       service_name_text LIKE '%broken%' OR service_name_text LIKE '%not working%' THEN
        RETURN 'REPAIR';
    END IF;
    
    -- Maintenance services
    IF service_name_text LIKE '%mainten%' OR service_name_text LIKE '%tune%' OR
       service_name_text LIKE '%service%' OR service_name_text LIKE '%clean%' THEN
        RETURN 'MAINTENANCE';
    END IF;
    
    -- Inspection services
    IF service_name_text LIKE '%inspect%' OR service_name_text LIKE '%check%' OR
       service_name_text LIKE '%diagnostic%' THEN
        RETURN 'INSPECTION';
    END IF;
    
    -- Upgrade services
    IF service_name_text LIKE '%upgrad%' OR service_name_text LIKE '%improv%' THEN
        RETURN 'UPGRADE';
    END IF;
    
    -- Consultation services
    IF service_name_text LIKE '%consult%' OR service_name_text LIKE '%assessment%' OR
       service_name_text LIKE '%estimate%' THEN
        RETURN 'CONSULTATION';
    END IF;
    
    -- Default to repair for most services
    RETURN 'REPAIR';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Update business_services with mapped trade and service type
UPDATE business_services SET
    trade_slug = COALESCE(trade_slug, map_category_to_trade_slug(COALESCE(category_id::text, ''), service_name)),
    service_type_code = map_service_to_type_code(service_name, is_emergency);

-- Set trade_id and service_type_id from the mapped slugs/codes
UPDATE business_services SET
    trade_id = (SELECT id FROM trades WHERE slug = business_services.trade_slug),
    service_type_id = (SELECT id FROM service_types WHERE code = business_services.service_type_code);

-- Set base_price from existing price fields
UPDATE business_services SET
    base_price = CASE 
        WHEN price_min IS NOT NULL THEN price_min
        WHEN price_max IS NOT NULL THEN price_max
        ELSE 150.00 -- Default price
    END;

-- Set estimated_duration_minutes (default 2 hours, adjust for service type)
UPDATE business_services SET
    estimated_duration_minutes = CASE service_type_code
        WHEN 'INSTALL' THEN 240      -- 4 hours
        WHEN 'REPLACEMENT' THEN 360  -- 6 hours
        WHEN 'REPAIR' THEN 120       -- 2 hours
        WHEN 'MAINTENANCE' THEN 90   -- 1.5 hours
        WHEN 'INSPECTION' THEN 60    -- 1 hour
        WHEN 'EMERGENCY' THEN 120    -- 2 hours
        WHEN 'UPGRADE' THEN 180      -- 3 hours
        WHEN 'CONSULTATION' THEN 60  -- 1 hour
        ELSE 120                     -- Default 2 hours
    END;

-- =============================================
-- NORMALIZE SERVICE AREAS TABLE
-- =============================================

-- Add postal_code column if it doesn't exist
ALTER TABLE service_areas 
ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20),
ADD COLUMN IF NOT EXISTS region VARCHAR(100),
ADD COLUMN IF NOT EXISTS timezone VARCHAR(100) DEFAULT 'America/New_York',
ADD COLUMN IF NOT EXISTS dispatch_fee_cents INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS min_response_time_hours INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS max_response_time_hours INTEGER DEFAULT 24,
ADD COLUMN IF NOT EXISTS emergency_services_available BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS regular_services_available BOOLEAN DEFAULT TRUE;

-- Create a temporary table to hold normalized service areas
CREATE TEMP TABLE temp_normalized_service_areas AS
SELECT DISTINCT
    sa.id,
    sa.business_id,
    sa.country_code,
    unnest(sa.postal_codes) as postal_code_normalized,
    sa.city,
    sa.state as region,
    COALESCE(sa.timezone, 'America/New_York') as timezone,
    COALESCE(sa.travel_fee * 100, 0)::INTEGER as dispatch_fee_cents, -- Convert to cents
    2 as min_response_time_hours,
    24 as max_response_time_hours,
    TRUE as emergency_services_available,
    TRUE as regular_services_available,
    sa.is_active,
    sa.created_at,
    sa.updated_at
FROM service_areas sa
WHERE sa.postal_codes IS NOT NULL AND array_length(sa.postal_codes, 1) > 0;

-- Update existing rows with normalized postal codes (first one from array)
UPDATE service_areas SET
    postal_code = (
        SELECT postal_code_normalized 
        FROM temp_normalized_service_areas t 
        WHERE t.id = service_areas.id 
        LIMIT 1
    ),
    region = COALESCE(region, state),
    dispatch_fee_cents = COALESCE(dispatch_fee_cents, (travel_fee * 100)::INTEGER, 0),
    min_response_time_hours = COALESCE(min_response_time_hours, 2),
    max_response_time_hours = COALESCE(max_response_time_hours, 24),
    emergency_services_available = COALESCE(emergency_services_available, TRUE),
    regular_services_available = COALESCE(regular_services_available, TRUE)
WHERE EXISTS (SELECT 1 FROM temp_normalized_service_areas t WHERE t.id = service_areas.id);

-- Insert additional rows for remaining postal codes in arrays
INSERT INTO service_areas (
    business_id, area_name, city, state, country_code, postal_code, region,
    service_radius_miles, travel_fee, minimum_job_amount, is_active, priority_level,
    kind, location_slug, address, county, is_primary, postal_codes,
    timezone, dispatch_fee_cents, min_response_time_hours, max_response_time_hours,
    emergency_services_available, regular_services_available, created_at, updated_at
)
SELECT DISTINCT
    t.business_id,
    sa.area_name,
    t.city,
    t.region,
    t.country_code,
    t.postal_code_normalized,
    t.region,
    sa.service_radius_miles,
    sa.travel_fee,
    sa.minimum_job_amount,
    t.is_active,
    sa.priority_level,
    sa.kind,
    sa.location_slug || '-' || t.postal_code_normalized, -- Make unique location_slug
    sa.address,
    sa.county,
    FALSE, -- Not primary for additional rows
    ARRAY[t.postal_code_normalized], -- Single postal code array
    t.timezone,
    t.dispatch_fee_cents,
    t.min_response_time_hours,
    t.max_response_time_hours,
    t.emergency_services_available,
    t.regular_services_available,
    t.created_at,
    t.updated_at
FROM temp_normalized_service_areas t
JOIN service_areas sa ON sa.id = t.id
WHERE t.postal_code_normalized != (
    SELECT unnest(sa.postal_codes) LIMIT 1 -- Skip the first postal code (already updated above)
);

-- =============================================
-- CREATE SERVICE CATALOG VIEW
-- =============================================

CREATE OR REPLACE VIEW v_service_catalog AS
SELECT 
    bs.id,
    bs.business_id,
    bs.service_name,
    bs.service_slug,
    bs.description,
    
    -- Trade information
    t.id as trade_id,
    t.slug as trade_slug,
    t.name as trade_name,
    t.display_name as trade_display_name,
    t.market_type as trade_market_type,
    t.icon as trade_icon,
    t.color as trade_color,
    
    -- Service type information
    st.id as service_type_id,
    st.code as service_type_code,
    st.name as service_type_name,
    st.display_name as service_type_display_name,
    st.is_emergency as service_type_is_emergency,
    
    -- Pricing and duration
    bs.base_price,
    bs.price_type,
    bs.price_min,
    bs.price_max,
    bs.price_unit,
    bs.estimated_duration_minutes,
    
    -- Service options
    bs.is_emergency,
    bs.is_commercial,
    bs.is_residential,
    bs.is_bookable,
    
    -- Status and display
    bs.is_active,
    bs.display_order,
    
    -- Legacy fields (deprecated)
    bs.category_id as legacy_category_id,
    
    -- Metadata
    bs.created_at,
    bs.updated_at
FROM business_services bs
LEFT JOIN trades t ON bs.trade_id = t.id
LEFT JOIN service_types st ON bs.service_type_id = st.id
WHERE bs.is_active = TRUE;

-- =============================================
-- CREATE INDEXES
-- =============================================

CREATE INDEX IF NOT EXISTS idx_trades_slug ON trades(slug);
CREATE INDEX IF NOT EXISTS idx_trades_market_type ON trades(market_type);
CREATE INDEX IF NOT EXISTS idx_trades_active ON trades(is_active);

CREATE INDEX IF NOT EXISTS idx_service_types_code ON service_types(code);
CREATE INDEX IF NOT EXISTS idx_service_types_emergency ON service_types(is_emergency);
CREATE INDEX IF NOT EXISTS idx_service_types_active ON service_types(is_active);

CREATE INDEX IF NOT EXISTS idx_business_services_trade ON business_services(trade_id);
CREATE INDEX IF NOT EXISTS idx_business_services_service_type ON business_services(service_type_id);
CREATE INDEX IF NOT EXISTS idx_business_services_trade_slug ON business_services(trade_slug);
CREATE INDEX IF NOT EXISTS idx_business_services_service_type_code ON business_services(service_type_code);
CREATE INDEX IF NOT EXISTS idx_business_services_bookable ON business_services(is_bookable);
CREATE INDEX IF NOT EXISTS idx_business_services_base_price ON business_services(base_price);

-- Note: Unique constraint for service areas will be added after data cleanup
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_service_areas_unique_postal 
-- ON service_areas(business_id, country_code, postal_code) 
-- WHERE is_active = TRUE AND postal_code IS NOT NULL;

-- =============================================
-- CLEANUP FUNCTIONS
-- =============================================

-- Drop the temporary mapping functions
DROP FUNCTION IF EXISTS map_category_to_trade_slug(TEXT, TEXT);
DROP FUNCTION IF EXISTS map_service_to_type_code(TEXT, BOOLEAN);

COMMIT;
