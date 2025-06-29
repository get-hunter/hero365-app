-- Create Projects Schema
-- This migration adds comprehensive project management tables
-- Date: 2025-01-31
-- Version: Projects Feature Implementation

-- Projects table
CREATE TABLE "public"."projects" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(200) NOT NULL,
    "description" TEXT NOT NULL,
    "created_by" TEXT NOT NULL,
    "client_id" UUID NOT NULL REFERENCES "public"."contacts"("id") ON DELETE SET NULL,
    "client_name" VARCHAR(200) NOT NULL,
    "client_address" TEXT NOT NULL,
    "project_type" VARCHAR(50) NOT NULL CHECK (project_type IN ('maintenance', 'installation', 'renovation', 'emergency', 'consultation', 'inspection', 'repair', 'construction')),
    "status" VARCHAR(50) DEFAULT 'planning' CHECK (status IN ('planning', 'active', 'on_hold', 'completed', 'cancelled')),
    "priority" VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    "start_date" TIMESTAMP WITH TIME ZONE NOT NULL,
    "end_date" TIMESTAMP WITH TIME ZONE,
    "estimated_budget" NUMERIC(12,2) DEFAULT 0 CHECK (estimated_budget >= 0),
    "actual_cost" NUMERIC(12,2) DEFAULT 0 CHECK (actual_cost >= 0),
    "manager" VARCHAR(200),
    "manager_id" UUID,
    "team_members" TEXT[] DEFAULT '{}',
    "tags" TEXT[] DEFAULT '{}',
    "notes" TEXT,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT "projects_end_date_after_start" CHECK (end_date IS NULL OR end_date > start_date)
);

-- Project Templates table
CREATE TABLE "public"."project_templates" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(200) NOT NULL,
    "description" TEXT NOT NULL,
    "project_type" VARCHAR(50) NOT NULL CHECK (project_type IN ('maintenance', 'installation', 'renovation', 'emergency', 'consultation', 'inspection', 'repair', 'construction')),
    "priority" VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    "estimated_budget" NUMERIC(12,2) DEFAULT 0 CHECK (estimated_budget >= 0),
    "estimated_duration" INTEGER CHECK (estimated_duration IS NULL OR estimated_duration > 0),
    "tags" TEXT[] DEFAULT '{}',
    "is_system_template" BOOLEAN DEFAULT FALSE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT "project_templates_business_or_system" CHECK (
        (business_id IS NOT NULL AND is_system_template = FALSE) OR 
        (business_id IS NULL AND is_system_template = TRUE)
    )
);

-- Add project_id to jobs table for project-job association
ALTER TABLE "public"."jobs" 
ADD COLUMN IF NOT EXISTS "project_id" UUID REFERENCES "public"."projects"("id") ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX "idx_projects_business_id" ON "public"."projects" ("business_id");
CREATE INDEX "idx_projects_client_id" ON "public"."projects" ("client_id");
CREATE INDEX "idx_projects_status" ON "public"."projects" ("status");
CREATE INDEX "idx_projects_start_date" ON "public"."projects" ("start_date");
CREATE INDEX "idx_projects_manager_id" ON "public"."projects" ("manager_id");
CREATE INDEX "idx_projects_created_date" ON "public"."projects" ("created_date");
CREATE INDEX "idx_projects_project_type" ON "public"."projects" ("project_type");
CREATE INDEX "idx_projects_priority" ON "public"."projects" ("priority");
CREATE INDEX "idx_projects_tags" ON "public"."projects" USING GIN ("tags");

-- Composite indexes for common query patterns
CREATE INDEX "idx_projects_business_status" ON "public"."projects" ("business_id", "status");
CREATE INDEX "idx_projects_business_type" ON "public"."projects" ("business_id", "project_type");
CREATE INDEX "idx_projects_business_priority" ON "public"."projects" ("business_id", "priority");
CREATE INDEX "idx_projects_business_start_date" ON "public"."projects" ("business_id", "start_date");

-- Project templates indexes
CREATE INDEX "idx_project_templates_business_id" ON "public"."project_templates" ("business_id");
CREATE INDEX "idx_project_templates_type" ON "public"."project_templates" ("project_type");
CREATE INDEX "idx_project_templates_system" ON "public"."project_templates" ("is_system_template");
CREATE INDEX "idx_project_templates_business_type" ON "public"."project_templates" ("business_id", "project_type");

-- Jobs project association index
CREATE INDEX "idx_jobs_project_id" ON "public"."jobs" ("project_id");

-- Full-text search index for projects
CREATE INDEX "idx_projects_search" ON "public"."projects" USING gin(to_tsvector('english', name || ' ' || description || ' ' || client_name));

-- Create update trigger function for projects
CREATE OR REPLACE FUNCTION update_projects_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for projects
CREATE TRIGGER projects_update_last_modified
    BEFORE UPDATE ON public.projects
    FOR EACH ROW
    EXECUTE FUNCTION update_projects_last_modified();

