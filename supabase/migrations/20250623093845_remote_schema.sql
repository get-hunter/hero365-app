create type "public"."activity_priority" as enum ('low', 'medium', 'high', 'urgent');

create type "public"."activity_status" as enum ('pending', 'in_progress', 'completed', 'cancelled', 'overdue');

create type "public"."activity_type" as enum ('interaction', 'status_change', 'task', 'reminder', 'note', 'system_event', 'service_event', 'financial_event', 'document_event');

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

alter table "public"."contacts" drop constraint "contacts_lifecycle_stage_check";

alter table "public"."contacts" drop constraint "contacts_priority_check";

alter table "public"."contacts" drop constraint "contacts_relationship_status_check";

alter table "public"."contacts" drop constraint "contacts_source_check";

alter table "public"."contacts" drop constraint "contacts_status_check";

alter table "public"."job_activities" drop constraint "job_activities_activity_type_check";

alter table "public"."job_notes" drop constraint "job_notes_note_type_check";

alter table "public"."jobs" drop constraint "jobs_job_type_check";

alter table "public"."jobs" drop constraint "jobs_priority_check";

alter table "public"."jobs" drop constraint "jobs_source_check";

alter table "public"."jobs" drop constraint "jobs_status_check";

drop index if exists "public"."idx_jobs_assigned_status";

drop index if exists "public"."idx_jobs_scheduled_end_active";

create table "public"."activities" (
    "id" uuid not null default gen_random_uuid(),
    "business_id" uuid not null,
    "contact_id" uuid not null,
    "template_id" uuid,
    "parent_activity_id" uuid,
    "activity_type" activity_type not null,
    "title" character varying(500) not null,
    "description" text,
    "status" activity_status default 'pending'::activity_status,
    "priority" activity_priority default 'medium'::activity_priority,
    "scheduled_date" timestamp with time zone,
    "due_date" timestamp with time zone,
    "completed_date" timestamp with time zone,
    "duration_minutes" integer,
    "location" character varying(500),
    "created_by" character varying(100) not null,
    "assigned_to" character varying(100),
    "tags" text[] default '{}'::text[],
    "metadata" jsonb default '{}'::jsonb,
    "created_date" timestamp with time zone default CURRENT_TIMESTAMP,
    "last_modified" timestamp with time zone default CURRENT_TIMESTAMP
);


alter table "public"."activities" enable row level security;

create table "public"."activity_participants" (
    "id" uuid not null default gen_random_uuid(),
    "activity_id" uuid not null,
    "user_id" character varying(100) not null,
    "name" character varying(200) not null,
    "role" character varying(50) default 'participant'::character varying,
    "is_primary" boolean default false,
    "created_date" timestamp with time zone default CURRENT_TIMESTAMP
);


alter table "public"."activity_participants" enable row level security;

create table "public"."activity_reminders" (
    "id" uuid not null default gen_random_uuid(),
    "activity_id" uuid not null,
    "reminder_time" timestamp with time zone not null,
    "reminder_type" character varying(50) default 'notification'::character varying,
    "message" text,
    "is_sent" boolean default false,
    "sent_at" timestamp with time zone,
    "created_date" timestamp with time zone default CURRENT_TIMESTAMP
);


alter table "public"."activity_reminders" enable row level security;

create table "public"."activity_templates" (
    "id" uuid not null default gen_random_uuid(),
    "business_id" uuid not null,
    "name" character varying(200) not null,
    "description" text,
    "activity_type" activity_type not null,
    "default_duration" integer,
    "default_reminders" jsonb default '[]'::jsonb,
    "default_participants" text[] default '{}'::text[],
    "custom_fields" jsonb default '{}'::jsonb,
    "is_active" boolean default true,
    "created_by" character varying(100) not null,
    "created_date" timestamp with time zone default CURRENT_TIMESTAMP,
    "last_modified" timestamp with time zone default CURRENT_TIMESTAMP
);


alter table "public"."activity_templates" enable row level security;

CREATE UNIQUE INDEX activities_pkey ON public.activities USING btree (id);

CREATE UNIQUE INDEX activity_participants_activity_id_user_id_key ON public.activity_participants USING btree (activity_id, user_id);

CREATE UNIQUE INDEX activity_participants_pkey ON public.activity_participants USING btree (id);

CREATE UNIQUE INDEX activity_reminders_pkey ON public.activity_reminders USING btree (id);

CREATE UNIQUE INDEX activity_templates_pkey ON public.activity_templates USING btree (id);

CREATE INDEX idx_activities_assigned_to ON public.activities USING btree (assigned_to);

CREATE INDEX idx_activities_business_id ON public.activities USING btree (business_id);

