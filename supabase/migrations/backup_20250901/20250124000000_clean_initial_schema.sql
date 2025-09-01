-- Hero365 Clean Initial Schema
-- This migration consolidates all previous migrations into a clean starting point
-- Date: 2025-01-24
-- Version: Clean Development Schema

-- Drop all existing tables to start fresh
DROP TABLE IF EXISTS public.workload_capacity CASCADE;
DROP TABLE IF EXISTS public.user_skills CASCADE;
DROP TABLE IF EXISTS public.user_certifications CASCADE;
DROP TABLE IF EXISTS public.user_capabilities CASCADE;
DROP TABLE IF EXISTS public.time_off_requests CASCADE;
DROP TABLE IF EXISTS public.working_hours_templates CASCADE;
DROP TABLE IF EXISTS public.calendar_preferences CASCADE;
DROP TABLE IF EXISTS public.calendar_events CASCADE;
DROP TABLE IF EXISTS public.availability_windows CASCADE;
DROP TABLE IF EXISTS public.activity_templates CASCADE;
DROP TABLE IF EXISTS public.activity_reminders CASCADE;
DROP TABLE IF EXISTS public.activity_participants CASCADE;
DROP TABLE IF EXISTS public.activities CASCADE;
DROP TABLE IF EXISTS public.job_templates CASCADE;
DROP TABLE IF EXISTS public.job_attachments CASCADE;
DROP TABLE IF EXISTS public.job_notes CASCADE;
DROP TABLE IF EXISTS public.job_activities CASCADE;
DROP TABLE IF EXISTS public.jobs CASCADE;
DROP TABLE IF EXISTS public.contact_segment_memberships CASCADE;
DROP TABLE IF EXISTS public.contact_segments CASCADE;
DROP TABLE IF EXISTS public.contact_notes CASCADE;
DROP TABLE IF EXISTS public.contact_activities CASCADE;
DROP TABLE IF EXISTS public.contacts CASCADE;
DROP TABLE IF EXISTS public.departments CASCADE;
DROP TABLE IF EXISTS public.business_invitations CASCADE;
DROP TABLE IF EXISTS public.business_memberships CASCADE;
DROP TABLE IF EXISTS public.businesses CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Users table (synced with auth.users)
CREATE TABLE "public"."users" (
    "id" UUID PRIMARY KEY,
    "email" VARCHAR(320) NOT NULL UNIQUE,
    "full_name" VARCHAR(255),
    "display_name" VARCHAR(255) NOT NULL,
    "avatar_url" VARCHAR(500),
    "phone" VARCHAR(20),
    "is_active" BOOLEAN DEFAULT TRUE,
    "last_sign_in" TIMESTAMP WITH TIME ZONE,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Businesses
CREATE TABLE "public"."businesses" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "name" VARCHAR(255) NOT NULL,
    "display_name" VARCHAR(255),
    "description" TEXT,
    "industry" VARCHAR(100),
    "company_size" VARCHAR(50),
    "website" VARCHAR(500),
    "logo_url" VARCHAR(500),
    "phone" VARCHAR(20),
    "email" VARCHAR(320),
    "address" TEXT,
    "city" VARCHAR(100),
    "state" VARCHAR(100),
    "postal_code" VARCHAR(20),
    "country" VARCHAR(100) DEFAULT 'US',
    "timezone" VARCHAR(100) DEFAULT 'UTC',
    "owner_id" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE CASCADE,
    "referral_source" VARCHAR(100),
    "onboarding_completed" BOOLEAN DEFAULT FALSE,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Business Memberships
CREATE TABLE "public"."business_memberships" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE CASCADE,
    "role" VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'manager', 'employee', 'contractor', 'viewer')),
    "permissions" JSONB DEFAULT '[]' NOT NULL,
    "joined_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    "invited_date" TIMESTAMP WITH TIME ZONE,
    "invited_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "is_active" BOOLEAN DEFAULT TRUE,
    "department_id" UUID,
    "job_title" VARCHAR(100),
    CONSTRAINT "business_memberships_permissions_not_empty" CHECK (jsonb_array_length(permissions) > 0),
    UNIQUE(business_id, user_id)
);

