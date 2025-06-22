

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


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pg_trgm" WITH SCHEMA "public";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






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


CREATE OR REPLACE FUNCTION "public"."update_businesses_last_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_businesses_last_modified"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_departments_last_modified"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.last_modified = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_departments_last_modified"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."business_invitations" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "business_name" character varying(255) NOT NULL,
    "invited_email" character varying(320),
    "invited_phone" character varying(20),
    "invited_by" "text" NOT NULL,
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
    CONSTRAINT "business_invitations_role_check" CHECK ((("role")::"text" = ANY ((ARRAY['owner'::character varying, 'admin'::character varying, 'manager'::character varying, 'employee'::character varying, 'contractor'::character varying, 'viewer'::character varying])::"text"[]))),
    CONSTRAINT "business_invitations_status_check" CHECK ((("status")::"text" = ANY ((ARRAY['pending'::character varying, 'accepted'::character varying, 'declined'::character varying, 'expired'::character varying, 'cancelled'::character varying])::"text"[])))
);


ALTER TABLE "public"."business_invitations" OWNER TO "postgres";


COMMENT ON TABLE "public"."business_invitations" IS 'Invitations for users to join business teams';



COMMENT ON COLUMN "public"."business_invitations"."permissions" IS 'Array of permission strings for the invited role';



CREATE TABLE IF NOT EXISTS "public"."business_memberships" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "user_id" "text" NOT NULL,
    "role" character varying(50) NOT NULL,
    "permissions" "jsonb" DEFAULT '[]'::"jsonb" NOT NULL,
    "joined_date" timestamp with time zone DEFAULT "now"() NOT NULL,
    "invited_date" timestamp with time zone,
    "invited_by" "text",
    "is_active" boolean DEFAULT true,
    "department_id" "uuid",
    "job_title" character varying(100),
    CONSTRAINT "business_memberships_permissions_not_empty" CHECK (("jsonb_array_length"("permissions") > 0)),
    CONSTRAINT "business_memberships_role_check" CHECK ((("role")::"text" = ANY ((ARRAY['owner'::character varying, 'admin'::character varying, 'manager'::character varying, 'employee'::character varying, 'contractor'::character varying, 'viewer'::character varying])::"text"[])))
);


ALTER TABLE "public"."business_memberships" OWNER TO "postgres";


COMMENT ON TABLE "public"."business_memberships" IS 'User memberships in businesses with roles and permissions';



COMMENT ON COLUMN "public"."business_memberships"."permissions" IS 'Array of permission strings for this membership';



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
    CONSTRAINT "businesses_company_size_check" CHECK ((("company_size")::"text" = ANY ((ARRAY['just_me'::character varying, 'small'::character varying, 'medium'::character varying, 'large'::character varying, 'enterprise'::character varying])::"text"[]))),
    CONSTRAINT "businesses_email_format" CHECK ((("business_email" IS NULL) OR (("business_email")::"text" ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::"text"))),
    CONSTRAINT "businesses_referral_source_check" CHECK ((("referral_source")::"text" = ANY ((ARRAY['tiktok'::character varying, 'tv'::character varying, 'online_ad'::character varying, 'web_search'::character varying, 'podcast_radio'::character varying, 'reddit'::character varying, 'review_sites'::character varying, 'youtube'::character varying, 'facebook_instagram'::character varying, 'referral'::character varying, 'other'::character varying])::"text"[]))),
    CONSTRAINT "businesses_website_format" CHECK ((("website" IS NULL) OR (("website")::"text" ~ '^https?://'::"text")))
);


ALTER TABLE "public"."businesses" OWNER TO "postgres";


COMMENT ON TABLE "public"."businesses" IS 'Core business entities with profile, settings, and subscription information';



COMMENT ON COLUMN "public"."businesses"."selected_features" IS 'Array of feature names selected during onboarding';



COMMENT ON COLUMN "public"."businesses"."primary_goals" IS 'Array of primary business goals';



COMMENT ON COLUMN "public"."businesses"."enabled_features" IS 'Array of currently enabled feature names';



CREATE TABLE IF NOT EXISTS "public"."departments" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "business_id" "uuid" NOT NULL,
    "name" character varying(255) NOT NULL,
    "description" "text",
    "manager_id" "text",
    "is_active" boolean DEFAULT true,
    "created_date" timestamp with time zone DEFAULT "now"(),
    "last_modified" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."departments" OWNER TO "postgres";


COMMENT ON TABLE "public"."departments" IS 'Organizational departments within businesses';



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



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_name_business_unique" UNIQUE ("business_id", "name");



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_pkey" PRIMARY KEY ("id");



