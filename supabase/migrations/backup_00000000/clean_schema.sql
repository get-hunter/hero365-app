

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE TYPE "public"."activity_priority" AS ENUM (
    'low',
    'medium',
    'high',
    'urgent'
);


ALTER TYPE "public"."activity_priority" OWNER TO "postgres";


CREATE TYPE "public"."activity_status" AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'cancelled',
    'overdue'
);


ALTER TYPE "public"."activity_status" OWNER TO "postgres";


CREATE TYPE "public"."activity_type" AS ENUM (
    'interaction',
    'status_change',
    'task',
    'reminder',
    'note',
    'system_event',
    'service_event',
    'financial_event',
    'document_event'
);


ALTER TYPE "public"."activity_type" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."add_contact_interaction_to_history"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."add_contact_interaction_to_history"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."assign_default_permissions"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    -- If permissions array is empty or null, assign default permissions based on role
    IF NEW.permissions IS NULL OR jsonb_array_length(NEW.permissions) = 0 THEN
        NEW.permissions = get_default_permissions_for_role(NEW.role);
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."assign_default_permissions"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."cleanup_expired_invitations"("days_old" integer DEFAULT 30) RETURNS integer
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM business_invitations 
    WHERE status IN ('expired', 'declined', 'cancelled')
    AND invitation_date < now() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;


ALTER FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."cleanup_old_activities"() RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."cleanup_old_activities"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_default_permissions_for_role"("role_name" "text") RETURNS "jsonb"
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
BEGIN
    CASE role_name
        WHEN 'owner' THEN
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "delete_contacts", "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_projects", "create_projects", "edit_projects", "delete_projects", "edit_business_profile", "view_business_settings", "edit_business_settings", "invite_team_members", "edit_team_members", "remove_team_members", "view_invoices", "create_invoices", "edit_invoices", "delete_invoices", "view_estimates", "create_estimates", "edit_estimates", "delete_estimates", "view_reports", "edit_reports", "view_accounting", "edit_accounting"]'::jsonb;
        WHEN 'admin' THEN  
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "delete_contacts", "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_projects", "create_projects", "edit_projects", "delete_projects", "view_business_settings", "invite_team_members", "edit_team_members", "view_invoices", "create_invoices", "edit_invoices", "delete_invoices", "view_estimates", "create_estimates", "edit_estimates", "delete_estimates", "view_reports", "edit_reports", "view_accounting", "edit_accounting"]'::jsonb;
        WHEN 'manager' THEN
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs", "view_projects", "create_projects", "edit_projects", "view_invoices", "create_invoices", "edit_invoices", "view_estimates", "create_estimates", "edit_estimates", "invite_team_members", "view_reports"]'::jsonb;
        WHEN 'employee' THEN
            RETURN '["view_contacts", "create_contacts", "edit_contacts", "view_jobs", "create_jobs", "edit_jobs", "view_projects", "create_projects", "edit_projects", "view_invoices", "view_estimates"]'::jsonb;
        WHEN 'contractor' THEN
            RETURN '["view_contacts", "view_jobs", "view_projects"]'::jsonb;
        WHEN 'viewer' THEN
            RETURN '["view_contacts", "view_jobs", "view_projects"]'::jsonb;
        ELSE
            RETURN '["view_contacts"]'::jsonb; -- Fallback to minimum permissions
    END CASE;
END;
$$;


ALTER FUNCTION "public"."get_default_permissions_for_role"("role_name" "text") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_job_statistics"("p_business_id" "uuid") RETURNS "jsonb"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."get_job_statistics"("p_business_id" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."get_next_job_number"("p_business_id" "uuid", "p_prefix" "text" DEFAULT 'JOB'::"text") RETURNS "text"
    LANGUAGE "plpgsql"
    AS $_$
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
$_$;


ALTER FUNCTION "public"."get_next_job_number"("p_business_id" "uuid", "p_prefix" "text") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."log_job_activity"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."log_job_activity"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."mark_expired_invitations"() RETURNS integer
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE business_invitations 
    SET status = 'expired'
    WHERE status = 'pending' 
    AND expiry_date < now();
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$;


ALTER FUNCTION "public"."mark_expired_invitations"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_activity_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_activity_modified"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_businesses_last_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_businesses_last_modified"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_contact_last_contacted"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."update_contact_last_contacted"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_contact_status_history"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."update_contact_status_history"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_departments_last_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_departments_last_modified"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_job_last_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_job_last_modified"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_last_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_last_modified"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_last_modified_column"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_last_modified_column"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_overdue_activities"() RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
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
$$;


ALTER FUNCTION "public"."update_overdue_activities"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_users_updated_at"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_users_updated_at"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."user_has_permission"("user_permissions" "jsonb", "required_permission" "text") RETURNS boolean
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
BEGIN
    -- If user has "*" permission (owner), they have all permissions
    IF user_permissions ? '*' THEN
        RETURN true;
    END IF;
    
    -- Otherwise check for specific permission
    RETURN user_permissions ? required_permission;
END;
$$;


ALTER FUNCTION "public"."user_has_permission"("user_permissions" "jsonb", "required_permission" "text") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."validate_assigned_to_users"("user_ids" "uuid"[]) RETURNS boolean
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    -- Check if all user IDs in the array exist in auth.users
    RETURN NOT EXISTS (
        SELECT 1 
        FROM unnest(user_ids) AS uid
        WHERE uid IS NOT NULL 
        AND NOT EXISTS (SELECT 1 FROM auth.users WHERE id = uid)
    );
END;
$$;


ALTER FUNCTION "public"."validate_assigned_to_users"("user_ids" "uuid"[]) OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."activities" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "contact_id" "uuid" NOT NULL,
    "template_id" "uuid",
    "parent_activity_id" "uuid",
    "activity_type" "public"."activity_type" NOT NULL,
    "title" character varying(500) NOT NULL,
    "description" "text",
    "status" "public"."activity_status" DEFAULT 'pending'::"public"."activity_status",
    "priority" "public"."activity_priority" DEFAULT 'medium'::"public"."activity_priority",
    "scheduled_date" timestamp with time zone,
    "due_date" timestamp with time zone,
    "completed_date" timestamp with time zone,
    "duration_minutes" integer,
    "location" character varying(500),
    "created_by" character varying(100) NOT NULL,
    "assigned_to" character varying(100),
    "tags" "text"[] DEFAULT '{}'::"text"[],
    "metadata" "jsonb" DEFAULT '{}'::"jsonb",
    "created_date" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "last_modified" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "check_completed_when_status_completed" CHECK (((("status" = 'completed'::"public"."activity_status") AND ("completed_date" IS NOT NULL)) OR (("status" <> 'completed'::"public"."activity_status") AND ("completed_date" IS NULL)))),
    CONSTRAINT "check_due_after_scheduled" CHECK ((("due_date" IS NULL) OR ("scheduled_date" IS NULL) OR ("due_date" >= "scheduled_date")))
);


ALTER TABLE "public"."activities" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."activity_participants" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "activity_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "name" character varying(200) NOT NULL,
    "role" character varying(50) DEFAULT 'participant'::character varying,
    "is_primary" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE "public"."activity_participants" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."activity_reminders" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "activity_id" "uuid" NOT NULL,
    "reminder_time" timestamp with time zone NOT NULL,
    "reminder_type" character varying(50) DEFAULT 'notification'::character varying,
    "message" "text",
    "is_sent" boolean DEFAULT false,
    "sent_at" timestamp with time zone,
    "created_date" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE "public"."activity_reminders" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."activity_templates" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "name" character varying(200) NOT NULL,
    "description" "text",
    "activity_type" "public"."activity_type" NOT NULL,
    "default_duration" integer,
    "default_reminders" "jsonb" DEFAULT '[]'::"jsonb",
    "default_participants" "text"[] DEFAULT '{}'::"text"[],
    "custom_fields" "jsonb" DEFAULT '{}'::"jsonb",
    "is_active" boolean DEFAULT true,
    "created_by" character varying(100) NOT NULL,
    "created_date" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "last_modified" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE "public"."activity_templates" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."contacts" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "contact_type" character varying(20) NOT NULL,
    "status" character varying(20) DEFAULT 'active'::character varying,
    "first_name" character varying(100),
    "last_name" character varying(100),
    "company_name" character varying(200),
    "job_title" character varying(100),
    "email" character varying(320),
    "phone" character varying(20),
    "mobile_phone" character varying(20),
    "website" character varying(200),
    "address" "jsonb",
    "priority" character varying(10) DEFAULT 'medium'::character varying,
    "source" character varying(20),
    "tags" "jsonb" DEFAULT '[]'::"jsonb",
    "notes" "text",
    "estimated_value" numeric(15,2),
    "currency" character varying(3) DEFAULT 'USD'::character varying,
    "assigned_to" "uuid",
    "created_by" "uuid",
    "custom_fields" "jsonb" DEFAULT '{}'::"jsonb",
    "created_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_modified" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_contacted" timestamp with time zone,
    "display_name" character varying(200) GENERATED ALWAYS AS (
CASE
    WHEN (("company_name" IS NOT NULL) AND (("company_name")::"text" <> ''::"text")) THEN
    CASE
        WHEN (("first_name" IS NOT NULL) AND ("last_name" IS NOT NULL)) THEN ((((((("first_name")::"text" || ' '::"text") || ("last_name")::"text") || ' ('::"text") || ("company_name")::"text") || ')'::"text"))::character varying
        WHEN ("first_name" IS NOT NULL) THEN ((((("first_name")::"text" || ' ('::"text") || ("company_name")::"text") || ')'::"text"))::character varying
        WHEN ("last_name" IS NOT NULL) THEN ((((("last_name")::"text" || ' ('::"text") || ("company_name")::"text") || ')'::"text"))::character varying
        ELSE "company_name"
    END
    WHEN (("first_name" IS NOT NULL) AND ("last_name" IS NOT NULL)) THEN (((("first_name")::"text" || ' '::"text") || ("last_name")::"text"))::character varying
    WHEN ("first_name" IS NOT NULL) THEN "first_name"
    WHEN ("last_name" IS NOT NULL) THEN "last_name"
    ELSE 'Unknown Contact'::character varying
END) STORED,
    "interaction_history" "jsonb" DEFAULT '[]'::"jsonb",
    "lifecycle_stage" character varying(20) DEFAULT 'awareness'::character varying,
    "relationship_status" character varying(20) DEFAULT 'prospect'::character varying,
    "status_history" "jsonb" DEFAULT '[]'::"jsonb",
    CONSTRAINT "contacts_contact_method_required" CHECK (((("email" IS NOT NULL) AND (("email")::"text" <> ''::"text")) OR (("phone" IS NOT NULL) AND (("phone")::"text" <> ''::"text")) OR (("mobile_phone" IS NOT NULL) AND (("mobile_phone")::"text" <> ''::"text")))),
    CONSTRAINT "contacts_contact_type_check" CHECK ((("contact_type")::"text" = ANY (ARRAY[('customer'::character varying)::"text", ('lead'::character varying)::"text", ('prospect'::character varying)::"text", ('vendor'::character varying)::"text", ('partner'::character varying)::"text", ('contractor'::character varying)::"text"]))),
    CONSTRAINT "contacts_currency_format" CHECK ((("currency" IS NULL) OR ("length"(("currency")::"text") = 3))),
    CONSTRAINT "contacts_custom_fields_is_object" CHECK (("jsonb_typeof"("custom_fields") = 'object'::"text")),
    CONSTRAINT "contacts_email_format" CHECK ((("email" IS NULL) OR (("email")::"text" ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::"text"))),
    CONSTRAINT "contacts_estimated_value_positive" CHECK ((("estimated_value" IS NULL) OR ("estimated_value" >= (0)::numeric))),
    CONSTRAINT "contacts_lifecycle_stage_check" CHECK ((("lifecycle_stage")::"text" = ANY (ARRAY[('awareness'::character varying)::"text", ('interest'::character varying)::"text", ('consideration'::character varying)::"text", ('decision'::character varying)::"text", ('retention'::character varying)::"text", ('customer'::character varying)::"text"]))),
    CONSTRAINT "contacts_mobile_phone_format" CHECK ((("mobile_phone" IS NULL) OR ("length"("regexp_replace"(("mobile_phone")::"text", '[^0-9]'::"text", ''::"text", 'g'::"text")) >= 10))),
    CONSTRAINT "contacts_name_required" CHECK (((("first_name" IS NOT NULL) AND (("first_name")::"text" <> ''::"text")) OR (("last_name" IS NOT NULL) AND (("last_name")::"text" <> ''::"text")) OR (("company_name" IS NOT NULL) AND (("company_name")::"text" <> ''::"text")))),
    CONSTRAINT "contacts_phone_format" CHECK ((("phone" IS NULL) OR ("length"("regexp_replace"(("phone")::"text", '[^0-9]'::"text", ''::"text", 'g'::"text")) >= 10))),
    CONSTRAINT "contacts_priority_check" CHECK ((("priority")::"text" = ANY (ARRAY[('low'::character varying)::"text", ('medium'::character varying)::"text", ('high'::character varying)::"text", ('urgent'::character varying)::"text"]))),
    CONSTRAINT "contacts_relationship_status_check" CHECK ((("relationship_status")::"text" = ANY (ARRAY[('prospect'::character varying)::"text", ('qualified_lead'::character varying)::"text", ('opportunity'::character varying)::"text", ('active_client'::character varying)::"text", ('past_client'::character varying)::"text", ('lost_lead'::character varying)::"text", ('inactive'::character varying)::"text"]))),
    CONSTRAINT "contacts_source_check" CHECK ((("source")::"text" = ANY (ARRAY[('website'::character varying)::"text", ('google_ads'::character varying)::"text", ('social_media'::character varying)::"text", ('referral'::character varying)::"text", ('phone_call'::character varying)::"text", ('walk_in'::character varying)::"text", ('email_marketing'::character varying)::"text", ('trade_show'::character varying)::"text", ('direct_mail'::character varying)::"text", ('yellow_pages'::character varying)::"text", ('partner'::character varying)::"text", ('existing_customer'::character varying)::"text", ('cold_outreach'::character varying)::"text", ('event'::character varying)::"text", ('direct'::character varying)::"text", ('other'::character varying)::"text"]))),
    CONSTRAINT "contacts_status_check" CHECK ((("status")::"text" = ANY (ARRAY[('active'::character varying)::"text", ('inactive'::character varying)::"text", ('archived'::character varying)::"text", ('blocked'::character varying)::"text"]))),
    CONSTRAINT "contacts_tags_is_array" CHECK (("jsonb_typeof"("tags") = 'array'::"text")),
    CONSTRAINT "contacts_website_format" CHECK ((("website" IS NULL) OR (("website")::"text" ~ '^https?://'::"text") OR (("website")::"text" ~ '\.'::"text")))
);


