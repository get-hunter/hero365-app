-- =============================================
-- SEO SEED DATA
-- =============================================
-- Templates, services, and locations for SEO Revenue Engine
-- Depends on: SEO schema tables

-- =============================================
-- SEO TEMPLATES
-- =============================================

INSERT INTO seo_templates (name, page_type, content, is_active) VALUES
(
    'service_location',
    'service_location',
    '{
        "title": "{service_name} in {city}, {state} | 24/7 Service | {business_name}",
        "meta_description": "Professional {service_name} services in {city}, {state}. Same-day service, licensed & insured. Call {phone} for free estimate.",
        "h1_heading": "Expert {service_name} Services in {city}, {state}",
        "content": "Need reliable {service_name} in {city}? {business_name} has been serving {city} residents for {years_experience} years with professional, affordable {service_name} solutions. Our certified technicians provide comprehensive {service_name} services including installation, repair, and maintenance. We are dedicated to providing top-notch service to our community in {city}, {state}. Contact us today for a free estimate!",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": "{service_name}",
            "areaServed": {
                "@type": "City",
                "name": "{city}"
            },
            "provider": {
                "@type": "LocalBusiness",
                "name": "{business_name}",
                "telephone": "{phone}",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "{city}",
                    "addressRegion": "{state}"
                }
            }
        },
        "target_keywords": ["{service_name} {city}", "{city} {service_name} repair", "{business_name} {service_name}"]
    }',
    true
),
(
    'service',
    'service',
    '{
        "title": "{service_name} Services | Professional {service_name} | {business_name}",
        "meta_description": "Comprehensive {service_name} services by {business_name}. Expert technicians, competitive pricing, and guaranteed satisfaction.",
        "h1_heading": "Professional {service_name} Services",
        "content": "Looking for reliable {service_name} services? {business_name} provides comprehensive {service_name} solutions for residential and commercial clients. Our experienced team delivers quality workmanship with competitive pricing and exceptional customer service.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": "{service_name}",
            "provider": {
                "@type": "LocalBusiness",
                "name": "{business_name}"
            }
        },
        "target_keywords": ["{service_name} services", "{business_name} {service_name}", "professional {service_name}"]
    }',
    true
),
(
    'location',
    'location',
    '{
        "title": "{business_name} in {city}, {state} | Local {primary_trade} Services",
        "meta_description": "Local {primary_trade} services in {city}, {state}. {business_name} is your trusted local expert for all {primary_trade} needs.",
        "h1_heading": "{business_name} Serving {city}, {state}",
        "content": "Proudly serving {city}, {state} and surrounding areas, {business_name} is your local {primary_trade} expert. We provide comprehensive {primary_trade} services to homeowners and businesses throughout {city}.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "{business_name}",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "{city}",
                "addressRegion": "{state}"
            }
        },
        "target_keywords": ["{city} {primary_trade}", "{business_name} {city}", "local {primary_trade} {city}"]
    }',
    true
),
(
    'emergency_service',
    'emergency_service',
    '{
        "title": "Emergency {service_name} in {city}, {state} | 24/7 Service | {business_name}",
        "meta_description": "24/7 emergency {service_name} in {city}. Fast response, licensed technicians. Call {phone} now for immediate service!",
        "h1_heading": "24/7 Emergency {service_name} in {city}, {state}",
        "content": "Need emergency {service_name} in {city}? {business_name} provides 24/7 emergency {service_name} services with fast response times. Our licensed technicians are available around the clock to handle your urgent {service_name} needs.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "EmergencyService",
            "serviceType": "{service_name}",
            "areaServed": {
                "@type": "City",
                "name": "{city}"
            },
            "provider": {
                "@type": "LocalBusiness",
                "name": "{business_name}",
                "telephone": "{phone}"
            }
        },
        "target_keywords": ["emergency {service_name} {city}", "24/7 {service_name} {city}", "{service_name} emergency {city}"]
    }',
    true
)
ON CONFLICT (name) DO NOTHING;

-- =============================================
-- SERVICE SEO CONFIGURATIONS
-- =============================================

