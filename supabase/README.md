# Supabase Local Development Setup

This directory contains the Supabase configuration for local development and production environments.

## Prerequisites

1. Install Supabase CLI:
   ```bash
   brew install supabase/tap/supabase
   # or
   npm install -g supabase
   ```

2. Docker Desktop (for local development)

## Environment Management

### Local Development Environment

1. **Start Local Supabase Stack:**
   ```bash
   supabase start
   ```
   
   This will start:
   - PostgreSQL database (port 54322)
   - Supabase API (port 54321)
   - Supabase Studio (port 54323)
   - Inbucket (email testing, port 54324)
   - Realtime server
   - Storage server

2. **Access Services:**
   - Supabase Studio: http://127.0.0.1:54323
   - API: http://127.0.0.1:54321
   - Database: postgresql://postgres:postgres@127.0.0.1:54322/postgres
   - Email Testing: http://127.0.0.1:54324

3. **Environment Variables for Local Development:**
   ```bash
   # Add to your backend/.env or root .env
   SUPABASE_URL=http://127.0.0.1:54321
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJlZmVyZW5jZS1pZCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjQ1NTUzNzU0LCJleHAiOjE5NjEwNDI5NTR9.OZPUi5HaT7n_h1HGqnmfMcWbBfGjO4mLVaHJVDOZ0do
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJlZmVyZW5jZS1pZCIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJpYXQiOjE2NDU1NTM3NTQsImV4cCI6MTk2MTA0Mjk1NH0.pNhwkdMF7gVn1nL_tCnwP8FZBZbkNJN2y3v7Z8Vj1nw
   ```

### Production Environment

1. **Link to Production Project:**
   ```bash
   supabase link --project-ref xflkldekhpqjpdrpeupg
   ```

2. **Pull Production Schema:**
   ```bash
   supabase db pull
   ```

### Staging Environment

1. **Create Staging Project:**
   - Go to https://supabase.com/dashboard
   - Create a new project for staging
   - Note the project reference ID

2. **Link to Staging:**
   ```bash
   supabase link --project-ref your-staging-project-ref
   ```

## Database Migrations

### Creating New Migrations

1. **Create a new migration:**
   ```bash
   supabase migration new migration_name
   ```

2. **Write your migration in the generated file:**
   ```sql
   -- Example: supabase/migrations/20240101000000_migration_name.sql
   CREATE TABLE IF NOT EXISTS example_table (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       name VARCHAR(255) NOT NULL,
       created_at TIMESTAMPTZ DEFAULT now()
   );
   ```

### Applying Migrations

1. **To Local Development:**
   ```bash
   supabase db reset  # Resets and applies all migrations
   # or
   supabase migration up  # Applies pending migrations
   ```

2. **To Production:**
   ```bash
   supabase db push --linked
   ```

3. **To Staging:**
   ```bash
   supabase link --project-ref your-staging-project-ref
   supabase db push --linked
   ```

### Migration Best Practices

1. **Always test migrations locally first**
2. **Use descriptive migration names**
3. **Include rollback instructions in comments**
4. **Use IF NOT EXISTS for safety**
5. **Never edit existing migrations once deployed**

## Schema Management

### Pulling Schema Changes

If someone makes changes directly in production (not recommended):

```bash
supabase db pull
```

This creates a new migration with the diff.

### Diffing Schemas

```bash
supabase db diff --linked
```

Shows differences between local and remote schemas.

## Seed Data

### Local Development Seeds

1. **Edit seed file:**
   ```bash
   # Edit supabase/seed.sql
   ```

2. **Apply seeds:**
   ```bash
   supabase db reset  # Applies migrations + seeds
   # or
   supabase seed
   ```

### Production Data

⚠️ **Never use seed files in production!** Use proper data migration scripts instead.

## Backup and Restore

### Backup Production Database

```bash
supabase db dump --linked > backup.sql
```

### Restore to Local

```bash
supabase db reset
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" < backup.sql
```

## Troubleshooting

### Common Issues

1. **Port Conflicts:**
   ```bash
   supabase stop
   supabase start
   ```

2. **Migration Conflicts:**
   ```bash
   supabase migration repair --status completed
   ```

3. **Reset Local Database:**
   ```bash
   supabase db reset
   ```

### Useful Commands

```bash
# Check status
supabase status

# View logs
supabase logs

# Stop all services
supabase stop

# List projects
supabase projects list

# Generate TypeScript types
supabase gen types typescript --linked > types/supabase.ts
```

## Multiple Environment Workflow

### Development Flow

1. **Local Development:**
   ```bash
   supabase start
   # Develop and test locally
   ```

2. **Create Migration:**
   ```bash
   supabase migration new add_feature_x
   # Edit the migration file
   ```

3. **Test Migration:**
   ```bash
   supabase db reset
   # Verify everything works
   ```

4. **Deploy to Staging:**
   ```bash
   supabase link --project-ref staging-project-ref
   supabase db push --linked
   ```

5. **Deploy to Production:**
   ```bash
   supabase link --project-ref xflkldekhpqjpdrpeupg
   supabase db push --linked
   ```

### Environment-Specific Configuration

Create separate config files for each environment:

- `supabase/config.local.toml`
- `supabase/config.staging.toml`
- `supabase/config.production.toml`

Use `--config` flag to specify:
```bash
supabase start --config supabase/config.local.toml
```

## Security Notes

1. **Never commit real credentials to version control**
2. **Use environment variables for sensitive data**
3. **Rotate keys regularly**
4. **Use service role keys only in backend**
5. **Implement proper RLS policies**

## Integration with Hero365 Backend

Your backend should use these environment variables:

```python
# backend/app/core/config.py
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")  
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
```

Local development:
```bash
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=<local-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<local-service-role-key>
```

Production:
```bash
SUPABASE_URL=https://xflkldekhpqjpdrpeupg.supabase.co
SUPABASE_ANON_KEY=<production-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<production-service-role-key>
``` 