ALTER TABLE "public"."contacts" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."activity_timeline_view" AS
 SELECT "a"."id",
    "a"."business_id",
    "a"."contact_id",
    "c"."display_name" AS "contact_name",
    "c"."email" AS "contact_email",
    "c"."phone" AS "contact_phone",
    "a"."activity_type",
    "a"."title",
    "a"."description",
    "a"."status",
    "a"."priority",
    "a"."scheduled_date",
    "a"."due_date",
    "a"."completed_date",
    "a"."duration_minutes",
    "a"."location",
    "a"."created_by",
    "a"."assigned_to",
    "a"."tags",
    "a"."metadata",
    "a"."created_date",
    "a"."last_modified",
        CASE
            WHEN (("a"."status" = ANY (ARRAY['pending'::"public"."activity_status", 'in_progress'::"public"."activity_status"])) AND ((("a"."due_date" IS NOT NULL) AND ("a"."due_date" < "now"())) OR (("a"."due_date" IS NULL) AND ("a"."scheduled_date" IS NOT NULL) AND ("a"."scheduled_date" < ("now"() - '1 day'::interval))))) THEN true
            ELSE false
        END AS "is_overdue",
        CASE
            WHEN (("a"."scheduled_date" IS NOT NULL) AND ("a"."scheduled_date" > "now"()) AND ("a"."scheduled_date" <= ("now"() + '7 days'::interval))) THEN true
            ELSE false
        END AS "is_upcoming"
   FROM ("public"."activities" "a"
     JOIN "public"."contacts" "c" ON (("a"."contact_id" = "c"."id")));


ALTER VIEW "public"."activity_timeline_view" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."availability_windows" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_capabilities_id" "uuid" NOT NULL,
    "day_of_week" integer NOT NULL,
    "start_time" time without time zone NOT NULL,
    "end_time" time without time zone NOT NULL,
    "availability_type" character varying(20) DEFAULT 'regular'::character varying,
    "max_hours_per_day" numeric(4,2),
    "break_duration_minutes" integer DEFAULT 30,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "availability_windows_availability_type_check" CHECK ((("availability_type")::"text" = ANY (ARRAY[('regular'::character varying)::"text", ('flexible'::character varying)::"text", ('on_call'::character varying)::"text", ('project_based'::character varying)::"text"]))),
    CONSTRAINT "availability_windows_break_duration_minutes_check" CHECK ((("break_duration_minutes" >= 0) AND ("break_duration_minutes" <= 120))),
    CONSTRAINT "availability_windows_check" CHECK (("end_time" > "start_time")),
    CONSTRAINT "availability_windows_day_of_week_check" CHECK ((("day_of_week" >= 0) AND ("day_of_week" <= 6))),
    CONSTRAINT "availability_windows_max_hours_per_day_check" CHECK (("max_hours_per_day" > (0)::numeric))
);


ALTER TABLE "public"."availability_windows" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."business_invitations" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "business_name" character varying(255) NOT NULL,
    "invited_email" character varying(320),
    "invited_phone" character varying(20),
    "invited_by" "uuid" NOT NULL,
    "invited_by_name" character varying(255) NOT NULL,
    "role" character varying(50) NOT NULL,
    "permissions" "jsonb" DEFAULT '[]'::"jsonb" NOT NULL,
    "invitation_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "expiry_date" timestamp with time zone NOT NULL,
    "status" character varying(20) DEFAULT 'pending'::character varying,
    "message" "text",
    "accepted_date" timestamp with time zone,
    "declined_date" timestamp with time zone,
    CONSTRAINT "business_invitations_accepted_date_check" CHECK ((((("status")::"text" = 'accepted'::"text") AND ("accepted_date" IS NOT NULL)) OR ((("status")::"text" <> 'accepted'::"text") AND ("accepted_date" IS NULL)))),
    CONSTRAINT "business_invitations_contact_required" CHECK (((("invited_email" IS NOT NULL) AND (("invited_email")::"text" <> ''::"text")) OR (("invited_phone" IS NOT NULL) AND (("invited_phone")::"text" <> ''::"text")))),
    CONSTRAINT "business_invitations_declined_date_check" CHECK ((((("status")::"text" = 'declined'::"text") AND ("declined_date" IS NOT NULL)) OR ((("status")::"text" <> 'declined'::"text") AND ("declined_date" IS NULL)))),
    CONSTRAINT "business_invitations_email_format" CHECK ((("invited_email" IS NULL) OR (("invited_email")::"text" ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::"text"))),
    CONSTRAINT "business_invitations_expiry_future" CHECK (("expiry_date" > "invitation_date")),
    CONSTRAINT "business_invitations_permissions_not_empty" CHECK (("jsonb_array_length"("permissions") > 0)),
    CONSTRAINT "business_invitations_phone_format" CHECK ((("invited_phone" IS NULL) OR ("length"("regexp_replace"(("invited_phone")::"text", '[^0-9]'::"text", ''::"text", 'g'::"text")) >= 10))),
    CONSTRAINT "business_invitations_role_check" CHECK ((("role")::"text" = ANY (ARRAY[('owner'::character varying)::"text", ('admin'::character varying)::"text", ('manager'::character varying)::"text", ('employee'::character varying)::"text", ('contractor'::character varying)::"text", ('viewer'::character varying)::"text"]))),
    CONSTRAINT "business_invitations_status_check" CHECK ((("status")::"text" = ANY (ARRAY[('pending'::character varying)::"text", ('accepted'::character varying)::"text", ('declined'::character varying)::"text", ('expired'::character varying)::"text", ('cancelled'::character varying)::"text"])))
);


ALTER TABLE "public"."business_invitations" OWNER TO "postgres";


COMMENT ON TABLE "public"."business_invitations" IS 'Invitations for users to join business teams';



COMMENT ON COLUMN "public"."business_invitations"."permissions" IS 'Array of permission strings for the invited role';



CREATE TABLE IF NOT EXISTS "public"."business_memberships" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "role" character varying(50) NOT NULL,
    "permissions" "jsonb" DEFAULT '[]'::"jsonb" NOT NULL,
    "joined_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "invited_date" timestamp with time zone,
    "invited_by" "uuid",
    "is_active" boolean DEFAULT true,
    "department_id" "uuid",
    "job_title" character varying(100),
    CONSTRAINT "business_memberships_permissions_not_empty" CHECK (("jsonb_array_length"("permissions") > 0)),
    CONSTRAINT "business_memberships_role_check" CHECK ((("role")::"text" = ANY (ARRAY[('owner'::character varying)::"text", ('admin'::character varying)::"text", ('manager'::character varying)::"text", ('employee'::character varying)::"text", ('contractor'::character varying)::"text", ('viewer'::character varying)::"text"])))
);


ALTER TABLE "public"."business_memberships" OWNER TO "postgres";


COMMENT ON TABLE "public"."business_memberships" IS 'User memberships in businesses with roles and permissions';



COMMENT ON COLUMN "public"."business_memberships"."permissions" IS 'Array of permission strings for this membership';



CREATE OR REPLACE VIEW "public"."business_membership_permissions" AS
 SELECT "id",
    "business_id",
    "user_id",
    "role",
    "permissions",
    "is_active",
    "joined_date",
    "invited_by",
        CASE
            WHEN ("permissions" @> '["view_contacts"]'::"jsonb") THEN true
            ELSE false
        END AS "can_view_contacts",
        CASE
            WHEN ("permissions" @> '["create_contacts"]'::"jsonb") THEN true
            ELSE false
        END AS "can_create_contacts",
        CASE
            WHEN ("permissions" @> '["edit_contacts"]'::"jsonb") THEN true
            ELSE false
        END AS "can_edit_contacts",
        CASE
            WHEN ("permissions" @> '["delete_contacts"]'::"jsonb") THEN true
            ELSE false
        END AS "can_delete_contacts",
        CASE
            WHEN ("permissions" @> '["view_jobs"]'::"jsonb") THEN true
            ELSE false
        END AS "can_view_jobs",
        CASE
            WHEN ("permissions" @> '["create_jobs"]'::"jsonb") THEN true
            ELSE false
        END AS "can_create_jobs",
        CASE
            WHEN ("permissions" @> '["edit_jobs"]'::"jsonb") THEN true
            ELSE false
        END AS "can_edit_jobs",
        CASE
            WHEN ("permissions" @> '["delete_jobs"]'::"jsonb") THEN true
            ELSE false
        END AS "can_delete_jobs",
        CASE
            WHEN ("permissions" @> '["invite_team_members"]'::"jsonb") THEN true
            ELSE false
        END AS "can_invite_team_members",
        CASE
            WHEN ("permissions" @> '["edit_team_members"]'::"jsonb") THEN true
            ELSE false
        END AS "can_edit_team_members",
        CASE
            WHEN ("permissions" @> '["remove_team_members"]'::"jsonb") THEN true
            ELSE false
        END AS "can_remove_team_members",
        CASE
            WHEN ("permissions" @> '["view_business_settings"]'::"jsonb") THEN true
            ELSE false
        END AS "can_view_business_settings",
        CASE
            WHEN ("permissions" @> '["edit_business_settings"]'::"jsonb") THEN true
            ELSE false
        END AS "can_edit_business_settings"
   FROM "public"."business_memberships" "bm"
  WHERE ("is_active" = true);


ALTER VIEW "public"."business_membership_permissions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."businesses" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "name" character varying(255) NOT NULL,
    "industry" character varying(255) NOT NULL,
    "custom_industry" character varying(255),
    "company_size" character varying(50) NOT NULL,
    "owner_id" "uuid" NOT NULL,
    "description" "text",
    "phone_number" character varying(20),
    "business_address" "text",
    "website" character varying(500),
    "logo_url" character varying(500),
    "business_email" character varying(320),
    "business_registration_number" character varying(100),
    "tax_id" character varying(100),
    "business_license" character varying(100),
    "insurance_number" character varying(100),
    "selected_features" "jsonb" DEFAULT '[]'::"jsonb",
    "primary_goals" "jsonb" DEFAULT '[]'::"jsonb",
    "referral_source" character varying(50),
    "onboarding_completed" boolean DEFAULT false,
    "onboarding_completed_date" timestamp with time zone,
    "timezone" character varying(100),
    "currency" character varying(3) DEFAULT 'USD'::character varying,
    "business_hours" "jsonb",
    "is_active" boolean DEFAULT true,
    "max_team_members" integer,
    "subscription_tier" character varying(50),
    "enabled_features" "jsonb" DEFAULT '[]'::"jsonb",
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "businesses_company_size_check" CHECK ((("company_size")::"text" = ANY (ARRAY[('just_me'::character varying)::"text", ('small'::character varying)::"text", ('medium'::character varying)::"text", ('large'::character varying)::"text", ('enterprise'::character varying)::"text"]))),
    CONSTRAINT "businesses_email_format" CHECK ((("business_email" IS NULL) OR (("business_email")::"text" ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::"text"))),
    CONSTRAINT "businesses_referral_source_check" CHECK ((("referral_source")::"text" = ANY (ARRAY[('tiktok'::character varying)::"text", ('tv'::character varying)::"text", ('online_ad'::character varying)::"text", ('web_search'::character varying)::"text", ('podcast_radio'::character varying)::"text", ('reddit'::character varying)::"text", ('review_sites'::character varying)::"text", ('youtube'::character varying)::"text", ('facebook_instagram'::character varying)::"text", ('referral'::character varying)::"text", ('other'::character varying)::"text"]))),
    CONSTRAINT "businesses_website_format" CHECK ((("website" IS NULL) OR (("website")::"text" ~ '^https?://'::"text")))
);


ALTER TABLE "public"."businesses" OWNER TO "postgres";


COMMENT ON TABLE "public"."businesses" IS 'Core business entities with profile, settings, and subscription information';



COMMENT ON COLUMN "public"."businesses"."selected_features" IS 'Array of feature names selected during onboarding';