-- Business Invitations
CREATE TABLE "public"."business_invitations" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "business_name" VARCHAR(255) NOT NULL,
    "invited_email" VARCHAR(320),
    "invited_phone" VARCHAR(20),
    "invited_by" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "invited_by_name" VARCHAR(255) NOT NULL,
    "role" VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'manager', 'employee', 'contractor', 'viewer')),
    "permissions" JSONB DEFAULT '[]' NOT NULL,
    "invitation_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    "expiry_date" TIMESTAMP WITH TIME ZONE NOT NULL,
    "status" VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired', 'cancelled')),
    "message" TEXT,
    "accepted_date" TIMESTAMP WITH TIME ZONE,
    "declined_date" TIMESTAMP WITH TIME ZONE,
    CONSTRAINT "business_invitations_contact_required" CHECK (
        (invited_email IS NOT NULL AND invited_email <> '') OR 
        (invited_phone IS NOT NULL AND invited_phone <> '')
    ),
    CONSTRAINT "business_invitations_email_format" CHECK (
        invited_email IS NULL OR invited_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT "business_invitations_expiry_future" CHECK (expiry_date > invitation_date),
    CONSTRAINT "business_invitations_permissions_not_empty" CHECK (jsonb_array_length(permissions) > 0)
);

-- Departments  
CREATE TABLE "public"."departments" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "manager_id" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contacts
CREATE TABLE "public"."contacts" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "first_name" VARCHAR(100),
    "last_name" VARCHAR(100),
    "company_name" VARCHAR(255),
    "email" VARCHAR(320),
    "phone" VARCHAR(20),
    "mobile_phone" VARCHAR(20),
    "address" TEXT,
    "city" VARCHAR(100),
    "state" VARCHAR(100),
    "postal_code" VARCHAR(20),
    "country" VARCHAR(100) DEFAULT 'US',
    "contact_type" VARCHAR(50) DEFAULT 'individual',
    "source" VARCHAR(100) DEFAULT 'manual',
    "status" VARCHAR(50) DEFAULT 'active',
    "lifecycle_stage" VARCHAR(50) DEFAULT 'lead',
    "priority" VARCHAR(20) DEFAULT 'medium',
    "relationship_status" VARCHAR(50) DEFAULT 'new',
    "tags" TEXT[],
    "notes" TEXT,
    "created_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "assigned_to" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "last_contacted" TIMESTAMP WITH TIME ZONE,
    "next_contact_date" DATE,
    "status_history" JSONB DEFAULT '[]',
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs
CREATE TABLE "public"."jobs" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "job_number" VARCHAR(50) NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "job_type" VARCHAR(100) DEFAULT 'service',
    "status" VARCHAR(50) DEFAULT 'draft',
    "priority" VARCHAR(20) DEFAULT 'medium',
    "source" VARCHAR(100) DEFAULT 'manual',
    "contact_id" UUID REFERENCES "public"."contacts"("id") ON DELETE SET NULL,
    "assigned_to" UUID[],
    "estimated_duration_hours" NUMERIC(8,2),
    "actual_duration_hours" NUMERIC(8,2),
    "estimated_cost" NUMERIC(10,2),
    "actual_cost" NUMERIC(10,2),
    "scheduled_start" TIMESTAMP WITH TIME ZONE,
    "scheduled_end" TIMESTAMP WITH TIME ZONE,
    "actual_start" TIMESTAMP WITH TIME ZONE,
    "actual_end" TIMESTAMP WITH TIME ZONE,
    "location_address" TEXT,
    "location_city" VARCHAR(100),
    "location_state" VARCHAR(100),
    "location_postal_code" VARCHAR(20),
    "location_country" VARCHAR(100) DEFAULT 'US',
    "location_latitude" NUMERIC(10,8),
    "location_longitude" NUMERIC(11,8),
    "special_instructions" TEXT,
    "internal_notes" TEXT,
    "created_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_id, job_number)
);