CREATE INDEX "idx_business_invitations_business_id" ON "public"."business_invitations" USING "btree" ("business_id");



CREATE INDEX "idx_business_invitations_expiry_date" ON "public"."business_invitations" USING "btree" ("expiry_date");



CREATE INDEX "idx_business_invitations_invited_by" ON "public"."business_invitations" USING "btree" ("invited_by");



CREATE INDEX "idx_business_invitations_invited_email" ON "public"."business_invitations" USING "btree" ("invited_email");



CREATE INDEX "idx_business_invitations_invited_phone" ON "public"."business_invitations" USING "btree" ("invited_phone");



CREATE INDEX "idx_business_invitations_status" ON "public"."business_invitations" USING "btree" ("status");



CREATE INDEX "idx_business_memberships_business_id" ON "public"."business_memberships" USING "btree" ("business_id");



CREATE INDEX "idx_business_memberships_is_active" ON "public"."business_memberships" USING "btree" ("is_active");



CREATE INDEX "idx_business_memberships_joined_date" ON "public"."business_memberships" USING "btree" ("joined_date");



CREATE INDEX "idx_business_memberships_role" ON "public"."business_memberships" USING "btree" ("role");



CREATE INDEX "idx_business_memberships_user_id" ON "public"."business_memberships" USING "btree" ("user_id");



CREATE INDEX "idx_businesses_created_date" ON "public"."businesses" USING "btree" ("created_date");



CREATE INDEX "idx_businesses_industry" ON "public"."businesses" USING "btree" ("industry");



CREATE INDEX "idx_businesses_is_active" ON "public"."businesses" USING "btree" ("is_active");



CREATE INDEX "idx_businesses_name_gin" ON "public"."businesses" USING "gin" ("name" "public"."gin_trgm_ops");



CREATE INDEX "idx_businesses_owner_id" ON "public"."businesses" USING "btree" ("owner_id");



CREATE INDEX "idx_departments_business_id" ON "public"."departments" USING "btree" ("business_id");



CREATE INDEX "idx_departments_is_active" ON "public"."departments" USING "btree" ("is_active");



CREATE INDEX "idx_departments_manager_id" ON "public"."departments" USING "btree" ("manager_id");



CREATE OR REPLACE TRIGGER "businesses_update_last_modified" BEFORE UPDATE ON "public"."businesses" FOR EACH ROW EXECUTE FUNCTION "public"."update_businesses_last_modified"();



CREATE OR REPLACE TRIGGER "departments_update_last_modified" BEFORE UPDATE ON "public"."departments" FOR EACH ROW EXECUTE FUNCTION "public"."update_departments_last_modified"();



ALTER TABLE ONLY "public"."business_invitations"
    ADD CONSTRAINT "business_invitations_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."business_memberships"
    ADD CONSTRAINT "business_memberships_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."businesses"
    ADD CONSTRAINT "businesses_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."departments"
    ADD CONSTRAINT "departments_business_id_fkey" FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;





ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_in"("cstring") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_in"("cstring") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_in"("cstring") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_in"("cstring") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_out"("public"."gtrgm") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_out"("public"."gtrgm") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_out"("public"."gtrgm") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_out"("public"."gtrgm") TO "service_role";

























































































































































GRANT ALL ON FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."cleanup_expired_invitations"("days_old" integer) TO "service_role";