COMMENT ON COLUMN "public"."businesses"."primary_goals" IS 'Array of primary business goals';



COMMENT ON COLUMN "public"."businesses"."enabled_features" IS 'Array of currently enabled feature names';



CREATE TABLE IF NOT EXISTS "public"."calendar_events" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "title" character varying(200) NOT NULL,
    "description" "text",
    "event_type" character varying(50) DEFAULT 'work_schedule'::character varying,
    "start_datetime" timestamp with time zone NOT NULL,
    "end_datetime" timestamp with time zone NOT NULL,
    "is_all_day" boolean DEFAULT false,
    "timezone" character varying(100) DEFAULT 'UTC'::character varying,
    "recurrence_type" character varying(20) DEFAULT 'none'::character varying,
    "recurrence_end_date" "date",
    "recurrence_count" integer,
    "recurrence_interval" integer DEFAULT 1,
    "recurrence_days_of_week" integer[] DEFAULT '{}'::integer[],
    "blocks_scheduling" boolean DEFAULT true,
    "allows_emergency_override" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    "is_active" boolean DEFAULT true,
    CONSTRAINT "calendar_events_end_after_start" CHECK (("end_datetime" > "start_datetime")),
    CONSTRAINT "calendar_events_event_type_check" CHECK ((("event_type")::"text" = ANY (ARRAY[('work_schedule'::character varying)::"text", ('time_off'::character varying)::"text", ('break'::character varying)::"text", ('meeting'::character varying)::"text", ('training'::character varying)::"text", ('personal'::character varying)::"text"]))),
    CONSTRAINT "calendar_events_recurrence_count_check" CHECK (("recurrence_count" > 0)),
    CONSTRAINT "calendar_events_recurrence_days_valid" CHECK ((("array_length"("recurrence_days_of_week", 1) IS NULL) OR ("recurrence_days_of_week" <@ ARRAY[0, 1, 2, 3, 4, 5, 6]))),
    CONSTRAINT "calendar_events_recurrence_interval_check" CHECK (("recurrence_interval" > 0)),
    CONSTRAINT "calendar_events_recurrence_type_check" CHECK ((("recurrence_type")::"text" = ANY (ARRAY[('none'::character varying)::"text", ('daily'::character varying)::"text", ('weekly'::character varying)::"text", ('biweekly'::character varying)::"text", ('monthly'::character varying)::"text", ('custom'::character varying)::"text"])))
);


ALTER TABLE "public"."calendar_events" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."calendar_preferences" (
    "user_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "timezone" character varying(100) DEFAULT 'UTC'::character varying,
    "date_format" character varying(20) DEFAULT 'YYYY-MM-DD'::character varying,
    "time_format" character varying(5) DEFAULT '24h'::character varying,
    "week_start_day" integer DEFAULT 0,
    "preferred_working_hours_template_id" "uuid",
    "min_time_between_jobs_minutes" integer DEFAULT 30,
    "max_commute_time_minutes" integer DEFAULT 60,
    "allows_back_to_back_jobs" boolean DEFAULT false,
    "requires_prep_time_minutes" integer DEFAULT 15,
    "job_reminder_minutes_before" integer[] DEFAULT '{60,15}'::integer[],
    "schedule_change_notifications" boolean DEFAULT true,
    "new_job_notifications" boolean DEFAULT true,
    "cancellation_notifications" boolean DEFAULT true,
    "auto_accept_jobs_in_hours" boolean DEFAULT false,
    "auto_decline_outside_hours" boolean DEFAULT true,
    "emergency_availability_outside_hours" boolean DEFAULT false,
    "weekend_availability" boolean DEFAULT false,
    "holiday_availability" boolean DEFAULT false,
    "travel_buffer_percentage" numeric(3,2) DEFAULT 1.20,
    "job_buffer_minutes" integer DEFAULT 15,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "calendar_preferences_job_buffer_minutes_check" CHECK (("job_buffer_minutes" >= 0)),
    CONSTRAINT "calendar_preferences_max_commute_time_minutes_check" CHECK (("max_commute_time_minutes" >= 0)),
    CONSTRAINT "calendar_preferences_min_time_between_jobs_minutes_check" CHECK (("min_time_between_jobs_minutes" >= 0)),
    CONSTRAINT "calendar_preferences_requires_prep_time_minutes_check" CHECK (("requires_prep_time_minutes" >= 0)),
    CONSTRAINT "calendar_preferences_time_format_check" CHECK ((("time_format")::"text" = ANY (ARRAY[('12h'::character varying)::"text", ('24h'::character varying)::"text"]))),
    CONSTRAINT "calendar_preferences_travel_buffer_percentage_check" CHECK (("travel_buffer_percentage" >= 1.0)),
    CONSTRAINT "calendar_preferences_week_start_day_check" CHECK ((("week_start_day" >= 0) AND ("week_start_day" <= 6)))
);


ALTER TABLE "public"."calendar_preferences" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."contact_activities" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "contact_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "activity_type" character varying(50) NOT NULL,
    "subject" character varying(200),
    "description" "text",
    "activity_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "duration_minutes" integer,
    "outcome" character varying(50),
    "performed_by" "uuid" NOT NULL,
    "related_job_id" "uuid",
    "related_project_id" "uuid",
    "related_invoice_id" "uuid",
    "created_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_modified" timestamp with time zone DEFAULT "now"() NOT NULL,
    "activity_data" "jsonb" DEFAULT '{}'::"jsonb",
    CONSTRAINT "contact_activities_activity_type_check" CHECK ((("activity_type")::"text" = ANY (ARRAY[('call'::character varying)::"text", ('email'::character varying)::"text", ('meeting'::character varying)::"text", ('note'::character varying)::"text", ('task'::character varying)::"text", ('quote'::character varying)::"text", ('invoice'::character varying)::"text", ('payment'::character varying)::"text", ('other'::character varying)::"text"]))),
    CONSTRAINT "contact_activities_data_is_object" CHECK (("jsonb_typeof"("activity_data") = 'object'::"text")),
    CONSTRAINT "contact_activities_duration_positive" CHECK ((("duration_minutes" IS NULL) OR ("duration_minutes" >= 0))),
    CONSTRAINT "contact_activities_outcome_check" CHECK ((("outcome")::"text" = ANY (ARRAY[('successful'::character varying)::"text", ('no_answer'::character varying)::"text", ('busy'::character varying)::"text", ('scheduled'::character varying)::"text", ('completed'::character varying)::"text", ('cancelled'::character varying)::"text"])))
);


ALTER TABLE "public"."contact_activities" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."contact_notes" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "contact_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "title" character varying(200),
    "content" "text" NOT NULL,
    "note_type" character varying(20) DEFAULT 'general'::character varying,
    "is_private" boolean DEFAULT false,
    "created_by" "uuid" NOT NULL,
    "created_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_modified" timestamp with time zone DEFAULT "now"() NOT NULL,
    "tags" "jsonb" DEFAULT '[]'::"jsonb",
    CONSTRAINT "contact_notes_note_type_check" CHECK ((("note_type")::"text" = ANY (ARRAY[('general'::character varying)::"text", ('meeting'::character varying)::"text", ('call'::character varying)::"text", ('email'::character varying)::"text", ('task'::character varying)::"text", ('reminder'::character varying)::"text"]))),
    CONSTRAINT "contact_notes_tags_is_array" CHECK (("jsonb_typeof"("tags") = 'array'::"text"))
);


ALTER TABLE "public"."contact_notes" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."contact_enhanced_summary" AS
 SELECT "id",
    "business_id",
    "contact_type",
    "status",
    "first_name",
    "last_name",
    "company_name",
    "job_title",
    "email",
    "phone",
    "mobile_phone",
    "website",
    "address",
    "priority",
    "source",
    "tags",
    "notes",
    "estimated_value",
    "currency",
    "assigned_to",
    "created_by",
    "custom_fields",
    "created_date",
    "last_modified",
    "last_contacted",
    "display_name",
    "interaction_history",
    "lifecycle_stage",
    "relationship_status",
    "status_history",
        CASE
            WHEN (("relationship_status")::"text" = 'active_client'::"text") THEN 'Active Client'::"text"
            WHEN (("relationship_status")::"text" = 'qualified_lead'::"text") THEN 'Qualified Lead'::"text"
            WHEN (("relationship_status")::"text" = 'opportunity'::"text") THEN 'Opportunity'::"text"
            WHEN (("relationship_status")::"text" = 'prospect'::"text") THEN 'Prospect'::"text"
            WHEN (("relationship_status")::"text" = 'past_client'::"text") THEN 'Past Client'::"text"
            WHEN (("relationship_status")::"text" = 'lost_lead'::"text") THEN 'Lost Lead'::"text"
            WHEN (("relationship_status")::"text" = 'inactive'::"text") THEN 'Inactive'::"text"
            ELSE 'Unknown'::"text"
        END AS "relationship_status_display",
        CASE
            WHEN (("lifecycle_stage")::"text" = 'awareness'::"text") THEN 'Awareness'::"text"
            WHEN (("lifecycle_stage")::"text" = 'interest'::"text") THEN 'Interest'::"text"
            WHEN (("lifecycle_stage")::"text" = 'consideration'::"text") THEN 'Consideration'::"text"
            WHEN (("lifecycle_stage")::"text" = 'decision'::"text") THEN 'Decision'::"text"
            WHEN (("lifecycle_stage")::"text" = 'retention'::"text") THEN 'Retention'::"text"
            WHEN (("lifecycle_stage")::"text" = 'customer'::"text") THEN 'Customer'::"text"
            ELSE 'Unknown'::"text"
        END AS "lifecycle_stage_display",
    ( SELECT "count"(*) AS "count"
           FROM "public"."contact_activities" "ca"
          WHERE ("ca"."contact_id" = "c"."id")) AS "total_interactions",
    ( SELECT "count"(*) AS "count"
           FROM "public"."contact_notes" "cn"
          WHERE ("cn"."contact_id" = "c"."id")) AS "total_notes",
    "jsonb_array_length"("status_history") AS "status_changes_count",
    "jsonb_array_length"("interaction_history") AS "interaction_summary_count"
   FROM "public"."contacts" "c"
  WHERE (("status")::"text" <> 'archived'::"text");


ALTER VIEW "public"."contact_enhanced_summary" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."contact_segment_memberships" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "contact_id" "uuid" NOT NULL,
    "segment_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "added_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "added_by" "text"
);


ALTER TABLE "public"."contact_segment_memberships" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."contact_segments" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "name" character varying(100) NOT NULL,
    "description" "text",
    "segment_type" character varying(20) DEFAULT 'manual'::character varying,
    "criteria" "jsonb",
    "color" character varying(7),
    "is_active" boolean DEFAULT true,
    "created_by" "uuid" NOT NULL,
    "created_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_modified" timestamp with time zone DEFAULT "now"() NOT NULL,
    CONSTRAINT "contact_segments_color_format" CHECK ((("color" IS NULL) OR (("color")::"text" ~ '^#[0-9A-Fa-f]{6}$'::"text"))),
    CONSTRAINT "contact_segments_criteria_is_object" CHECK ((("criteria" IS NULL) OR ("jsonb_typeof"("criteria") = 'object'::"text"))),
    CONSTRAINT "contact_segments_segment_type_check" CHECK ((("segment_type")::"text" = ANY (ARRAY[('manual'::character varying)::"text", ('dynamic'::character varying)::"text", ('imported'::character varying)::"text"])))
);


ALTER TABLE "public"."contact_segments" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."contact_summary" AS
 SELECT "id",
    "business_id",
    "contact_type",
    "status",
    "priority",
    COALESCE("company_name", ("concat"("first_name", ' ', "last_name"))::character varying) AS "display_name",
    COALESCE("email", "phone", "mobile_phone") AS "primary_contact",
    "estimated_value",
    "assigned_to",
    "created_date",
    "last_contacted",
    ( SELECT "count"(*) AS "count"
           FROM "public"."contact_activities" "ca"
          WHERE ("ca"."contact_id" = "c"."id")) AS "activity_count",
    ( SELECT "count"(*) AS "count"
           FROM "public"."contact_notes" "cn"
          WHERE ("cn"."contact_id" = "c"."id")) AS "note_count"
   FROM "public"."contacts" "c"
  WHERE (("status")::"text" <> 'archived'::"text");


ALTER VIEW "public"."contact_summary" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."departments" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "name" character varying(255) NOT NULL,
    "description" "text",
    "manager_id" "uuid",
    "is_active" boolean DEFAULT true,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."departments" OWNER TO "postgres";


COMMENT ON TABLE "public"."departments" IS 'Organizational departments within businesses';



CREATE TABLE IF NOT EXISTS "public"."job_activities" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "job_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "activity_type" character varying(50) NOT NULL,
    "description" "text" NOT NULL,
    "old_values" "jsonb" DEFAULT '{}'::"jsonb",
    "new_values" "jsonb" DEFAULT '{}'::"jsonb",
    "metadata" "jsonb" DEFAULT '{}'::"jsonb",
    "created_date" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "job_activities_activity_type_check" CHECK ((("activity_type")::"text" = ANY (ARRAY[('created'::character varying)::"text", ('updated'::character varying)::"text", ('status_changed'::character varying)::"text", ('assigned'::character varying)::"text", ('unassigned'::character varying)::"text", ('started'::character varying)::"text", ('paused'::character varying)::"text", ('resumed'::character varying)::"text", ('completed'::character varying)::"text", ('cancelled'::character varying)::"text", ('note_added'::character varying)::"text", ('file_attached'::character varying)::"text", ('time_logged'::character varying)::"text", ('cost_updated'::character varying)::"text"])))
);


