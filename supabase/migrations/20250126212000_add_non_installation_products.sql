-- Add sample products that don't require professional installation
-- These can be added to cart directly without installation options

INSERT INTO products (
    business_id,
    name,
    sku,
    description,
    long_description,
    unit_price,
    category_id,
    warranty_years,
    requires_professional_install,
    show_on_website,
    is_active,
    is_featured,
    current_stock,
    featured_image_url,
    product_highlights,
    technical_specs,
    meta_title,
    meta_description
) VALUES 

-- HVAC Filter - No installation required
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'Honeywell MERV 11 Air Filter 20x25x1',
    'HW-MERV11-20x25x1',
    'High-efficiency air filter for improved indoor air quality',
    'Premium MERV 11 rated air filter that captures 85% of particles 3.0 to 10.0 microns in size. Perfect for homes with pets or allergies. Easy DIY replacement - no professional installation required.',
    24.99,
    '315bf716-2e80-4e9d-b94b-e2cfbab9b0be', -- HVAC category
    1,
    FALSE, -- No installation required
    TRUE,
    TRUE,
    FALSE,
    50,
    'https://images.unsplash.com/photo-1558618047-3c8c76ca7b60?w=800&h=600&fit=crop',
    '["MERV 11 rating", "Captures 85% of particles", "Lasts up to 3 months", "Easy DIY installation", "Improves air quality"]',
    '{"dimensions": "20x25x1 inches", "merv_rating": 11, "efficiency": "85% particles 3-10 microns", "lifespan": "3 months", "material": "Synthetic pleated"}',
    'Honeywell MERV 11 Air Filter 20x25x1 - Easy DIY Replacement',
    'High-efficiency MERV 11 air filter for improved indoor air quality. Easy DIY installation, no professional service required. 85% particle capture rate.'
),

-- Thermostat Batteries - No installation required  
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'Honeywell Thermostat Battery Pack (4-Pack AA)',
    'HW-BATT-AA4',
    'Long-lasting alkaline batteries for digital thermostats',
    'Premium alkaline batteries specifically designed for thermostat use. Long-lasting power ensures your thermostat maintains accurate temperature control. Simple replacement - just open thermostat and swap batteries.',
    12.99,
    '315bf716-2e80-4e9d-b94b-e2cfbab9b0be', -- HVAC category
    0, -- Consumable item
    FALSE, -- No installation required
    TRUE,
    TRUE,
    FALSE,
    100,
    'https://images.unsplash.com/photo-1609146728104-d6994e23f63e?w=800&h=600&fit=crop',
    '["Long-lasting power", "Thermostat compatible", "4-pack value", "Easy replacement", "Premium alkaline"]',
    '{"type": "AA Alkaline", "quantity": 4, "voltage": "1.5V", "shelf_life": "7 years", "temperature_range": "-18°C to 55°C"}',
    'Thermostat Battery Pack - 4 AA Alkaline Batteries',
    'Long-lasting AA alkaline batteries for digital thermostats. 4-pack value with 7-year shelf life. Easy DIY replacement.'
),

-- Pipe Insulation - No installation required
(
    'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    'Pipe Insulation Foam Sleeve 3/4" x 6ft',
    'PIPE-INS-34-6',
    'Energy-saving foam pipe insulation for hot water lines',
    'Self-sealing foam pipe insulation helps prevent heat loss and condensation. Easy DIY installation with pre-slit design - simply wrap around pipes. Saves energy costs and prevents pipe sweating.',
    8.99,
    '315bf716-2e80-4e9d-b94b-e2cfbab9b0be', -- HVAC category  
    5,
    FALSE, -- No installation required
    TRUE,
    TRUE,
    TRUE, -- Featured product
    75,
    'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=800&h=600&fit=crop',
    '["Self-sealing design", "Pre-slit for easy install", "Prevents condensation", "Energy savings", "UV resistant"]',
    '{"pipe_size": "3/4 inch", "length": "6 feet", "material": "Closed-cell foam", "temperature_range": "-40°F to 200°F", "thickness": "1/2 inch"}',
    'Pipe Insulation Foam Sleeve 3/4" x 6ft - Easy DIY Install',
    'Self-sealing foam pipe insulation for 3/4" pipes. Easy DIY installation prevents heat loss and condensation. 6-foot length with pre-slit design.'
);
