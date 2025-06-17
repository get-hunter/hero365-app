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

## Step 4: Supabase Authentication Configuration

### Basic Authentication Settings

1. **Go to Authentication → Settings in Supabase Dashboard**

2. **Configure Site URL**:
   - Add your frontend URL (e.g., `http://localhost:5173` for dev)
   - Add production URL

3. **Email Templates** (Optional):
   - Customize signup confirmation email
   - Customize password reset email

### OAuth Provider Setup

#### Google OAuth

1. **Create Google OAuth App**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Set application type to "Web application"
   - Add authorized redirect URIs:
     - `https://your-project.supabase.co/auth/v1/callback`
     - `http://localhost:5173` (for development)

2. **Configure in Supabase**:
   - Go to Authentication → Providers in Supabase Dashboard
   - Enable Google provider
   - Add your Google Client ID and Client Secret
   - Set redirect URL: `https://your-project.supabase.co/auth/v1/callback`

#### Apple OAuth

1. **Create Apple App**:
   - Go to [Apple Developer Console](https://developer.apple.com/)
   - Create a new App ID or use existing one
   - Enable "Sign In with Apple" capability
   - Create a Services ID for web authentication
   - Configure domains and redirect URLs:
     - Domain: `your-project.supabase.co`
     - Redirect URL: `https://your-project.supabase.co/auth/v1/callback`

2. **Generate Key**:
   - Create a new Key for "Sign In with Apple"
   - Download the .p8 key file

3. **Configure in Supabase**:
   - Go to Authentication → Providers in Supabase Dashboard
   - Enable Apple provider
   - Add your Apple Team ID, Key ID, and Private Key

#### GitHub OAuth (Optional)

1. **Create GitHub OAuth App**:
   - Go to GitHub Settings → Developer settings → OAuth Apps
   - Create a new OAuth App
   - Set Authorization callback URL: `https://your-project.supabase.co/auth/v1/callback`

2. **Configure in Supabase**:
   - Go to Authentication → Providers
   - Enable GitHub provider
   - Add Client ID and Client Secret

### Phone Authentication Setup

1. **Enable Phone Authentication**:
   - Go to Authentication → Settings in Supabase Dashboard
   - Enable "Enable phone confirmations"

2. **Configure SMS Provider**:
   - **Option A: Twilio**
     - Sign up for Twilio account
     - Get Account SID and Auth Token
     - Purchase a phone number
     - Add Twilio credentials in Supabase Settings

   - **Option B: MessageBird**
     - Sign up for MessageBird account
     - Get API key
     - Add MessageBird credentials in Supabase Settings

3. **Phone Number Format**:
   - Use international format: `+1234567890`
   - Validate phone numbers in your frontend

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
   - `POST /api/v1/auth/signup` - Email/password signup
   - `POST /api/v1/auth/signup/phone` - Phone/password signup
   - `POST /api/v1/auth/signin` - Email/password signin
   - `POST /api/v1/auth/signin/phone` - Phone/password signin
   - `POST /api/v1/auth/otp/send` - Send OTP to phone
   - `POST /api/v1/auth/otp/verify` - Verify OTP
   - `GET /api/v1/auth/oauth/{provider}` - OAuth URL generation
   - `GET /api/v1/users/me` - Get current user

### Frontend Testing

1. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test authentication flows**:
   - Email/password signup and signin
   - Phone/password signup and signin
   - Phone OTP authentication
   - Google OAuth signin
   - Apple OAuth signin
   - GitHub OAuth signin (if enabled)
   - Test password reset
   - Test user profile updates

## Step 6: Postman Testing Guide

### Email/Password Authentication

#### Signup
```
POST http://localhost:8000/api/v1/auth/signup
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "SecurePassword123!",
  "full_name": "Test User"
}
```

#### Signin
```
POST http://localhost:8000/api/v1/auth/signin
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "SecurePassword123!"
}
```

### Phone Authentication

#### Phone Signup
```
POST http://localhost:8000/api/v1/auth/signup/phone
Content-Type: application/json

{
  "phone": "+1234567890",
  "password": "SecurePassword123!",
  "full_name": "Test User"
}
```

#### Phone Signin
```
POST http://localhost:8000/api/v1/auth/signin/phone
Content-Type: application/json

{
  "phone": "+1234567890",
  "password": "SecurePassword123!"
}
```

#### Send OTP
```
POST http://localhost:8000/api/v1/auth/otp/send
Content-Type: application/json

{
  "phone": "+1234567890"
}
```

#### Verify OTP
```
POST http://localhost:8000/api/v1/auth/otp/verify
Content-Type: application/json

{
  "phone": "+1234567890",
  "token": "123456"
}
```

### OAuth Authentication

#### Get OAuth URL
```
GET http://localhost:8000/api/v1/auth/oauth/google
GET http://localhost:8000/api/v1/auth/oauth/apple
GET http://localhost:8000/api/v1/auth/oauth/github
```

### Using Authentication Token

For protected endpoints, add the Bearer token:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 7: Production Deployment

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

### ✅ Authentication Methods

- **Email/Password**: Traditional email and password authentication
- **Phone/Password**: Phone number and password authentication
- **Phone/OTP**: Passwordless authentication using SMS OTP
- **Google OAuth**: Sign in with Google account
- **Apple OAuth**: Sign in with Apple ID
- **GitHub OAuth**: Sign in with GitHub account (optional)

### ✅ Backend Features

- **Supabase Database**: PostgreSQL database hosted by Supabase
- **JWT Token Verification**: Both legacy and Supabase tokens accepted
- **Auto User Creation**: Users created in local DB when they sign in via Supabase
- **Password Reset**: Using Supabase's built-in email system
- **User Management**: Admin endpoints for user management

### ✅ Frontend Features

- **Unified Auth Hook**: Single hook managing all authentication methods
- **OAuth Integration**: Seamless OAuth provider integration
- **Phone Authentication**: Complete phone auth UI with OTP verification
- **Responsive Design**: Mobile-friendly authentication forms
- **Error Handling**: Comprehensive error handling and user feedback

### 🔄 Migration Features

- **Dual Authentication**: Supports both legacy and Supabase auth
- **Gradual Migration**: Can migrate users gradually from legacy to Supabase
- **Backward Compatibility**: Existing users continue to work

## Security Considerations

1. **Environment Variables**: Keep service role key secret
2. **RLS Policies**: Implement proper row-level security
3. **CORS Configuration**: Configure allowed origins properly
4. **Rate Limiting**: Consider implementing rate limiting for auth endpoints
5. **Phone Verification**: Always verify phone numbers before allowing access
6. **OAuth Scopes**: Request minimal necessary OAuth scopes

## Troubleshooting

### Common Issues

1. **OAuth Not Working**:
   - Check redirect URLs match exactly
   - Verify client credentials
   - Check Supabase provider configuration

2. **Phone Auth Not Working**:
   - Verify SMS provider configuration
   - Check phone number format (+country code)
   - Ensure sufficient SMS credits

3. **Database Connection Issues**:
   - Verify Supabase URL and keys
   - Check database migration status
   - Review connection string format

4. **CORS Errors**:
   - Add frontend domain to Supabase allowed origins
   - Check CORS middleware configuration

### Support

- Supabase Documentation: [docs.supabase.com](https://docs.supabase.com)
- Community Support: [supabase.com/support](https://supabase.com/support)
- GitHub Issues: Create issues in your repository for project-specific problems

---

Your Hero365 application is now integrated with Supabase! 🎉 