GRANT ALL ON FUNCTION "public"."gin_extract_query_trgm"("text", "internal", smallint, "internal", "internal", "internal", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gin_extract_query_trgm"("text", "internal", smallint, "internal", "internal", "internal", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gin_extract_query_trgm"("text", "internal", smallint, "internal", "internal", "internal", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gin_extract_query_trgm"("text", "internal", smallint, "internal", "internal", "internal", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gin_extract_value_trgm"("text", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gin_extract_value_trgm"("text", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gin_extract_value_trgm"("text", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gin_extract_value_trgm"("text", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gin_trgm_consistent"("internal", smallint, "text", integer, "internal", "internal", "internal", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gin_trgm_consistent"("internal", smallint, "text", integer, "internal", "internal", "internal", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gin_trgm_consistent"("internal", smallint, "text", integer, "internal", "internal", "internal", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gin_trgm_consistent"("internal", smallint, "text", integer, "internal", "internal", "internal", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gin_trgm_triconsistent"("internal", smallint, "text", integer, "internal", "internal", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gin_trgm_triconsistent"("internal", smallint, "text", integer, "internal", "internal", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gin_trgm_triconsistent"("internal", smallint, "text", integer, "internal", "internal", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gin_trgm_triconsistent"("internal", smallint, "text", integer, "internal", "internal", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_compress"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_compress"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_compress"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_compress"("internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_consistent"("internal", "text", smallint, "oid", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_consistent"("internal", "text", smallint, "oid", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_consistent"("internal", "text", smallint, "oid", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_consistent"("internal", "text", smallint, "oid", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_decompress"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_decompress"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_decompress"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_decompress"("internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_distance"("internal", "text", smallint, "oid", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_distance"("internal", "text", smallint, "oid", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_distance"("internal", "text", smallint, "oid", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_distance"("internal", "text", smallint, "oid", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_options"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_options"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_options"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_options"("internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_penalty"("internal", "internal", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_penalty"("internal", "internal", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_penalty"("internal", "internal", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_penalty"("internal", "internal", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_picksplit"("internal", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_picksplit"("internal", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_picksplit"("internal", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_picksplit"("internal", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_same"("public"."gtrgm", "public"."gtrgm", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_same"("public"."gtrgm", "public"."gtrgm", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_same"("public"."gtrgm", "public"."gtrgm", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_same"("public"."gtrgm", "public"."gtrgm", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."gtrgm_union"("internal", "internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."gtrgm_union"("internal", "internal") TO "anon";
GRANT ALL ON FUNCTION "public"."gtrgm_union"("internal", "internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."gtrgm_union"("internal", "internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."mark_expired_invitations"() TO "anon";
GRANT ALL ON FUNCTION "public"."mark_expired_invitations"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."mark_expired_invitations"() TO "service_role";



GRANT ALL ON FUNCTION "public"."set_limit"(real) TO "postgres";
GRANT ALL ON FUNCTION "public"."set_limit"(real) TO "anon";
GRANT ALL ON FUNCTION "public"."set_limit"(real) TO "authenticated";
GRANT ALL ON FUNCTION "public"."set_limit"(real) TO "service_role";



GRANT ALL ON FUNCTION "public"."show_limit"() TO "postgres";
GRANT ALL ON FUNCTION "public"."show_limit"() TO "anon";
GRANT ALL ON FUNCTION "public"."show_limit"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."show_limit"() TO "service_role";



GRANT ALL ON FUNCTION "public"."show_trgm"("text") TO "postgres";
GRANT ALL ON FUNCTION "public"."show_trgm"("text") TO "anon";
GRANT ALL ON FUNCTION "public"."show_trgm"("text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."show_trgm"("text") TO "service_role";



GRANT ALL ON FUNCTION "public"."similarity"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."similarity"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."similarity"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."similarity"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."similarity_dist"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."similarity_dist"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."similarity_dist"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."similarity_dist"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."similarity_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."similarity_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."similarity_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."similarity_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."strict_word_similarity"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."strict_word_similarity"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."strict_word_similarity"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strict_word_similarity"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."strict_word_similarity_commutator_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_commutator_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_commutator_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_commutator_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_commutator_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_commutator_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_commutator_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_commutator_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_dist_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."strict_word_similarity_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strict_word_similarity_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."update_businesses_last_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_businesses_last_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_businesses_last_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_departments_last_modified"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_departments_last_modified"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_departments_last_modified"() TO "service_role";



GRANT ALL ON FUNCTION "public"."word_similarity"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."word_similarity"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."word_similarity"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."word_similarity"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."word_similarity_commutator_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."word_similarity_commutator_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."word_similarity_commutator_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."word_similarity_commutator_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."word_similarity_dist_commutator_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."word_similarity_dist_commutator_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."word_similarity_dist_commutator_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."word_similarity_dist_commutator_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."word_similarity_dist_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."word_similarity_dist_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."word_similarity_dist_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."word_similarity_dist_op"("text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."word_similarity_op"("text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."word_similarity_op"("text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."word_similarity_op"("text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."word_similarity_op"("text", "text") TO "service_role";


















GRANT ALL ON TABLE "public"."business_invitations" TO "anon";
GRANT ALL ON TABLE "public"."business_invitations" TO "authenticated";
GRANT ALL ON TABLE "public"."business_invitations" TO "service_role";



GRANT ALL ON TABLE "public"."business_memberships" TO "anon";
GRANT ALL ON TABLE "public"."business_memberships" TO "authenticated";
GRANT ALL ON TABLE "public"."business_memberships" TO "service_role";



GRANT ALL ON TABLE "public"."businesses" TO "anon";
GRANT ALL ON TABLE "public"."businesses" TO "authenticated";
GRANT ALL ON TABLE "public"."businesses" TO "service_role";



GRANT ALL ON TABLE "public"."departments" TO "anon";
GRANT ALL ON TABLE "public"."departments" TO "authenticated";
GRANT ALL ON TABLE "public"."departments" TO "service_role";









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
