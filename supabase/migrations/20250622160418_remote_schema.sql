alter table "public"."business_invitations" drop constraint "business_invitations_role_check";

alter table "public"."business_invitations" drop constraint "business_invitations_status_check";

alter table "public"."business_memberships" drop constraint "business_memberships_role_check";

alter table "public"."businesses" drop constraint "businesses_company_size_check";

alter table "public"."businesses" drop constraint "businesses_referral_source_check";

create table "public"."contact_activities" (
    "id" uuid not null default uuid_generate_v4(),
    "contact_id" uuid not null,
    "business_id" uuid not null,
    "activity_type" character varying(50) not null,
    "subject" character varying(200),
    "description" text,
    "activity_date" timestamp with time zone not null default now(),
    "duration_minutes" integer,
    "outcome" character varying(50),
    "performed_by" text not null,
    "related_job_id" uuid,
    "related_project_id" uuid,
    "related_invoice_id" uuid,
    "created_date" timestamp with time zone not null default now(),
    "last_modified" timestamp with time zone not null default now(),
    "activity_data" jsonb default '{}'::jsonb
);


create table "public"."contact_notes" (
    "id" uuid not null default uuid_generate_v4(),
    "contact_id" uuid not null,
    "business_id" uuid not null,
    "title" character varying(200),
    "content" text not null,
    "note_type" character varying(20) default 'general'::character varying,
    "is_private" boolean default false,
    "created_by" text not null,
    "created_date" timestamp with time zone not null default now(),
    "last_modified" timestamp with time zone not null default now(),
    "tags" jsonb default '[]'::jsonb
);


create table "public"."contact_segment_memberships" (
    "id" uuid not null default uuid_generate_v4(),
    "contact_id" uuid not null,
    "segment_id" uuid not null,
    "business_id" uuid not null,
    "added_date" timestamp with time zone not null default now(),
    "added_by" text
);


create table "public"."contact_segments" (
    "id" uuid not null default uuid_generate_v4(),
    "business_id" uuid not null,
    "name" character varying(100) not null,
    "description" text,
    "segment_type" character varying(20) default 'manual'::character varying,
    "criteria" jsonb,
    "color" character varying(7),
    "is_active" boolean default true,
    "created_by" text not null,
    "created_date" timestamp with time zone not null default now(),
    "last_modified" timestamp with time zone not null default now()
);


create table "public"."contacts" (
    "id" uuid not null default uuid_generate_v4(),
    "business_id" uuid not null,
    "contact_type" character varying(20) not null,
    "status" character varying(20) default 'active'::character varying,
    "first_name" character varying(100),
    "last_name" character varying(100),
    "company_name" character varying(200),
    "job_title" character varying(100),
    "email" character varying(320),
    "phone" character varying(20),
    "mobile_phone" character varying(20),
    "website" character varying(200),
    "address" jsonb,
    "priority" character varying(10) default 'medium'::character varying,
    "source" character varying(20),
    "tags" jsonb default '[]'::jsonb,
    "notes" text,
    "estimated_value" numeric(15,2),
    "currency" character varying(3) default 'USD'::character varying,
    "assigned_to" text,
    "created_by" text,
    "custom_fields" jsonb default '{}'::jsonb,
    "created_date" timestamp with time zone not null default now(),
    "last_modified" timestamp with time zone not null default now(),
    "last_contacted" timestamp with time zone
);


CREATE UNIQUE INDEX contact_activities_pkey ON public.contact_activities USING btree (id);

CREATE UNIQUE INDEX contact_notes_pkey ON public.contact_notes USING btree (id);

CREATE UNIQUE INDEX contact_segment_memberships_pkey ON public.contact_segment_memberships USING btree (id);

CREATE UNIQUE INDEX contact_segment_memberships_unique ON public.contact_segment_memberships USING btree (contact_id, segment_id);

CREATE UNIQUE INDEX contact_segments_business_name_unique ON public.contact_segments USING btree (business_id, name);

CREATE UNIQUE INDEX contact_segments_pkey ON public.contact_segments USING btree (id);

CREATE UNIQUE INDEX contacts_pkey ON public.contacts USING btree (id);

CREATE INDEX idx_contact_activities_business_date ON public.contact_activities USING btree (business_id, activity_date DESC);

CREATE INDEX idx_contact_activities_business_id ON public.contact_activities USING btree (business_id);

