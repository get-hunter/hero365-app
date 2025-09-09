#!/bin/bash

# Apply the new data model migration
# This script applies the trades and service types normalization

set -e

echo "🚀 Applying data model migration..."

# Change to project root
cd "$(dirname "$0")/.."

# Apply the migration using Supabase CLI
echo "📝 Applying migration: create_trades_and_service_types"
npx supabase db push

echo "✅ Migration applied successfully!"

# Optionally generate new TypeScript types
echo "🔧 Generating TypeScript types..."
npx supabase gen types typescript --local > website-builder/lib/types/supabase.ts

echo "🎉 Data model migration complete!"
echo ""
echo "Summary of changes:"
echo "- ✅ Created trades table with canonical trade categories"
echo "- ✅ Created service_types table (INSTALL, REPAIR, MAINTENANCE, etc.)"
echo "- ✅ Added trade_id, service_type_id to business_services"
echo "- ✅ Normalized service_areas schema (postal_code column)"
echo "- ✅ Created v_service_catalog view for optimized queries"
echo "- ✅ Updated backend API to use new normalized data"
echo "- ✅ Updated frontend to use trade-based categories"
echo ""
echo "🔍 You can now:"
echo "- Filter services by trade (HVAC, Plumbing, Electrical, etc.)"
echo "- Filter by service type (Install, Repair, Maintenance, etc.)"
echo "- Use consistent trade categories across the platform"
echo "- Query service areas efficiently by postal code"
