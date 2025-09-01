-- Fix company_size case to match enum values
-- Update SMALL to small to match CompanySize enum

UPDATE businesses 
SET company_size = 'small'
WHERE company_size = 'SMALL';

-- Success message
SELECT 'Company size case fixed! 🎉' as message,
       'Updated SMALL to small to match enum values' as summary;
