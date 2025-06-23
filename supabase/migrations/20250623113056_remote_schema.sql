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

create table "public"."availability_windows" (
    "id" uuid not null default gen_random_uuid(),
    "user_capabilities_id" uuid not null,
    "day_of_week" integer not null,
    "start_time" time without time zone not null,
    "end_time" time without time zone not null,
    "availability_type" character varying(20) default 'regular'::character varying,
    "max_hours_per_day" numeric(4,2),
    "break_duration_minutes" integer default 30,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


alter table "public"."availability_windows" enable row level security;

create table "public"."calendar_events" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" text not null,
    "business_id" uuid not null,
    "title" character varying(200) not null,
    "description" text,
    "event_type" character varying(50) default 'work_schedule'::character varying,
    "start_datetime" timestamp with time zone not null,
    "end_datetime" timestamp with time zone not null,
    "is_all_day" boolean default false,
    "timezone" character varying(100) default 'UTC'::character varying,
    "recurrence_type" character varying(20) default 'none'::character varying,
    "recurrence_end_date" date,
    "recurrence_count" integer,
    "recurrence_interval" integer default 1,
    "recurrence_days_of_week" integer[] default '{}'::integer[],
    "blocks_scheduling" boolean default true,
    "allows_emergency_override" boolean default false,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now(),
    "is_active" boolean default true
);


alter table "public"."calendar_events" enable row level security;

