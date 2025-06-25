#!/bin/bash

# Hero365 Migration Consolidation Script
# This script consolidates all existing migrations into a clean schema

set -e

echo "🔄 Starting Migration Consolidation Process..."

# Step 1: Backup existing migrations
echo "📁 Backing up existing migrations..."
mkdir -p supabase/migrations/backup
cp supabase/migrations/*.sql supabase/migrations/backup/ 2>/dev/null || true

# Step 2: Reset local database
echo "🗑️  Resetting local database..."
supabase db reset --local

# Step 3: Remove old migration files (but keep the clean one)
echo "🧹 Cleaning up old migration files..."
find supabase/migrations -name "*.sql" -not -name "20250124000000_clean_initial_schema.sql" -delete

# Step 4: Apply the clean migration
echo "🚀 Applying clean migration..."
supabase db reset --local

# Step 5: Verify schema
echo "✅ Verifying schema..."
supabase db dump --local -s public -f schema_verification.sql

echo "✨ Migration consolidation complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Review the new clean schema in 20250124000000_clean_initial_schema.sql"
echo "   2. Test your application with the new schema"
echo "   3. Update your models/entities to match the clean schema"
echo "   4. Push the consolidated migration to production when ready"
echo ""
echo "🔄 To push to production later:"
echo "   supabase db push" 