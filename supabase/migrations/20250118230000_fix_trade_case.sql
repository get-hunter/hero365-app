-- Fix trade case to match enum values
-- Update HVAC to hvac to match ResidentialTrade enum

UPDATE businesses 
SET residential_trades = ARRAY['hvac']
WHERE residential_trades = ARRAY['HVAC'];

-- Success message
SELECT 'Trade case fixed! 🎉' as message,
       'Updated HVAC to hvac to match enum values' as summary;