-- Activities  
CREATE TABLE "public"."activities" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "activity_type" VARCHAR(50) DEFAULT 'task',
    "status" VARCHAR(50) DEFAULT 'pending',
    "priority" VARCHAR(20) DEFAULT 'medium',
    "contact_id" UUID REFERENCES "public"."contacts"("id") ON DELETE CASCADE,
    "assigned_to" UUID[],
    "due_date" TIMESTAMP WITH TIME ZONE,
    "completed_date" TIMESTAMP WITH TIME ZONE,
    "estimated_duration_minutes" INTEGER,
    "actual_duration_minutes" INTEGER,
    "outcome" VARCHAR(100),
    "notes" TEXT,
    "template_id" UUID,
    "parent_activity_id" UUID REFERENCES "public"."activities"("id") ON DELETE SET NULL,
    "is_recurring" BOOLEAN DEFAULT FALSE,
    "recurrence_pattern" JSONB,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contact Activities
CREATE TABLE "public"."contact_activities" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "contact_id" UUID NOT NULL REFERENCES "public"."contacts"("id") ON DELETE CASCADE,
    "activity_type" VARCHAR(50) DEFAULT 'interaction',
    "description" TEXT,
    "activity_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "performed_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "outcome" VARCHAR(100),
    "notes" TEXT,
    "metadata" JSONB DEFAULT '{}',
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contact Notes
CREATE TABLE "public"."contact_notes" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "contact_id" UUID NOT NULL REFERENCES "public"."contacts"("id") ON DELETE CASCADE,
    "note_type" VARCHAR(50) DEFAULT 'general',
    "content" TEXT NOT NULL,
    "is_private" BOOLEAN DEFAULT FALSE,
    "created_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contact Segments
CREATE TABLE "public"."contact_segments" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "segment_type" VARCHAR(50) DEFAULT 'manual',
    "criteria" JSONB DEFAULT '{}',
    "created_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contact Segment Memberships
CREATE TABLE "public"."contact_segment_memberships" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "contact_id" UUID NOT NULL REFERENCES "public"."contacts"("id") ON DELETE CASCADE,
    "segment_id" UUID NOT NULL REFERENCES "public"."contact_segments"("id") ON DELETE CASCADE,
    "added_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "added_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    UNIQUE(contact_id, segment_id)
);

-- Job Activities
CREATE TABLE "public"."job_activities" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "job_id" UUID NOT NULL REFERENCES "public"."jobs"("id") ON DELETE CASCADE,
    "activity_type" VARCHAR(50) DEFAULT 'status_change',
    "description" TEXT NOT NULL,
    "performed_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "user_id" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "old_status" VARCHAR(50),
    "new_status" VARCHAR(50),
    "metadata" JSONB DEFAULT '{}',
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job Notes
CREATE TABLE "public"."job_notes" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "job_id" UUID NOT NULL REFERENCES "public"."jobs"("id") ON DELETE CASCADE,
    "note_type" VARCHAR(50) DEFAULT 'general',
    "content" TEXT NOT NULL,
    "is_internal" BOOLEAN DEFAULT FALSE,
    "user_id" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job Templates
CREATE TABLE "public"."job_templates" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "job_type" VARCHAR(100),
    "estimated_duration_hours" NUMERIC(8,2),
    "estimated_cost" NUMERIC(10,2),
    "checklist" JSONB DEFAULT '[]',
    "required_skills" TEXT[],
    "instructions" TEXT,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job Attachments
