# Intelligent Scheduling System Setup Guide

## Environment Variables Required

Add these variables to your `.env` file in the `environments/` folder:

### Google Maps API (Required for Real-time Route Optimization)

```bash
# Google Maps Platform API Key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

**How to get Google Maps API Key:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - **Distance Matrix API** (for travel time calculations)
   - **Directions API** (for route optimization)
   - **Maps JavaScript API** (optional, for frontend maps)
   - **Geocoding API** (optional, for address conversion)
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the API key and add it to your `.env` file
6. **Important**: Restrict the API key for security:
   - Set application restrictions (HTTP referrers for web)
   - Set API restrictions to only the APIs you enabled

**Pricing**: Google Maps Platform has a free tier with $200 monthly credit. Most small to medium businesses won't exceed this limit.

### Weather Service API (Required for Weather Impact Analysis)

```bash
# OpenWeatherMap API Key
WEATHER_API_KEY=your_openweathermap_api_key_here
```

**How to get OpenWeatherMap API Key:**

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Go to "API keys" in your account dashboard
4. Copy the default API key or create a new one
5. Add it to your `.env` file

**Pricing**: OpenWeatherMap has a free tier with 1,000 calls/day. For production use, consider upgrading to a paid plan.

### SMS Notifications (Optional - for schedule notifications)

```bash
# Twilio SMS Service (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

**How to get Twilio credentials:**

1. Go to [Twilio Console](https://console.twilio.com/)
2. Sign up for an account (free trial available)
3. Find your Account SID and Auth Token in the dashboard
4. Buy a phone number or use the trial number
5. Add credentials to your `.env` file

## Complete .env File Example

Here's what your `environments/.env` file should look like:

```bash
# Existing Hero365 configuration
PROJECT_NAME="Hero365"
ENVIRONMENT=local
SECRET_KEY=your_secret_key_here
FRONTEND_HOST=http://localhost:5173

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Email Configuration
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
EMAILS_FROM_EMAIL=noreply@hero365.ai
EMAILS_FROM_NAME=Hero365

# External Services for Intelligent Scheduling
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here

# Optional: SMS Notifications
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

## API Functionality Without Keys

The system is designed to work gracefully without API keys:

### Without Google Maps API Key:
- Falls back to Haversine formula for distance calculations
- Uses estimated travel times based on distance
- Still provides basic route optimization using nearest neighbor algorithm
- **Limitation**: No real-time traffic data or accurate travel times

### Without Weather API Key:
- Uses default weather conditions (clear, 20°C)
- No weather impact analysis
- All jobs treated as weather-safe
- **Limitation**: No weather-based schedule adjustments

### Without Twilio SMS:
- Notifications will be logged but not sent
- System continues to function normally
- **Limitation**: No SMS alerts for schedule changes

## Testing the Setup

Once you've added the API keys, test the system:

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Check the API documentation**:
   - Go to `http://localhost:8000/docs`
   - Look for the "Intelligent Scheduling" section
   - Test the `/scheduling/optimize` endpoint

3. **Test API key integration**:
   - Check logs for any API key warnings
   - Make a test scheduling optimization request
   - Verify external services are being called

## Cost Estimation

For a typical home services business with 50-100 jobs per day:

- **Google Maps API**: ~$50-100/month (well within free tier initially)
- **OpenWeatherMap**: Free tier sufficient for most use cases
- **Twilio SMS**: ~$0.0075 per SMS (very low cost)

**Total estimated cost**: $0-50/month for most small to medium businesses.

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment-specific .env files**
3. **Restrict Google Maps API key to your domains**
4. **Rotate API keys regularly**
5. **Monitor API usage in respective dashboards**

## Troubleshooting

### Common Issues:

1. **"Invalid API key" errors**:
   - Verify the API key is correct
   - Check if the required APIs are enabled
   - Ensure API key restrictions allow your server IP

2. **"Quota exceeded" errors**:
   - Check your API usage in the respective dashboards
   - Consider upgrading to a paid plan
   - Implement request caching to reduce API calls

3. **Import errors**:
   - Ensure all dependencies are installed
   - Check that the .env file is in the correct location
   - Restart the server after adding new environment variables

## Next Steps

After setting up the environment variables:

1. Test the scheduling optimization endpoints
2. Integrate with your frontend application
3. Monitor API usage and costs
4. Consider implementing caching for frequently accessed data
5. Set up monitoring and alerting for API failures

The intelligent scheduling system will provide significant value even with basic setup, and the external services will enhance the experience with real-time data and optimizations. 