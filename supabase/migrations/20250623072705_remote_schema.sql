alter table "public"."business_invitations" drop constraint "business_invitations_role_check";

alter table "public"."business_invitations" drop constraint "business_invitations_status_check";

alter table "public"."business_memberships" drop constraint "business_memberships_role_check";

alter table "public"."businesses" drop constraint "businesses_company_size_check";

alter table "public"."businesses" drop constraint "businesses_referral_source_check";

alter table "public"."contact_activities" drop constraint "contact_activities_activity_type_check";

alter table "public"."contact_activities" drop constraint "contact_activities_outcome_check";

alter table "public"."contact_notes" drop constraint "contact_notes_note_type_check";

alter table "public"."contact_segments" drop constraint "contact_segments_segment_type_check";

alter table "public"."contacts" drop constraint "contacts_contact_type_check";

alter table "public"."contacts" drop constraint "contacts_priority_check";

alter table "public"."contacts" drop constraint "contacts_source_check";

alter table "public"."contacts" drop constraint "contacts_status_check";

create table "public"."job_activities" (
    "id" uuid not null default uuid_generate_v4(),
    "job_id" uuid not null,
    "business_id" uuid not null,
    "user_id" text not null,
    "activity_type" character varying(50) not null,
    "description" text not null,
    "old_values" jsonb default '{}'::jsonb,
    "new_values" jsonb default '{}'::jsonb,
    "metadata" jsonb default '{}'::jsonb,
    "created_date" timestamp with time zone default now()
);


create table "public"."job_attachments" (
    "id" uuid not null default uuid_generate_v4(),
    "job_id" uuid not null,
    "business_id" uuid not null,
    "user_id" text not null,
    "file_name" character varying(255) not null,
    "file_path" text not null,
    "file_size" integer not null,
    "file_type" character varying(100) not null,
    "mime_type" character varying(100),
    "description" text,
    "is_public" boolean default false,
    "created_date" timestamp with time zone default now()
);