CREATE TABLE "public"."job_attachments" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "job_id" UUID NOT NULL REFERENCES "public"."jobs"("id") ON DELETE CASCADE,
    "file_name" VARCHAR(255) NOT NULL,
    "file_url" VARCHAR(500) NOT NULL,
    "file_type" VARCHAR(50),
    "file_size" INTEGER,
    "uploaded_by" UUID REFERENCES "public"."users"("id") ON DELETE SET NULL,
    "upload_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Capabilities
CREATE TABLE "public"."user_capabilities" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE CASCADE,
    "home_base_address" TEXT,
    "home_base_latitude" NUMERIC(10,8),
    "home_base_longitude" NUMERIC(11,8),
    "vehicle_type" VARCHAR(50),
    "has_vehicle" BOOLEAN DEFAULT TRUE,
    "preferred_start_time" TIME,
    "preferred_end_time" TIME,
    "min_time_between_jobs_minutes" INTEGER DEFAULT 30,
    "max_commute_time_minutes" INTEGER DEFAULT 60,
    "average_job_rating" NUMERIC(3,2),
    "completion_rate" NUMERIC(5,2),
    "punctuality_score" NUMERIC(5,2),
    "working_hours_template_id" UUID,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "is_active" BOOLEAN DEFAULT TRUE,
    UNIQUE(business_id, user_id)
);

-- Working Hours Templates
CREATE TABLE "public"."working_hours_templates" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "monday_start" TIME,
    "monday_end" TIME,
    "tuesday_start" TIME,
    "tuesday_end" TIME,
    "wednesday_start" TIME,
    "wednesday_end" TIME,
    "thursday_start" TIME,
    "thursday_end" TIME,
    "friday_start" TIME,
    "friday_end" TIME,
    "saturday_start" TIME,
    "saturday_end" TIME,
    "sunday_start" TIME,
    "sunday_end" TIME,
    "break_duration_minutes" INTEGER DEFAULT 30,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Calendar Events
CREATE TABLE "public"."calendar_events" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE CASCADE,
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "title" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "event_type" VARCHAR(50) DEFAULT 'work_schedule',
    "start_datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
    "end_datetime" TIMESTAMP WITH TIME ZONE NOT NULL,
    "is_all_day" BOOLEAN DEFAULT FALSE,
    "timezone" VARCHAR(100) DEFAULT 'UTC',
    "recurrence_type" VARCHAR(20) DEFAULT 'none',
    "recurrence_end_date" DATE,
    "recurrence_count" INTEGER,
    "recurrence_interval" INTEGER DEFAULT 1,
    "recurrence_days_of_week" INTEGER[] DEFAULT '{}',
    "blocks_scheduling" BOOLEAN DEFAULT TRUE,
    "allows_emergency_override" BOOLEAN DEFAULT FALSE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "is_active" BOOLEAN DEFAULT TRUE
);

-- Calendar Preferences
CREATE TABLE "public"."calendar_preferences" (
    "user_id" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE CASCADE,
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "timezone" VARCHAR(100) DEFAULT 'UTC',
    "date_format" VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    "time_format" VARCHAR(5) DEFAULT '24h',
    "week_start_day" INTEGER DEFAULT 0,
    "preferred_working_hours_template_id" UUID REFERENCES "public"."working_hours_templates"("id") ON DELETE SET NULL,
    "min_time_between_jobs_minutes" INTEGER DEFAULT 30,
    "max_commute_time_minutes" INTEGER DEFAULT 60,
    "allows_back_to_back_jobs" BOOLEAN DEFAULT FALSE,
    "requires_prep_time_minutes" INTEGER DEFAULT 15,
    "job_reminder_minutes_before" INTEGER[] DEFAULT '{60,15}',
    "schedule_change_notifications" BOOLEAN DEFAULT TRUE,
    "new_job_notifications" BOOLEAN DEFAULT TRUE,
    "cancellation_notifications" BOOLEAN DEFAULT TRUE,
    "auto_accept_jobs_in_hours" BOOLEAN DEFAULT FALSE,
    "auto_decline_outside_hours" BOOLEAN DEFAULT TRUE,
    "emergency_availability_outside_hours" BOOLEAN DEFAULT FALSE,
    "weekend_availability" BOOLEAN DEFAULT FALSE,
    "holiday_availability" BOOLEAN DEFAULT FALSE,
    "travel_buffer_percentage" NUMERIC(3,2) DEFAULT 1.20,
    "job_buffer_minutes" INTEGER DEFAULT 15,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, business_id)
);