INSERT INTO service_seo_config (service_name, service_slug, target_keywords, priority_score, enable_llm_enhancement) VALUES
('HVAC Repair', 'hvac-repair', ARRAY['hvac repair', 'ac repair', 'heating repair', 'air conditioning repair'], 90, true),
('Plumbing Repair', 'plumbing-repair', ARRAY['plumber', 'plumbing repair', 'emergency plumber', 'drain cleaning'], 85, true),
('Electrical Repair', 'electrical-repair', ARRAY['electrician', 'electrical repair', 'electrical service', 'wiring'], 80, true),
('AC Installation', 'ac-installation', ARRAY['ac installation', 'air conditioning installation', 'hvac installation'], 85, true),
('Water Heater Repair', 'water-heater-repair', ARRAY['water heater repair', 'hot water heater', 'tankless water heater'], 75, false),
('Furnace Repair', 'furnace-repair', ARRAY['furnace repair', 'heating repair', 'furnace service'], 70, false),
('Duct Cleaning', 'duct-cleaning', ARRAY['duct cleaning', 'air duct cleaning', 'hvac cleaning'], 60, false),
('Emergency HVAC', 'emergency-hvac', ARRAY['emergency hvac', '24/7 hvac', 'emergency ac repair'], 95, true),
('Commercial HVAC', 'commercial-hvac', ARRAY['commercial hvac', 'commercial air conditioning', 'business hvac'], 70, false),
('Preventive Maintenance', 'preventive-maintenance', ARRAY['hvac maintenance', 'ac tune up', 'preventive maintenance'], 50, false),
('Chimney Repair', 'chimney-repair', ARRAY['chimney repair', 'chimney cleaning', 'fireplace repair'], 65, false),
('Roofing Repair', 'roofing-repair', ARRAY['roof repair', 'roofing contractor', 'roof leak repair'], 80, true),
('Garage Door Repair', 'garage-door-repair', ARRAY['garage door repair', 'garage door installation', 'door opener repair'], 70, false),
('Septic Service', 'septic-service', ARRAY['septic pumping', 'septic repair', 'septic tank service'], 75, false),
('Pest Control', 'pest-control', ARRAY['pest control', 'exterminator', 'bug control'], 70, false)
ON CONFLICT (service_slug) DO NOTHING;

-- =============================================
-- LOCATION PAGES (TEXAS MARKETS)
-- =============================================

INSERT INTO location_pages (city, state, county, slug, zip_codes, neighborhoods, population, median_income, monthly_searches, competition_level, conversion_potential) VALUES
-- Major Texas Cities
('Austin', 'TX', 'Travis', 'austin-tx', ARRAY['78701', '78702', '78703', '78704', '78705', '78731', '78732', '78733', '78734', '78735'], ARRAY['Downtown', 'South Congress', 'East Austin', 'Zilker', 'Westlake', 'Tarrytown'], 1000000, 75000, 5000, 'high', 0.08),
('Houston', 'TX', 'Harris', 'houston-tx', ARRAY['77001', '77002', '77003', '77004', '77005', '77006', '77007', '77008', '77009', '77010'], ARRAY['Downtown', 'Montrose', 'River Oaks', 'Heights', 'Midtown'], 2300000, 52000, 8000, 'high', 0.06),
('Dallas', 'TX', 'Dallas', 'dallas-tx', ARRAY['75201', '75202', '75203', '75204', '75205', '75206', '75207', '75208', '75209', '75210'], ARRAY['Downtown', 'Deep Ellum', 'Uptown', 'Bishop Arts', 'Knox-Henderson'], 1340000, 54000, 6500, 'high', 0.07),
('San Antonio', 'TX', 'Bexar', 'san-antonio-tx', ARRAY['78201', '78202', '78203', '78204', '78205', '78206', '78207', '78208', '78209', '78210'], ARRAY['Downtown', 'Southtown', 'Alamo Heights', 'Stone Oak', 'The Dominion'], 1550000, 48000, 4500, 'medium', 0.09),

-- Austin Metro Area
('Round Rock', 'TX', 'Williamson', 'round-rock-tx', ARRAY['78664', '78665', '78681'], ARRAY['Downtown Round Rock', 'Teravista', 'Walsh Ranch', 'Stone Canyon'], 130000, 85000, 1200, 'medium', 0.12),
('Cedar Park', 'TX', 'Williamson', 'cedar-park-tx', ARRAY['78613', '78630'], ARRAY['Cedar Park Center', 'Buttercup Creek', 'Anderson Mill'], 80000, 90000, 800, 'low', 0.15),
('Pflugerville', 'TX', 'Travis', 'pflugerville-tx', ARRAY['78660'], ARRAY['Falcon Pointe', 'Springbrook Centre', 'Wilshire'], 70000, 80000, 600, 'low', 0.18),
('Georgetown', 'TX', 'Williamson', 'georgetown-tx', ARRAY['78626', '78628', '78633'], ARRAY['Downtown Georgetown', 'Sun City', 'Wolf Ranch'], 80000, 75000, 700, 'medium', 0.10),
('Leander', 'TX', 'Williamson', 'leander-tx', ARRAY['78641', '78645'], ARRAY['Crystal Falls', 'Travisso', 'Bryson'], 65000, 85000, 500, 'low', 0.20),

-- Houston Metro Area
('The Woodlands', 'TX', 'Montgomery', 'the-woodlands-tx', ARRAY['77380', '77381', '77382', '77384', '77385'], ARRAY['Town Center', 'Panther Creek', 'Cochrans Crossing'], 120000, 95000, 900, 'medium', 0.14),
('Sugar Land', 'TX', 'Fort Bend', 'sugar-land-tx', ARRAY['77478', '77479', '77496', '77498'], ARRAY['First Colony', 'Sweetwater', 'Riverstone'], 120000, 110000, 850, 'medium', 0.13),
('Katy', 'TX', 'Harris', 'katy-tx', ARRAY['77449', '77450', '77494'], ARRAY['Cinco Ranch', 'Cross Creek Ranch', 'Grand Lakes'], 22000, 85000, 650, 'medium', 0.16),

