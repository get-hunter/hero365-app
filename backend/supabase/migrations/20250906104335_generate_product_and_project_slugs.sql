-- Generate slugs for products and projects
-- This migration creates slugs based on names/titles for better URL structure

-- Function to create URL-friendly slugs
CREATE OR REPLACE FUNCTION generate_slug(input_text TEXT) 
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(input_text, '[^a-zA-Z0-9\s-]', '', 'g'),
                '\s+', '-', 'g'
            ),
            '-+', '-', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql;

-- Update products with generated slugs
UPDATE products 
SET slug = generate_slug(name) || '-' || SUBSTRING(id::text, 1, 8)
WHERE slug IS NULL;

-- Update featured_projects with generated slugs  
UPDATE featured_projects 
SET slug = generate_slug(title) || '-' || SUBSTRING(id::text, 1, 8)
WHERE slug IS NULL;

-- Create unique indexes to prevent duplicate slugs
CREATE UNIQUE INDEX IF NOT EXISTS idx_products_slug_unique ON products(slug) WHERE slug IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_featured_projects_slug_unique ON featured_projects(slug) WHERE slug IS NOT NULL;

-- Drop the helper function as it's no longer needed
DROP FUNCTION generate_slug(TEXT);
