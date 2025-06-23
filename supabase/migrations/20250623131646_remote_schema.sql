alter table "public"."availability_windows" drop constraint "availability_windows_availability_type_check";

alter table "public"."business_invitations" drop constraint "business_invitations_role_check";

alter table "public"."business_invitations" drop constraint "business_invitations_status_check";

alter table "public"."business_memberships" drop constraint "business_memberships_role_check";

alter table "public"."businesses" drop constraint "businesses_company_size_check";

alter table "public"."businesses" drop constraint "businesses_referral_source_check";

alter table "public"."calendar_events" drop constraint "calendar_events_event_type_check";

alter table "public"."calendar_events" drop constraint "calendar_events_recurrence_type_check";

alter table "public"."calendar_preferences" drop constraint "calendar_preferences_time_format_check";

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

alter table "public"."time_off_requests" drop constraint "time_off_requests_status_check";

alter table "public"."time_off_requests" drop constraint "time_off_requests_time_off_type_check";

alter table "public"."user_certifications" drop constraint "user_certifications_status_check";

alter table "public"."user_skills" drop constraint "user_skills_category_check";

alter table "public"."user_skills" drop constraint "user_skills_level_check";

drop index if exists "public"."idx_jobs_assigned_status";

drop index if exists "public"."idx_jobs_scheduled_end_active";

CREATE INDEX idx_jobs_assigned_status ON public.jobs USING gin (assigned_to) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

CREATE INDEX idx_jobs_scheduled_end_active ON public.jobs USING btree (business_id, scheduled_end) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

alter table "public"."availability_windows" add constraint "availability_windows_availability_type_check" CHECK (((availability_type)::text = ANY ((ARRAY['regular'::character varying, 'flexible'::character varying, 'on_call'::character varying, 'project_based'::character varying])::text[]))) not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_availability_type_check";

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

alter table "public"."calendar_events" add constraint "calendar_events_event_type_check" CHECK (((event_type)::text = ANY ((ARRAY['work_schedule'::character varying, 'time_off'::character varying, 'break'::character varying, 'meeting'::character varying, 'training'::character varying, 'personal'::character varying])::text[]))) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_event_type_check";

alter table "public"."calendar_events" add constraint "calendar_events_recurrence_type_check" CHECK (((recurrence_type)::text = ANY ((ARRAY['none'::character varying, 'daily'::character varying, 'weekly'::character varying, 'biweekly'::character varying, 'monthly'::character varying, 'custom'::character varying])::text[]))) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_recurrence_type_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_time_format_check" CHECK (((time_format)::text = ANY ((ARRAY['12h'::character varying, '24h'::character varying])::text[]))) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_time_format_check";

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

alter table "public"."time_off_requests" add constraint "time_off_requests_status_check" CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'denied'::character varying, 'cancelled'::character varying])::text[]))) not valid;

alter table "public"."time_off_requests" validate constraint "time_off_requests_status_check";

alter table "public"."time_off_requests" add constraint "time_off_requests_time_off_type_check" CHECK (((time_off_type)::text = ANY ((ARRAY['vacation'::character varying, 'sick_leave'::character varying, 'personal'::character varying, 'holiday'::character varying, 'training'::character varying, 'emergency'::character varying, 'unpaid'::character varying])::text[]))) not valid;

alter table "public"."time_off_requests" validate constraint "time_off_requests_time_off_type_check";

alter table "public"."user_certifications" add constraint "user_certifications_status_check" CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'expired'::character varying, 'pending'::character varying, 'suspended'::character varying])::text[]))) not valid;

alter table "public"."user_certifications" validate constraint "user_certifications_status_check";

alter table "public"."user_skills" add constraint "user_skills_category_check" CHECK (((category)::text = ANY ((ARRAY['technical'::character varying, 'mechanical'::character varying, 'electrical'::character varying, 'plumbing'::character varying, 'hvac'::character varying, 'carpentry'::character varying, 'painting'::character varying, 'cleaning'::character varying, 'security'::character varying, 'administrative'::character varying])::text[]))) not valid;

alter table "public"."user_skills" validate constraint "user_skills_category_check";

alter table "public"."user_skills" add constraint "user_skills_level_check" CHECK (((level)::text = ANY ((ARRAY['beginner'::character varying, 'intermediate'::character varying, 'advanced'::character varying, 'expert'::character varying, 'master'::character varying])::text[]))) not valid;

alter table "public"."user_skills" validate constraint "user_skills_level_check";