CREATE INDEX idx_contact_activities_contact_date ON public.contact_activities USING btree (contact_id, activity_date DESC);

CREATE INDEX idx_contact_activities_contact_id ON public.contact_activities USING btree (contact_id);

CREATE INDEX idx_contact_activities_date ON public.contact_activities USING btree (activity_date);

CREATE INDEX idx_contact_activities_performed_by ON public.contact_activities USING btree (performed_by);

CREATE INDEX idx_contact_activities_type ON public.contact_activities USING btree (activity_type);

CREATE INDEX idx_contact_notes_business_id ON public.contact_notes USING btree (business_id);

CREATE INDEX idx_contact_notes_contact_id ON public.contact_notes USING btree (contact_id);

CREATE INDEX idx_contact_notes_content_search ON public.contact_notes USING gin (to_tsvector('english'::regconfig, (((COALESCE(title, ''::character varying))::text || ' '::text) || COALESCE(content, ''::text))));

CREATE INDEX idx_contact_notes_created_by ON public.contact_notes USING btree (created_by);

CREATE INDEX idx_contact_notes_created_date ON public.contact_notes USING btree (created_date DESC);

CREATE INDEX idx_contact_notes_private ON public.contact_notes USING btree (is_private);

CREATE INDEX idx_contact_notes_tags ON public.contact_notes USING gin (tags);

CREATE INDEX idx_contact_notes_type ON public.contact_notes USING btree (note_type);

CREATE INDEX idx_contact_segment_memberships_business ON public.contact_segment_memberships USING btree (business_id);

CREATE INDEX idx_contact_segment_memberships_contact ON public.contact_segment_memberships USING btree (contact_id);

CREATE INDEX idx_contact_segment_memberships_segment ON public.contact_segment_memberships USING btree (segment_id);

CREATE INDEX idx_contact_segments_active ON public.contact_segments USING btree (is_active);

CREATE INDEX idx_contact_segments_business_id ON public.contact_segments USING btree (business_id);

CREATE INDEX idx_contact_segments_created_by ON public.contact_segments USING btree (created_by);

CREATE INDEX idx_contact_segments_type ON public.contact_segments USING btree (segment_type);

CREATE INDEX idx_contacts_assigned_to ON public.contacts USING btree (assigned_to);

CREATE INDEX idx_contacts_business_assigned ON public.contacts USING btree (business_id, assigned_to);

CREATE UNIQUE INDEX idx_contacts_business_email_unique ON public.contacts USING btree (business_id, email) WHERE ((email IS NOT NULL) AND ((email)::text <> ''::text));

CREATE INDEX idx_contacts_business_id ON public.contacts USING btree (business_id);

CREATE UNIQUE INDEX idx_contacts_business_phone_unique ON public.contacts USING btree (business_id, phone) WHERE ((phone IS NOT NULL) AND ((phone)::text <> ''::text));

CREATE INDEX idx_contacts_business_priority ON public.contacts USING btree (business_id, priority);

CREATE INDEX idx_contacts_business_status ON public.contacts USING btree (business_id, status);

CREATE INDEX idx_contacts_business_type ON public.contacts USING btree (business_id, contact_type);

CREATE INDEX idx_contacts_contact_type ON public.contacts USING btree (contact_type);

CREATE INDEX idx_contacts_created_by ON public.contacts USING btree (created_by);

CREATE INDEX idx_contacts_created_date ON public.contacts USING btree (created_date);

CREATE INDEX idx_contacts_custom_fields ON public.contacts USING gin (custom_fields);

CREATE INDEX idx_contacts_email_search ON public.contacts USING gin (to_tsvector('english'::regconfig, (COALESCE(email, ''::character varying))::text));

CREATE INDEX idx_contacts_last_contacted ON public.contacts USING btree (last_contacted);

CREATE INDEX idx_contacts_last_modified ON public.contacts USING btree (last_modified);

CREATE INDEX idx_contacts_name_search ON public.contacts USING gin (to_tsvector('english'::regconfig, (((((COALESCE(first_name, ''::character varying))::text || ' '::text) || (COALESCE(last_name, ''::character varying))::text) || ' '::text) || (COALESCE(company_name, ''::character varying))::text)));

CREATE INDEX idx_contacts_priority ON public.contacts USING btree (priority);

