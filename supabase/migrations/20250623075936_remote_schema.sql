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

alter table "public"."job_activities" drop constraint "job_activities_activity_type_check";

alter table "public"."job_notes" drop constraint "job_notes_note_type_check";

alter table "public"."jobs" drop constraint "jobs_job_type_check";

alter table "public"."jobs" drop constraint "jobs_priority_check";

alter table "public"."jobs" drop constraint "jobs_source_check";

alter table "public"."jobs" drop constraint "jobs_status_check";

drop index if exists "public"."idx_jobs_assigned_status";

drop index if exists "public"."idx_jobs_scheduled_end_active";

alter table "public"."contacts" add column "display_name" character varying(200) generated always as (
CASE
    WHEN ((company_name IS NOT NULL) AND ((company_name)::text <> ''::text)) THEN
    CASE
        WHEN ((first_name IS NOT NULL) AND (last_name IS NOT NULL)) THEN (((((((first_name)::text || ' '::text) || (last_name)::text) || ' ('::text) || (company_name)::text) || ')'::text))::character varying
        WHEN (first_name IS NOT NULL) THEN (((((first_name)::text || ' ('::text) || (company_name)::text) || ')'::text))::character varying
        WHEN (last_name IS NOT NULL) THEN (((((last_name)::text || ' ('::text) || (company_name)::text) || ')'::text))::character varying
        ELSE company_name
    END
    WHEN ((first_name IS NOT NULL) AND (last_name IS NOT NULL)) THEN ((((first_name)::text || ' '::text) || (last_name)::text))::character varying
    WHEN (first_name IS NOT NULL) THEN first_name
    WHEN (last_name IS NOT NULL) THEN last_name
    ELSE 'Unknown Contact'::character varying
END) stored;

alter table "public"."contacts" add column "interaction_history" jsonb default '[]'::jsonb;

alter table "public"."contacts" add column "lifecycle_stage" character varying(20) default 'awareness'::character varying;

alter table "public"."contacts" add column "relationship_status" character varying(20) default 'prospect'::character varying;

alter table "public"."contacts" add column "status_history" jsonb default '[]'::jsonb;

CREATE INDEX idx_contacts_display_name ON public.contacts USING btree (display_name);

CREATE INDEX idx_contacts_interaction_history ON public.contacts USING gin (interaction_history);

CREATE INDEX idx_contacts_lifecycle_stage ON public.contacts USING btree (lifecycle_stage);

CREATE INDEX idx_contacts_relationship_status ON public.contacts USING btree (relationship_status);

CREATE INDEX idx_contacts_status_history ON public.contacts USING gin (status_history);

CREATE INDEX idx_jobs_assigned_status ON public.jobs USING gin (assigned_to) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

CREATE INDEX idx_jobs_scheduled_end_active ON public.jobs USING btree (business_id, scheduled_end) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

alter table "public"."contacts" add constraint "contacts_lifecycle_stage_check" CHECK (((lifecycle_stage)::text = ANY ((ARRAY['awareness'::character varying, 'interest'::character varying, 'consideration'::character varying, 'decision'::character varying, 'retention'::character varying, 'customer'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_lifecycle_stage_check";

alter table "public"."contacts" add constraint "contacts_relationship_status_check" CHECK (((relationship_status)::text = ANY ((ARRAY['prospect'::character varying, 'qualified_lead'::character varying, 'opportunity'::character varying, 'active_client'::character varying, 'past_client'::character varying, 'lost_lead'::character varying, 'inactive'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_relationship_status_check";

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

CREATE OR REPLACE FUNCTION public.add_contact_interaction_to_history()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Add the new activity to the contact's interaction_history
    UPDATE contacts 
    SET interaction_history = interaction_history || jsonb_build_object(
        'id', NEW.id,
        'type', NEW.activity_type,
        'description', NEW.description,
        'timestamp', NEW.activity_date,
        'performed_by', NEW.performed_by,
        'outcome', NEW.outcome
    )
    WHERE id = NEW.contact_id;
    
    RETURN NEW;
END;
$function$
;

create or replace view "public"."contact_enhanced_summary" as  SELECT id,
    business_id,
    contact_type,
    status,
    first_name,
    last_name,
    company_name,
    job_title,
    email,
    phone,
    mobile_phone,
    website,
    address,
    priority,
    source,
    tags,
    notes,
    estimated_value,
    currency,
    assigned_to,
    created_by,
    custom_fields,
    created_date,
    last_modified,
    last_contacted,
    relationship_status,
    lifecycle_stage,
    status_history,
    interaction_history,
    display_name,
        CASE
            WHEN ((relationship_status)::text = 'active_client'::text) THEN 'Active Client'::text
            WHEN ((relationship_status)::text = 'qualified_lead'::text) THEN 'Qualified Lead'::text
            WHEN ((relationship_status)::text = 'opportunity'::text) THEN 'Opportunity'::text
            WHEN ((relationship_status)::text = 'prospect'::text) THEN 'Prospect'::text
            WHEN ((relationship_status)::text = 'past_client'::text) THEN 'Past Client'::text
            WHEN ((relationship_status)::text = 'lost_lead'::text) THEN 'Lost Lead'::text
            WHEN ((relationship_status)::text = 'inactive'::text) THEN 'Inactive'::text
            ELSE 'Unknown'::text
        END AS relationship_status_display,
        CASE
            WHEN ((lifecycle_stage)::text = 'awareness'::text) THEN 'Awareness'::text
            WHEN ((lifecycle_stage)::text = 'interest'::text) THEN 'Interest'::text
            WHEN ((lifecycle_stage)::text = 'consideration'::text) THEN 'Consideration'::text
            WHEN ((lifecycle_stage)::text = 'decision'::text) THEN 'Decision'::text
            WHEN ((lifecycle_stage)::text = 'retention'::text) THEN 'Retention'::text
            WHEN ((lifecycle_stage)::text = 'customer'::text) THEN 'Customer'::text
            ELSE 'Unknown'::text
        END AS lifecycle_stage_display,
    ( SELECT count(*) AS count
           FROM contact_activities ca
          WHERE (ca.contact_id = c.id)) AS total_interactions,
    ( SELECT count(*) AS count
           FROM contact_notes cn
          WHERE (cn.contact_id = c.id)) AS total_notes,
    jsonb_array_length(status_history) AS status_changes_count,
    jsonb_array_length(interaction_history) AS interaction_summary_count
   FROM contacts c
  WHERE ((status)::text <> 'archived'::text);


CREATE OR REPLACE FUNCTION public.update_contact_status_history()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Only update status_history if relationship_status actually changed
    IF OLD.relationship_status IS DISTINCT FROM NEW.relationship_status THEN
        NEW.status_history = status_history || jsonb_build_object(
            'id', gen_random_uuid(),
            'from_status', OLD.relationship_status,
            'to_status', NEW.relationship_status,
            'timestamp', now(),
            'changed_by', COALESCE(NEW.assigned_to, NEW.created_by, 'system'),
            'reason', COALESCE(NEW.notes, 'Status updated')
        );
    END IF;
    
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER add_contact_interaction_to_history_trigger AFTER INSERT ON public.contact_activities FOR EACH ROW EXECUTE FUNCTION add_contact_interaction_to_history();

CREATE TRIGGER update_contact_status_history_trigger BEFORE UPDATE ON public.contacts FOR EACH ROW EXECUTE FUNCTION update_contact_status_history();