ALTER TABLE "public"."job_activities" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."job_attachments" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "job_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "user_id" "text" NOT NULL,
    "file_name" character varying(255) NOT NULL,
    "file_path" "text" NOT NULL,
    "file_size" integer NOT NULL,
    "file_type" character varying(100) NOT NULL,
    "mime_type" character varying(100),
    "description" "text",
    "is_public" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."job_attachments" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."job_notes" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "job_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "note_type" character varying(20) DEFAULT 'general'::character varying NOT NULL,
    "title" character varying(255),
    "content" "text" NOT NULL,
    "is_private" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "job_notes_note_type_check" CHECK ((("note_type")::"text" = ANY (ARRAY[('general'::character varying)::"text", ('customer'::character varying)::"text", ('internal'::character varying)::"text", ('technical'::character varying)::"text", ('follow_up'::character varying)::"text"])))
);


ALTER TABLE "public"."job_notes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."job_templates" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "name" character varying(255) NOT NULL,
    "description" "text",
    "job_type" character varying(20) NOT NULL,
    "priority" character varying(20) DEFAULT 'medium'::character varying NOT NULL,
    "estimated_duration_hours" numeric(10,2),
    "default_cost_estimate" "jsonb" DEFAULT '{}'::"jsonb",
    "default_tags" "text"[] DEFAULT '{}'::"text"[],
    "template_data" "jsonb" DEFAULT '{}'::"jsonb",
    "is_active" boolean DEFAULT true,
    "created_by" "uuid" NOT NULL,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."job_templates" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."jobs" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "contact_id" "uuid",
    "job_number" character varying(50) NOT NULL,
    "title" character varying(255) NOT NULL,
    "description" "text",
    "job_type" character varying(20) NOT NULL,
    "status" character varying(20) DEFAULT 'draft'::character varying NOT NULL,
    "priority" character varying(20) DEFAULT 'medium'::character varying NOT NULL,
    "source" character varying(20) DEFAULT 'other'::character varying NOT NULL,
    "job_address" "jsonb" NOT NULL,
    "scheduled_start" timestamp with time zone,
    "scheduled_end" timestamp with time zone,
    "actual_start" timestamp with time zone,
    "actual_end" timestamp with time zone,
    "assigned_to" "uuid"[] DEFAULT '{}'::"uuid"[],
    "created_by" "uuid" NOT NULL,
    "time_tracking" "jsonb" DEFAULT '{}'::"jsonb",
    "cost_estimate" "jsonb" DEFAULT '{}'::"jsonb",
    "tags" "text"[] DEFAULT '{}'::"text"[],
    "notes" "text",
    "internal_notes" "text",
    "customer_requirements" "text",
    "completion_notes" "text",
    "custom_fields" "jsonb" DEFAULT '{}'::"jsonb",
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    "completed_date" timestamp with time zone,
    CONSTRAINT "chk_jobs_assigned_to_valid_users" CHECK ("public"."validate_assigned_to_users"("assigned_to")),
    CONSTRAINT "jobs_check" CHECK ((("scheduled_end" IS NULL) OR ("scheduled_start" IS NULL) OR ("scheduled_end" > "scheduled_start"))),
    CONSTRAINT "jobs_check1" CHECK ((("actual_end" IS NULL) OR ("actual_start" IS NULL) OR ("actual_end" > "actual_start"))),
    CONSTRAINT "jobs_job_type_check" CHECK ((("job_type")::"text" = ANY (ARRAY[('service'::character varying)::"text", ('installation'::character varying)::"text", ('maintenance'::character varying)::"text", ('repair'::character varying)::"text", ('inspection'::character varying)::"text", ('consultation'::character varying)::"text", ('emergency'::character varying)::"text", ('project'::character varying)::"text", ('other'::character varying)::"text"]))),
    CONSTRAINT "jobs_priority_check" CHECK ((("priority")::"text" = ANY (ARRAY[('low'::character varying)::"text", ('medium'::character varying)::"text", ('high'::character varying)::"text", ('urgent'::character varying)::"text", ('emergency'::character varying)::"text"]))),
    CONSTRAINT "jobs_source_check" CHECK ((("source")::"text" = ANY (ARRAY[('website'::character varying)::"text", ('google_ads'::character varying)::"text", ('social_media'::character varying)::"text", ('referral'::character varying)::"text", ('phone_call'::character varying)::"text", ('walk_in'::character varying)::"text", ('email_marketing'::character varying)::"text", ('trade_show'::character varying)::"text", ('direct_mail'::character varying)::"text", ('yellow_pages'::character varying)::"text", ('repeat_customer'::character varying)::"text", ('partner'::character varying)::"text", ('existing_customer'::character varying)::"text", ('cold_outreach'::character varying)::"text", ('emergency_call'::character varying)::"text", ('event'::character varying)::"text", ('direct'::character varying)::"text", ('other'::character varying)::"text"]))),
    CONSTRAINT "jobs_status_check" CHECK ((("status")::"text" = ANY (ARRAY[('draft'::character varying)::"text", ('quoted'::character varying)::"text", ('scheduled'::character varying)::"text", ('in_progress'::character varying)::"text", ('on_hold'::character varying)::"text", ('completed'::character varying)::"text", ('cancelled'::character varying)::"text", ('invoiced'::character varying)::"text", ('paid'::character varying)::"text"])))
);


ALTER TABLE "public"."jobs" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."time_off_requests" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid" NOT NULL,
    "business_id" "uuid" NOT NULL,
    "time_off_type" character varying(20) NOT NULL,
    "start_date" "date" NOT NULL,
    "end_date" "date" NOT NULL,
    "reason" "text",
    "notes" "text",
    "status" character varying(20) DEFAULT 'pending'::character varying,
    "requested_by" "uuid" NOT NULL,
    "approved_by" "uuid",
    "approval_date" timestamp with time zone,
    "denial_reason" "text",
    "affects_scheduling" boolean DEFAULT true,
    "emergency_contact_allowed" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "time_off_denial_reason_required" CHECK ((((("status")::"text" = 'denied'::"text") AND ("denial_reason" IS NOT NULL)) OR (("status")::"text" <> 'denied'::"text"))),
    CONSTRAINT "time_off_end_after_start" CHECK (("end_date" >= "start_date")),
    CONSTRAINT "time_off_requests_status_check" CHECK ((("status")::"text" = ANY (ARRAY[('pending'::character varying)::"text", ('approved'::character varying)::"text", ('denied'::character varying)::"text", ('cancelled'::character varying)::"text"]))),
    CONSTRAINT "time_off_requests_time_off_type_check" CHECK ((("time_off_type")::"text" = ANY (ARRAY[('vacation'::character varying)::"text", ('sick_leave'::character varying)::"text", ('personal'::character varying)::"text", ('holiday'::character varying)::"text", ('training'::character varying)::"text", ('emergency'::character varying)::"text", ('unpaid'::character varying)::"text"])))
);


ALTER TABLE "public"."time_off_requests" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_capabilities" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "home_base_address" "text",
    "home_base_latitude" numeric(10,8),
    "home_base_longitude" numeric(11,8),
    "vehicle_type" character varying(50),
    "has_vehicle" boolean DEFAULT true,
    "preferred_start_time" time without time zone,
    "preferred_end_time" time without time zone,
    "min_time_between_jobs_minutes" integer DEFAULT 30,
    "max_commute_time_minutes" integer DEFAULT 60,
    "average_job_rating" numeric(3,2),
    "completion_rate" numeric(5,2),
    "punctuality_score" numeric(5,2),
    "working_hours_template_id" "uuid",
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    "is_active" boolean DEFAULT true,
    CONSTRAINT "user_capabilities_average_job_rating_check" CHECK ((("average_job_rating" >= (0)::numeric) AND ("average_job_rating" <= (5)::numeric))),
    CONSTRAINT "user_capabilities_check" CHECK ((("home_base_latitude" IS NULL) = ("home_base_longitude" IS NULL))),
    CONSTRAINT "user_capabilities_completion_rate_check" CHECK ((("completion_rate" >= (0)::numeric) AND ("completion_rate" <= (100)::numeric))),
    CONSTRAINT "user_capabilities_max_commute_time_minutes_check" CHECK (("max_commute_time_minutes" > 0)),
    CONSTRAINT "user_capabilities_min_time_between_jobs_minutes_check" CHECK (("min_time_between_jobs_minutes" >= 0)),
    CONSTRAINT "user_capabilities_punctuality_score_check" CHECK ((("punctuality_score" >= (0)::numeric) AND ("punctuality_score" <= (100)::numeric)))
);


ALTER TABLE "public"."user_capabilities" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_certifications" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_capabilities_id" "uuid" NOT NULL,
    "certification_id" character varying(100) NOT NULL,
    "name" character varying(200) NOT NULL,
    "issuing_authority" character varying(200) NOT NULL,
    "issue_date" timestamp with time zone NOT NULL,
    "expiry_date" timestamp with time zone,
    "status" character varying(20) DEFAULT 'active'::character varying,
    "verification_number" character varying(100),
    "renewal_required" boolean DEFAULT true,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "user_certifications_check" CHECK ((("expiry_date" IS NULL) OR ("expiry_date" > "issue_date"))),
    CONSTRAINT "user_certifications_status_check" CHECK ((("status")::"text" = ANY (ARRAY[('active'::character varying)::"text", ('expired'::character varying)::"text", ('pending'::character varying)::"text", ('suspended'::character varying)::"text"])))
);


ALTER TABLE "public"."user_certifications" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."user_dashboard_activities" AS
 SELECT "a"."id",
    "a"."business_id",
    "a"."contact_id",
    "c"."display_name" AS "contact_name",
    "a"."activity_type",
    "a"."title",
    "a"."status",
    "a"."priority",
    "a"."scheduled_date",
    "a"."due_date",
    "a"."assigned_to",
    "a"."created_date",
        CASE
            WHEN (("a"."status" = ANY (ARRAY['pending'::"public"."activity_status", 'in_progress'::"public"."activity_status"])) AND ((("a"."due_date" IS NOT NULL) AND ("a"."due_date" < "now"())) OR (("a"."due_date" IS NULL) AND ("a"."scheduled_date" IS NOT NULL) AND ("a"."scheduled_date" < ("now"() - '1 day'::interval))))) THEN 'overdue'::"text"
            WHEN (("a"."scheduled_date" IS NOT NULL) AND ("a"."scheduled_date" > "now"()) AND ("a"."scheduled_date" <= ("now"() + '7 days'::interval))) THEN 'upcoming'::"text"
            ELSE 'normal'::"text"
        END AS "urgency_status"
   FROM ("public"."activities" "a"
     JOIN "public"."contacts" "c" ON (("a"."contact_id" = "c"."id")))
  WHERE ("a"."status" = ANY (ARRAY['pending'::"public"."activity_status", 'in_progress'::"public"."activity_status"]))
  ORDER BY
        CASE
            WHEN ("a"."priority" = 'urgent'::"public"."activity_priority") THEN 1
            WHEN ("a"."priority" = 'high'::"public"."activity_priority") THEN 2
            WHEN ("a"."priority" = 'medium'::"public"."activity_priority") THEN 3
            ELSE 4
        END, "a"."due_date", "a"."scheduled_date";


ALTER VIEW "public"."user_dashboard_activities" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_skills" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_capabilities_id" "uuid" NOT NULL,
    "skill_id" character varying(100) NOT NULL,
    "name" character varying(200) NOT NULL,
    "category" character varying(50) NOT NULL,
    "level" character varying(20) NOT NULL,
    "years_experience" numeric(4,2) NOT NULL,
    "last_used" timestamp with time zone,
    "proficiency_score" numeric(5,2),
    "certification_required" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "user_skills_category_check" CHECK ((("category")::"text" = ANY (ARRAY[('technical'::character varying)::"text", ('mechanical'::character varying)::"text", ('electrical'::character varying)::"text", ('plumbing'::character varying)::"text", ('hvac'::character varying)::"text", ('carpentry'::character varying)::"text", ('painting'::character varying)::"text", ('cleaning'::character varying)::"text", ('security'::character varying)::"text", ('administrative'::character varying)::"text"]))),
    CONSTRAINT "user_skills_level_check" CHECK ((("level")::"text" = ANY (ARRAY[('beginner'::character varying)::"text", ('intermediate'::character varying)::"text", ('advanced'::character varying)::"text", ('expert'::character varying)::"text", ('master'::character varying)::"text"]))),
    CONSTRAINT "user_skills_proficiency_score_check" CHECK ((("proficiency_score" >= (0)::numeric) AND ("proficiency_score" <= (100)::numeric))),
    CONSTRAINT "user_skills_years_experience_check" CHECK (("years_experience" >= (0)::numeric))
);


ALTER TABLE "public"."user_skills" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "email" character varying(320) NOT NULL,
    "full_name" character varying(255),
    "display_name" character varying(255) NOT NULL,
    "avatar_url" character varying(500),
    "phone" character varying(20),
    "is_active" boolean DEFAULT true,
    "last_sign_in" timestamp with time zone,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."users" OWNER TO "postgres";