CREATE INDEX idx_activities_business_timeline ON public.activities USING btree (business_id, scheduled_date DESC, created_date DESC);

CREATE INDEX idx_activities_contact_id ON public.activities USING btree (contact_id);

CREATE INDEX idx_activities_contact_timeline ON public.activities USING btree (contact_id, business_id, scheduled_date DESC, created_date DESC);

CREATE INDEX idx_activities_created_by ON public.activities USING btree (created_by);

CREATE INDEX idx_activities_created_date ON public.activities USING btree (created_date);

CREATE INDEX idx_activities_due_date ON public.activities USING btree (due_date);

CREATE INDEX idx_activities_last_modified ON public.activities USING btree (last_modified);

CREATE INDEX idx_activities_overdue ON public.activities USING btree (business_id, status, due_date) WHERE (status = ANY (ARRAY['pending'::activity_status, 'in_progress'::activity_status]));

CREATE INDEX idx_activities_parent_id ON public.activities USING btree (parent_activity_id);

CREATE INDEX idx_activities_priority ON public.activities USING btree (priority);

CREATE INDEX idx_activities_scheduled_date ON public.activities USING btree (scheduled_date);

CREATE INDEX idx_activities_status ON public.activities USING btree (status);

CREATE INDEX idx_activities_template_id ON public.activities USING btree (template_id);

CREATE INDEX idx_activities_type ON public.activities USING btree (activity_type);

CREATE INDEX idx_activities_upcoming ON public.activities USING btree (business_id, scheduled_date) WHERE (status = ANY (ARRAY['pending'::activity_status, 'in_progress'::activity_status]));

CREATE INDEX idx_activities_user_tasks ON public.activities USING btree (business_id, assigned_to, status, due_date);

CREATE INDEX idx_activity_participants_activity_id ON public.activity_participants USING btree (activity_id);

CREATE INDEX idx_activity_participants_user_id ON public.activity_participants USING btree (user_id);

CREATE INDEX idx_activity_reminders_activity_id ON public.activity_reminders USING btree (activity_id);

CREATE INDEX idx_activity_reminders_pending ON public.activity_reminders USING btree (is_sent, reminder_time) WHERE (is_sent = false);

CREATE INDEX idx_activity_reminders_time ON public.activity_reminders USING btree (reminder_time);

CREATE INDEX idx_activity_templates_active ON public.activity_templates USING btree (is_active);

CREATE INDEX idx_activity_templates_business_id ON public.activity_templates USING btree (business_id);

CREATE INDEX idx_activity_templates_type ON public.activity_templates USING btree (activity_type);

CREATE INDEX idx_jobs_assigned_status ON public.jobs USING gin (assigned_to) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

CREATE INDEX idx_jobs_scheduled_end_active ON public.jobs USING btree (business_id, scheduled_end) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

alter table "public"."activities" add constraint "activities_pkey" PRIMARY KEY using index "activities_pkey";

alter table "public"."activity_participants" add constraint "activity_participants_pkey" PRIMARY KEY using index "activity_participants_pkey";

alter table "public"."activity_reminders" add constraint "activity_reminders_pkey" PRIMARY KEY using index "activity_reminders_pkey";

alter table "public"."activity_templates" add constraint "activity_templates_pkey" PRIMARY KEY using index "activity_templates_pkey";

alter table "public"."activities" add constraint "activities_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."activities" validate constraint "activities_business_id_fkey";

alter table "public"."activities" add constraint "activities_contact_id_fkey" FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE not valid;

alter table "public"."activities" validate constraint "activities_contact_id_fkey";

alter table "public"."activities" add constraint "activities_parent_activity_id_fkey" FOREIGN KEY (parent_activity_id) REFERENCES activities(id) ON DELETE SET NULL not valid;

alter table "public"."activities" validate constraint "activities_parent_activity_id_fkey";

alter table "public"."activities" add constraint "activities_template_id_fkey" FOREIGN KEY (template_id) REFERENCES activity_templates(id) ON DELETE SET NULL not valid;

alter table "public"."activities" validate constraint "activities_template_id_fkey";

alter table "public"."activities" add constraint "check_completed_when_status_completed" CHECK ((((status = 'completed'::activity_status) AND (completed_date IS NOT NULL)) OR ((status <> 'completed'::activity_status) AND (completed_date IS NULL)))) not valid;

alter table "public"."activities" validate constraint "check_completed_when_status_completed";

alter table "public"."activities" add constraint "check_due_after_scheduled" CHECK (((due_date IS NULL) OR (scheduled_date IS NULL) OR (due_date >= scheduled_date))) not valid;