create table "public"."calendar_preferences" (
    "user_id" text not null,
    "business_id" uuid not null,
    "timezone" character varying(100) default 'UTC'::character varying,
    "date_format" character varying(20) default 'YYYY-MM-DD'::character varying,
    "time_format" character varying(5) default '24h'::character varying,
    "week_start_day" integer default 0,
    "preferred_working_hours_template_id" uuid,
    "min_time_between_jobs_minutes" integer default 30,
    "max_commute_time_minutes" integer default 60,
    "allows_back_to_back_jobs" boolean default false,
    "requires_prep_time_minutes" integer default 15,
    "job_reminder_minutes_before" integer[] default '{60,15}'::integer[],
    "schedule_change_notifications" boolean default true,
    "new_job_notifications" boolean default true,
    "cancellation_notifications" boolean default true,
    "auto_accept_jobs_in_hours" boolean default false,
    "auto_decline_outside_hours" boolean default true,
    "emergency_availability_outside_hours" boolean default false,
    "weekend_availability" boolean default false,
    "holiday_availability" boolean default false,
    "travel_buffer_percentage" numeric(3,2) default 1.20,
    "job_buffer_minutes" integer default 15,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


alter table "public"."calendar_preferences" enable row level security;

create table "public"."time_off_requests" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" text not null,
    "business_id" uuid not null,
    "time_off_type" character varying(20) not null,
    "start_date" date not null,
    "end_date" date not null,
    "reason" text,
    "notes" text,
    "status" character varying(20) default 'pending'::character varying,
    "requested_by" text not null,
    "approved_by" text,
    "approval_date" timestamp with time zone,
    "denial_reason" text,
    "affects_scheduling" boolean default true,
    "emergency_contact_allowed" boolean default false,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


alter table "public"."time_off_requests" enable row level security;

create table "public"."user_capabilities" (
    "id" uuid not null default gen_random_uuid(),
    "business_id" uuid not null,
    "user_id" text not null,
    "home_base_address" text,
    "home_base_latitude" numeric(10,8),
    "home_base_longitude" numeric(11,8),
    "vehicle_type" character varying(50),
    "has_vehicle" boolean default true,
    "preferred_start_time" time without time zone,
    "preferred_end_time" time without time zone,
    "min_time_between_jobs_minutes" integer default 30,
    "max_commute_time_minutes" integer default 60,
    "average_job_rating" numeric(3,2),
    "completion_rate" numeric(5,2),
    "punctuality_score" numeric(5,2),
    "working_hours_template_id" uuid,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now(),
    "is_active" boolean default true
);


alter table "public"."user_capabilities" enable row level security;

create table "public"."user_certifications" (
    "id" uuid not null default gen_random_uuid(),
    "user_capabilities_id" uuid not null,
    "certification_id" character varying(100) not null,
    "name" character varying(200) not null,
    "issuing_authority" character varying(200) not null,
    "issue_date" timestamp with time zone not null,
    "expiry_date" timestamp with time zone,
    "status" character varying(20) default 'active'::character varying,
    "verification_number" character varying(100),
    "renewal_required" boolean default true,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


alter table "public"."user_certifications" enable row level security;

create table "public"."user_skills" (
    "id" uuid not null default gen_random_uuid(),
    "user_capabilities_id" uuid not null,
    "skill_id" character varying(100) not null,
    "name" character varying(200) not null,
    "category" character varying(50) not null,
    "level" character varying(20) not null,
    "years_experience" numeric(4,2) not null,
    "last_used" timestamp with time zone,
    "proficiency_score" numeric(5,2),
    "certification_required" boolean default false,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


alter table "public"."user_skills" enable row level security;

create table "public"."working_hours_templates" (
    "id" uuid not null default gen_random_uuid(),
    "name" character varying(100) not null,
    "description" text,
    "monday_start" time without time zone,
    "monday_end" time without time zone,
    "tuesday_start" time without time zone,
    "tuesday_end" time without time zone,
    "wednesday_start" time without time zone,
    "wednesday_end" time without time zone,
    "thursday_start" time without time zone,
    "thursday_end" time without time zone,
    "friday_start" time without time zone,
    "friday_end" time without time zone,
    "saturday_start" time without time zone,
    "saturday_end" time without time zone,
    "sunday_start" time without time zone,
    "sunday_end" time without time zone,
    "break_duration_minutes" integer default 30,
    "lunch_start_time" time without time zone,
    "lunch_duration_minutes" integer default 60,
    "allows_flexible_start" boolean default false,
    "flexible_start_window_minutes" integer default 30,
    "allows_overtime" boolean default false,
    "max_overtime_hours_per_day" numeric(3,1) default 2.0,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now(),
    "is_active" boolean default true
);


alter table "public"."working_hours_templates" enable row level security;

create table "public"."workload_capacity" (
    "id" uuid not null default gen_random_uuid(),
    "user_capabilities_id" uuid not null,
    "max_concurrent_jobs" integer default 3,
    "max_daily_hours" numeric(4,2) default 8.0,
    "max_weekly_hours" numeric(5,2) default 40.0,
    "preferred_job_types" text[] default '{}'::text[],
    "max_travel_distance_km" numeric(6,2) default 50.0,
    "overtime_willingness" boolean default false,
    "emergency_availability" boolean default false,
    "created_date" timestamp with time zone default now(),
    "last_modified" timestamp with time zone default now()
);


alter table "public"."workload_capacity" enable row level security;

CREATE UNIQUE INDEX availability_windows_pkey ON public.availability_windows USING btree (id);

CREATE UNIQUE INDEX calendar_events_pkey ON public.calendar_events USING btree (id);

CREATE UNIQUE INDEX calendar_preferences_pkey ON public.calendar_preferences USING btree (user_id, business_id);

CREATE INDEX idx_availability_windows_capabilities_id ON public.availability_windows USING btree (user_capabilities_id);

CREATE INDEX idx_availability_windows_day ON public.availability_windows USING btree (day_of_week);

CREATE INDEX idx_calendar_events_active ON public.calendar_events USING btree (is_active) WHERE (is_active = true);

CREATE INDEX idx_calendar_events_datetime ON public.calendar_events USING btree (start_datetime, end_datetime);

CREATE INDEX idx_calendar_events_recurrence ON public.calendar_events USING btree (recurrence_type) WHERE ((recurrence_type)::text <> 'none'::text);

CREATE INDEX idx_calendar_events_user_business ON public.calendar_events USING btree (user_id, business_id);

CREATE INDEX idx_time_off_dates ON public.time_off_requests USING btree (start_date, end_date);

CREATE INDEX idx_time_off_pending ON public.time_off_requests USING btree (business_id, status) WHERE ((status)::text = 'pending'::text);

CREATE INDEX idx_time_off_status ON public.time_off_requests USING btree (status);

CREATE INDEX idx_time_off_user_business ON public.time_off_requests USING btree (user_id, business_id);

CREATE INDEX idx_user_capabilities_active ON public.user_capabilities USING btree (is_active) WHERE (is_active = true);

CREATE INDEX idx_user_capabilities_business_id ON public.user_capabilities USING btree (business_id);

CREATE INDEX idx_user_capabilities_user_id ON public.user_capabilities USING btree (user_id);

CREATE INDEX idx_user_certifications_capabilities_id ON public.user_certifications USING btree (user_capabilities_id);

CREATE INDEX idx_user_certifications_expiry ON public.user_certifications USING btree (expiry_date) WHERE (expiry_date IS NOT NULL);

CREATE INDEX idx_user_certifications_status ON public.user_certifications USING btree (status);

CREATE INDEX idx_user_skills_capabilities_id ON public.user_skills USING btree (user_capabilities_id);

CREATE INDEX idx_user_skills_category ON public.user_skills USING btree (category);

CREATE INDEX idx_user_skills_level ON public.user_skills USING btree (level);

CREATE INDEX idx_user_skills_skill_id ON public.user_skills USING btree (skill_id);

CREATE INDEX idx_working_hours_templates_active ON public.working_hours_templates USING btree (is_active) WHERE (is_active = true);

CREATE INDEX idx_workload_capacity_capabilities_id ON public.workload_capacity USING btree (user_capabilities_id);

CREATE UNIQUE INDEX time_off_requests_pkey ON public.time_off_requests USING btree (id);

CREATE UNIQUE INDEX user_capabilities_business_id_user_id_key ON public.user_capabilities USING btree (business_id, user_id);

CREATE UNIQUE INDEX user_capabilities_pkey ON public.user_capabilities USING btree (id);

CREATE UNIQUE INDEX user_certifications_pkey ON public.user_certifications USING btree (id);

CREATE UNIQUE INDEX user_certifications_user_capabilities_id_certification_id_key ON public.user_certifications USING btree (user_capabilities_id, certification_id);

CREATE UNIQUE INDEX user_skills_pkey ON public.user_skills USING btree (id);

CREATE UNIQUE INDEX user_skills_user_capabilities_id_skill_id_key ON public.user_skills USING btree (user_capabilities_id, skill_id);

CREATE UNIQUE INDEX working_hours_templates_pkey ON public.working_hours_templates USING btree (id);

CREATE UNIQUE INDEX workload_capacity_pkey ON public.workload_capacity USING btree (id);

CREATE UNIQUE INDEX workload_capacity_user_capabilities_id_key ON public.workload_capacity USING btree (user_capabilities_id);

CREATE INDEX idx_jobs_assigned_status ON public.jobs USING gin (assigned_to) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

CREATE INDEX idx_jobs_scheduled_end_active ON public.jobs USING btree (business_id, scheduled_end) WHERE ((status)::text = ANY ((ARRAY['scheduled'::character varying, 'in_progress'::character varying])::text[]));

alter table "public"."availability_windows" add constraint "availability_windows_pkey" PRIMARY KEY using index "availability_windows_pkey";

alter table "public"."calendar_events" add constraint "calendar_events_pkey" PRIMARY KEY using index "calendar_events_pkey";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_pkey" PRIMARY KEY using index "calendar_preferences_pkey";

alter table "public"."time_off_requests" add constraint "time_off_requests_pkey" PRIMARY KEY using index "time_off_requests_pkey";

alter table "public"."user_capabilities" add constraint "user_capabilities_pkey" PRIMARY KEY using index "user_capabilities_pkey";

alter table "public"."user_certifications" add constraint "user_certifications_pkey" PRIMARY KEY using index "user_certifications_pkey";

alter table "public"."user_skills" add constraint "user_skills_pkey" PRIMARY KEY using index "user_skills_pkey";

alter table "public"."working_hours_templates" add constraint "working_hours_templates_pkey" PRIMARY KEY using index "working_hours_templates_pkey";

alter table "public"."workload_capacity" add constraint "workload_capacity_pkey" PRIMARY KEY using index "workload_capacity_pkey";

alter table "public"."availability_windows" add constraint "availability_windows_availability_type_check" CHECK (((availability_type)::text = ANY ((ARRAY['regular'::character varying, 'flexible'::character varying, 'on_call'::character varying, 'project_based'::character varying])::text[]))) not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_availability_type_check";

alter table "public"."availability_windows" add constraint "availability_windows_break_duration_minutes_check" CHECK (((break_duration_minutes >= 0) AND (break_duration_minutes <= 120))) not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_break_duration_minutes_check";

alter table "public"."availability_windows" add constraint "availability_windows_check" CHECK ((end_time > start_time)) not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_check";

alter table "public"."availability_windows" add constraint "availability_windows_day_of_week_check" CHECK (((day_of_week >= 0) AND (day_of_week <= 6))) not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_day_of_week_check";

alter table "public"."availability_windows" add constraint "availability_windows_max_hours_per_day_check" CHECK ((max_hours_per_day > (0)::numeric)) not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_max_hours_per_day_check";

alter table "public"."availability_windows" add constraint "availability_windows_user_capabilities_id_fkey" FOREIGN KEY (user_capabilities_id) REFERENCES user_capabilities(id) ON DELETE CASCADE not valid;

alter table "public"."availability_windows" validate constraint "availability_windows_user_capabilities_id_fkey";

alter table "public"."calendar_events" add constraint "calendar_events_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_business_id_fkey";

alter table "public"."calendar_events" add constraint "calendar_events_end_after_start" CHECK ((end_datetime > start_datetime)) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_end_after_start";

alter table "public"."calendar_events" add constraint "calendar_events_event_type_check" CHECK (((event_type)::text = ANY ((ARRAY['work_schedule'::character varying, 'time_off'::character varying, 'break'::character varying, 'meeting'::character varying, 'training'::character varying, 'personal'::character varying])::text[]))) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_event_type_check";

alter table "public"."calendar_events" add constraint "calendar_events_recurrence_count_check" CHECK ((recurrence_count > 0)) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_recurrence_count_check";

alter table "public"."calendar_events" add constraint "calendar_events_recurrence_days_valid" CHECK (((array_length(recurrence_days_of_week, 1) IS NULL) OR (recurrence_days_of_week <@ ARRAY[0, 1, 2, 3, 4, 5, 6]))) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_recurrence_days_valid";

alter table "public"."calendar_events" add constraint "calendar_events_recurrence_interval_check" CHECK ((recurrence_interval > 0)) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_recurrence_interval_check";

alter table "public"."calendar_events" add constraint "calendar_events_recurrence_type_check" CHECK (((recurrence_type)::text = ANY ((ARRAY['none'::character varying, 'daily'::character varying, 'weekly'::character varying, 'biweekly'::character varying, 'monthly'::character varying, 'custom'::character varying])::text[]))) not valid;

alter table "public"."calendar_events" validate constraint "calendar_events_recurrence_type_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_business_id_fkey";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_job_buffer_minutes_check" CHECK ((job_buffer_minutes >= 0)) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_job_buffer_minutes_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_max_commute_time_minutes_check" CHECK ((max_commute_time_minutes >= 0)) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_max_commute_time_minutes_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_min_time_between_jobs_minutes_check" CHECK ((min_time_between_jobs_minutes >= 0)) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_min_time_between_jobs_minutes_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_preferred_working_hours_template_id_fkey" FOREIGN KEY (preferred_working_hours_template_id) REFERENCES working_hours_templates(id) ON DELETE SET NULL not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_preferred_working_hours_template_id_fkey";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_requires_prep_time_minutes_check" CHECK ((requires_prep_time_minutes >= 0)) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_requires_prep_time_minutes_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_time_format_check" CHECK (((time_format)::text = ANY ((ARRAY['12h'::character varying, '24h'::character varying])::text[]))) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_time_format_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_travel_buffer_percentage_check" CHECK ((travel_buffer_percentage >= 1.0)) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_travel_buffer_percentage_check";

alter table "public"."calendar_preferences" add constraint "calendar_preferences_week_start_day_check" CHECK (((week_start_day >= 0) AND (week_start_day <= 6))) not valid;

alter table "public"."calendar_preferences" validate constraint "calendar_preferences_week_start_day_check";

alter table "public"."time_off_requests" add constraint "time_off_denial_reason_required" CHECK (((((status)::text = 'denied'::text) AND (denial_reason IS NOT NULL)) OR ((status)::text <> 'denied'::text))) not valid;

alter table "public"."time_off_requests" validate constraint "time_off_denial_reason_required";

alter table "public"."time_off_requests" add constraint "time_off_end_after_start" CHECK ((end_date >= start_date)) not valid;

alter table "public"."time_off_requests" validate constraint "time_off_end_after_start";

alter table "public"."time_off_requests" add constraint "time_off_requests_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."time_off_requests" validate constraint "time_off_requests_business_id_fkey";

alter table "public"."time_off_requests" add constraint "time_off_requests_status_check" CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'denied'::character varying, 'cancelled'::character varying])::text[]))) not valid;