COMMENT ON TABLE "public"."users" IS 'User profiles for development - independent of auth.users';



CREATE TABLE IF NOT EXISTS "public"."working_hours_templates" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" character varying(100) NOT NULL,
    "description" "text",
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
    "break_duration_minutes" integer DEFAULT 30,
    "lunch_start_time" time without time zone,
    "lunch_duration_minutes" integer DEFAULT 60,
    "allows_flexible_start" boolean DEFAULT false,
    "flexible_start_window_minutes" integer DEFAULT 30,
    "allows_overtime" boolean DEFAULT false,
    "max_overtime_hours_per_day" numeric(3,1) DEFAULT 2.0,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    "is_active" boolean DEFAULT true,
    CONSTRAINT "working_hours_templates_break_duration_minutes_check" CHECK ((("break_duration_minutes" >= 0) AND ("break_duration_minutes" <= 120))),
    CONSTRAINT "working_hours_templates_flexible_start_window_minutes_check" CHECK ((("flexible_start_window_minutes" >= 0) AND ("flexible_start_window_minutes" <= 120))),
    CONSTRAINT "working_hours_templates_lunch_duration_minutes_check" CHECK ((("lunch_duration_minutes" >= 0) AND ("lunch_duration_minutes" <= 180))),
    CONSTRAINT "working_hours_templates_max_overtime_hours_per_day_check" CHECK ((("max_overtime_hours_per_day" >= (0)::numeric) AND ("max_overtime_hours_per_day" <= (8)::numeric)))
);


ALTER TABLE "public"."working_hours_templates" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."workload_capacity" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_capabilities_id" "uuid" NOT NULL,
    "max_concurrent_jobs" integer DEFAULT 3,
    "max_daily_hours" numeric(4,2) DEFAULT 8.0,
    "max_weekly_hours" numeric(5,2) DEFAULT 40.0,
    "preferred_job_types" "text"[] DEFAULT '{}'::"text"[],
    "max_travel_distance_km" numeric(6,2) DEFAULT 50.0,
    "overtime_willingness" boolean DEFAULT false,
    "emergency_availability" boolean DEFAULT false,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "workload_capacity_max_concurrent_jobs_check" CHECK (("max_concurrent_jobs" > 0)),
    CONSTRAINT "workload_capacity_max_daily_hours_check" CHECK (("max_daily_hours" > (0)::numeric)),
    CONSTRAINT "workload_capacity_max_travel_distance_km_check" CHECK (("max_travel_distance_km" >= (0)::numeric)),
    CONSTRAINT "workload_capacity_max_weekly_hours_check" CHECK (("max_weekly_hours" > (0)::numeric))
);


ALTER TABLE "public"."workload_capacity" OWNER TO "postgres";


ALTER TABLE ONLY "public"."activities"
    ADD CONSTRAINT "activities_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."activity_participants"
    ADD CONSTRAINT "activity_participants_activity_id_user_id_key" UNIQUE ("activity_id", "user_id");



ALTER TABLE ONLY "public"."activity_participants"
    ADD CONSTRAINT "activity_participants_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."activity_reminders"
    ADD CONSTRAINT "activity_reminders_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."activity_templates"
    ADD CONSTRAINT "activity_templates_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."availability_windows"
    ADD CONSTRAINT "availability_windows_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."business_invitations"
    ADD CONSTRAINT "business_invitations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."business_memberships"
    ADD CONSTRAINT "business_memberships_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."business_memberships"
    ADD CONSTRAINT "business_memberships_unique" UNIQUE ("business_id", "user_id");



ALTER TABLE ONLY "public"."businesses"
    ADD CONSTRAINT "businesses_name_owner_unique" UNIQUE ("name", "owner_id");



ALTER TABLE ONLY "public"."businesses"
    ADD CONSTRAINT "businesses_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."calendar_events"
    ADD CONSTRAINT "calendar_events_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."calendar_preferences"
    ADD CONSTRAINT "calendar_preferences_pkey" PRIMARY KEY ("user_id", "business_id");



ALTER TABLE ONLY "public"."contact_activities"
    ADD CONSTRAINT "contact_activities_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."contact_notes"
    ADD CONSTRAINT "contact_notes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."contact_segment_memberships"
    ADD CONSTRAINT "contact_segment_memberships_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."contact_segment_memberships"
    ADD CONSTRAINT "contact_segment_memberships_unique" UNIQUE ("contact_id", "segment_id");



ALTER TABLE ONLY "public"."contact_segments"
    ADD CONSTRAINT "contact_segments_business_name_unique" UNIQUE ("business_id", "name");



ALTER TABLE ONLY "public"."contact_segments"
    ADD CONSTRAINT "contact_segments_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_name_business_unique" UNIQUE ("business_id", "name");



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."job_activities"
    ADD CONSTRAINT "job_activities_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."job_attachments"
    ADD CONSTRAINT "job_attachments_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."job_notes"
    ADD CONSTRAINT "job_notes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."job_templates"
    ADD CONSTRAINT "job_templates_business_id_name_key" UNIQUE ("business_id", "name");



ALTER TABLE ONLY "public"."job_templates"
    ADD CONSTRAINT "job_templates_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_business_id_job_number_key" UNIQUE ("business_id", "job_number");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."time_off_requests"
    ADD CONSTRAINT "time_off_requests_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_capabilities"
    ADD CONSTRAINT "user_capabilities_business_id_user_id_key" UNIQUE ("business_id", "user_id");



ALTER TABLE ONLY "public"."user_capabilities"
    ADD CONSTRAINT "user_capabilities_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_certifications"
    ADD CONSTRAINT "user_certifications_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_certifications"
    ADD CONSTRAINT "user_certifications_user_capabilities_id_certification_id_key" UNIQUE ("user_capabilities_id", "certification_id");



ALTER TABLE ONLY "public"."user_skills"
    ADD CONSTRAINT "user_skills_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_skills"
    ADD CONSTRAINT "user_skills_user_capabilities_id_skill_id_key" UNIQUE ("user_capabilities_id", "skill_id");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_email_key" UNIQUE ("email");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."working_hours_templates"
    ADD CONSTRAINT "working_hours_templates_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."workload_capacity"
    ADD CONSTRAINT "workload_capacity_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."workload_capacity"
    ADD CONSTRAINT "workload_capacity_user_capabilities_id_key" UNIQUE ("user_capabilities_id");



CREATE INDEX "idx_activities_assigned_to" ON "public"."activities" USING "btree" ("assigned_to");



CREATE INDEX "idx_activities_business_id" ON "public"."activities" USING "btree" ("business_id");



CREATE INDEX "idx_activities_business_timeline" ON "public"."activities" USING "btree" ("business_id", "scheduled_date" DESC, "created_date" DESC);



CREATE INDEX "idx_activities_contact_id" ON "public"."activities" USING "btree" ("contact_id");



CREATE INDEX "idx_activities_contact_timeline" ON "public"."activities" USING "btree" ("contact_id", "business_id", "scheduled_date" DESC, "created_date" DESC);



CREATE INDEX "idx_activities_created_by" ON "public"."activities" USING "btree" ("created_by");



CREATE INDEX "idx_activities_created_date" ON "public"."activities" USING "btree" ("created_date");



CREATE INDEX "idx_activities_due_date" ON "public"."activities" USING "btree" ("due_date");



CREATE INDEX "idx_activities_last_modified" ON "public"."activities" USING "btree" ("last_modified");



CREATE INDEX "idx_activities_overdue" ON "public"."activities" USING "btree" ("business_id", "status", "due_date") WHERE ("status" = ANY (ARRAY['pending'::"public"."activity_status", 'in_progress'::"public"."activity_status"]));



CREATE INDEX "idx_activities_parent_id" ON "public"."activities" USING "btree" ("parent_activity_id");



CREATE INDEX "idx_activities_priority" ON "public"."activities" USING "btree" ("priority");



CREATE INDEX "idx_activities_scheduled_date" ON "public"."activities" USING "btree" ("scheduled_date");



CREATE INDEX "idx_activities_status" ON "public"."activities" USING "btree" ("status");



CREATE INDEX "idx_activities_template_id" ON "public"."activities" USING "btree" ("template_id");



CREATE INDEX "idx_activities_type" ON "public"."activities" USING "btree" ("activity_type");



CREATE INDEX "idx_activities_upcoming" ON "public"."activities" USING "btree" ("business_id", "scheduled_date") WHERE ("status" = ANY (ARRAY['pending'::"public"."activity_status", 'in_progress'::"public"."activity_status"]));



CREATE INDEX "idx_activities_user_tasks" ON "public"."activities" USING "btree" ("business_id", "assigned_to", "status", "due_date");



CREATE INDEX "idx_activity_participants_activity_id" ON "public"."activity_participants" USING "btree" ("activity_id");



CREATE INDEX "idx_activity_participants_user_id" ON "public"."activity_participants" USING "btree" ("user_id");



CREATE INDEX "idx_activity_reminders_activity_id" ON "public"."activity_reminders" USING "btree" ("activity_id");



CREATE INDEX "idx_activity_reminders_pending" ON "public"."activity_reminders" USING "btree" ("is_sent", "reminder_time") WHERE ("is_sent" = false);



CREATE INDEX "idx_activity_reminders_time" ON "public"."activity_reminders" USING "btree" ("reminder_time");



CREATE INDEX "idx_activity_templates_active" ON "public"."activity_templates" USING "btree" ("is_active");



CREATE INDEX "idx_activity_templates_business_id" ON "public"."activity_templates" USING "btree" ("business_id");



CREATE INDEX "idx_activity_templates_type" ON "public"."activity_templates" USING "btree" ("activity_type");



CREATE INDEX "idx_availability_windows_capabilities_id" ON "public"."availability_windows" USING "btree" ("user_capabilities_id");



CREATE INDEX "idx_availability_windows_day" ON "public"."availability_windows" USING "btree" ("day_of_week");



CREATE INDEX "idx_business_invitations_business_id" ON "public"."business_invitations" USING "btree" ("business_id");



CREATE INDEX "idx_business_invitations_expiry_date" ON "public"."business_invitations" USING "btree" ("expiry_date");



CREATE INDEX "idx_business_invitations_invited_by" ON "public"."business_invitations" USING "btree" ("invited_by");



CREATE INDEX "idx_business_invitations_invited_email" ON "public"."business_invitations" USING "btree" ("invited_email");



CREATE INDEX "idx_business_invitations_invited_phone" ON "public"."business_invitations" USING "btree" ("invited_phone");



CREATE INDEX "idx_business_invitations_status" ON "public"."business_invitations" USING "btree" ("status");



CREATE INDEX "idx_business_memberships_business_id" ON "public"."business_memberships" USING "btree" ("business_id");



CREATE INDEX "idx_business_memberships_invited_by" ON "public"."business_memberships" USING "btree" ("invited_by") WHERE ("invited_by" IS NOT NULL);



CREATE INDEX "idx_business_memberships_is_active" ON "public"."business_memberships" USING "btree" ("is_active");



CREATE INDEX "idx_business_memberships_joined_date" ON "public"."business_memberships" USING "btree" ("joined_date");



CREATE INDEX "idx_business_memberships_role" ON "public"."business_memberships" USING "btree" ("role");



CREATE INDEX "idx_business_memberships_user_id" ON "public"."business_memberships" USING "btree" ("user_id");



CREATE INDEX "idx_businesses_created_date" ON "public"."businesses" USING "btree" ("created_date");



CREATE INDEX "idx_businesses_industry" ON "public"."businesses" USING "btree" ("industry");



CREATE INDEX "idx_businesses_is_active" ON "public"."businesses" USING "btree" ("is_active");



CREATE INDEX "idx_businesses_name_gin" ON "public"."businesses" USING "gin" ("name" "public"."gin_trgm_ops");



CREATE INDEX "idx_businesses_owner_id" ON "public"."businesses" USING "btree" ("owner_id");



CREATE INDEX "idx_calendar_events_active" ON "public"."calendar_events" USING "btree" ("is_active") WHERE ("is_active" = true);



CREATE INDEX "idx_calendar_events_datetime" ON "public"."calendar_events" USING "btree" ("start_datetime", "end_datetime");



CREATE INDEX "idx_calendar_events_recurrence" ON "public"."calendar_events" USING "btree" ("recurrence_type") WHERE (("recurrence_type")::"text" <> 'none'::"text");



CREATE INDEX "idx_calendar_events_user_business" ON "public"."calendar_events" USING "btree" ("user_id", "business_id");



CREATE INDEX "idx_calendar_events_user_id" ON "public"."calendar_events" USING "btree" ("user_id");



CREATE INDEX "idx_calendar_preferences_user_id" ON "public"."calendar_preferences" USING "btree" ("user_id");



CREATE INDEX "idx_contact_activities_business_date" ON "public"."contact_activities" USING "btree" ("business_id", "activity_date" DESC);



CREATE INDEX "idx_contact_activities_business_id" ON "public"."contact_activities" USING "btree" ("business_id");



CREATE INDEX "idx_contact_activities_contact_date" ON "public"."contact_activities" USING "btree" ("contact_id", "activity_date" DESC);



CREATE INDEX "idx_contact_activities_contact_id" ON "public"."contact_activities" USING "btree" ("contact_id");



