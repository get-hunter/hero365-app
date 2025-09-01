-- Fix missing foreign key constraints for template_id fields
-- These were accidentally dropped in the previous migration without being recreated

-- First, clean up invalid template_id references in invoices
UPDATE public.invoices 
SET template_id = NULL 
WHERE template_id IS NOT NULL 
AND template_id NOT IN (SELECT id FROM public.document_templates);

-- Clean up invalid template_id references in estimates  
UPDATE public.estimates 
SET template_id = NULL 
WHERE template_id IS NOT NULL 
AND template_id NOT IN (SELECT id FROM public.document_templates);

-- Now re-add foreign key constraint for invoices.template_id -> document_templates.id
ALTER TABLE public.invoices 
ADD CONSTRAINT invoices_template_id_fkey 
FOREIGN KEY (template_id) REFERENCES public.document_templates(id) ON DELETE SET NULL;

-- Re-add foreign key constraint for estimates.template_id -> document_templates.id
ALTER TABLE public.estimates 
ADD CONSTRAINT estimates_template_id_fkey 
FOREIGN KEY (template_id) REFERENCES public.document_templates(id) ON DELETE SET NULL;

-- Add comments for documentation
COMMENT ON CONSTRAINT invoices_template_id_fkey ON public.invoices IS 'Foreign key to document_templates table for invoice templates';
COMMENT ON CONSTRAINT estimates_template_id_fkey ON public.estimates IS 'Foreign key to document_templates table for estimate templates';