alter table "public"."time_off_requests" validate constraint "time_off_requests_status_check";

alter table "public"."time_off_requests" add constraint "time_off_requests_time_off_type_check" CHECK (((time_off_type)::text = ANY ((ARRAY['vacation'::character varying, 'sick_leave'::character varying, 'personal'::character varying, 'holiday'::character varying, 'training'::character varying, 'emergency'::character varying, 'unpaid'::character varying])::text[]))) not valid;

alter table "public"."time_off_requests" validate constraint "time_off_requests_time_off_type_check";

alter table "public"."user_capabilities" add constraint "fk_user_capabilities_working_hours_template" FOREIGN KEY (working_hours_template_id) REFERENCES working_hours_templates(id) ON DELETE SET NULL not valid;

alter table "public"."user_capabilities" validate constraint "fk_user_capabilities_working_hours_template";

alter table "public"."user_capabilities" add constraint "user_capabilities_average_job_rating_check" CHECK (((average_job_rating >= (0)::numeric) AND (average_job_rating <= (5)::numeric))) not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_average_job_rating_check";

alter table "public"."user_capabilities" add constraint "user_capabilities_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_business_id_fkey";

alter table "public"."user_capabilities" add constraint "user_capabilities_business_id_user_id_key" UNIQUE using index "user_capabilities_business_id_user_id_key";