CREATE INDEX "idx_contact_activities_date" ON "public"."contact_activities" USING "btree" ("activity_date");



CREATE INDEX "idx_contact_activities_performed_by" ON "public"."contact_activities" USING "btree" ("performed_by");



CREATE INDEX "idx_contact_activities_type" ON "public"."contact_activities" USING "btree" ("activity_type");



CREATE INDEX "idx_contact_notes_business_id" ON "public"."contact_notes" USING "btree" ("business_id");



CREATE INDEX "idx_contact_notes_contact_id" ON "public"."contact_notes" USING "btree" ("contact_id");



CREATE INDEX "idx_contact_notes_content_search" ON "public"."contact_notes" USING "gin" ("to_tsvector"('"english"'::"regconfig", (((COALESCE("title", ''::character varying))::"text" || ' '::"text") || COALESCE("content", ''::"text"))));



CREATE INDEX "idx_contact_notes_created_by" ON "public"."contact_notes" USING "btree" ("created_by");



CREATE INDEX "idx_contact_notes_created_date" ON "public"."contact_notes" USING "btree" ("created_date" DESC);



CREATE INDEX "idx_contact_notes_private" ON "public"."contact_notes" USING "btree" ("is_private");



CREATE INDEX "idx_contact_notes_tags" ON "public"."contact_notes" USING "gin" ("tags");



CREATE INDEX "idx_contact_notes_type" ON "public"."contact_notes" USING "btree" ("note_type");



CREATE INDEX "idx_contact_segment_memberships_business" ON "public"."contact_segment_memberships" USING "btree" ("business_id");



CREATE INDEX "idx_contact_segment_memberships_contact" ON "public"."contact_segment_memberships" USING "btree" ("contact_id");



CREATE INDEX "idx_contact_segment_memberships_segment" ON "public"."contact_segment_memberships" USING "btree" ("segment_id");



CREATE INDEX "idx_contact_segments_active" ON "public"."contact_segments" USING "btree" ("is_active");



CREATE INDEX "idx_contact_segments_business_id" ON "public"."contact_segments" USING "btree" ("business_id");



CREATE INDEX "idx_contact_segments_created_by" ON "public"."contact_segments" USING "btree" ("created_by");



CREATE INDEX "idx_contact_segments_type" ON "public"."contact_segments" USING "btree" ("segment_type");



CREATE INDEX "idx_contacts_assigned_to" ON "public"."contacts" USING "btree" ("assigned_to");



CREATE INDEX "idx_contacts_assigned_to_users" ON "public"."contacts" USING "btree" ("assigned_to") WHERE ("assigned_to" IS NOT NULL);



CREATE INDEX "idx_contacts_business_assigned" ON "public"."contacts" USING "btree" ("business_id", "assigned_to");



CREATE UNIQUE INDEX "idx_contacts_business_email_unique" ON "public"."contacts" USING "btree" ("business_id", "email") WHERE (("email" IS NOT NULL) AND (("email")::"text" <> ''::"text"));



CREATE INDEX "idx_contacts_business_id" ON "public"."contacts" USING "btree" ("business_id");



CREATE UNIQUE INDEX "idx_contacts_business_phone_unique" ON "public"."contacts" USING "btree" ("business_id", "phone") WHERE (("phone" IS NOT NULL) AND (("phone")::"text" <> ''::"text"));



CREATE INDEX "idx_contacts_business_priority" ON "public"."contacts" USING "btree" ("business_id", "priority");



CREATE INDEX "idx_contacts_business_status" ON "public"."contacts" USING "btree" ("business_id", "status");



CREATE INDEX "idx_contacts_business_type" ON "public"."contacts" USING "btree" ("business_id", "contact_type");



CREATE INDEX "idx_contacts_contact_type" ON "public"."contacts" USING "btree" ("contact_type");



CREATE INDEX "idx_contacts_created_by" ON "public"."contacts" USING "btree" ("created_by");



CREATE INDEX "idx_contacts_created_by_users" ON "public"."contacts" USING "btree" ("created_by") WHERE ("created_by" IS NOT NULL);



CREATE INDEX "idx_contacts_created_date" ON "public"."contacts" USING "btree" ("created_date");



CREATE INDEX "idx_contacts_custom_fields" ON "public"."contacts" USING "gin" ("custom_fields");



CREATE INDEX "idx_contacts_display_name" ON "public"."contacts" USING "btree" ("display_name");



CREATE INDEX "idx_contacts_email_search" ON "public"."contacts" USING "gin" ("to_tsvector"('"english"'::"regconfig", (COALESCE("email", ''::character varying))::"text"));



CREATE INDEX "idx_contacts_interaction_history" ON "public"."contacts" USING "gin" ("interaction_history");



CREATE INDEX "idx_contacts_last_contacted" ON "public"."contacts" USING "btree" ("last_contacted");



CREATE INDEX "idx_contacts_last_modified" ON "public"."contacts" USING "btree" ("last_modified");



CREATE INDEX "idx_contacts_lifecycle_stage" ON "public"."contacts" USING "btree" ("lifecycle_stage");



CREATE INDEX "idx_contacts_name_search" ON "public"."contacts" USING "gin" ("to_tsvector"('"english"'::"regconfig", (((((COALESCE("first_name", ''::character varying))::"text" || ' '::"text") || (COALESCE("last_name", ''::character varying))::"text") || ' '::"text") || (COALESCE("company_name", ''::character varying))::"text")));



CREATE INDEX "idx_contacts_priority" ON "public"."contacts" USING "btree" ("priority");



CREATE INDEX "idx_contacts_relationship_status" ON "public"."contacts" USING "btree" ("relationship_status");



CREATE INDEX "idx_contacts_source" ON "public"."contacts" USING "btree" ("source");



CREATE INDEX "idx_contacts_status" ON "public"."contacts" USING "btree" ("status");



CREATE INDEX "idx_contacts_status_history" ON "public"."contacts" USING "gin" ("status_history");



CREATE INDEX "idx_contacts_tags" ON "public"."contacts" USING "gin" ("tags");



CREATE INDEX "idx_departments_business_id" ON "public"."departments" USING "btree" ("business_id");



CREATE INDEX "idx_departments_is_active" ON "public"."departments" USING "btree" ("is_active");



CREATE INDEX "idx_departments_manager_id" ON "public"."departments" USING "btree" ("manager_id");



CREATE INDEX "idx_job_activities_business_id" ON "public"."job_activities" USING "btree" ("business_id");



CREATE INDEX "idx_job_activities_created_date" ON "public"."job_activities" USING "btree" ("created_date");



CREATE INDEX "idx_job_activities_job_id" ON "public"."job_activities" USING "btree" ("job_id");



CREATE INDEX "idx_job_activities_type" ON "public"."job_activities" USING "btree" ("activity_type");



CREATE INDEX "idx_job_activities_user_id" ON "public"."job_activities" USING "btree" ("user_id");



CREATE INDEX "idx_job_attachments_business_id" ON "public"."job_attachments" USING "btree" ("business_id");



CREATE INDEX "idx_job_attachments_file_type" ON "public"."job_attachments" USING "btree" ("file_type");



CREATE INDEX "idx_job_attachments_job_id" ON "public"."job_attachments" USING "btree" ("job_id");



CREATE INDEX "idx_job_attachments_user_id" ON "public"."job_attachments" USING "btree" ("user_id");



CREATE INDEX "idx_job_notes_business_id" ON "public"."job_notes" USING "btree" ("business_id");



CREATE INDEX "idx_job_notes_created_date" ON "public"."job_notes" USING "btree" ("created_date");



CREATE INDEX "idx_job_notes_job_id" ON "public"."job_notes" USING "btree" ("job_id");



CREATE INDEX "idx_job_notes_note_type" ON "public"."job_notes" USING "btree" ("note_type");



CREATE INDEX "idx_job_notes_user_id" ON "public"."job_notes" USING "btree" ("user_id");



CREATE INDEX "idx_job_templates_active" ON "public"."job_templates" USING "btree" ("business_id", "is_active");



CREATE INDEX "idx_job_templates_business_id" ON "public"."job_templates" USING "btree" ("business_id");



CREATE INDEX "idx_job_templates_job_type" ON "public"."job_templates" USING "btree" ("business_id", "job_type");



CREATE INDEX "idx_jobs_actual_end" ON "public"."jobs" USING "btree" ("business_id", "actual_end");



CREATE INDEX "idx_jobs_actual_start" ON "public"."jobs" USING "btree" ("business_id", "actual_start");



CREATE INDEX "idx_jobs_assigned_status" ON "public"."jobs" USING "gin" ("assigned_to") WHERE (("status")::"text" = ANY (ARRAY[('scheduled'::character varying)::"text", ('in_progress'::character varying)::"text"]));



CREATE INDEX "idx_jobs_assigned_to" ON "public"."jobs" USING "gin" ("assigned_to");



CREATE INDEX "idx_jobs_business_id" ON "public"."jobs" USING "btree" ("business_id");



CREATE INDEX "idx_jobs_completed_date" ON "public"."jobs" USING "btree" ("business_id", "completed_date");



CREATE INDEX "idx_jobs_contact_id" ON "public"."jobs" USING "btree" ("contact_id");



CREATE INDEX "idx_jobs_cost_estimate" ON "public"."jobs" USING "gin" ("cost_estimate");



CREATE INDEX "idx_jobs_created_by" ON "public"."jobs" USING "btree" ("created_by");



CREATE INDEX "idx_jobs_created_date" ON "public"."jobs" USING "btree" ("business_id", "created_date");



CREATE INDEX "idx_jobs_custom_fields" ON "public"."jobs" USING "gin" ("custom_fields");



CREATE INDEX "idx_jobs_description_search" ON "public"."jobs" USING "gin" ("to_tsvector"('"english"'::"regconfig", "description"));



CREATE INDEX "idx_jobs_job_address" ON "public"."jobs" USING "gin" ("job_address");



CREATE INDEX "idx_jobs_job_number" ON "public"."jobs" USING "btree" ("business_id", "job_number");



CREATE INDEX "idx_jobs_job_type" ON "public"."jobs" USING "btree" ("business_id", "job_type");



CREATE INDEX "idx_jobs_last_modified" ON "public"."jobs" USING "btree" ("business_id", "last_modified");



CREATE INDEX "idx_jobs_priority" ON "public"."jobs" USING "btree" ("business_id", "priority");



CREATE INDEX "idx_jobs_scheduled_end" ON "public"."jobs" USING "btree" ("business_id", "scheduled_end");



CREATE INDEX "idx_jobs_scheduled_end_active" ON "public"."jobs" USING "btree" ("business_id", "scheduled_end") WHERE (("status")::"text" = ANY (ARRAY[('scheduled'::character varying)::"text", ('in_progress'::character varying)::"text"]));



CREATE INDEX "idx_jobs_scheduled_start" ON "public"."jobs" USING "btree" ("business_id", "scheduled_start");



CREATE INDEX "idx_jobs_source" ON "public"."jobs" USING "btree" ("business_id", "source");



CREATE INDEX "idx_jobs_status" ON "public"."jobs" USING "btree" ("business_id", "status");



CREATE INDEX "idx_jobs_status_priority" ON "public"."jobs" USING "btree" ("business_id", "status", "priority");



CREATE INDEX "idx_jobs_tags" ON "public"."jobs" USING "gin" ("tags");



CREATE INDEX "idx_jobs_time_tracking" ON "public"."jobs" USING "gin" ("time_tracking");



CREATE INDEX "idx_jobs_title_search" ON "public"."jobs" USING "gin" ("to_tsvector"('"english"'::"regconfig", ("title")::"text"));



CREATE INDEX "idx_jobs_type_status" ON "public"."jobs" USING "btree" ("business_id", "job_type", "status");



CREATE INDEX "idx_time_off_dates" ON "public"."time_off_requests" USING "btree" ("start_date", "end_date");



CREATE INDEX "idx_time_off_pending" ON "public"."time_off_requests" USING "btree" ("business_id", "status") WHERE (("status")::"text" = 'pending'::"text");



CREATE INDEX "idx_time_off_requests_approved_by" ON "public"."time_off_requests" USING "btree" ("approved_by") WHERE ("approved_by" IS NOT NULL);



CREATE INDEX "idx_time_off_requests_requested_by" ON "public"."time_off_requests" USING "btree" ("requested_by");



CREATE INDEX "idx_time_off_requests_user_id" ON "public"."time_off_requests" USING "btree" ("user_id");



CREATE INDEX "idx_time_off_status" ON "public"."time_off_requests" USING "btree" ("status");



CREATE INDEX "idx_time_off_user_business" ON "public"."time_off_requests" USING "btree" ("user_id", "business_id");



CREATE INDEX "idx_user_capabilities_active" ON "public"."user_capabilities" USING "btree" ("is_active") WHERE ("is_active" = true);



CREATE INDEX "idx_user_capabilities_business_id" ON "public"."user_capabilities" USING "btree" ("business_id");



CREATE INDEX "idx_user_capabilities_user_id" ON "public"."user_capabilities" USING "btree" ("user_id");



CREATE INDEX "idx_user_certifications_capabilities_id" ON "public"."user_certifications" USING "btree" ("user_capabilities_id");



CREATE INDEX "idx_user_certifications_expiry" ON "public"."user_certifications" USING "btree" ("expiry_date") WHERE ("expiry_date" IS NOT NULL);



