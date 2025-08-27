-- Featured Projects System Migration
-- Creates tables for project showcase and related data

-- Featured Projects table
CREATE TABLE IF NOT EXISTS featured_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    trade VARCHAR(100) NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    completion_date DATE NOT NULL,
    project_duration VARCHAR(100), -- e.g., "3 days", "1 week"
    project_value DECIMAL(10,2), -- Optional project value
    customer_name VARCHAR(255),
    customer_testimonial TEXT,
    before_images TEXT[] DEFAULT '{}', -- Array of image URLs
    after_images TEXT[] DEFAULT '{}', -- Array of image URLs
    gallery_images TEXT[] DEFAULT '{}', -- Additional gallery images
    video_url VARCHAR(500), -- Optional project video
    challenges_faced TEXT[] DEFAULT '{}', -- Array of challenges
    solutions_provided TEXT[] DEFAULT '{}', -- Array of solutions
    equipment_installed TEXT[] DEFAULT '{}', -- Array of equipment/products
    warranty_info TEXT,
    is_featured BOOLEAN DEFAULT false,
    seo_slug VARCHAR(255) UNIQUE NOT NULL,
    tags TEXT[] DEFAULT '{}', -- Array of tags for filtering
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- Project Categories table (for filtering and organization)
CREATE TABLE IF NOT EXISTS project_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100), -- Icon name for UI
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_id, slug)
);

-- Project Tags table (for flexible tagging system)
CREATE TABLE IF NOT EXISTS project_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6', -- Hex color for tag display
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_id, slug)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_featured_projects_business_id ON featured_projects(business_id);
CREATE INDEX IF NOT EXISTS idx_featured_projects_trade ON featured_projects(trade);
CREATE INDEX IF NOT EXISTS idx_featured_projects_category ON featured_projects(service_category);
CREATE INDEX IF NOT EXISTS idx_featured_projects_featured ON featured_projects(is_featured);
CREATE INDEX IF NOT EXISTS idx_featured_projects_completion_date ON featured_projects(completion_date DESC);
CREATE INDEX IF NOT EXISTS idx_featured_projects_display_order ON featured_projects(display_order);
CREATE INDEX IF NOT EXISTS idx_featured_projects_seo_slug ON featured_projects(seo_slug);


CREATE INDEX IF NOT EXISTS idx_project_categories_business_id ON project_categories(business_id);
CREATE INDEX IF NOT EXISTS idx_project_categories_active ON project_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_project_tags_business_id ON project_tags(business_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_active ON project_tags(is_active);

-- RLS Policies
ALTER TABLE featured_projects ENABLE ROW LEVEL SECURITY;

ALTER TABLE project_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_tags ENABLE ROW LEVEL SECURITY;

-- Public read access for featured projects (for website display)
CREATE POLICY "Public can read featured projects" ON featured_projects
    FOR SELECT USING (true);



CREATE POLICY "Public can read project categories" ON project_categories
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can read project tags" ON project_tags
    FOR SELECT USING (is_active = true);

-- Business members can manage their projects
CREATE POLICY "Business members can manage featured projects" ON featured_projects
    FOR ALL USING (business_id IN (
        SELECT business_id FROM business_memberships WHERE user_id = auth.uid() AND is_active = true
    ));



CREATE POLICY "Business members can manage project categories" ON project_categories
    FOR ALL USING (business_id IN (
        SELECT business_id FROM business_memberships WHERE user_id = auth.uid() AND is_active = true
    ));

CREATE POLICY "Business members can manage project tags" ON project_tags
    FOR ALL USING (business_id IN (
        SELECT business_id FROM business_memberships WHERE user_id = auth.uid() AND is_active = true
    ));

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_featured_projects_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_featured_projects_updated_at
    BEFORE UPDATE ON featured_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_featured_projects_updated_at();



-- Insert default project categories for common trades
INSERT INTO project_categories (business_id, name, slug, description, icon, display_order) 
SELECT 
    b.id,
    category.name,
    category.slug,
    category.description,
    category.icon,
    category.display_order
FROM businesses b
CROSS JOIN (
    VALUES 
        ('HVAC Installation', 'hvac-installation', 'Complete HVAC system installations', 'thermometer', 1),
        ('HVAC Repair', 'hvac-repair', 'Emergency and scheduled HVAC repairs', 'wrench', 2),
        ('Plumbing Installation', 'plumbing-installation', 'New plumbing system installations', 'droplet', 3),
        ('Plumbing Repair', 'plumbing-repair', 'Emergency and routine plumbing repairs', 'tool', 4),
        ('Electrical Installation', 'electrical-installation', 'Electrical system installations and upgrades', 'zap', 5),
        ('Electrical Repair', 'electrical-repair', 'Electrical troubleshooting and repairs', 'lightning-bolt', 6),
        ('Maintenance', 'maintenance', 'Preventive maintenance and tune-ups', 'calendar', 7),
        ('Emergency Service', 'emergency-service', '24/7 emergency service calls', 'alert-circle', 8)
) AS category(name, slug, description, icon, display_order)
WHERE b.is_active = true
ON CONFLICT (business_id, slug) DO NOTHING;

-- Insert default project tags
INSERT INTO project_tags (business_id, name, slug, color) 
SELECT 
    b.id,
    tag.name,
    tag.slug,
    tag.color
FROM businesses b
CROSS JOIN (
    VALUES 
        ('Residential', 'residential', '#10B981'),
        ('Commercial', 'commercial', '#3B82F6'),
        ('Emergency', 'emergency', '#EF4444'),
        ('Energy Efficient', 'energy-efficient', '#059669'),
        ('Smart Home', 'smart-home', '#8B5CF6'),
        ('Warranty Work', 'warranty-work', '#F59E0B'),
        ('Upgrade', 'upgrade', '#6366F1'),
        ('New Construction', 'new-construction', '#84CC16')
) AS tag(name, slug, color)
WHERE b.is_active = true
ON CONFLICT (business_id, slug) DO NOTHING;