alter table "public"."user_capabilities" add constraint "user_capabilities_check" CHECK (((home_base_latitude IS NULL) = (home_base_longitude IS NULL))) not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_check";

alter table "public"."user_capabilities" add constraint "user_capabilities_completion_rate_check" CHECK (((completion_rate >= (0)::numeric) AND (completion_rate <= (100)::numeric))) not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_completion_rate_check";

alter table "public"."user_capabilities" add constraint "user_capabilities_max_commute_time_minutes_check" CHECK ((max_commute_time_minutes > 0)) not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_max_commute_time_minutes_check";

alter table "public"."user_capabilities" add constraint "user_capabilities_min_time_between_jobs_minutes_check" CHECK ((min_time_between_jobs_minutes >= 0)) not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_min_time_between_jobs_minutes_check";

alter table "public"."user_capabilities" add constraint "user_capabilities_punctuality_score_check" CHECK (((punctuality_score >= (0)::numeric) AND (punctuality_score <= (100)::numeric))) not valid;

alter table "public"."user_capabilities" validate constraint "user_capabilities_punctuality_score_check";

alter table "public"."user_certifications" add constraint "user_certifications_check" CHECK (((expiry_date IS NULL) OR (expiry_date > issue_date))) not valid;

alter table "public"."user_certifications" validate constraint "user_certifications_check";

