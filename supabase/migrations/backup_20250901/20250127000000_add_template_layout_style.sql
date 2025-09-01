-- Add layout_style column to templates table for quick filtering and mobile app detection
-- This is optional and can be derived from the JSONB config, but helps with performance

ALTER TABLE public.templates 
ADD COLUMN layout_style VARCHAR(50) CHECK (layout_style IN (
    'modern_minimal', 'corporate_bold', 'creative_split', 
    'professional', 'elegant_simple'
));

-- Create index for layout_style filtering
CREATE INDEX idx_templates_layout_style ON public.templates(layout_style) 
WHERE layout_style IS NOT NULL;

-- Add computed column function to extract layout_style from config
CREATE OR REPLACE FUNCTION get_template_layout_style(config_data JSONB)
RETURNS VARCHAR(50) AS $$
BEGIN
    RETURN config_data->'visual_config'->>'layout_style';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create functional index on the computed layout style
CREATE INDEX idx_templates_config_layout_style ON public.templates 
USING btree(get_template_layout_style(config)) 
WHERE get_template_layout_style(config) IS NOT NULL;

COMMENT ON COLUMN public.templates.layout_style IS 'Optional layout style for quick filtering. Can be derived from config.visual_config.layout_style';
COMMENT ON FUNCTION get_template_layout_style IS 'Extract layout_style from template config JSONB';