CREATE INDEX "idx_user_certifications_status" ON "public"."user_certifications" USING "btree" ("status");



CREATE INDEX "idx_user_skills_capabilities_id" ON "public"."user_skills" USING "btree" ("user_capabilities_id");



CREATE INDEX "idx_user_skills_category" ON "public"."user_skills" USING "btree" ("category");



CREATE INDEX "idx_user_skills_level" ON "public"."user_skills" USING "btree" ("level");



CREATE INDEX "idx_user_skills_skill_id" ON "public"."user_skills" USING "btree" ("skill_id");



CREATE INDEX "idx_users_display_name" ON "public"."users" USING "btree" ("display_name");



CREATE INDEX "idx_users_email" ON "public"."users" USING "btree" ("email");



CREATE INDEX "idx_users_is_active" ON "public"."users" USING "btree" ("is_active") WHERE ("is_active" = true);



CREATE INDEX "idx_working_hours_templates_active" ON "public"."working_hours_templates" USING "btree" ("is_active") WHERE ("is_active" = true);



CREATE INDEX "idx_workload_capacity_capabilities_id" ON "public"."workload_capacity" USING "btree" ("user_capabilities_id");



CREATE OR REPLACE TRIGGER "add_contact_interaction_to_history_trigger" AFTER INSERT ON "public"."contact_activities" FOR EACH ROW EXECUTE FUNCTION "public"."add_contact_interaction_to_history"();



CREATE OR REPLACE TRIGGER "businesses_update_last_modified" BEFORE UPDATE ON "public"."businesses" FOR EACH ROW EXECUTE FUNCTION "public"."update_businesses_last_modified"();



CREATE OR REPLACE TRIGGER "departments_update_last_modified" BEFORE UPDATE ON "public"."departments" FOR EACH ROW EXECUTE FUNCTION "public"."update_departments_last_modified"();



CREATE OR REPLACE TRIGGER "trigger_assign_default_permissions" BEFORE INSERT OR UPDATE ON "public"."business_memberships" FOR EACH ROW EXECUTE FUNCTION "public"."assign_default_permissions"();



CREATE OR REPLACE TRIGGER "trigger_log_job_activity" AFTER INSERT OR UPDATE ON "public"."jobs" FOR EACH ROW EXECUTE FUNCTION "public"."log_job_activity"();



CREATE OR REPLACE TRIGGER "trigger_update_job_last_modified" BEFORE UPDATE ON "public"."jobs" FOR EACH ROW EXECUTE FUNCTION "public"."update_job_last_modified"();



CREATE OR REPLACE TRIGGER "trigger_update_job_notes_last_modified" BEFORE UPDATE ON "public"."job_notes" FOR EACH ROW EXECUTE FUNCTION "public"."update_job_last_modified"();



CREATE OR REPLACE TRIGGER "trigger_update_job_templates_last_modified" BEFORE UPDATE ON "public"."job_templates" FOR EACH ROW EXECUTE FUNCTION "public"."update_job_last_modified"();



CREATE OR REPLACE TRIGGER "update_activities_modified" BEFORE UPDATE ON "public"."activities" FOR EACH ROW EXECUTE FUNCTION "public"."update_activity_modified"();



CREATE OR REPLACE TRIGGER "update_activity_templates_modified" BEFORE UPDATE ON "public"."activity_templates" FOR EACH ROW EXECUTE FUNCTION "public"."update_activity_modified"();



CREATE OR REPLACE TRIGGER "update_availability_windows_last_modified" BEFORE UPDATE ON "public"."availability_windows" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_calendar_events_last_modified" BEFORE UPDATE ON "public"."calendar_events" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_calendar_preferences_last_modified" BEFORE UPDATE ON "public"."calendar_preferences" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_contact_activities_last_modified" BEFORE UPDATE ON "public"."contact_activities" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified_column"();



CREATE OR REPLACE TRIGGER "update_contact_last_contacted_trigger" AFTER INSERT ON "public"."contact_activities" FOR EACH ROW EXECUTE FUNCTION "public"."update_contact_last_contacted"();



CREATE OR REPLACE TRIGGER "update_contact_notes_last_modified" BEFORE UPDATE ON "public"."contact_notes" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified_column"();



CREATE OR REPLACE TRIGGER "update_contact_segments_last_modified" BEFORE UPDATE ON "public"."contact_segments" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified_column"();



CREATE OR REPLACE TRIGGER "update_contact_status_history_trigger" BEFORE UPDATE ON "public"."contacts" FOR EACH ROW EXECUTE FUNCTION "public"."update_contact_status_history"();



CREATE OR REPLACE TRIGGER "update_contacts_last_modified" BEFORE UPDATE ON "public"."contacts" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified_column"();



CREATE OR REPLACE TRIGGER "update_time_off_requests_last_modified" BEFORE UPDATE ON "public"."time_off_requests" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_user_capabilities_last_modified" BEFORE UPDATE ON "public"."user_capabilities" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_user_certifications_last_modified" BEFORE UPDATE ON "public"."user_certifications" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_user_skills_last_modified" BEFORE UPDATE ON "public"."user_skills" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_working_hours_templates_last_modified" BEFORE UPDATE ON "public"."working_hours_templates" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "update_workload_capacity_last_modified" BEFORE UPDATE ON "public"."workload_capacity" FOR EACH ROW EXECUTE FUNCTION "public"."update_last_modified"();



CREATE OR REPLACE TRIGGER "users_update_updated_at" BEFORE UPDATE ON "public"."users" FOR EACH ROW EXECUTE FUNCTION "public"."update_users_updated_at"();