alter table "public"."user_certifications" add constraint "user_certifications_status_check" CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'expired'::character varying, 'pending'::character varying, 'suspended'::character varying])::text[]))) not valid;

alter table "public"."user_certifications" validate constraint "user_certifications_status_check";

alter table "public"."user_certifications" add constraint "user_certifications_user_capabilities_id_certification_id_key" UNIQUE using index "user_certifications_user_capabilities_id_certification_id_key";

alter table "public"."user_certifications" add constraint "user_certifications_user_capabilities_id_fkey" FOREIGN KEY (user_capabilities_id) REFERENCES user_capabilities(id) ON DELETE CASCADE not valid;

alter table "public"."user_certifications" validate constraint "user_certifications_user_capabilities_id_fkey";

alter table "public"."user_skills" add constraint "user_skills_category_check" CHECK (((category)::text = ANY ((ARRAY['technical'::character varying, 'mechanical'::character varying, 'electrical'::character varying, 'plumbing'::character varying, 'hvac'::character varying, 'carpentry'::character varying, 'painting'::character varying, 'cleaning'::character varying, 'security'::character varying, 'administrative'::character varying])::text[]))) not valid;

alter table "public"."user_skills" validate constraint "user_skills_category_check";

alter table "public"."user_skills" add constraint "user_skills_level_check" CHECK (((level)::text = ANY ((ARRAY['beginner'::character varying, 'intermediate'::character varying, 'advanced'::character varying, 'expert'::character varying, 'master'::character varying])::text[]))) not valid;

alter table "public"."user_skills" validate constraint "user_skills_level_check";

alter table "public"."user_skills" add constraint "user_skills_proficiency_score_check" CHECK (((proficiency_score >= (0)::numeric) AND (proficiency_score <= (100)::numeric))) not valid;

alter table "public"."user_skills" validate constraint "user_skills_proficiency_score_check";

alter table "public"."user_skills" add constraint "user_skills_user_capabilities_id_fkey" FOREIGN KEY (user_capabilities_id) REFERENCES user_capabilities(id) ON DELETE CASCADE not valid;

alter table "public"."user_skills" validate constraint "user_skills_user_capabilities_id_fkey";

alter table "public"."user_skills" add constraint "user_skills_user_capabilities_id_skill_id_key" UNIQUE using index "user_skills_user_capabilities_id_skill_id_key";

alter table "public"."user_skills" add constraint "user_skills_years_experience_check" CHECK ((years_experience >= (0)::numeric)) not valid;

alter table "public"."user_skills" validate constraint "user_skills_years_experience_check";

alter table "public"."working_hours_templates" add constraint "working_hours_templates_break_duration_minutes_check" CHECK (((break_duration_minutes >= 0) AND (break_duration_minutes <= 120))) not valid;

alter table "public"."working_hours_templates" validate constraint "working_hours_templates_break_duration_minutes_check";

alter table "public"."working_hours_templates" add constraint "working_hours_templates_flexible_start_window_minutes_check" CHECK (((flexible_start_window_minutes >= 0) AND (flexible_start_window_minutes <= 120))) not valid;

alter table "public"."working_hours_templates" validate constraint "working_hours_templates_flexible_start_window_minutes_check";

alter table "public"."working_hours_templates" add constraint "working_hours_templates_lunch_duration_minutes_check" CHECK (((lunch_duration_minutes >= 0) AND (lunch_duration_minutes <= 180))) not valid;

alter table "public"."working_hours_templates" validate constraint "working_hours_templates_lunch_duration_minutes_check";

alter table "public"."working_hours_templates" add constraint "working_hours_templates_max_overtime_hours_per_day_check" CHECK (((max_overtime_hours_per_day >= (0)::numeric) AND (max_overtime_hours_per_day <= (8)::numeric))) not valid;

alter table "public"."working_hours_templates" validate constraint "working_hours_templates_max_overtime_hours_per_day_check";

alter table "public"."workload_capacity" add constraint "workload_capacity_max_concurrent_jobs_check" CHECK ((max_concurrent_jobs > 0)) not valid;

alter table "public"."workload_capacity" validate constraint "workload_capacity_max_concurrent_jobs_check";

alter table "public"."workload_capacity" add constraint "workload_capacity_max_daily_hours_check" CHECK ((max_daily_hours > (0)::numeric)) not valid;

alter table "public"."workload_capacity" validate constraint "workload_capacity_max_daily_hours_check";

alter table "public"."workload_capacity" add constraint "workload_capacity_max_travel_distance_km_check" CHECK ((max_travel_distance_km >= (0)::numeric)) not valid;

alter table "public"."workload_capacity" validate constraint "workload_capacity_max_travel_distance_km_check";

alter table "public"."workload_capacity" add constraint "workload_capacity_max_weekly_hours_check" CHECK ((max_weekly_hours > (0)::numeric)) not valid;

alter table "public"."workload_capacity" validate constraint "workload_capacity_max_weekly_hours_check";