-- Activity Templates
CREATE TABLE "public"."activity_templates" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "business_id" UUID NOT NULL REFERENCES "public"."businesses"("id") ON DELETE CASCADE,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "activity_type" VARCHAR(50) DEFAULT 'task',
    "estimated_duration_minutes" INTEGER,
    "checklist" JSONB DEFAULT '[]',
    "instructions" TEXT,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "last_modified" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activity Participants
CREATE TABLE "public"."activity_participants" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "activity_id" UUID NOT NULL REFERENCES "public"."activities"("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "public"."users"("id") ON DELETE CASCADE,
    "role" VARCHAR(50) DEFAULT 'participant',
    "added_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(activity_id, user_id)
);

-- Activity Reminders
CREATE TABLE "public"."activity_reminders" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "activity_id" UUID NOT NULL REFERENCES "public"."activities"("id") ON DELETE CASCADE,
    "reminder_type" VARCHAR(50) DEFAULT 'email',
    "reminder_time" TIMESTAMP WITH TIME ZONE NOT NULL,
    "message" TEXT,
    "is_sent" BOOLEAN DEFAULT FALSE,
    "sent_date" TIMESTAMP WITH TIME ZONE,
    "created_date" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX "idx_users_email" ON "public"."users" ("email");
CREATE INDEX "idx_users_display_name" ON "public"."users" ("display_name");
CREATE INDEX "idx_users_is_active" ON "public"."users" ("is_active") WHERE is_active = TRUE;

CREATE INDEX "idx_businesses_owner_id" ON "public"."businesses" ("owner_id");
CREATE INDEX "idx_businesses_is_active" ON "public"."businesses" ("is_active") WHERE is_active = TRUE;

CREATE INDEX "idx_business_memberships_business_id" ON "public"."business_memberships" ("business_id");
CREATE INDEX "idx_business_memberships_user_id" ON "public"."business_memberships" ("user_id");
CREATE INDEX "idx_business_memberships_active" ON "public"."business_memberships" ("is_active") WHERE is_active = TRUE;

CREATE INDEX "idx_contacts_business_id" ON "public"."contacts" ("business_id");
CREATE INDEX "idx_contacts_created_by" ON "public"."contacts" ("created_by");
CREATE INDEX "idx_contacts_assigned_to" ON "public"."contacts" ("assigned_to");
CREATE INDEX "idx_contacts_status" ON "public"."contacts" ("status");

CREATE INDEX "idx_jobs_business_id" ON "public"."jobs" ("business_id");
CREATE INDEX "idx_jobs_contact_id" ON "public"."jobs" ("contact_id");
CREATE INDEX "idx_jobs_status" ON "public"."jobs" ("status");
CREATE INDEX "idx_jobs_scheduled_start" ON "public"."jobs" ("scheduled_start");

CREATE INDEX "idx_activities_business_id" ON "public"."activities" ("business_id");
CREATE INDEX "idx_activities_contact_id" ON "public"."activities" ("contact_id");
CREATE INDEX "idx_activities_status" ON "public"."activities" ("status");
CREATE INDEX "idx_activities_due_date" ON "public"."activities" ("due_date");

CREATE INDEX "idx_contact_activities_business_id" ON "public"."contact_activities" ("business_id");
CREATE INDEX "idx_contact_activities_contact_id" ON "public"."contact_activities" ("contact_id");
CREATE INDEX "idx_contact_activities_performed_by" ON "public"."contact_activities" ("performed_by");
CREATE INDEX "idx_contact_activities_activity_date" ON "public"."contact_activities" ("activity_date");