-- Dallas Metro Area
('Plano', 'TX', 'Collin', 'plano-tx', ARRAY['75023', '75024', '75025', '75074', '75075'], ARRAY['West Plano', 'East Plano', 'Legacy West'], 290000, 95000, 1800, 'high', 0.11),
('Frisco', 'TX', 'Collin', 'frisco-tx', ARRAY['75033', '75034', '75035'], ARRAY['Stonebriar', 'Frisco Square', 'The Star'], 200000, 120000, 1400, 'medium', 0.12),
('McKinney', 'TX', 'Collin', 'mckinney-tx', ARRAY['75069', '75070', '75071'], ARRAY['Historic Downtown', 'Stonebridge Ranch', 'Craig Ranch'], 200000, 85000, 1200, 'medium', 0.13),

-- Other Major Markets
('Fort Worth', 'TX', 'Tarrant', 'fort-worth-tx', ARRAY['76101', '76102', '76103', '76104', '76105'], ARRAY['Downtown', 'Cultural District', 'Sundance Square'], 920000, 52000, 3500, 'high', 0.08),
('El Paso', 'TX', 'El Paso', 'el-paso-tx', ARRAY['79901', '79902', '79903', '79904', '79905'], ARRAY['Downtown', 'Westside', 'Northeast'], 680000, 42000, 2200, 'medium', 0.11),
('Arlington', 'TX', 'Tarrant', 'arlington-tx', ARRAY['76001', '76002', '76003', '76004', '76005'], ARRAY['Downtown', 'Entertainment District', 'Pantego'], 400000, 58000, 2000, 'medium', 0.10)

ON CONFLICT (city, state) DO NOTHING;

-- =============================================
-- SERVICE + LOCATION COMBINATIONS (HIGH VALUE)
-- =============================================

-- Generate high-value service+location combinations for major cities
INSERT INTO service_location_pages (service_slug, location_slug, page_url, priority_score, enable_llm_enhancement, target_keywords, monthly_search_volume, estimated_monthly_visitors, estimated_monthly_revenue) VALUES
-- Austin combinations (high priority)
('hvac-repair', 'austin-tx', '/services/hvac-repair/austin-tx', 95, true, ARRAY['hvac repair austin', 'austin hvac repair', 'ac repair austin'], 2500, 1250, 6250),
('emergency-hvac', 'austin-tx', '/emergency/hvac-repair/austin-tx', 90, true, ARRAY['emergency hvac austin', '24/7 hvac austin'], 800, 400, 2000),
('ac-installation', 'austin-tx', '/services/ac-installation/austin-tx', 85, true, ARRAY['ac installation austin', 'austin air conditioning installation'], 1200, 600, 3000),
('plumbing-repair', 'austin-tx', '/services/plumbing-repair/austin-tx', 85, true, ARRAY['plumber austin', 'austin plumbing repair'], 2000, 1000, 5000),

-- Round Rock combinations
('hvac-repair', 'round-rock-tx', '/services/hvac-repair/round-rock-tx', 80, false, ARRAY['hvac repair round rock', 'round rock hvac'], 600, 300, 1500),
('plumbing-repair', 'round-rock-tx', '/services/plumbing-repair/round-rock-tx', 75, false, ARRAY['plumber round rock', 'round rock plumbing'], 500, 250, 1250),

-- Cedar Park combinations  
('hvac-repair', 'cedar-park-tx', '/services/hvac-repair/cedar-park-tx', 75, false, ARRAY['hvac repair cedar park', 'cedar park hvac'], 400, 200, 1000),
('ac-installation', 'cedar-park-tx', '/services/ac-installation/cedar-park-tx', 70, false, ARRAY['ac installation cedar park'], 300, 150, 750),

-- Houston combinations (high volume)
('hvac-repair', 'houston-tx', '/services/hvac-repair/houston-tx', 95, true, ARRAY['hvac repair houston', 'houston hvac repair'], 4000, 2000, 10000),
('plumbing-repair', 'houston-tx', '/services/plumbing-repair/houston-tx', 90, true, ARRAY['plumber houston', 'houston plumbing'], 3500, 1750, 8750),

-- Dallas combinations
('hvac-repair', 'dallas-tx', '/services/hvac-repair/dallas-tx', 95, true, ARRAY['hvac repair dallas', 'dallas hvac repair'], 3200, 1600, 8000),
('electrical-repair', 'dallas-tx', '/services/electrical-repair/dallas-tx', 80, false, ARRAY['electrician dallas', 'dallas electrical repair'], 2000, 1000, 5000)

ON CONFLICT (service_slug, location_slug) DO NOTHING;

COMMIT;