alter table "public"."workload_capacity" add constraint "workload_capacity_user_capabilities_id_fkey" FOREIGN KEY (user_capabilities_id) REFERENCES user_capabilities(id) ON DELETE CASCADE not valid;

alter table "public"."workload_capacity" validate constraint "workload_capacity_user_capabilities_id_fkey";

alter table "public"."workload_capacity" add constraint "workload_capacity_user_capabilities_id_key" UNIQUE using index "workload_capacity_user_capabilities_id_key";

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

CREATE OR REPLACE FUNCTION public.update_last_modified()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$function$
;

grant delete on table "public"."availability_windows" to "anon";

grant insert on table "public"."availability_windows" to "anon";

grant references on table "public"."availability_windows" to "anon";

grant select on table "public"."availability_windows" to "anon";

grant trigger on table "public"."availability_windows" to "anon";

grant truncate on table "public"."availability_windows" to "anon";

grant update on table "public"."availability_windows" to "anon";

grant delete on table "public"."availability_windows" to "authenticated";

grant insert on table "public"."availability_windows" to "authenticated";

grant references on table "public"."availability_windows" to "authenticated";

grant select on table "public"."availability_windows" to "authenticated";

grant trigger on table "public"."availability_windows" to "authenticated";

grant truncate on table "public"."availability_windows" to "authenticated";

grant update on table "public"."availability_windows" to "authenticated";

grant delete on table "public"."availability_windows" to "service_role";

grant insert on table "public"."availability_windows" to "service_role";

grant references on table "public"."availability_windows" to "service_role";

grant select on table "public"."availability_windows" to "service_role";

grant trigger on table "public"."availability_windows" to "service_role";

grant truncate on table "public"."availability_windows" to "service_role";

grant update on table "public"."availability_windows" to "service_role";

grant delete on table "public"."calendar_events" to "anon";

grant insert on table "public"."calendar_events" to "anon";

grant references on table "public"."calendar_events" to "anon";

grant select on table "public"."calendar_events" to "anon";

grant trigger on table "public"."calendar_events" to "anon";

grant truncate on table "public"."calendar_events" to "anon";

grant update on table "public"."calendar_events" to "anon";

grant delete on table "public"."calendar_events" to "authenticated";

grant insert on table "public"."calendar_events" to "authenticated";

grant references on table "public"."calendar_events" to "authenticated";

grant select on table "public"."calendar_events" to "authenticated";

grant trigger on table "public"."calendar_events" to "authenticated";

grant truncate on table "public"."calendar_events" to "authenticated";

grant update on table "public"."calendar_events" to "authenticated";

grant delete on table "public"."calendar_events" to "service_role";

grant insert on table "public"."calendar_events" to "service_role";

grant references on table "public"."calendar_events" to "service_role";

grant select on table "public"."calendar_events" to "service_role";

grant trigger on table "public"."calendar_events" to "service_role";

grant truncate on table "public"."calendar_events" to "service_role";

grant update on table "public"."calendar_events" to "service_role";

grant delete on table "public"."calendar_preferences" to "anon";

grant insert on table "public"."calendar_preferences" to "anon";

grant references on table "public"."calendar_preferences" to "anon";

grant select on table "public"."calendar_preferences" to "anon";

grant trigger on table "public"."calendar_preferences" to "anon";

grant truncate on table "public"."calendar_preferences" to "anon";

grant update on table "public"."calendar_preferences" to "anon";

grant delete on table "public"."calendar_preferences" to "authenticated";

grant insert on table "public"."calendar_preferences" to "authenticated";

grant references on table "public"."calendar_preferences" to "authenticated";

grant select on table "public"."calendar_preferences" to "authenticated";

grant trigger on table "public"."calendar_preferences" to "authenticated";

grant truncate on table "public"."calendar_preferences" to "authenticated";

grant update on table "public"."calendar_preferences" to "authenticated";

grant delete on table "public"."calendar_preferences" to "service_role";

grant insert on table "public"."calendar_preferences" to "service_role";

grant references on table "public"."calendar_preferences" to "service_role";

grant select on table "public"."calendar_preferences" to "service_role";

grant trigger on table "public"."calendar_preferences" to "service_role";

grant truncate on table "public"."calendar_preferences" to "service_role";

grant update on table "public"."calendar_preferences" to "service_role";

grant delete on table "public"."time_off_requests" to "anon";

grant insert on table "public"."time_off_requests" to "anon";

grant references on table "public"."time_off_requests" to "anon";

grant select on table "public"."time_off_requests" to "anon";

grant trigger on table "public"."time_off_requests" to "anon";

grant truncate on table "public"."time_off_requests" to "anon";

grant update on table "public"."time_off_requests" to "anon";

grant delete on table "public"."time_off_requests" to "authenticated";

grant insert on table "public"."time_off_requests" to "authenticated";

grant references on table "public"."time_off_requests" to "authenticated";

grant select on table "public"."time_off_requests" to "authenticated";

grant trigger on table "public"."time_off_requests" to "authenticated";

grant truncate on table "public"."time_off_requests" to "authenticated";