CREATE INDEX "idx_contact_notes_business_id" ON "public"."contact_notes" ("business_id");
CREATE INDEX "idx_contact_notes_contact_id" ON "public"."contact_notes" ("contact_id");
CREATE INDEX "idx_contact_notes_created_by" ON "public"."contact_notes" ("created_by");

CREATE INDEX "idx_job_activities_business_id" ON "public"."job_activities" ("business_id");
CREATE INDEX "idx_job_activities_job_id" ON "public"."job_activities" ("job_id");
CREATE INDEX "idx_job_activities_user_id" ON "public"."job_activities" ("user_id");

CREATE INDEX "idx_job_notes_business_id" ON "public"."job_notes" ("business_id");
CREATE INDEX "idx_job_notes_job_id" ON "public"."job_notes" ("job_id");
CREATE INDEX "idx_job_notes_user_id" ON "public"."job_notes" ("user_id");

CREATE INDEX "idx_user_capabilities_business_id" ON "public"."user_capabilities" ("business_id");
CREATE INDEX "idx_user_capabilities_user_id" ON "public"."user_capabilities" ("user_id");
CREATE INDEX "idx_user_capabilities_active" ON "public"."user_capabilities" ("is_active") WHERE is_active = TRUE;

CREATE INDEX "idx_calendar_events_user_business" ON "public"."calendar_events" ("user_id", "business_id");
CREATE INDEX "idx_calendar_events_datetime" ON "public"."calendar_events" ("start_datetime", "end_datetime");
CREATE INDEX "idx_calendar_events_active" ON "public"."calendar_events" ("is_active") WHERE is_active = TRUE;

CREATE INDEX "idx_working_hours_templates_active" ON "public"."working_hours_templates" ("is_active") WHERE is_active = TRUE;

-- Functions for triggers
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_businesses_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_default_permissions_for_role(role_name TEXT)
RETURNS JSONB AS $$
BEGIN
    RETURN CASE role_name
        WHEN 'owner' THEN '["*"]'::jsonb
        WHEN 'admin' THEN '["manage_team", "view_team_members", "invite_team_members", "manage_contacts", "view_contacts", "manage_jobs", "view_jobs", "manage_activities", "view_activities"]'::jsonb
        WHEN 'manager' THEN '["view_team_members", "manage_contacts", "view_contacts", "manage_jobs", "view_jobs", "manage_activities", "view_activities"]'::jsonb
        WHEN 'employee' THEN '["view_contacts", "manage_own_jobs", "view_jobs", "manage_own_activities", "view_activities"]'::jsonb
        WHEN 'contractor' THEN '["view_contacts", "manage_own_jobs", "view_own_jobs", "manage_own_activities", "view_own_activities"]'::jsonb
        WHEN 'viewer' THEN '["view_contacts", "view_jobs", "view_activities"]'::jsonb
        ELSE '[]'::jsonb
    END;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION assign_default_permissions()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.permissions = '[]'::jsonb OR NEW.permissions IS NULL THEN
        NEW.permissions = get_default_permissions_for_role(NEW.role);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Sync function to automatically create/update public.users when auth.users changes
CREATE OR REPLACE FUNCTION sync_user_data()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        INSERT INTO public.users (
            id,
            email,
            full_name,
            display_name,
            avatar_url,
            phone,
            last_sign_in,
            updated_at
        )
        VALUES (
            NEW.id,
            NEW.email,
            COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
            COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email),
            NEW.raw_user_meta_data->>'avatar_url',
            NEW.raw_user_meta_data->>'phone',
            NEW.last_sign_in_at,
            NOW()
        )
        ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            full_name = COALESCE(EXCLUDED.full_name, users.full_name),
            display_name = COALESCE(EXCLUDED.display_name, users.display_name),
            avatar_url = COALESCE(EXCLUDED.avatar_url, users.avatar_url),
            phone = COALESCE(EXCLUDED.phone, users.phone),
            last_sign_in = EXCLUDED.last_sign_in,
            updated_at = NOW();
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Don't actually delete users, just mark as inactive
        UPDATE public.users SET is_active = FALSE WHERE id = OLD.id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Triggers
