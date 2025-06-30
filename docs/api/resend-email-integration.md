# Resend Email Integration API Documentation

## Overview

Hero365 uses [Resend](https://resend.com) for professional email delivery. Resend provides excellent email deliverability, modern APIs, and comprehensive analytics for all email communications.

## Configuration

### Required Environment Variables

Add the following environment variables to your `.env` file:

```env
# Resend Configuration (Required)
RESEND_API_KEY=re_your_resend_api_key_here
DEFAULT_FROM_EMAIL=onboarding@hero365.app
DEFAULT_FROM_NAME=Hero365
```

### Resend Setup Steps

1. **Create Resend Account**: Sign up at [resend.com](https://resend.com)
2. **Generate API Key**: Create an API key in your Resend dashboard
3. **Verify Domain**: Add and verify your sending domain in Resend
4. **Configure Environment**: Set the `RESEND_API_KEY` environment variable

## Features

### Email Types Supported

The integration supports all existing email types:

- **Welcome Emails**: New user onboarding with Hero365 branding
- **Password Reset**: Secure password reset with expiring links
- **Email Verification**: Account verification emails
- **Notifications**: General business notifications
- **Template Emails**: Custom template-based emails

### Enhanced Features

#### Professional Email Templates
- Modern, responsive HTML email templates
- Consistent Hero365 branding
- Mobile-optimized layouts
- Fallback text versions

#### Improved Deliverability
- Better inbox placement rates
- Built-in spam prevention
- Domain reputation management
- Real-time delivery tracking

#### Email Tagging
- Automatic email categorization
- Performance tracking by email type
- Enhanced analytics capabilities

## API Interface

The email service maintains the same interface as before, ensuring backward compatibility:

```python
from app.infrastructure.config.dependency_injection import get_email_service

# Get email service (automatically uses Resend if configured)
email_service = get_email_service()

# Send welcome email
result = await email_service.send_welcome_email(
    to_email="user@example.com",
    user_name="John Doe",
    activation_link="https://hero365.app/activate?token=..."
)

# Send password reset email
result = await email_service.send_password_reset_email(
    to_email="user@example.com",
    user_name="John Doe",
    reset_link="https://hero365.app/reset?token=...",
    reset_token="secure_token"
)
```

## Error Handling

- All email sending operations return structured `EmailResult` objects
- Detailed error messages for troubleshooting
- Automatic retry logic for transient failures
- Comprehensive logging for monitoring

## Migration to Resend

No code changes required for existing email functionality. The system uses:

1. Resend for all email delivery
2. Professional email templates with Hero365 branding
3. Enhanced deliverability and analytics
4. Consistent error handling behavior

## Monitoring and Analytics

### Available Metrics
- Email delivery success rates
- Email open rates (when supported)
- Bounce and complaint tracking
- Performance by email type

### Logging
All email operations are logged with:
- Timestamp and recipient
- Email type and status
- Error details (if any)
- Delivery confirmation from Resend

## Best Practices

1. **Domain Setup**: Always verify your sending domain in Resend
2. **From Address**: Use a professional from address like `noreply@yourdomain.com`
3. **Content**: Ensure both HTML and text versions of emails
4. **Testing**: Test emails in different email clients
5. **Monitoring**: Monitor delivery rates and bounce rates regularly

## Troubleshooting

### Common Issues

**Invalid API Key**
```
Error: Resend API key is required. Set RESEND_API_KEY environment variable.
```
Solution: Verify API key is correctly set in environment variables.

**Domain Not Verified**
```
Error: Domain not verified in Resend
```
Solution: Verify your sending domain in the Resend dashboard.

**Rate Limiting**
```
Error: Rate limit exceeded
```
Solution: Implement exponential backoff or contact Resend support for higher limits.

## Support

For issues related to:
- **Hero365 Integration**: Contact development team
- **Resend Service**: Visit [Resend Documentation](https://resend.com/docs) or contact Resend support
- **Email Deliverability**: Check domain reputation and Resend analytics

---

*Last Updated: January 2024* 