grant update on table "public"."time_off_requests" to "authenticated";

grant delete on table "public"."time_off_requests" to "service_role";

grant insert on table "public"."time_off_requests" to "service_role";

grant references on table "public"."time_off_requests" to "service_role";

grant select on table "public"."time_off_requests" to "service_role";

grant trigger on table "public"."time_off_requests" to "service_role";

grant truncate on table "public"."time_off_requests" to "service_role";

grant update on table "public"."time_off_requests" to "service_role";

grant delete on table "public"."user_capabilities" to "anon";

grant insert on table "public"."user_capabilities" to "anon";

grant references on table "public"."user_capabilities" to "anon";

grant select on table "public"."user_capabilities" to "anon";

grant trigger on table "public"."user_capabilities" to "anon";

grant truncate on table "public"."user_capabilities" to "anon";

grant update on table "public"."user_capabilities" to "anon";

grant delete on table "public"."user_capabilities" to "authenticated";

grant insert on table "public"."user_capabilities" to "authenticated";

grant references on table "public"."user_capabilities" to "authenticated";

grant select on table "public"."user_capabilities" to "authenticated";

grant trigger on table "public"."user_capabilities" to "authenticated";

grant truncate on table "public"."user_capabilities" to "authenticated";

grant update on table "public"."user_capabilities" to "authenticated";

grant delete on table "public"."user_capabilities" to "service_role";

grant insert on table "public"."user_capabilities" to "service_role";

grant references on table "public"."user_capabilities" to "service_role";

grant select on table "public"."user_capabilities" to "service_role";

grant trigger on table "public"."user_capabilities" to "service_role";

grant truncate on table "public"."user_capabilities" to "service_role";

grant update on table "public"."user_capabilities" to "service_role";

grant delete on table "public"."user_certifications" to "anon";

grant insert on table "public"."user_certifications" to "anon";

grant references on table "public"."user_certifications" to "anon";

grant select on table "public"."user_certifications" to "anon";

grant trigger on table "public"."user_certifications" to "anon";

grant truncate on table "public"."user_certifications" to "anon";

grant update on table "public"."user_certifications" to "anon";

grant delete on table "public"."user_certifications" to "authenticated";

grant insert on table "public"."user_certifications" to "authenticated";

grant references on table "public"."user_certifications" to "authenticated";

grant select on table "public"."user_certifications" to "authenticated";

grant trigger on table "public"."user_certifications" to "authenticated";

grant truncate on table "public"."user_certifications" to "authenticated";

grant update on table "public"."user_certifications" to "authenticated";

grant delete on table "public"."user_certifications" to "service_role";

grant insert on table "public"."user_certifications" to "service_role";

grant references on table "public"."user_certifications" to "service_role";

grant select on table "public"."user_certifications" to "service_role";

grant trigger on table "public"."user_certifications" to "service_role";

grant truncate on table "public"."user_certifications" to "service_role";

grant update on table "public"."user_certifications" to "service_role";

grant delete on table "public"."user_skills" to "anon";

grant insert on table "public"."user_skills" to "anon";

grant references on table "public"."user_skills" to "anon";

grant select on table "public"."user_skills" to "anon";

grant trigger on table "public"."user_skills" to "anon";

grant truncate on table "public"."user_skills" to "anon";

grant update on table "public"."user_skills" to "anon";

grant delete on table "public"."user_skills" to "authenticated";

grant insert on table "public"."user_skills" to "authenticated";

grant references on table "public"."user_skills" to "authenticated";

grant select on table "public"."user_skills" to "authenticated";

grant trigger on table "public"."user_skills" to "authenticated";

grant truncate on table "public"."user_skills" to "authenticated";

grant update on table "public"."user_skills" to "authenticated";

grant delete on table "public"."user_skills" to "service_role";

grant insert on table "public"."user_skills" to "service_role";

grant references on table "public"."user_skills" to "service_role";

grant select on table "public"."user_skills" to "service_role";

grant trigger on table "public"."user_skills" to "service_role";

grant truncate on table "public"."user_skills" to "service_role";

grant update on table "public"."user_skills" to "service_role";

grant delete on table "public"."working_hours_templates" to "anon";

grant insert on table "public"."working_hours_templates" to "anon";

grant references on table "public"."working_hours_templates" to "anon";

grant select on table "public"."working_hours_templates" to "anon";

grant trigger on table "public"."working_hours_templates" to "anon";

grant truncate on table "public"."working_hours_templates" to "anon";

grant update on table "public"."working_hours_templates" to "anon";

grant delete on table "public"."working_hours_templates" to "authenticated";

grant insert on table "public"."working_hours_templates" to "authenticated";

grant references on table "public"."working_hours_templates" to "authenticated";

grant select on table "public"."working_hours_templates" to "authenticated";

grant trigger on table "public"."working_hours_templates" to "authenticated";

grant truncate on table "public"."working_hours_templates" to "authenticated";

grant update on table "public"."working_hours_templates" to "authenticated";