CREATE TRIGGER users_update_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();

CREATE TRIGGER businesses_update_last_modified
    BEFORE UPDATE ON public.businesses
    FOR EACH ROW
    EXECUTE FUNCTION update_businesses_last_modified();

CREATE TRIGGER trigger_assign_default_permissions
    BEFORE INSERT OR UPDATE ON public.business_memberships
    FOR EACH ROW
    EXECUTE FUNCTION assign_default_permissions();

-- Trigger to sync auth.users with public.users
CREATE TRIGGER sync_user_data_trigger
    AFTER INSERT OR UPDATE OR DELETE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION sync_user_data();

-- Enable RLS
ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."businesses" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."business_memberships" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."business_invitations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."departments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."contacts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."jobs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."activities" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."contact_activities" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."contact_notes" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."contact_segments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."contact_segment_memberships" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."job_activities" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."job_notes" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."job_templates" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."job_attachments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."user_capabilities" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."calendar_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."calendar_preferences" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."activity_templates" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."activity_participants" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."activity_reminders" ENABLE ROW LEVEL SECURITY;

-- RLS Policies (simplified for development)
CREATE POLICY "users_business_isolation" ON "public"."users"
FOR ALL USING (
    EXISTS (
        SELECT 1 FROM business_memberships bm1
        JOIN business_memberships bm2 ON bm1.business_id = bm2.business_id
        WHERE bm1.user_id = current_setting('app.current_user_id', true)::uuid
        AND bm2.user_id = users.id
        AND bm1.is_active = TRUE
        AND bm2.is_active = TRUE
    )
);

CREATE POLICY "businesses_business_isolation" ON "public"."businesses"
FOR ALL USING (
    id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "business_memberships_business_isolation" ON "public"."business_memberships"
FOR ALL USING (
    user_id = current_setting('app.current_user_id', true)::uuid
    OR business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
        AND permissions @> '["view_team_members"]'
    )
);

CREATE POLICY "contacts_business_isolation" ON "public"."contacts"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "jobs_business_isolation" ON "public"."jobs"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "activities_business_isolation" ON "public"."activities"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "contact_activities_business_isolation" ON "public"."contact_activities"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "contact_notes_business_isolation" ON "public"."contact_notes"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "contact_segments_business_isolation" ON "public"."contact_segments"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "job_activities_business_isolation" ON "public"."job_activities"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "job_notes_business_isolation" ON "public"."job_notes"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "user_capabilities_business_isolation" ON "public"."user_capabilities"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "calendar_events_business_isolation" ON "public"."calendar_events"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "activity_templates_business_isolation" ON "public"."activity_templates"
FOR ALL USING (
    business_id IN (
        SELECT business_id FROM business_memberships
        WHERE user_id = current_setting('app.current_user_id', true)::uuid
        AND is_active = TRUE
    )
);

CREATE POLICY "working_hours_templates_public_read" ON "public"."working_hours_templates"
FOR SELECT USING (true);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon;

-- Comments
COMMENT ON TABLE "public"."users" IS 'User profiles for development - independent of auth.users';
COMMENT ON TABLE "public"."businesses" IS 'Business entities in the system';
COMMENT ON TABLE "public"."business_memberships" IS 'User memberships in businesses with roles and permissions';
COMMENT ON TABLE "public"."contacts" IS 'Contact management for businesses';
COMMENT ON TABLE "public"."jobs" IS 'Job/work order management';
COMMENT ON TABLE "public"."activities" IS 'Activity/task management'; 