ALTER TABLE ONLY "public"."activities"
    ADD CONSTRAINT "activities_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."activities"
    ADD CONSTRAINT "activities_contact_id_fkey" FOREIGN KEY ("contact_id") REFERENCES "public"."contacts"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."activities"
    ADD CONSTRAINT "activities_parent_activity_id_fkey" FOREIGN KEY ("parent_activity_id") REFERENCES "public"."activities"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."activities"
    ADD CONSTRAINT "activities_template_id_fkey" FOREIGN KEY ("template_id") REFERENCES "public"."activity_templates"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."activity_participants"
    ADD CONSTRAINT "activity_participants_activity_id_fkey" FOREIGN KEY ("activity_id") REFERENCES "public"."activities"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."activity_reminders"
    ADD CONSTRAINT "activity_reminders_activity_id_fkey" FOREIGN KEY ("activity_id") REFERENCES "public"."activities"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."activity_templates"
    ADD CONSTRAINT "activity_templates_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."availability_windows"
    ADD CONSTRAINT "availability_windows_user_capabilities_id_fkey" FOREIGN KEY ("user_capabilities_id") REFERENCES "public"."user_capabilities"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."business_invitations"
    ADD CONSTRAINT "business_invitations_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."business_invitations"
    ADD CONSTRAINT "business_invitations_invited_by_fkey" FOREIGN KEY ("invited_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."business_memberships"
    ADD CONSTRAINT "business_memberships_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."business_memberships"
    ADD CONSTRAINT "business_memberships_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."businesses"
    ADD CONSTRAINT "businesses_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."calendar_events"
    ADD CONSTRAINT "calendar_events_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."calendar_preferences"
    ADD CONSTRAINT "calendar_preferences_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."calendar_preferences"
    ADD CONSTRAINT "calendar_preferences_preferred_working_hours_template_id_fkey" FOREIGN KEY ("preferred_working_hours_template_id") REFERENCES "public"."working_hours_templates"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."contact_activities"
    ADD CONSTRAINT "contact_activities_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_activities"
    ADD CONSTRAINT "contact_activities_contact_id_fkey" FOREIGN KEY ("contact_id") REFERENCES "public"."contacts"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_activities"
    ADD CONSTRAINT "contact_activities_performed_by_fkey" FOREIGN KEY ("performed_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."contact_notes"
    ADD CONSTRAINT "contact_notes_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_notes"
    ADD CONSTRAINT "contact_notes_contact_id_fkey" FOREIGN KEY ("contact_id") REFERENCES "public"."contacts"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_notes"
    ADD CONSTRAINT "contact_notes_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."contact_segment_memberships"
    ADD CONSTRAINT "contact_segment_memberships_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_segment_memberships"
    ADD CONSTRAINT "contact_segment_memberships_contact_id_fkey" FOREIGN KEY ("contact_id") REFERENCES "public"."contacts"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_segment_memberships"
    ADD CONSTRAINT "contact_segment_memberships_segment_id_fkey" FOREIGN KEY ("segment_id") REFERENCES "public"."contact_segments"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_segments"
    ADD CONSTRAINT "contact_segments_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contact_segments"
    ADD CONSTRAINT "contact_segments_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_assigned_to_fkey" FOREIGN KEY ("assigned_to") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "contacts_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_manager_id_fkey" FOREIGN KEY ("manager_id") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."calendar_events"
    ADD CONSTRAINT "fk_calendar_events_user_id" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



COMMENT ON CONSTRAINT "fk_calendar_events_user_id" ON "public"."calendar_events" IS 'Links calendar events to authenticated users';



ALTER TABLE ONLY "public"."calendar_preferences"
    ADD CONSTRAINT "fk_calendar_preferences_user_id" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



COMMENT ON CONSTRAINT "fk_calendar_preferences_user_id" ON "public"."calendar_preferences" IS 'Links calendar preferences to authenticated users';



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "fk_contacts_assigned_to_users" FOREIGN KEY ("assigned_to") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."contacts"
    ADD CONSTRAINT "fk_contacts_created_by_users" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."time_off_requests"
    ADD CONSTRAINT "fk_time_off_requests_approved_by" FOREIGN KEY ("approved_by") REFERENCES "auth"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."time_off_requests"
    ADD CONSTRAINT "fk_time_off_requests_requested_by" FOREIGN KEY ("requested_by") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."time_off_requests"
    ADD CONSTRAINT "fk_time_off_requests_user_id" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



COMMENT ON CONSTRAINT "fk_time_off_requests_user_id" ON "public"."time_off_requests" IS 'Links time off requests to authenticated users';



ALTER TABLE ONLY "public"."user_capabilities"
    ADD CONSTRAINT "fk_user_capabilities_user_id" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



COMMENT ON CONSTRAINT "fk_user_capabilities_user_id" ON "public"."user_capabilities" IS 'Links user capabilities to authenticated users';



ALTER TABLE ONLY "public"."user_capabilities"
    ADD CONSTRAINT "fk_user_capabilities_working_hours_template" FOREIGN KEY ("working_hours_template_id") REFERENCES "public"."working_hours_templates"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."job_activities"
    ADD CONSTRAINT "job_activities_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_activities"
    ADD CONSTRAINT "job_activities_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_activities"
    ADD CONSTRAINT "job_activities_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."job_attachments"
    ADD CONSTRAINT "job_attachments_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_attachments"
    ADD CONSTRAINT "job_attachments_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_notes"
    ADD CONSTRAINT "job_notes_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_notes"
    ADD CONSTRAINT "job_notes_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_notes"
    ADD CONSTRAINT "job_notes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."job_templates"
    ADD CONSTRAINT "job_templates_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_contact_id_fkey" FOREIGN KEY ("contact_id") REFERENCES "public"."contacts"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."time_off_requests"
    ADD CONSTRAINT "time_off_requests_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_capabilities"
    ADD CONSTRAINT "user_capabilities_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_certifications"
    ADD CONSTRAINT "user_certifications_user_capabilities_id_fkey" FOREIGN KEY ("user_capabilities_id") REFERENCES "public"."user_capabilities"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_skills"
    ADD CONSTRAINT "user_skills_user_capabilities_id_fkey" FOREIGN KEY ("user_capabilities_id") REFERENCES "public"."user_capabilities"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."workload_capacity"
    ADD CONSTRAINT "workload_capacity_user_capabilities_id_fkey" FOREIGN KEY ("user_capabilities_id") REFERENCES "public"."user_capabilities"("id") ON DELETE CASCADE;



ALTER TABLE "public"."activities" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "activities_business_isolation" ON "public"."activities" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."activity_participants" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "activity_participants_business_isolation" ON "public"."activity_participants" USING (("activity_id" IN ( SELECT "activities"."id"
   FROM "public"."activities"
  WHERE ("activities"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



ALTER TABLE "public"."activity_reminders" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "activity_reminders_business_isolation" ON "public"."activity_reminders" USING (("activity_id" IN ( SELECT "activities"."id"
   FROM "public"."activities"
  WHERE ("activities"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



ALTER TABLE "public"."activity_templates" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "activity_templates_business_isolation" ON "public"."activity_templates" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."availability_windows" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "availability_windows_business_isolation" ON "public"."availability_windows" USING (("user_capabilities_id" IN ( SELECT "user_capabilities"."id"
   FROM "public"."user_capabilities"
  WHERE ("user_capabilities"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



CREATE POLICY "business_invitations_business_isolation" ON "public"."business_invitations" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true) AND ("business_memberships"."permissions" @> '["invite_team_members"]'::"jsonb")))));



CREATE POLICY "business_memberships_business_isolation" ON "public"."business_memberships" USING ((("user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") OR ("business_id" IN ( SELECT "business_memberships_1"."business_id"
   FROM "public"."business_memberships" "business_memberships_1"
  WHERE (("business_memberships_1"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships_1"."is_active" = true) AND ("business_memberships_1"."permissions" @> '["view_team_members"]'::"jsonb"))))));



CREATE POLICY "businesses_business_isolation" ON "public"."businesses" USING (("id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."calendar_events" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "calendar_events_business_isolation" ON "public"."calendar_events" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."calendar_preferences" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "calendar_preferences_business_isolation" ON "public"."calendar_preferences" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



CREATE POLICY "contact_activities_business_isolation" ON "public"."contact_activities" USING (("contact_id" IN ( SELECT "contacts"."id"
   FROM "public"."contacts"
  WHERE ("contacts"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



CREATE POLICY "contact_notes_business_isolation" ON "public"."contact_notes" USING (("contact_id" IN ( SELECT "contacts"."id"
   FROM "public"."contacts"
  WHERE ("contacts"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



CREATE POLICY "contact_segments_business_isolation" ON "public"."contact_segments" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



CREATE POLICY "contacts_business_isolation" ON "public"."contacts" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



CREATE POLICY "job_activities_business_isolation" ON "public"."job_activities" USING (("job_id" IN ( SELECT "jobs"."id"
   FROM "public"."jobs"
  WHERE ("jobs"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



CREATE POLICY "job_notes_business_isolation" ON "public"."job_notes" USING (("job_id" IN ( SELECT "jobs"."id"
   FROM "public"."jobs"
  WHERE ("jobs"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



CREATE POLICY "jobs_business_isolation" ON "public"."jobs" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."time_off_requests" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "time_off_requests_business_isolation" ON "public"."time_off_requests" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."user_capabilities" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "user_capabilities_business_isolation" ON "public"."user_capabilities" USING (("business_id" IN ( SELECT "business_memberships"."business_id"
   FROM "public"."business_memberships"
  WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))));



ALTER TABLE "public"."user_certifications" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "user_certifications_business_isolation" ON "public"."user_certifications" USING (("user_capabilities_id" IN ( SELECT "user_capabilities"."id"
   FROM "public"."user_capabilities"
  WHERE ("user_capabilities"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



ALTER TABLE "public"."user_skills" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "user_skills_business_isolation" ON "public"."user_skills" USING (("user_capabilities_id" IN ( SELECT "user_capabilities"."id"
   FROM "public"."user_capabilities"
  WHERE ("user_capabilities"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "users_business_isolation" ON "public"."users" USING ((EXISTS ( SELECT 1
   FROM ("public"."business_memberships" "bm1"
     JOIN "public"."business_memberships" "bm2" ON (("bm1"."business_id" = "bm2"."business_id")))
  WHERE (("bm1"."user_id" = "auth"."uid"()) AND ("bm2"."user_id" = "users"."id") AND ("bm1"."is_active" = true) AND ("bm2"."is_active" = true)))));



ALTER TABLE "public"."working_hours_templates" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "working_hours_templates_public_read" ON "public"."working_hours_templates" FOR SELECT USING (true);



ALTER TABLE "public"."workload_capacity" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "workload_capacity_business_isolation" ON "public"."workload_capacity" USING (("user_capabilities_id" IN ( SELECT "user_capabilities"."id"
   FROM "public"."user_capabilities"
  WHERE ("user_capabilities"."business_id" IN ( SELECT "business_memberships"."business_id"
           FROM "public"."business_memberships"
          WHERE (("business_memberships"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::"uuid") AND ("business_memberships"."is_active" = true)))))));



GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON FUNCTION "public"."add_contact_interaction_to_history"() TO "anon";
GRANT ALL ON FUNCTION "public"."add_contact_interaction_to_history"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."add_contact_interaction_to_history"() TO "service_role";



GRANT ALL ON FUNCTION "public"."assign_default_permissions"() TO "anon";
GRANT ALL ON FUNCTION "public"."assign_default_permissions"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."assign_default_permissions"() TO "service_role";



GRANT ALL ON FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) TO "service_role";



GRANT ALL ON FUNCTION "public"."cleanup_old_activities"() TO "anon";
GRANT ALL ON FUNCTION "public"."cleanup_old_activities"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."cleanup_old_activities"() TO "service_role";



GRANT ALL ON FUNCTION "public"."get_default_permissions_for_role"("role_name" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."get_default_permissions_for_role"("role_name" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_default_permissions_for_role"("role_name" "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."get_job_statistics"("p_business_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."get_job_statistics"("p_business_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_job_statistics"("p_business_id" "uuid") TO "service_role";



GRANT ALL ON FUNCTION "public"."get_next_job_number"("p_business_id" "uuid", "p_prefix" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."get_next_job_number"("p_business_id" "uuid", "p_prefix" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_next_job_number"("p_business_id" "uuid", "p_prefix" "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."log_job_activity"() TO "anon";
GRANT ALL ON FUNCTION "public"."log_job_activity"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."log_job_activity"() TO "service_role";



GRANT ALL ON FUNCTION "public"."mark_expired_invitations"() TO "anon";
GRANT ALL ON FUNCTION "public"."mark_expired_invitations"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."mark_expired_invitations"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_activity_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_activity_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_activity_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_businesses_last_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_businesses_last_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_businesses_last_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_contact_last_contacted"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_contact_last_contacted"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_contact_last_contacted"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_contact_status_history"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_contact_status_history"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_contact_status_history"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_departments_last_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_departments_last_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_departments_last_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_job_last_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_job_last_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_job_last_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_last_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_last_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_last_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_last_modified_column"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_last_modified_column"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_last_modified_column"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_overdue_activities"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_overdue_activities"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_overdue_activities"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_users_updated_at"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_users_updated_at"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_users_updated_at"() TO "service_role";



GRANT ALL ON FUNCTION "public"."user_has_permission"("user_permissions" "jsonb", "required_permission" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."user_has_permission"("user_permissions" "jsonb", "required_permission" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."user_has_permission"("user_permissions" "jsonb", "required_permission" "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."validate_assigned_to_users"("user_ids" "uuid"[]) TO "anon";
GRANT ALL ON FUNCTION "public"."validate_assigned_to_users"("user_ids" "uuid"[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."validate_assigned_to_users"("user_ids" "uuid"[]) TO "service_role";



GRANT ALL ON TABLE "public"."activities" TO "anon";
GRANT ALL ON TABLE "public"."activities" TO "authenticated";
GRANT ALL ON TABLE "public"."activities" TO "service_role";



GRANT ALL ON TABLE "public"."activity_participants" TO "anon";
GRANT ALL ON TABLE "public"."activity_participants" TO "authenticated";
GRANT ALL ON TABLE "public"."activity_participants" TO "service_role";



GRANT ALL ON TABLE "public"."activity_reminders" TO "anon";
GRANT ALL ON TABLE "public"."activity_reminders" TO "authenticated";
GRANT ALL ON TABLE "public"."activity_reminders" TO "service_role";



GRANT ALL ON TABLE "public"."activity_templates" TO "anon";
GRANT ALL ON TABLE "public"."activity_templates" TO "authenticated";
GRANT ALL ON TABLE "public"."activity_templates" TO "service_role";



GRANT ALL ON TABLE "public"."contacts" TO "anon";
GRANT ALL ON TABLE "public"."contacts" TO "authenticated";
GRANT ALL ON TABLE "public"."contacts" TO "service_role";



GRANT ALL ON TABLE "public"."activity_timeline_view" TO "anon";
GRANT ALL ON TABLE "public"."activity_timeline_view" TO "authenticated";
GRANT ALL ON TABLE "public"."activity_timeline_view" TO "service_role";



GRANT ALL ON TABLE "public"."availability_windows" TO "anon";
GRANT ALL ON TABLE "public"."availability_windows" TO "authenticated";
GRANT ALL ON TABLE "public"."availability_windows" TO "service_role";



GRANT ALL ON TABLE "public"."business_invitations" TO "anon";
GRANT ALL ON TABLE "public"."business_invitations" TO "authenticated";
GRANT ALL ON TABLE "public"."business_invitations" TO "service_role";



GRANT ALL ON TABLE "public"."business_memberships" TO "anon";
GRANT ALL ON TABLE "public"."business_memberships" TO "authenticated";
GRANT ALL ON TABLE "public"."business_memberships" TO "service_role";



GRANT ALL ON TABLE "public"."business_membership_permissions" TO "anon";
GRANT ALL ON TABLE "public"."business_membership_permissions" TO "authenticated";
GRANT ALL ON TABLE "public"."business_membership_permissions" TO "service_role";



GRANT ALL ON TABLE "public"."businesses" TO "anon";
GRANT ALL ON TABLE "public"."businesses" TO "authenticated";
GRANT ALL ON TABLE "public"."businesses" TO "service_role";



GRANT ALL ON TABLE "public"."calendar_events" TO "anon";
GRANT ALL ON TABLE "public"."calendar_events" TO "authenticated";
GRANT ALL ON TABLE "public"."calendar_events" TO "service_role";



GRANT ALL ON TABLE "public"."calendar_preferences" TO "anon";
GRANT ALL ON TABLE "public"."calendar_preferences" TO "authenticated";
GRANT ALL ON TABLE "public"."calendar_preferences" TO "service_role";



GRANT ALL ON TABLE "public"."contact_activities" TO "anon";
GRANT ALL ON TABLE "public"."contact_activities" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_activities" TO "service_role";



GRANT ALL ON TABLE "public"."contact_notes" TO "anon";
GRANT ALL ON TABLE "public"."contact_notes" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_notes" TO "service_role";



GRANT ALL ON TABLE "public"."contact_enhanced_summary" TO "anon";
GRANT ALL ON TABLE "public"."contact_enhanced_summary" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_enhanced_summary" TO "service_role";



GRANT ALL ON TABLE "public"."contact_segment_memberships" TO "anon";
GRANT ALL ON TABLE "public"."contact_segment_memberships" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_segment_memberships" TO "service_role";



GRANT ALL ON TABLE "public"."contact_segments" TO "anon";
GRANT ALL ON TABLE "public"."contact_segments" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_segments" TO "service_role";



GRANT ALL ON TABLE "public"."contact_summary" TO "anon";
GRANT ALL ON TABLE "public"."contact_summary" TO "authenticated";
GRANT ALL ON TABLE "public"."contact_summary" TO "service_role";



GRANT ALL ON TABLE "public"."departments" TO "anon";
GRANT ALL ON TABLE "public"."departments" TO "authenticated";
GRANT ALL ON TABLE "public"."departments" TO "service_role";



GRANT ALL ON TABLE "public"."job_activities" TO "anon";
GRANT ALL ON TABLE "public"."job_activities" TO "authenticated";
GRANT ALL ON TABLE "public"."job_activities" TO "service_role";



GRANT ALL ON TABLE "public"."job_attachments" TO "anon";
GRANT ALL ON TABLE "public"."job_attachments" TO "authenticated";
GRANT ALL ON TABLE "public"."job_attachments" TO "service_role";



GRANT ALL ON TABLE "public"."job_notes" TO "anon";
GRANT ALL ON TABLE "public"."job_notes" TO "authenticated";
GRANT ALL ON TABLE "public"."job_notes" TO "service_role";



GRANT ALL ON TABLE "public"."job_templates" TO "anon";
GRANT ALL ON TABLE "public"."job_templates" TO "authenticated";
GRANT ALL ON TABLE "public"."job_templates" TO "service_role";



GRANT ALL ON TABLE "public"."jobs" TO "anon";
GRANT ALL ON TABLE "public"."jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs" TO "service_role";



GRANT ALL ON TABLE "public"."time_off_requests" TO "anon";
GRANT ALL ON TABLE "public"."time_off_requests" TO "authenticated";
GRANT ALL ON TABLE "public"."time_off_requests" TO "service_role";



GRANT ALL ON TABLE "public"."user_capabilities" TO "anon";
GRANT ALL ON TABLE "public"."user_capabilities" TO "authenticated";
GRANT ALL ON TABLE "public"."user_capabilities" TO "service_role";



GRANT ALL ON TABLE "public"."user_certifications" TO "anon";
GRANT ALL ON TABLE "public"."user_certifications" TO "authenticated";
GRANT ALL ON TABLE "public"."user_certifications" TO "service_role";



GRANT ALL ON TABLE "public"."user_dashboard_activities" TO "anon";
GRANT ALL ON TABLE "public"."user_dashboard_activities" TO "authenticated";
GRANT ALL ON TABLE "public"."user_dashboard_activities" TO "service_role";



GRANT ALL ON TABLE "public"."user_skills" TO "anon";
GRANT ALL ON TABLE "public"."user_skills" TO "authenticated";
GRANT ALL ON TABLE "public"."user_skills" TO "service_role";



GRANT ALL ON TABLE "public"."users" TO "anon";
GRANT ALL ON TABLE "public"."users" TO "authenticated";
GRANT ALL ON TABLE "public"."users" TO "service_role";



GRANT ALL ON TABLE "public"."working_hours_templates" TO "anon";
GRANT ALL ON TABLE "public"."working_hours_templates" TO "authenticated";
GRANT ALL ON TABLE "public"."working_hours_templates" TO "service_role";



GRANT ALL ON TABLE "public"."workload_capacity" TO "anon";
GRANT ALL ON TABLE "public"."workload_capacity" TO "authenticated";
GRANT ALL ON TABLE "public"."workload_capacity" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";






RESET ALL;
