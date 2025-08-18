-- Drop legacy estimate_templates table if it still exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'estimate_templates'
    ) THEN
        -- Drop dependent foreign keys in estimates/invoices if they still reference estimate_templates
        -- These were updated to reference document_templates in a previous migration, but handle stale refs safely.
        BEGIN
            ALTER TABLE IF EXISTS public.estimates
            DROP CONSTRAINT IF EXISTS estimates_template_id_fkey;
        EXCEPTION WHEN others THEN
            -- ignore
        END;

        BEGIN
            ALTER TABLE IF EXISTS public.invoices
            DROP CONSTRAINT IF EXISTS invoices_template_id_fkey;
        EXCEPTION WHEN others THEN
            -- ignore
        END;

        -- Drop indexes and policies (if any)
        BEGIN
            DROP INDEX IF EXISTS public.idx_estimate_templates_business_id;
            DROP INDEX IF EXISTS public.idx_estimate_templates_type;
            DROP INDEX IF EXISTS public.idx_estimate_templates_active;
            DROP INDEX IF EXISTS public.idx_estimate_templates_default;
            DROP INDEX IF EXISTS public.idx_estimate_templates_business_active;
        EXCEPTION WHEN others THEN
            -- ignore
        END;

        BEGIN
            DROP POLICY IF EXISTS estimate_templates_business_isolation ON public.estimate_templates;
        EXCEPTION WHEN others THEN
            -- ignore
        END;

        -- Finally drop the table
        EXECUTE 'DROP TABLE IF EXISTS public.estimate_templates CASCADE';
    END IF;
END $$;
