-- Add subdomain column to businesses table
ALTER TABLE businesses 
ADD COLUMN subdomain character varying UNIQUE;

-- Create index for faster lookups
CREATE INDEX idx_businesses_subdomain ON businesses(subdomain);

-- Populate subdomain from website_configurations where available
UPDATE businesses 
SET subdomain = wc.subdomain
FROM website_configurations wc
WHERE businesses.id = wc.business_id 
AND wc.subdomain IS NOT NULL;

-- For businesses without website_configurations, generate subdomain from name
UPDATE businesses 
SET subdomain = (
  SELECT LOWER(
    TRIM(
      REGEXP_REPLACE(
        REGEXP_REPLACE(
          REGEXP_REPLACE(name, '[^a-zA-Z0-9\s-]', '', 'g'),
          '\s+', '-', 'g'
        ),
        '-+', '-', 'g'
      ), '-'
    )
  )
)
WHERE subdomain IS NULL
AND name IS NOT NULL;