grant delete on table "public"."working_hours_templates" to "service_role";

grant insert on table "public"."working_hours_templates" to "service_role";

grant references on table "public"."working_hours_templates" to "service_role";

grant select on table "public"."working_hours_templates" to "service_role";

grant trigger on table "public"."working_hours_templates" to "service_role";

grant truncate on table "public"."working_hours_templates" to "service_role";

grant update on table "public"."working_hours_templates" to "service_role";

grant delete on table "public"."workload_capacity" to "anon";

grant insert on table "public"."workload_capacity" to "anon";

grant references on table "public"."workload_capacity" to "anon";

grant select on table "public"."workload_capacity" to "anon";

grant trigger on table "public"."workload_capacity" to "anon";

grant truncate on table "public"."workload_capacity" to "anon";

grant update on table "public"."workload_capacity" to "anon";

grant delete on table "public"."workload_capacity" to "authenticated";

grant insert on table "public"."workload_capacity" to "authenticated";

grant references on table "public"."workload_capacity" to "authenticated";

grant select on table "public"."workload_capacity" to "authenticated";

grant trigger on table "public"."workload_capacity" to "authenticated";

grant truncate on table "public"."workload_capacity" to "authenticated";

grant update on table "public"."workload_capacity" to "authenticated";

grant delete on table "public"."workload_capacity" to "service_role";

grant insert on table "public"."workload_capacity" to "service_role";

grant references on table "public"."workload_capacity" to "service_role";

grant select on table "public"."workload_capacity" to "service_role";

grant trigger on table "public"."workload_capacity" to "service_role";

grant truncate on table "public"."workload_capacity" to "service_role";

grant update on table "public"."workload_capacity" to "service_role";

create policy "availability_windows_business_isolation"
on "public"."availability_windows"
as permissive
for all
to public
using ((user_capabilities_id IN ( SELECT user_capabilities.id
   FROM user_capabilities
  WHERE (user_capabilities.business_id IN ( SELECT business_memberships.business_id
           FROM business_memberships
          WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))))));


create policy "calendar_events_business_isolation"
on "public"."calendar_events"
as permissive
for all
to public
using ((business_id IN ( SELECT business_memberships.business_id
   FROM business_memberships
  WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))));


create policy "calendar_preferences_business_isolation"
on "public"."calendar_preferences"
as permissive
for all
to public
using ((business_id IN ( SELECT business_memberships.business_id
   FROM business_memberships
  WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))));


create policy "time_off_requests_business_isolation"
on "public"."time_off_requests"
as permissive
for all
to public
using ((business_id IN ( SELECT business_memberships.business_id
   FROM business_memberships
  WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))));


create policy "user_capabilities_business_isolation"
on "public"."user_capabilities"
as permissive
for all
to public
using ((business_id IN ( SELECT business_memberships.business_id
   FROM business_memberships
  WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))));


create policy "user_certifications_business_isolation"
on "public"."user_certifications"
as permissive
for all
to public
using ((user_capabilities_id IN ( SELECT user_capabilities.id
   FROM user_capabilities
  WHERE (user_capabilities.business_id IN ( SELECT business_memberships.business_id
           FROM business_memberships
          WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))))));


create policy "user_skills_business_isolation"
on "public"."user_skills"
as permissive
for all
to public
using ((user_capabilities_id IN ( SELECT user_capabilities.id
   FROM user_capabilities
  WHERE (user_capabilities.business_id IN ( SELECT business_memberships.business_id
           FROM business_memberships
          WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))))));


create policy "working_hours_templates_public_read"
on "public"."working_hours_templates"
as permissive
for select
to public
using (true);


create policy "workload_capacity_business_isolation"
on "public"."workload_capacity"
as permissive
for all
to public
using ((user_capabilities_id IN ( SELECT user_capabilities.id
   FROM user_capabilities
  WHERE (user_capabilities.business_id IN ( SELECT business_memberships.business_id
           FROM business_memberships
          WHERE ((business_memberships.user_id = current_setting('app.current_user_id'::text, true)) AND (business_memberships.is_active = true)))))));


CREATE TRIGGER update_availability_windows_last_modified BEFORE UPDATE ON public.availability_windows FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_calendar_events_last_modified BEFORE UPDATE ON public.calendar_events FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_calendar_preferences_last_modified BEFORE UPDATE ON public.calendar_preferences FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_time_off_requests_last_modified BEFORE UPDATE ON public.time_off_requests FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_user_capabilities_last_modified BEFORE UPDATE ON public.user_capabilities FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_user_certifications_last_modified BEFORE UPDATE ON public.user_certifications FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_user_skills_last_modified BEFORE UPDATE ON public.user_skills FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_working_hours_templates_last_modified BEFORE UPDATE ON public.working_hours_templates FOR EACH ROW EXECUTE FUNCTION update_last_modified();

CREATE TRIGGER update_workload_capacity_last_modified BEFORE UPDATE ON public.workload_capacity FOR EACH ROW EXECUTE FUNCTION update_last_modified();