CREATE INDEX idx_contacts_source ON public.contacts USING btree (source);

CREATE INDEX idx_contacts_status ON public.contacts USING btree (status);

CREATE INDEX idx_contacts_tags ON public.contacts USING gin (tags);

alter table "public"."contact_activities" add constraint "contact_activities_pkey" PRIMARY KEY using index "contact_activities_pkey";

alter table "public"."contact_notes" add constraint "contact_notes_pkey" PRIMARY KEY using index "contact_notes_pkey";

alter table "public"."contact_segment_memberships" add constraint "contact_segment_memberships_pkey" PRIMARY KEY using index "contact_segment_memberships_pkey";

alter table "public"."contact_segments" add constraint "contact_segments_pkey" PRIMARY KEY using index "contact_segments_pkey";

alter table "public"."contacts" add constraint "contacts_pkey" PRIMARY KEY using index "contacts_pkey";

alter table "public"."contact_activities" add constraint "contact_activities_activity_type_check" CHECK (((activity_type)::text = ANY ((ARRAY['call'::character varying, 'email'::character varying, 'meeting'::character varying, 'note'::character varying, 'task'::character varying, 'quote'::character varying, 'invoice'::character varying, 'payment'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_activity_type_check";

alter table "public"."contact_activities" add constraint "contact_activities_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_business_id_fkey";

alter table "public"."contact_activities" add constraint "contact_activities_contact_id_fkey" FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_contact_id_fkey";

alter table "public"."contact_activities" add constraint "contact_activities_data_is_object" CHECK ((jsonb_typeof(activity_data) = 'object'::text)) not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_data_is_object";

alter table "public"."contact_activities" add constraint "contact_activities_duration_positive" CHECK (((duration_minutes IS NULL) OR (duration_minutes >= 0))) not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_duration_positive";

alter table "public"."contact_activities" add constraint "contact_activities_outcome_check" CHECK (((outcome)::text = ANY ((ARRAY['successful'::character varying, 'no_answer'::character varying, 'busy'::character varying, 'scheduled'::character varying, 'completed'::character varying, 'cancelled'::character varying])::text[]))) not valid;

alter table "public"."contact_activities" validate constraint "contact_activities_outcome_check";

alter table "public"."contact_notes" add constraint "contact_notes_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."contact_notes" validate constraint "contact_notes_business_id_fkey";

alter table "public"."contact_notes" add constraint "contact_notes_contact_id_fkey" FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE not valid;

alter table "public"."contact_notes" validate constraint "contact_notes_contact_id_fkey";

alter table "public"."contact_notes" add constraint "contact_notes_note_type_check" CHECK (((note_type)::text = ANY ((ARRAY['general'::character varying, 'meeting'::character varying, 'call'::character varying, 'email'::character varying, 'task'::character varying, 'reminder'::character varying])::text[]))) not valid;

alter table "public"."contact_notes" validate constraint "contact_notes_note_type_check";

alter table "public"."contact_notes" add constraint "contact_notes_tags_is_array" CHECK ((jsonb_typeof(tags) = 'array'::text)) not valid;

alter table "public"."contact_notes" validate constraint "contact_notes_tags_is_array";

alter table "public"."contact_segment_memberships" add constraint "contact_segment_memberships_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."contact_segment_memberships" validate constraint "contact_segment_memberships_business_id_fkey";

alter table "public"."contact_segment_memberships" add constraint "contact_segment_memberships_contact_id_fkey" FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE not valid;

alter table "public"."contact_segment_memberships" validate constraint "contact_segment_memberships_contact_id_fkey";

alter table "public"."contact_segment_memberships" add constraint "contact_segment_memberships_segment_id_fkey" FOREIGN KEY (segment_id) REFERENCES contact_segments(id) ON DELETE CASCADE not valid;

alter table "public"."contact_segment_memberships" validate constraint "contact_segment_memberships_segment_id_fkey";

alter table "public"."contact_segment_memberships" add constraint "contact_segment_memberships_unique" UNIQUE using index "contact_segment_memberships_unique";

alter table "public"."contact_segments" add constraint "contact_segments_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."contact_segments" validate constraint "contact_segments_business_id_fkey";

alter table "public"."contact_segments" add constraint "contact_segments_business_name_unique" UNIQUE using index "contact_segments_business_name_unique";

alter table "public"."contact_segments" add constraint "contact_segments_color_format" CHECK (((color IS NULL) OR ((color)::text ~ '^#[0-9A-Fa-f]{6}$'::text))) not valid;

alter table "public"."contact_segments" validate constraint "contact_segments_color_format";

alter table "public"."contact_segments" add constraint "contact_segments_criteria_is_object" CHECK (((criteria IS NULL) OR (jsonb_typeof(criteria) = 'object'::text))) not valid;

alter table "public"."contact_segments" validate constraint "contact_segments_criteria_is_object";

alter table "public"."contact_segments" add constraint "contact_segments_segment_type_check" CHECK (((segment_type)::text = ANY ((ARRAY['manual'::character varying, 'dynamic'::character varying, 'imported'::character varying])::text[]))) not valid;

alter table "public"."contact_segments" validate constraint "contact_segments_segment_type_check";

alter table "public"."contacts" add constraint "contacts_business_id_fkey" FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE not valid;

alter table "public"."contacts" validate constraint "contacts_business_id_fkey";

alter table "public"."contacts" add constraint "contacts_contact_method_required" CHECK ((((email IS NOT NULL) AND ((email)::text <> ''::text)) OR ((phone IS NOT NULL) AND ((phone)::text <> ''::text)) OR ((mobile_phone IS NOT NULL) AND ((mobile_phone)::text <> ''::text)))) not valid;

alter table "public"."contacts" validate constraint "contacts_contact_method_required";

alter table "public"."contacts" add constraint "contacts_contact_type_check" CHECK (((contact_type)::text = ANY ((ARRAY['customer'::character varying, 'lead'::character varying, 'prospect'::character varying, 'vendor'::character varying, 'partner'::character varying, 'contractor'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_contact_type_check";

alter table "public"."contacts" add constraint "contacts_currency_format" CHECK (((currency IS NULL) OR (length((currency)::text) = 3))) not valid;

alter table "public"."contacts" validate constraint "contacts_currency_format";

alter table "public"."contacts" add constraint "contacts_custom_fields_is_object" CHECK ((jsonb_typeof(custom_fields) = 'object'::text)) not valid;

alter table "public"."contacts" validate constraint "contacts_custom_fields_is_object";

alter table "public"."contacts" add constraint "contacts_email_format" CHECK (((email IS NULL) OR ((email)::text ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))) not valid;

alter table "public"."contacts" validate constraint "contacts_email_format";

alter table "public"."contacts" add constraint "contacts_estimated_value_positive" CHECK (((estimated_value IS NULL) OR (estimated_value >= (0)::numeric))) not valid;

alter table "public"."contacts" validate constraint "contacts_estimated_value_positive";

alter table "public"."contacts" add constraint "contacts_mobile_phone_format" CHECK (((mobile_phone IS NULL) OR (length(regexp_replace((mobile_phone)::text, '[^0-9]'::text, ''::text, 'g'::text)) >= 10))) not valid;

alter table "public"."contacts" validate constraint "contacts_mobile_phone_format";

alter table "public"."contacts" add constraint "contacts_name_required" CHECK ((((first_name IS NOT NULL) AND ((first_name)::text <> ''::text)) OR ((last_name IS NOT NULL) AND ((last_name)::text <> ''::text)) OR ((company_name IS NOT NULL) AND ((company_name)::text <> ''::text)))) not valid;

alter table "public"."contacts" validate constraint "contacts_name_required";

alter table "public"."contacts" add constraint "contacts_phone_format" CHECK (((phone IS NULL) OR (length(regexp_replace((phone)::text, '[^0-9]'::text, ''::text, 'g'::text)) >= 10))) not valid;

alter table "public"."contacts" validate constraint "contacts_phone_format";

alter table "public"."contacts" add constraint "contacts_priority_check" CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'urgent'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_priority_check";

alter table "public"."contacts" add constraint "contacts_source_check" CHECK (((source)::text = ANY ((ARRAY['website'::character varying, 'referral'::character varying, 'social_media'::character varying, 'advertising'::character varying, 'cold_outreach'::character varying, 'event'::character varying, 'partner'::character varying, 'existing_customer'::character varying, 'direct'::character varying, 'other'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_source_check";

alter table "public"."contacts" add constraint "contacts_status_check" CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'archived'::character varying, 'blocked'::character varying])::text[]))) not valid;

alter table "public"."contacts" validate constraint "contacts_status_check";

alter table "public"."contacts" add constraint "contacts_tags_is_array" CHECK ((jsonb_typeof(tags) = 'array'::text)) not valid;

alter table "public"."contacts" validate constraint "contacts_tags_is_array";

alter table "public"."contacts" add constraint "contacts_website_format" CHECK (((website IS NULL) OR ((website)::text ~ '^https?://'::text) OR ((website)::text ~ '\.'::text))) not valid;

alter table "public"."contacts" validate constraint "contacts_website_format";

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

set check_function_bodies = off;

create or replace view "public"."contact_summary" as  SELECT id,
    business_id,
    contact_type,
    status,
    priority,
    COALESCE(company_name, (concat(first_name, ' ', last_name))::character varying) AS display_name,
    COALESCE(email, phone, mobile_phone) AS primary_contact,
    estimated_value,
    assigned_to,
    created_date,
    last_contacted,
    ( SELECT count(*) AS count
           FROM contact_activities ca
          WHERE (ca.contact_id = c.id)) AS activity_count,
    ( SELECT count(*) AS count
           FROM contact_notes cn
          WHERE (cn.contact_id = c.id)) AS note_count
   FROM contacts c
  WHERE ((status)::text <> 'archived'::text);


CREATE OR REPLACE FUNCTION public.update_contact_last_contacted()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Update the contact's last_contacted timestamp when a new activity is added
    IF NEW.activity_type IN ('call', 'email', 'meeting') THEN
        UPDATE contacts 
        SET last_contacted = NEW.activity_date 
        WHERE id = NEW.contact_id 
        AND (last_contacted IS NULL OR last_contacted < NEW.activity_date);
    END IF;
    
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_last_modified_column()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$function$
;

grant delete on table "public"."contact_activities" to "anon";

grant insert on table "public"."contact_activities" to "anon";

grant references on table "public"."contact_activities" to "anon";

grant select on table "public"."contact_activities" to "anon";

grant trigger on table "public"."contact_activities" to "anon";

grant truncate on table "public"."contact_activities" to "anon";

grant update on table "public"."contact_activities" to "anon";

grant delete on table "public"."contact_activities" to "authenticated";

grant insert on table "public"."contact_activities" to "authenticated";

grant references on table "public"."contact_activities" to "authenticated";

grant select on table "public"."contact_activities" to "authenticated";

grant trigger on table "public"."contact_activities" to "authenticated";

grant truncate on table "public"."contact_activities" to "authenticated";

grant update on table "public"."contact_activities" to "authenticated";

grant delete on table "public"."contact_activities" to "service_role";

grant insert on table "public"."contact_activities" to "service_role";

grant references on table "public"."contact_activities" to "service_role";

grant select on table "public"."contact_activities" to "service_role";

grant trigger on table "public"."contact_activities" to "service_role";

grant truncate on table "public"."contact_activities" to "service_role";

grant update on table "public"."contact_activities" to "service_role";

grant delete on table "public"."contact_notes" to "anon";

grant insert on table "public"."contact_notes" to "anon";

grant references on table "public"."contact_notes" to "anon";

grant select on table "public"."contact_notes" to "anon";

grant trigger on table "public"."contact_notes" to "anon";

grant truncate on table "public"."contact_notes" to "anon";

grant update on table "public"."contact_notes" to "anon";

grant delete on table "public"."contact_notes" to "authenticated";

grant insert on table "public"."contact_notes" to "authenticated";

grant references on table "public"."contact_notes" to "authenticated";

grant select on table "public"."contact_notes" to "authenticated";

grant trigger on table "public"."contact_notes" to "authenticated";

grant truncate on table "public"."contact_notes" to "authenticated";

grant update on table "public"."contact_notes" to "authenticated";

grant delete on table "public"."contact_notes" to "service_role";

grant insert on table "public"."contact_notes" to "service_role";

grant references on table "public"."contact_notes" to "service_role";

grant select on table "public"."contact_notes" to "service_role";

grant trigger on table "public"."contact_notes" to "service_role";

grant truncate on table "public"."contact_notes" to "service_role";

grant update on table "public"."contact_notes" to "service_role";

grant delete on table "public"."contact_segment_memberships" to "anon";

grant insert on table "public"."contact_segment_memberships" to "anon";

grant references on table "public"."contact_segment_memberships" to "anon";

grant select on table "public"."contact_segment_memberships" to "anon";

grant trigger on table "public"."contact_segment_memberships" to "anon";

grant truncate on table "public"."contact_segment_memberships" to "anon";

grant update on table "public"."contact_segment_memberships" to "anon";

grant delete on table "public"."contact_segment_memberships" to "authenticated";

grant insert on table "public"."contact_segment_memberships" to "authenticated";

grant references on table "public"."contact_segment_memberships" to "authenticated";

grant select on table "public"."contact_segment_memberships" to "authenticated";

grant trigger on table "public"."contact_segment_memberships" to "authenticated";

grant truncate on table "public"."contact_segment_memberships" to "authenticated";

grant update on table "public"."contact_segment_memberships" to "authenticated";

grant delete on table "public"."contact_segment_memberships" to "service_role";

grant insert on table "public"."contact_segment_memberships" to "service_role";

grant references on table "public"."contact_segment_memberships" to "service_role";

grant select on table "public"."contact_segment_memberships" to "service_role";

grant trigger on table "public"."contact_segment_memberships" to "service_role";

grant truncate on table "public"."contact_segment_memberships" to "service_role";

grant update on table "public"."contact_segment_memberships" to "service_role";

grant delete on table "public"."contact_segments" to "anon";

grant insert on table "public"."contact_segments" to "anon";

grant references on table "public"."contact_segments" to "anon";

grant select on table "public"."contact_segments" to "anon";

grant trigger on table "public"."contact_segments" to "anon";

grant truncate on table "public"."contact_segments" to "anon";

grant update on table "public"."contact_segments" to "anon";

grant delete on table "public"."contact_segments" to "authenticated";

grant insert on table "public"."contact_segments" to "authenticated";

grant references on table "public"."contact_segments" to "authenticated";

grant select on table "public"."contact_segments" to "authenticated";

grant trigger on table "public"."contact_segments" to "authenticated";

grant truncate on table "public"."contact_segments" to "authenticated";

grant update on table "public"."contact_segments" to "authenticated";

grant delete on table "public"."contact_segments" to "service_role";

grant insert on table "public"."contact_segments" to "service_role";

grant references on table "public"."contact_segments" to "service_role";

grant select on table "public"."contact_segments" to "service_role";

grant trigger on table "public"."contact_segments" to "service_role";

grant truncate on table "public"."contact_segments" to "service_role";

grant update on table "public"."contact_segments" to "service_role";

grant delete on table "public"."contacts" to "anon";

grant insert on table "public"."contacts" to "anon";

grant references on table "public"."contacts" to "anon";

grant select on table "public"."contacts" to "anon";

grant trigger on table "public"."contacts" to "anon";

grant truncate on table "public"."contacts" to "anon";

grant update on table "public"."contacts" to "anon";

grant delete on table "public"."contacts" to "authenticated";

grant insert on table "public"."contacts" to "authenticated";

grant references on table "public"."contacts" to "authenticated";

grant select on table "public"."contacts" to "authenticated";

grant trigger on table "public"."contacts" to "authenticated";

grant truncate on table "public"."contacts" to "authenticated";

grant update on table "public"."contacts" to "authenticated";

grant delete on table "public"."contacts" to "service_role";

grant insert on table "public"."contacts" to "service_role";

grant references on table "public"."contacts" to "service_role";

grant select on table "public"."contacts" to "service_role";

grant trigger on table "public"."contacts" to "service_role";

grant truncate on table "public"."contacts" to "service_role";

grant update on table "public"."contacts" to "service_role";

CREATE TRIGGER update_contact_activities_last_modified BEFORE UPDATE ON public.contact_activities FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

CREATE TRIGGER update_contact_last_contacted_trigger AFTER INSERT ON public.contact_activities FOR EACH ROW EXECUTE FUNCTION update_contact_last_contacted();

CREATE TRIGGER update_contact_notes_last_modified BEFORE UPDATE ON public.contact_notes FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

CREATE TRIGGER update_contact_segments_last_modified BEFORE UPDATE ON public.contact_segments FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();

CREATE TRIGGER update_contacts_last_modified BEFORE UPDATE ON public.contacts FOR EACH ROW EXECUTE FUNCTION update_last_modified_column();