create table "public"."job_notes" (
    "id" uuid not null default uuid_generate_v4(),
    "job_id" uuid not null,
    "business_id" uuid not null,
    "user_id" text not null,
    "note_type" character varying(20) not null default 'general'::character varying,
    "title" character varying(255),
    "content" text not null,
    "is_private" boolean default false,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


create table "public"."job_templates" (
    "id" uuid not null default uuid_generate_v4(),
    "business_id" uuid not null,
    "name" character varying(255) not null,
    "description" text,
    "job_type" character varying(20) not null,
    "priority" character varying(20) not null default 'medium'::character varying,
    "estimated_duration_hours" numeric(10,2),
    "default_cost_estimate" jsonb default '{}'::jsonb,
    "default_tags" text[] default '{}'::text[],
    "template_data" jsonb default '{}'::jsonb,
    "is_active" boolean default true,
    "created_by" text not null,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


create table "public"."jobs" (
    "id" uuid not null default uuid_generate_v4(),
    "business_id" uuid not null,
    "contact_id" uuid,
    "job_number" character varying(50) not null,
    "title" character varying(255) not null,
    "description" text,
    "job_type" character varying(20) not null,
    "status" character varying(20) not null default 'draft'::character varying,
    "priority" character varying(20) not null default 'medium'::character varying,
    "source" character varying(20) not null default 'other'::character varying,
    "job_address" jsonb not null,
    "scheduled_start" timestamp with time zone,
    "scheduled_end" timestamp with time zone,
    "actual_start" timestamp with time zone,
    "actual_end" timestamp with time zone,
    "assigned_to" text[] default '{}'::text[],
    "created_by" text not null,
    "time_tracking" jsonb default '{}'::jsonb,
    "cost_estimate" jsonb default '{}'::jsonb,
    "tags" text[] default '{}'::text[],
    "notes" text,
    "internal_notes" text,
    "customer_requirements" text,
    "completion_notes" text,
    "custom_fields" jsonb default '{}'::jsonb,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now(),
    "completed_date" timestamp with time zone
);


CREATE INDEX idx_job_activities_business_id ON public.job_activities USING btree (business_id);

CREATE INDEX idx_job_activities_created_date ON public.job_activities USING btree (created_date);

CREATE INDEX idx_job_activities_job_id ON public.job_activities USING btree (job_id);

CREATE INDEX idx_job_activities_type ON public.job_activities USING btree (activity_type);

CREATE INDEX idx_job_activities_user_id ON public.job_activities USING btree (user_id);

CREATE INDEX idx_job_attachments_business_id ON public.job_attachments USING btree (business_id);

CREATE INDEX idx_job_attachments_file_type ON public.job_attachments USING btree (file_type);

CREATE INDEX idx_job_attachments_job_id ON public.job_attachments USING btree (job_id);

CREATE INDEX idx_job_attachments_user_id ON public.job_attachments USING btree (user_id);

CREATE INDEX idx_job_notes_business_id ON public.job_notes USING btree (business_id);

CREATE INDEX idx_job_notes_created_date ON public.job_notes USING btree (created_date);

CREATE INDEX idx_job_notes_job_id ON public.job_notes USING btree (job_id);

CREATE INDEX idx_job_notes_note_type ON public.job_notes USING btree (note_type);

CREATE INDEX idx_job_notes_user_id ON public.job_notes USING btree (user_id);

CREATE INDEX idx_job_templates_active ON public.job_templates USING btree (business_id, is_active);

CREATE INDEX idx_job_templates_business_id ON public.job_templates USING btree (business_id);

CREATE INDEX idx_job_templates_job_type ON public.job_templates USING btree (business_id, job_type);

CREATE INDEX idx_jobs_actual_end ON public.jobs USING btree (business_id, actual_end);

CREATE INDEX idx_jobs_actual_start ON public.jobs USING btree (business_id, actual_start);

CREATE INDEX idx_jobs_assigned_status ON public.jobs USING gin (assigned_to) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

CREATE INDEX idx_jobs_assigned_to ON public.jobs USING gin (assigned_to);

CREATE INDEX idx_jobs_business_id ON public.jobs USING btree (business_id);

CREATE INDEX idx_jobs_completed_date ON public.jobs USING btree (business_id, completed_date);

CREATE INDEX idx_jobs_contact_id ON public.jobs USING btree (contact_id);

CREATE INDEX idx_jobs_cost_estimate ON public.jobs USING gin (cost_estimate);

CREATE INDEX idx_jobs_created_by ON public.jobs USING btree (created_by);

CREATE INDEX idx_jobs_created_date ON public.jobs USING btree (business_id, created_date);

CREATE INDEX idx_jobs_custom_fields ON public.jobs USING gin (custom_fields);

CREATE INDEX idx_jobs_description_search ON public.jobs USING gin (to_tsvector('english'::regconfig, description));

CREATE INDEX idx_jobs_job_address ON public.jobs USING gin (job_address);

CREATE INDEX idx_jobs_job_number ON public.jobs USING btree (business_id, job_number);

CREATE INDEX idx_jobs_job_type ON public.jobs USING btree (business_id, job_type);

CREATE INDEX idx_jobs_last_modified ON public.jobs USING btree (business_id, last_modified);

CREATE INDEX idx_jobs_priority ON public.jobs USING btree (business_id, priority);

CREATE INDEX idx_jobs_scheduled_end ON public.jobs USING btree (business_id, scheduled_end);

CREATE INDEX idx_jobs_scheduled_end_active ON public.jobs USING btree (business_id, scheduled_end) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

CREATE INDEX idx_jobs_scheduled_start ON public.jobs USING btree (business_id, scheduled_start);

CREATE INDEX idx_jobs_source ON public.jobs USING btree (business_id, source);

CREATE INDEX idx_jobs_status ON public.jobs USING btree (business_id, status);

CREATE INDEX idx_jobs_status_priority ON public.jobs USING btree (business_id, status, priority);

CREATE INDEX idx_jobs_tags ON public.jobs USING gin (tags);

CREATE INDEX idx_jobs_time_tracking ON public.jobs USING gin (time_tracking);

CREATE INDEX idx_jobs_title_search ON public.jobs USING gin (to_tsvector('english'::regconfig, (title)::text));

CREATE INDEX idx_jobs_type_status ON public.jobs USING btree (business_id, job_type, status);

CREATE UNIQUE INDEX job_activities_pkey ON public.job_activities USING btree (id);

CREATE UNIQUE INDEX job_attachments_pkey ON public.job_attachments USING btree (id);

CREATE UNIQUE INDEX job_notes_pkey ON public.job_notes USING btree (id);

CREATE UNIQUE INDEX job_templates_business_id_name_key ON public.job_templates USING btree (business_id, name);

CREATE UNIQUE INDEX job_templates_pkey ON public.job_templates USING btree (id);

CREATE UNIQUE INDEX jobs_business_id_job_number_key ON public.jobs USING btree (business_id, job_number);

CREATE UNIQUE INDEX jobs_pkey ON public.jobs USING btree (id);

alter table "public"."job_activities" add constraint "job_activities_pkey" PRIMARY KEY using index "job_activities_pkey";

alter table "public"."job_attachments" add constraint "job_attachments_pkey" PRIMARY KEY using index "job_attachments_pkey";

alter table "public"."job_notes" add constraint "job_notes_pkey" PRIMARY KEY using index "job_notes_pkey";

alter table "public"."job_templates" add constraint "job_templates_pkey" PRIMARY KEY using index "job_templates_pkey";

alter table "public"."jobs" add constraint "jobs_pkey" PRIMARY KEY using index "jobs_pkey";

alter table "public"."job_activities" add constraint "job_activities_activity_type_check" CHECK (((activity_type)::text = ANY ((ARRAY['created'::character varying, 'updated'::character varying, 'status_changed'::character varying, 'assigned'::character varying, 'unassigned'::character varying, 'started'::character varying, 'paused'::character varying, 'resumed'::character varying, 'completed'::character varying, 'cancelled'::character varying, 'note_added'::character varying, 'file_attached'::character varying, 'time_logged'::character varying, 'cost_updated'::character varying])::text[]))) not valid;

alter table "public"."job_activities" validate constraint "job_activities_activity_type_check";

alter table "public"."job_activities" add constraint "job_activities_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."job_activities" validate constraint "job_activities_business_id_fkey";

alter table "public"."job_activities" add constraint "job_activities_job_id_fkey" FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE not valid;

alter table "public"."job_activities" validate constraint "job_activities_job_id_fkey";

alter table "public"."job_attachments" add constraint "job_attachments_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."job_attachments" validate constraint "job_attachments_business_id_fkey";

alter table "public"."job_attachments" add constraint "job_attachments_job_id_fkey" FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE not valid;

alter table "public"."job_attachments" validate constraint "job_attachments_job_id_fkey";

alter table "public"."job_notes" add constraint "job_notes_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."job_notes" validate constraint "job_notes_business_id_fkey";

alter table "public"."job_notes" add constraint "job_notes_job_id_fkey" FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE not valid;

alter table "public"."job_notes" validate constraint "job_notes_job_id_fkey";

alter table "public"."job_notes" add constraint "job_notes_note_type_check" CHECK (((note_type)::text = ANY ((ARRAY['general'::character varying, 'customer'::character varying, 'internal'::character varying, 'technical'::character varying, 'follow_up'::character varying])::text[]))) not valid;

alter table "public"."job_notes" validate constraint "job_notes_note_type_check";

alter table "public"."job_templates" add constraint "job_templates_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."job_templates" validate constraint "job_templates_business_id_fkey";

alter table "public"."job_templates" add constraint "job_templates_business_id_name_key" UNIQUE using index "job_templates_business_id_name_key";

alter table "public"."jobs" add constraint "jobs_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."jobs" validate constraint "jobs_business_id_fkey";

alter table "public"."jobs" add constraint "jobs_business_id_job_number_key" UNIQUE using index "jobs_business_id_job_number_key";

alter table "public"."jobs" add constraint "jobs_check" CHECK (((scheduled_end IS NULL) OR (scheduled_start IS NULL) OR (scheduled_end > scheduled_start))) not valid;

alter table "public"."jobs" validate constraint "jobs_check";

alter table "public"."jobs" add constraint "jobs_check1" CHECK (((actual_end IS NULL) OR (actual_start IS NULL) OR (actual_end > actual_start))) not valid;

alter table "public"."jobs" validate constraint "jobs_check1";

alter table "public"."jobs" add constraint "jobs_contact_id_fkey" FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL not valid;

alter table "public"."jobs" validate constraint "jobs_contact_id_fkey";

alter table "public"."jobs" add constraint "jobs_job_type_check" CHECK (((job_type)::text = ANY ((ARRAY['service'::character varying, 'installation'::character varying, 'maintenance'::character varying, 'repair'::character varying, 'inspection'::character varying, 'consultation'::character varying, 'emergency'::character varying, 'project'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_job_type_check";

alter table "public"."jobs" add constraint "jobs_priority_check" CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'urgent'::character varying, 'emergency'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_priority_check";

alter table "public"."jobs" add constraint "jobs_source_check" CHECK (((source)::text = ANY ((ARRAY['website'::character varying, 'referral'::character varying, 'repeat_customer'::character varying, 'marketing'::character varying, 'cold_call'::character varying, 'emergency_call'::character varying, 'partner'::character varying, 'walk_in'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_source_check";

alter table "public"."jobs" add constraint "jobs_status_check" CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'quoted'::character varying, 'scheduled'::character varying, 'in_progress'::character varying, 'on_hold'::character varying, 'completed'::character varying, 'cancelled'::character varying, 'invoiced'::character varying, 'paid'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_status_check";

alter table "public"."business_invitations" add constraint "business_invitations_role_check" CHECK (((role)::text = ANY ((ARRAY['owner'::character varying, 'admin'::character varying, 'manager'::character varying, 'employee'::character varying, 'contractor'::character varying, 'viewer'::character varying])::text[]))) not valid;

alter table "public"."business_invitations" validate constraint "business_invitations_role_check";

alter table "public"."business_invitations" add constraint "business_invitations_status_check" CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'accepted'::character varying, 'declined'::character varying, 'expired'::character varying, 'cancelled'::character varying])::text[]))) not valid;

alter table "public"."business_invitations" validate constraint "business_invitations_status_check";

alter table "public"."business_memberships" add constraint "business_memberships_role_check" CHECK (((role)::text = ANY ((ARRAY['owner'::character varying, 'admin'::character varying, 'manager'::character varying, 'employee'::character varying, 'contractor'::character varying, 'viewer'::character varying])::text[]))) not valid;

alter table "public"."business_memberships" validate constraint "business_memberships_role_check";

alter table "public"."businesses" add constraint "businesses_company_size_check" CHECK (((company_size)::text = ANY ((ARRAY['just_me'::character varying, 'small'::character varying, 'medium'::character varying, 'large'::character varying, 'enterprise'::character varying])::text[]))) not valid;

alter table "public"."businesses" validate constraint "businesses_company_size_check";

alter table "public"."businesses" add constraint "businesses_referral_source_check" CHECK (((referral_source)::text = ANY ((ARRAY['tiktok'::character varying, 'tv'::character varying, 'online_ad'::character varying, 'web_search'::character varying, 'podcast_radio'::character varying, 'reddit'::character varying, 'review_sites'::character varying, 'youtube'::character varying, 'facebook_instagram'::character varying, 'referral'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."businesses" validate constraint "businesses_referral_source_check";

alter table "public"."contact_activities" add constraint "contact_activities_activity_type_check" CHECK (((activity_type)::text = ANY ((ARRAY['call'::character varying, 'email'::character varying, 'meeting'::character varying, 'note'::character varying, 'task'::character varying, 'quote'::character varying, 'invoice'::character varying, 'payment'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_activity_type_check";

alter table "public"."contact_activities" add constraint "contact_activities_outcome_check" CHECK (((outcome)::text = ANY ((ARRAY['successful'::character varying, 'no_answer'::character varying, 'busy'::character varying, 'scheduled'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[]))) not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_outcome_check";

alter table "public"."contact_notes" add constraint "contact_notes_note_type_check" CHECK (((note_type)::text = ANY ((ARRAY['general'::character varying, 'meeting'::character varying, 'call'::character varying, 'email'::character varying, 'task'::character varying, 'reminder'::character varying])::text[]))) not valid;

alter table "public"."contact_notes" validate constraint "contact_notes_note_type_check";

alter table "public"."contact_segments" add constraint "contact_segments_segment_type_check" CHECK (((segment_type)::text = ANY ((ARRAY['manual'::character varying, 'dynamic'::character varying, 'imported'::character varying])::text[]))) not valid;

alter table "public"."contact_segments" validate constraint "contact_segments_segment_type_check";

alter table "public"."contacts" add constraint "contacts_contact_type_check" CHECK (((contact_type)::text = ANY ((ARRAY['customer'::character varying, 'lead'::character varying, 'prospect'::character varying, 'vendor'::character varying, 'partner'::character varying, 'contractor'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_contact_type_check";

alter table "public"."contacts" add constraint "contacts_priority_check" CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'urgent'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_priority_check";

alter table "public"."contacts" add constraint "contacts_source_check" CHECK (((source)::text = ANY ((ARRAY['website'::character varying, 'referral'::character varying, 'social_media'::character varying, 'advertising'::character varying, 'cold_outreach'::character varying, 'event'::character varying, 'partner'::character varying, 'existing_customer'::character varying, 'direct'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_source_check";

alter table "public"."contacts" add constraint "contacts_status_check" CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'archived'::character varying, 'blocked'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_status_check";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_job_statistics(p_business_id uuid)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
    result JSONB;
    total_jobs INTEGER;
    jobs_by_status JSONB;
    jobs_by_type JSONB;
    jobs_by_priority JSONB;
    overdue_jobs INTEGER;
    emergency_jobs INTEGER;
    jobs_in_progress INTEGER;
    completed_this_month INTEGER;
    revenue_this_month DECIMAL;
    average_job_value DECIMAL;
BEGIN
    -- Total jobs
    SELECT COUNT(*) INTO total_jobs
    FROM jobs WHERE business_id = p_business_id;
    
    -- Jobs by status
    SELECT jsonb_object_agg(status, count)
    INTO jobs_by_status
    FROM (
        SELECT status, COUNT(*) as count
        FROM jobs
        WHERE business_id = p_business_id
        GROUP BY status
    ) s;
    
    -- Jobs by type
    SELECT jsonb_object_agg(job_type, count)
    INTO jobs_by_type
    FROM (
        SELECT job_type, COUNT(*) as count
        FROM jobs
        WHERE business_id = p_business_id
        GROUP BY job_type
    ) t;
    
    -- Jobs by priority
    SELECT jsonb_object_agg(priority, count)
    INTO jobs_by_priority
    FROM (
        SELECT priority, COUNT(*) as count
        FROM jobs
        WHERE business_id = p_business_id
        GROUP BY priority
    ) p;
    
    -- Overdue jobs
    SELECT COUNT(*) INTO overdue_jobs
    FROM jobs
    WHERE business_id = p_business_id
    AND status IN ('scheduled', 'in_progress')
    AND scheduled_end < NOW();
    
    -- Emergency jobs
    SELECT COUNT(*) INTO emergency_jobs
    FROM jobs
    WHERE business_id = p_business_id
    AND priority = 'emergency';
    
    -- Jobs in progress
    SELECT COUNT(*) INTO jobs_in_progress
    FROM jobs
    WHERE business_id = p_business_id
    AND status = 'in_progress';
    
    -- Completed this month
    SELECT COUNT(*) INTO completed_this_month
    FROM jobs
    WHERE business_id = p_business_id
    AND status = 'completed'
    AND completed_date >= DATE_TRUNC('month', NOW());
    
    -- Revenue this month (from cost estimates)
    SELECT COALESCE(SUM(
        COALESCE((cost_estimate->>'labor_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'material_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'equipment_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'overhead_cost')::DECIMAL, 0)
    ), 0) INTO revenue_this_month
    FROM jobs
    WHERE business_id = p_business_id
    AND status IN ('completed', 'invoiced', 'paid')
    AND completed_date >= DATE_TRUNC('month', NOW());
    
    -- Average job value
    SELECT COALESCE(AVG(
        COALESCE((cost_estimate->>'labor_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'material_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'equipment_cost')::DECIMAL, 0) +
        COALESCE((cost_estimate->>'overhead_cost')::DECIMAL, 0)
    ), 0) INTO average_job_value
    FROM jobs
    WHERE business_id = p_business_id
    AND status IN ('completed', 'invoiced', 'paid');
    
    -- Build result
    result := jsonb_build_object(
        'total_jobs', total_jobs,
        'jobs_by_status', COALESCE(jobs_by_status, '{}'::jsonb),
        'jobs_by_type', COALESCE(jobs_by_type, '{}'::jsonb),
        'jobs_by_priority', COALESCE(jobs_by_priority, '{}'::jsonb),
        'overdue_jobs', overdue_jobs,
        'emergency_jobs', emergency_jobs,
        'jobs_in_progress', jobs_in_progress,
        'completed_this_month', completed_this_month,
        'revenue_this_month', revenue_this_month,
        'average_job_value', average_job_value,
        'completion_rate', CASE WHEN total_jobs > 0 THEN 
            (SELECT COUNT(*)::DECIMAL / total_jobs * 100 
             FROM jobs 
             WHERE business_id = p_business_id AND status IN ('completed', 'invoiced', 'paid'))
            ELSE 0 END,
        'on_time_completion_rate', CASE WHEN completed_this_month > 0 THEN
            (SELECT COUNT(*)::DECIMAL / completed_this_month * 100
             FROM jobs
             WHERE business_id = p_business_id
             AND status = 'completed'
             AND completed_date >= DATE_TRUNC('month', NOW())
             AND (actual_end IS NULL OR scheduled_end IS NULL OR actual_end <= scheduled_end))
            ELSE 0 END
    );
    
    RETURN result;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.get_next_job_number(p_business_id uuid, p_prefix text DEFAULT 'JOB'::text)
 RETURNS text
 LANGUAGE plpgsql
AS $function$
DECLARE
    next_number INTEGER;
    job_number TEXT;
BEGIN
    -- Get the highest existing job number for this business
    SELECT COALESCE(
        MAX(
            CAST(
                SUBSTRING(job_number FROM LENGTH(p_prefix || '-') + 1) AS INTEGER
            )
        ), 0
    ) + 1
    INTO next_number
    FROM jobs
    WHERE business_id = p_business_id
    AND job_number ~ ('^' || p_prefix || '-[0-9]+$');
    
    -- Format the job number
    job_number := p_prefix || '-' || LPAD(next_number::TEXT, 6, '0');
    
    RETURN job_number;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.log_job_activity()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Log job creation
    IF TG_OP = 'INSERT' THEN
        INSERT INTO job_activities (job_id, business_id, user_id, activity_type, description, new_values)
        VALUES (NEW.id, NEW.business_id, NEW.created_by, 'created', 
                'Job created: ' || NEW.title, to_jsonb(NEW));
        RETURN NEW;
    END IF;
    
    -- Log job updates
    IF TG_OP = 'UPDATE' THEN
        -- Log status changes
        IF OLD.status != NEW.status THEN
            INSERT INTO job_activities (job_id, business_id, user_id, activity_type, description, old_values, new_values)
            VALUES (NEW.id, NEW.business_id, NEW.created_by, 'status_changed',
                    'Status changed from ' || OLD.status || ' to ' || NEW.status,
                    jsonb_build_object('status', OLD.status),
                    jsonb_build_object('status', NEW.status));
        END IF;
        
        -- Log assignment changes
        IF OLD.assigned_to != NEW.assigned_to THEN
            INSERT INTO job_activities (job_id, business_id, user_id, activity_type, description, old_values, new_values)
            VALUES (NEW.id, NEW.business_id, NEW.created_by, 'assigned',
                    'Assignment changed',
                    jsonb_build_object('assigned_to', OLD.assigned_to),
                    jsonb_build_object('assigned_to', NEW.assigned_to));
        END IF;
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_job_last_modified()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$function$
;

grant delete on table "public"."job_activities" to "anon";

grant insert on table "public"."job_activities" to "anon";

grant references on table "public"."job_activities" to "anon";

grant select on table "public"."job_activities" to "anon";

grant trigger on table "public"."job_activities" to "anon";

grant truncate on table "public"."job_activities" to "anon";

grant update on table "public"."job_activities" to "anon";

grant delete on table "public"."job_activities" to "authenticated";

grant insert on table "public"."job_activities" to "authenticated";

grant references on table "public"."job_activities" to "authenticated";

grant select on table "public"."job_activities" to "authenticated";

grant trigger on table "public"."job_activities" to "authenticated";

grant truncate on table "public"."job_activities" to "authenticated";

grant update on table "public"."job_activities" to "authenticated";

grant delete on table "public"."job_activities" to "service_role";

grant insert on table "public"."job_activities" to "service_role";

grant references on table "public"."job_activities" to "service_role";

grant select on table "public"."job_activities" to "service_role";

grant trigger on table "public"."job_activities" to "service_role";

grant truncate on table "public"."job_activities" to "service_role";

grant update on table "public"."job_activities" to "service_role";

grant delete on table "public"."job_attachments" to "anon";

grant insert on table "public"."job_attachments" to "anon";

grant references on table "public"."job_attachments" to "anon";

grant select on table "public"."job_attachments" to "anon";

grant trigger on table "public"."job_attachments" to "anon";

grant truncate on table "public"."job_attachments" to "anon";

grant update on table "public"."job_attachments" to "anon";

grant delete on table "public"."job_attachments" to "authenticated";

grant insert on table "public"."job_attachments" to "authenticated";

grant references on table "public"."job_attachments" to "authenticated";

grant select on table "public"."job_attachments" to "authenticated";

grant trigger on table "public"."job_attachments" to "authenticated";

grant truncate on table "public"."job_attachments" to "authenticated";

grant update on table "public"."job_attachments" to "authenticated";

grant delete on table "public"."job_attachments" to "service_role";

grant insert on table "public"."job_attachments" to "service_role";

grant references on table "public"."job_attachments" to "service_role";

grant select on table "public"."job_attachments" to "service_role";

grant trigger on table "public"."job_attachments" to "service_role";

grant truncate on table "public"."job_attachments" to "service_role";

grant update on table "public"."job_attachments" to "service_role";

grant delete on table "public"."job_notes" to "anon";

grant insert on table "public"."job_notes" to "anon";

grant references on table "public"."job_notes" to "anon";

grant select on table "public"."job_notes" to "anon";

grant trigger on table "public"."job_notes" to "anon";

grant truncate on table "public"."job_notes" to "anon";

grant update on table "public"."job_notes" to "anon";

grant delete on table "public"."job_notes" to "authenticated";

grant insert on table "public"."job_notes" to "authenticated";

grant references on table "public"."job_notes" to "authenticated";

grant select on table "public"."job_notes" to "authenticated";

grant trigger on table "public"."job_notes" to "authenticated";

grant truncate on table "public"."job_notes" to "authenticated";

grant update on table "public"."job_notes" to "authenticated";

grant delete on table "public"."job_notes" to "service_role";

grant insert on table "public"."job_notes" to "service_role";

grant references on table "public"."job_notes" to "service_role";

grant select on table "public"."job_notes" to "service_role";

grant trigger on table "public"."job_notes" to "service_role";

grant truncate on table "public"."job_notes" to "service_role";

grant update on table "public"."job_notes" to "service_role";

grant delete on table "public"."job_templates" to "anon";

grant insert on table "public"."job_templates" to "anon";

grant references on table "public"."job_templates" to "anon";

grant select on table "public"."job_templates" to "anon";

grant trigger on table "public"."job_templates" to "anon";

grant truncate on table "public"."job_templates" to "anon";

grant update on table "public"."job_templates" to "anon";

grant delete on table "public"."job_templates" to "authenticated";

grant insert on table "public"."job_templates" to "authenticated";

grant references on table "public"."job_templates" to "authenticated";

grant select on table "public"."job_templates" to "authenticated";

grant trigger on table "public"."job_templates" to "authenticated";

grant truncate on table "public"."job_templates" to "authenticated";

grant update on table "public"."job_templates" to "authenticated";

grant delete on table "public"."job_templates" to "service_role";

grant insert on table "public"."job_templates" to "service_role";

grant references on table "public"."job_templates" to "service_role";

grant select on table "public"."job_templates" to "service_role";

grant trigger on table "public"."job_templates" to "service_role";

grant truncate on table "public"."job_templates" to "service_role";

grant update on table "public"."job_templates" to "service_role";

grant delete on table "public"."jobs" to "anon";

grant insert on table "public"."jobs" to "anon";

grant references on table "public"."jobs" to "anon";

grant select on table "public"."jobs" to "anon";

grant trigger on table "public"."jobs" to "anon";

grant truncate on table "public"."jobs" to "anon";

grant update on table "public"."jobs" to "anon";

grant delete on table "public"."jobs" to "authenticated";

grant insert on table "public"."jobs" to "authenticated";

grant references on table "public"."jobs" to "authenticated";

grant select on table "public"."jobs" to "authenticated";

grant trigger on table "public"."jobs" to "authenticated";

grant truncate on table "public"."jobs" to "authenticated";

grant update on table "public"."jobs" to "authenticated";

grant delete on table "public"."jobs" to "service_role";

grant insert on table "public"."jobs" to "service_role";

grant references on table "public"."jobs" to "service_role";

grant select on table "public"."jobs" to "service_role";

grant trigger on table "public"."jobs" to "service_role";

grant truncate on table "public"."jobs" to "service_role";

grant update on table "public"."jobs" to "service_role";

CREATE TRIGGER trigger_update_job_notes_last_modified BEFORE UPDATE ON public.job_notes FOR EACH ROW EXECUTE FUNCTION update_job_last_modified();

CREATE TRIGGER trigger_update_job_templates_last_modified BEFORE UPDATE ON public.job_templates FOR EACH ROW EXECUTE FUNCTION update_job_last_modified();

CREATE TRIGGER trigger_log_job_activity AFTER INSERT OR UPDATE ON public.jobs FOR EACH ROW EXECUTE FUNCTION log_job_activity();

CREATE TRIGGER trigger_update_job_last_modified BEFORE UPDATE ON public.jobs FOR EACH ROW EXECUTE FUNCTION update_job_last_modified();


