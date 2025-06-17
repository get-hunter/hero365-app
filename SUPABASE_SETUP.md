# Supabase Integration Setup Guide

This guide will help you set up Supabase for your Hero365 application, replacing the local PostgreSQL database with Supabase's managed database and authentication system.

## Prerequisites

- Supabase account (sign up at [supabase.com](https://supabase.com))
- Access to your existing Hero365 application
- Node.js and Python environments set up

## Step 1: Create Supabase Project

1. **Sign in to Supabase Dashboard**
   - Go to [app.supabase.com](https://app.supabase.com)
   - Create a new project or use an existing one

2. **Get Project Credentials**
   - Go to Settings → API
   - Copy the following values:
     - `Project URL` (e.g., `https://your-project.supabase.co`)
     - `anon/public` key
     - `service_role` key (keep this secret!)

## Step 2: Environment Configuration

1. **Update your `.env` file** with Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Legacy PostgreSQL (optional for local development)
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
```

2. **Frontend Environment Variables**
   
Add to your frontend build process or `.env.local`:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key
```

## Step 3: Database Migration

### Option A: Fresh Setup (Recommended)

1. **Run Alembic migrations on Supabase**:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

2. **Create your first superuser**:
   ```bash
   uv run python -m app.initial_data
   ```

### Option B: Migrate Existing Data

1. **Export existing data**:
   ```bash
   # Export from local PostgreSQL
   pg_dump -h localhost -U postgres -d app > backup.sql
   ```

2. **Import to Supabase**:
   - Use Supabase Dashboard → SQL Editor
   - Run your migration scripts
   - Or use `psql` with Supabase connection string

## Step 4: Supabase Configuration

### Authentication Settings

1. **Go to Authentication → Settings in Supabase Dashboard**

2. **Configure Site URL**:
   - Add your frontend URL (e.g., `http://localhost:5173` for dev)
   - Add production URL

3. **Email Templates** (Optional):
   - Customize signup confirmation email
   - Customize password reset email

4. **Providers** (Optional):
   - Enable OAuth providers (Google, GitHub, etc.)

### Row Level Security (RLS)

1. **Enable RLS on user tables** (if needed):
   ```sql
   ALTER TABLE public.user ENABLE ROW LEVEL SECURITY;
   ALTER TABLE public.item ENABLE ROW LEVEL SECURITY;
   ```

2. **Create RLS policies**:
   ```sql
   -- Users can read their own data
   CREATE POLICY "Users can view own profile" ON public.user
   FOR SELECT USING (auth.uid()::text = id::text);
   
   -- Users can update their own data
   CREATE POLICY "Users can update own profile" ON public.user
   FOR UPDATE USING (auth.uid()::text = id::text);
   
   -- Users can access their own items
   CREATE POLICY "Users can view own items" ON public.item
   FOR SELECT USING (auth.uid()::text = owner_id::text);
   
   CREATE POLICY "Users can manage own items" ON public.item
   FOR ALL USING (auth.uid()::text = owner_id::text);
   ```

## Step 5: Testing the Integration

### Backend Testing

1. **Start the backend**:
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   ```

2. **Test Supabase connection**:
   - Check that the app starts without database errors
   - Test API endpoints at `http://localhost:8000/docs`

3. **Test authentication endpoints**:
   - `POST /api/v1/auth/signup` - Create account
   - `POST /api/v1/auth/signin` - Sign in (use frontend for this)
   - `GET /api/v1/users/me` - Get current user

### Frontend Testing

1. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test user flows**:
   - Sign up with email/password
   - Check email for verification (if enabled)
   - Sign in
   - Test password reset
   - Test user profile updates

## Step 6: Production Deployment

### Environment Variables

Ensure all production environments have:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

### Frontend Build

Update your build process to include Supabase environment variables:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
npm run build
```

### Docker Deployment

The Docker configuration has been updated to support Supabase. Use:

```bash
docker-compose up -d
```

## Features Enabled

### ✅ What's Working

- **Supabase Database**: PostgreSQL database hosted by Supabase
- **Supabase Authentication**: Email/password auth with JWT tokens
- **Backward Compatibility**: Legacy authentication still works
- **Auto User Creation**: Users created in local DB when they sign in via Supabase
- **Token Verification**: Both legacy and Supabase tokens are accepted
- **Password Reset**: Using Supabase's built-in email system
- **Real-time Ready**: Supabase client configured for real-time features

### 🔄 Migration Features

- **Dual Authentication**: Supports both legacy and Supabase auth
- **User ID Sync**: Existing users get Supabase IDs on first login
- **Database Fallback**: Falls back to local PostgreSQL if Supabase unavailable

### 🚀 Future Enhancements

- **Real-time Updates**: Add Supabase real-time subscriptions
- **File Storage**: Integrate Supabase Storage for file uploads
- **OAuth Providers**: Add Google, GitHub, etc. authentication
- **Edge Functions**: Use Supabase Edge Functions for serverless logic

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify SUPABASE_URL and SUPABASE_SERVICE_KEY
   - Check if your IP is whitelisted in Supabase (if required)

2. **Authentication Errors**:
   - Ensure SUPABASE_KEY is the anon/public key
   - Check Site URL in Supabase dashboard

3. **CORS Errors**:
   - Add your frontend URL to Supabase allowed origins
   - Check BACKEND_CORS_ORIGINS in your .env

4. **Migration Issues**:
   - Run migrations with Supabase connection string
   - Check table permissions and RLS policies

### Getting Help

- Check the [Supabase Documentation](https://supabase.com/docs)
- Review server logs for detailed error messages
- Test API endpoints using the FastAPI docs at `/docs`

## Security Considerations

1. **Never expose service_role key** in frontend code
2. **Use anon key** for frontend/client applications
3. **Enable RLS** for user data protection
4. **Validate tokens** on the backend before database operations
5. **Use HTTPS** in production for all Supabase communications

## Performance Tips

1. **Connection Pooling**: Supabase handles this automatically
2. **Query Optimization**: Use indexed columns for better performance
3. **Real-time Subscriptions**: Only subscribe to necessary data
4. **CDN**: Use Supabase's global CDN for better response times

---

Your Hero365 application is now integrated with Supabase! 🎉 