-- Create update trigger function for project templates
CREATE OR REPLACE FUNCTION update_project_templates_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for project templates
CREATE TRIGGER project_templates_update_last_modified
    BEFORE UPDATE ON public.project_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_project_templates_last_modified();

-- Row Level Security (RLS) policies for projects
ALTER TABLE "public"."projects" ENABLE ROW LEVEL SECURITY;

-- Policy for projects: users can only access projects from their businesses
CREATE POLICY "projects_business_isolation" ON "public"."projects"
    FOR ALL USING (
        business_id IN (
            SELECT bm.business_id 
            FROM public.business_memberships bm 
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- RLS policies for project templates
ALTER TABLE "public"."project_templates" ENABLE ROW LEVEL SECURITY;

-- Policy for templates: users can access system templates and their business templates
CREATE POLICY "project_templates_access" ON "public"."project_templates"
    FOR ALL USING (
        is_system_template = true OR
        business_id IN (
            SELECT bm.business_id 
            FROM public.business_memberships bm 
            WHERE bm.user_id = auth.uid() 
            AND bm.is_active = true
        )
    );

-- Insert some default system project templates
INSERT INTO "public"."project_templates" (
    "id", "name", "description", "project_type", "priority", 
    "estimated_budget", "estimated_duration", "tags", "is_system_template"
) VALUES
    (
        gen_random_uuid(),
        'Standard HVAC Installation',
        'Complete HVAC system installation for residential properties including equipment, ductwork, and testing',
        'installation',
        'medium',
        12000.00,
        14,
        ARRAY['hvac', 'residential', 'installation'],
        true
    ),
    (
        gen_random_uuid(),
        'Kitchen Renovation',
        'Full kitchen renovation including cabinets, countertops, appliances, and flooring',
        'renovation',
        'high',
        25000.00,
        21,
        ARRAY['kitchen', 'renovation', 'residential'],
        true
    ),
    (
        gen_random_uuid(),
        'Bathroom Remodel',
        'Complete bathroom remodeling including plumbing, tiling, fixtures, and vanity installation',
        'renovation',
        'medium',
        15000.00,
        14,
        ARRAY['bathroom', 'renovation', 'residential'],
        true
    ),
    (
        gen_random_uuid(),
        'Routine Maintenance Service',
        'Regular maintenance service including inspection, cleaning, and minor repairs',
        'maintenance',
        'low',
        500.00,
        3,
        ARRAY['maintenance', 'routine', 'service'],
        true
    ),
    (
        gen_random_uuid(),
        'Emergency Repair Service',
        'Emergency repair service for urgent issues requiring immediate attention',
        'emergency',
        'critical',
        2000.00,
        1,
        ARRAY['emergency', 'repair', 'urgent'],
        true
    ),
    (
        gen_random_uuid(),
        'Home Inspection',
        'Comprehensive home inspection service including systems, structure, and safety checks',
        'inspection',
        'medium',
        800.00,
        1,
        ARRAY['inspection', 'assessment', 'residential'],
        true
    ),
    (
        gen_random_uuid(),
        'New Construction Project',
        'Complete new construction project from foundation to finish',
        'construction',
        'high',
        150000.00,
        120,
        ARRAY['construction', 'new-build', 'residential'],
        true
    ),
    (
        gen_random_uuid(),
        'Consultation Service',
        'Professional consultation and assessment service for project planning',
        'consultation',
        'low',
        300.00,
        1,
        ARRAY['consultation', 'planning', 'assessment'],
        true
    );

-- Add helpful comments
COMMENT ON TABLE "public"."projects" IS 'Core projects table for tracking construction and service projects';
COMMENT ON COLUMN "public"."projects"."created_by" IS 'User ID of the person who created this project';
COMMENT ON COLUMN "public"."projects"."client_id" IS 'Reference to the contact/client for this project';
COMMENT ON COLUMN "public"."projects"."team_members" IS 'Array of user IDs assigned to this project';
COMMENT ON COLUMN "public"."projects"."tags" IS 'Array of tags for categorizing and searching projects';
COMMENT ON COLUMN "public"."projects"."estimated_budget" IS 'Estimated budget for the project in business currency';
COMMENT ON COLUMN "public"."projects"."actual_cost" IS 'Actual cost incurred for the project';

COMMENT ON TABLE "public"."project_templates" IS 'Templates for creating standardized projects';
COMMENT ON COLUMN "public"."project_templates"."business_id" IS 'NULL for system templates, business ID for custom templates';
COMMENT ON COLUMN "public"."project_templates"."is_system_template" IS 'TRUE for system-provided templates, FALSE for business-created templates';
COMMENT ON COLUMN "public"."project_templates"."estimated_duration" IS 'Estimated project duration in days'; 