alter table "public"."activities" validate constraint "check_due_after_scheduled";

alter table "public"."activity_participants" add constraint "activity_participants_activity_id_fkey" FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE not valid;

alter table "public"."activity_participants" validate constraint "activity_participants_activity_id_fkey";

alter table "public"."activity_participants" add constraint "activity_participants_activity_id_user_id_key" UNIQUE using index "activity_participants_activity_id_user_id_key";

alter table "public"."activity_reminders" add constraint "activity_reminders_activity_id_fkey" FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE not valid;

alter table "public"."activity_reminders" validate constraint "activity_reminders_activity_id_fkey";

alter table "public"."activity_templates" add constraint "activity_templates_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."activity_templates" validate constraint "activity_templates_business_id_fkey";

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

alter table "public"."contacts" add constraint "contacts_lifecycle_stage_check" CHECK (((lifecycle_stage)::text = ANY ((ARRAY['awareness'::character varying, 'interest'::character varying, 'consideration'::character varying, 'decision'::character varying, 'retention'::character varying, 'customer'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_lifecycle_stage_check";

alter table "public"."contacts" add constraint "contacts_priority_check" CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'urgent'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_priority_check";

alter table "public"."contacts" add constraint "contacts_relationship_status_check" CHECK (((relationship_status)::text = ANY ((ARRAY['prospect'::character varying, 'qualified_lead'::character varying, 'opportunity'::character varying, 'active_client'::character varying, 'past_client'::character varying, 'lost_lead'::character varying, 'inactive'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_relationship_status_check";

alter table "public"."contacts" add constraint "contacts_source_check" CHECK (((source)::text = ANY ((ARRAY['website'::character varying, 'referral'::character varying, 'social_media'::character varying, 'advertising'::character varying, 'cold_outreach'::character varying, 'event'::character varying, 'partner'::character varying, 'existing_customer'::character varying, 'direct'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_source_check";

alter table "public"."contacts" add constraint "contacts_status_check" CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'archived'::character varying, 'blocked'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_status_check";

alter table "public"."job_activities" add constraint "job_activities_activity_type_check" CHECK (((activity_type)::text = ANY ((ARRAY['created'::character varying, 'updated'::character varying, 'status_changed'::character varying, 'assigned'::character varying, 'unassigned'::character varying, 'started'::character varying, 'paused'::character varying, 'resumed'::character varying, 'completed'::character varying, 'cancelled'::character varying, 'note_added'::character varying, 'file_attached'::character varying, 'time_logged'::character varying, 'cost_updated'::character varying])::text[]))) not valid;

alter table "public"."job_activities" validate constraint "job_activities_activity_type_check";

alter table "public"."job_notes" add constraint "job_notes_note_type_check" CHECK (((note_type)::text = ANY ((ARRAY['general'::character varying, 'customer'::character varying, 'internal'::character varying, 'technical'::character varying, 'follow_up'::character varying])::text[]))) not valid;

alter table "public"."job_notes" validate constraint "job_notes_note_type_check";

alter table "public"."jobs" add constraint "jobs_job_type_check" CHECK (((job_type)::text = ANY ((ARRAY['service'::character varying, 'installation'::character varying, 'maintenance'::character varying, 'repair'::character varying, 'inspection'::character varying, 'consultation'::character varying, 'emergency'::character varying, 'project'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_job_type_check";

alter table "public"."jobs" add constraint "jobs_priority_check" CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'urgent'::character varying, 'emergency'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_priority_check";

alter table "public"."jobs" add constraint "jobs_source_check" CHECK (((source)::text = ANY ((ARRAY['website'::character varying, 'referral'::character varying, 'repeat_customer'::character varying, 'marketing'::character varying, 'cold_call'::character varying, 'emergency_call'::character varying, 'partner'::character varying, 'walk_in'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_source_check";

alter table "public"."jobs" add constraint "jobs_status_check" CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'quoted'::character varying, 'scheduled'::character varying, 'in_progress'::character varying, 'on_hold'::character varying, 'completed'::character varying, 'cancelled'::character varying, 'invoiced'::character varying, 'paid'::character varying])::text[]))) not valid;

alter table "public"."jobs" validate constraint "jobs_status_check";

set check_function_bodies = off;

create or replace view "public"."activity_timeline_view" as  SELECT a.id,
    a.business_id,
    a.contact_id,
    c.display_name AS contact_name,
    c.email AS contact_email,
    c.phone AS contact_phone,
    a.activity_type,
    a.title,
    a.description,
    a.status,
    a.priority,
    a.scheduled_date,
    a.due_date,
    a.completed_date,
    a.duration_minutes,
    a.location,
    a.created_by,
    a.assigned_to,
    a.tags,
    a.metadata,
    a.created_date,
    a.last_modified,
        CASE
            WHEN ((a.status = ANY (ARRAY['pending'::activity_status, 'in_progress'::activity_status])) AND (((a.due_date IS NOT NULL) AND (a.due_date < now())) OR ((a.due_date IS NULL) AND (a.scheduled_date IS NOT NULL) AND (a.scheduled_date < (now() - '1 day'::interval))))) THEN true
            ELSE false
        END AS is_overdue,
        CASE
            WHEN ((a.scheduled_date IS NOT NULL) AND (a.scheduled_date > now()) AND (a.scheduled_date <= (now() + '7 days'::interval))) THEN true
            ELSE false
        END AS is_upcoming
   FROM (activities a
     JOIN contacts c ON ((a.contact_id = c.id)));


CREATE OR REPLACE FUNCTION public.cleanup_old_activities()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Archive activities completed more than 2 years ago
    -- This is optional and can be adjusted based on business needs
    UPDATE activities 
    SET metadata = jsonb_set(
        COALESCE(metadata, '{}'),
        '{archived}',
        'true'
    )
    WHERE status = 'completed'
    AND completed_date < NOW() - INTERVAL '2 years'
    AND NOT (metadata ? 'archived');
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_activity_modified()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_overdue_activities()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    UPDATE activities 
    SET status = 'overdue',
        last_modified = NOW()
    WHERE status IN ('pending', 'in_progress')
    AND (
        (due_date IS NOT NULL AND due_date < NOW()) OR
        (due_date IS NULL AND scheduled_date IS NOT NULL AND scheduled_date < NOW() - INTERVAL '1 day')
    );
END;
$function$
;

create or replace view "public"."user_dashboard_activities" as  SELECT a.id,
    a.business_id,
    a.contact_id,
    c.display_name AS contact_name,
    a.activity_type,
    a.title,
    a.status,
    a.priority,
    a.scheduled_date,
    a.due_date,
    a.assigned_to,
    a.created_date,
        CASE
            WHEN ((a.status = ANY (ARRAY['pending'::activity_status, 'in_progress'::activity_status])) AND (((a.due_date IS NOT NULL) AND (a.due_date < now())) OR ((a.due_date IS NULL) AND (a.scheduled_date IS NOT NULL) AND (a.scheduled_date < (now() - '1 day'::interval))))) THEN 'overdue'::text
            WHEN ((a.scheduled_date IS NOT NULL) AND (a.scheduled_date > now()) AND (a.scheduled_date <= (now() + '7 days'::interval))) THEN 'upcoming'::text
            ELSE 'normal'::text
        END AS urgency_status
   FROM (activities a
     JOIN contacts c ON ((a.contact_id = c.id)))
  WHERE (a.status = ANY (ARRAY['pending'::activity_status, 'in_progress'::activity_status]))
  ORDER BY
        CASE
            WHEN (a.priority = 'urgent'::activity_priority) THEN 1
            WHEN (a.priority = 'high'::activity_priority) THEN 2
            WHEN (a.priority = 'medium'::activity_priority) THEN 3
            ELSE 4
        END, a.due_date, a.scheduled_date;


grant delete on table "public"."activities" to "anon";

grant insert on table "public"."activities" to "anon";

grant references on table "public"."activities" to "anon";

grant select on table "public"."activities" to "anon";

grant trigger on table "public"."activities" to "anon";

grant truncate on table "public"."activities" to "anon";

grant update on table "public"."activities" to "anon";

grant delete on table "public"."activities" to "authenticated";

grant insert on table "public"."activities" to "authenticated";

grant references on table "public"."activities" to "authenticated";

grant select on table "public"."activities" to "authenticated";

grant trigger on table "public"."activities" to "authenticated";

grant truncate on table "public"."activities" to "authenticated";

grant update on table "public"."activities" to "authenticated";

grant delete on table "public"."activities" to "service_role";

grant insert on table "public"."activities" to "service_role";

grant references on table "public"."activities" to "service_role";

grant select on table "public"."activities" to "service_role";

grant trigger on table "public"."activities" to "service_role";

grant truncate on table "public"."activities" to "service_role";

grant update on table "public"."activities" to "service_role";

grant delete on table "public"."activity_participants" to "anon";

grant insert on table "public"."activity_participants" to "anon";

grant references on table "public"."activity_participants" to "anon";

grant select on table "public"."activity_participants" to "anon";

grant trigger on table "public"."activity_participants" to "anon";

grant truncate on table "public"."activity_participants" to "anon";

grant update on table "public"."activity_participants" to "anon";

grant delete on table "public"."activity_participants" to "authenticated";

grant insert on table "public"."activity_participants" to "authenticated";

grant references on table "public"."activity_participants" to "authenticated";

grant select on table "public"."activity_participants" to "authenticated";

grant trigger on table "public"."activity_participants" to "authenticated";

grant truncate on table "public"."activity_participants" to "authenticated";

grant update on table "public"."activity_participants" to "authenticated";

grant delete on table "public"."activity_participants" to "service_role";

grant insert on table "public"."activity_participants" to "service_role";

grant references on table "public"."activity_participants" to "service_role";

grant select on table "public"."activity_participants" to "service_role";

grant trigger on table "public"."activity_participants" to "service_role";

grant truncate on table "public"."activity_participants" to "service_role";

grant update on table "public"."activity_participants" to "service_role";

grant delete on table "public"."activity_reminders" to "anon";

grant insert on table "public"."activity_reminders" to "anon";

grant references on table "public"."activity_reminders" to "anon";

grant select on table "public"."activity_reminders" to "anon";

grant trigger on table "public"."activity_reminders" to "anon";

grant truncate on table "public"."activity_reminders" to "anon";

grant update on table "public"."activity_reminders" to "anon";

grant delete on table "public"."activity_reminders" to "authenticated";

grant insert on table "public"."activity_reminders" to "authenticated";

grant references on table "public"."activity_reminders" to "authenticated";

grant select on table "public"."activity_reminders" to "authenticated";

grant trigger on table "public"."activity_reminders" to "authenticated";

grant truncate on table "public"."activity_reminders" to "authenticated";

grant update on table "public"."activity_reminders" to "authenticated";

grant delete on table "public"."activity_reminders" to "service_role";

grant insert on table "public"."activity_reminders" to "service_role";

grant references on table "public"."activity_reminders" to "service_role";

grant select on table "public"."activity_reminders" to "service_role";

grant trigger on table "public"."activity_reminders" to "service_role";

grant truncate on table "public"."activity_reminders" to "service_role";

grant update on table "public"."activity_reminders" to "service_role";

grant delete on table "public"."activity_templates" to "anon";

grant insert on table "public"."activity_templates" to "anon";

grant references on table "public"."activity_templates" to "anon";

grant select on table "public"."activity_templates" to "anon";

grant trigger on table "public"."activity_templates" to "anon";

grant truncate on table "public"."activity_templates" to "anon";

grant update on table "public"."activity_templates" to "anon";

grant delete on table "public"."activity_templates" to "authenticated";

grant insert on table "public"."activity_templates" to "authenticated";

grant references on table "public"."activity_templates" to "authenticated";

grant select on table "public"."activity_templates" to "authenticated";

grant trigger on table "public"."activity_templates" to "authenticated";

grant truncate on table "public"."activity_templates" to "authenticated";

grant update on table "public"."activity_templates" to "authenticated";

grant delete on table "public"."activity_templates" to "service_role";

grant insert on table "public"."activity_templates" to "service_role";

grant references on table "public"."activity_templates" to "service_role";

grant select on table "public"."activity_templates" to "service_role";

grant trigger on table "public"."activity_templates" to "service_role";

grant truncate on table "public"."activity_templates" to "service_role";

grant update on table "public"."activity_templates" to "service_role";

create policy "activities_business_isolation"
on "public"."activities"
as permissive
for all
to public
using ((business_id IN ( SELECT business_memberships.business_id
   FROM business_memberships
  WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))));


create policy "activity_participants_business_isolation"
on "public"."activity_participants"
as permissive
for all
to public
using ((activity_id IN ( SELECT activities.id
   FROM activities
  WHERE (activities.business_id IN ( SELECT business_memberships.business_id
           FROM business_memberships
          WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))))));


create policy "activity_reminders_business_isolation"
on "public"."activity_reminders"
as permissive
for all
to public
using ((activity_id IN ( SELECT activities.id
   FROM activities
  WHERE (activities.business_id IN ( SELECT business_memberships.business_id
           FROM business_memberships
          WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))))));


create policy "activity_templates_business_isolation"
on "public"."activity_templates"
as permissive
for all
to public
using ((business_id IN ( SELECT business_memberships.business_id
   FROM business_memberships
  WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))));


CREATE TRIGGER update_activities_modified BEFORE UPDATE ON public.activities FOR EACH ROW EXECUTE FUNCTION update_activity_modified();

CREATE TRIGGER update_activity_templates_modified BEFORE UPDATE ON public.activity_templates FOR EACH ROW EXECUTE FUNCTION update_activity_modified();


