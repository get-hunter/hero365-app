# Hero365 Custom Domain Configuration

## Overview

This document explains how to configure Hero365 to serve the API at `api.hero365.ai/v1/...` in production while maintaining `localhost:8000/api/v1/...` for local development.

## Architecture

```
Production:  https://api.hero365.ai/v1/businesses
Local:       http://localhost:8000/api/v1/businesses
```

## Environment-Specific Configuration

### Local Development
- **API Prefix**: `/api/v1`
- **Base URL**: `http://localhost:8000/api/v1`
- **CORS**: Allows `http://localhost:5173` (frontend)

### Production
- **API Prefix**: `/v1`
- **Base URL**: `https://api.hero365.ai/v1`
- **CORS**: Allows `https://api.hero365.ai`, `https://hero365.ai`, etc.

## Setup Process

### 1. Domain Prerequisites

Before running the setup script, ensure you have:

1. **Domain Ownership**: Own the `hero365.ai` domain
2. **Route 53 Hosted Zone**: Create a hosted zone for `hero365.ai`
3. **DNS Configuration**: Point your domain's nameservers to Route 53

### 2. Create Route 53 Hosted Zone

```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name hero365.ai \
    --caller-reference $(date +%s)

# Get nameservers
aws route53 get-hosted-zone --id /hostedzone/YOUR_ZONE_ID
```

Update your domain registrar to use the Route 53 nameservers.

### 3. Deploy Infrastructure

First, deploy the basic AWS infrastructure:

```bash
# Deploy ECS, ALB, and other resources
./aws/deploy.sh
```

### 4. Setup Custom Domain

Run the custom domain setup script:

```bash
# Configure api.hero365.ai
./aws/custom-domain-setup.sh
```

This script will:
- Request an SSL certificate for `api.hero365.ai`
- Create DNS validation records
- Wait for certificate validation
- Add HTTPS listener to the Application Load Balancer
- Configure `/v1/*` routing rules
- Create Route 53 A record pointing to the ALB

### 5. Update Environment Variables

For production deployment, set:

```bash
export ENVIRONMENT=production
export API_DOMAIN=api.hero365.ai
```

## Backend Configuration Changes

### 1. Dynamic API Prefix

The API prefix now changes based on environment:

```python
@computed_field
@property
def API_V1_STR(self) -> str:
    """Get the API prefix based on environment."""
    if self.ENVIRONMENT == "production":
        return "/v1"  # Production uses custom domain api.hero365.ai/v1
    else:
        return "/api/v1"  # Local/staging uses /api/v1 prefix
```

### 2. Environment-Specific CORS

CORS origins are configured per environment:

```python
@computed_field
@property
def all_cors_origins(self) -> list[str]:
    cors_origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
        self.FRONTEND_HOST
    ]
    
    # Add custom domain to CORS origins for production only
    if self.ENVIRONMENT == "production":
        cors_origins.extend([
            f"https://{self.API_DOMAIN}",
            "https://hero365.ai",
            "https://www.hero365.ai",
            "https://app.hero365.ai"
        ])
    
    return cors_origins
```

### 3. Health Check Endpoint

Added a health check endpoint outside the API prefix:

```python
@application.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
```

## Load Balancer Configuration

### HTTP Listener (Port 80)
- Redirects all traffic to HTTPS

### HTTPS Listener (Port 443)
- **Default Action**: Forward to backend target group
- **Rule Priority 100**: `/v1/*` → Backend target group
- **SSL Certificate**: Auto-managed by ACM

## DNS Configuration

### Route 53 Records

```
api.hero365.ai.    A    ALIAS    hero365-alb-123456789.us-east-1.elb.amazonaws.com
```

## Testing

### 1. Health Check
```bash
curl https://api.hero365.ai/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

### 2. API Endpoints
```bash
# Test authentication
curl https://api.hero365.ai/v1/auth/signup

# Test businesses endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.hero365.ai/v1/businesses
```

### 3. OpenAPI Documentation
Visit: `https://api.hero365.ai/v1/docs`

## SSL Certificate Management

### Automatic Renewal
- ACM automatically renews certificates
- No manual intervention required

### Certificate Validation
- Uses DNS validation
- Validation records created automatically in Route 53

## Monitoring

### CloudWatch Metrics
- **ALB Request Count**: Monitor API usage
- **Target Response Time**: Track performance
- **HTTP Status Codes**: Monitor errors

### Custom Metrics
```python
# Track API calls by endpoint
await cloudwatch.putMetricData({
    'Namespace': 'Hero365/API',
    'MetricData': [{
        'MetricName': 'RequestCount',
        'Value': 1,
        'Dimensions': [{
            'Name': 'Endpoint',
            'Value': '/v1/businesses'
        }]
    }]
})
```

## Troubleshooting

### Common Issues

1. **Certificate Validation Timeout**
   - Check DNS propagation: `dig api.hero365.ai`
   - Verify Route 53 hosted zone is active
   - Wait 5-10 minutes for DNS propagation

2. **CORS Errors**
   - Verify `ENVIRONMENT=production` is set
   - Check CORS origins in CloudWatch logs
   - Ensure frontend uses `https://api.hero365.ai`

3. **404 Errors**
   - Verify ALB listener rules are configured
   - Check target group health
   - Confirm ECS tasks are running

### Debug Commands

```bash
# Check certificate status
aws acm describe-certificate --certificate-arn YOUR_CERT_ARN

# Check ALB listeners
aws elbv2 describe-listeners --load-balancer-arn YOUR_ALB_ARN

# Check target group health
aws elbv2 describe-target-health --target-group-arn YOUR_TG_ARN

# Check Route 53 records
aws route53 list-resource-record-sets --hosted-zone-id YOUR_ZONE_ID
```

## Security Considerations

### 1. HTTPS Only
- All traffic encrypted with TLS 1.2+
- HTTP automatically redirects to HTTPS

### 2. CORS Configuration
- Strict origin validation
- Environment-specific origins

### 3. Rate Limiting
Consider adding rate limiting at the ALB level:

```bash
# Create WAF rule for rate limiting
aws wafv2 create-rule-group \
    --name hero365-rate-limit \
    --scope REGIONAL \
    --capacity 100
```

## Cost Optimization

### 1. ALB Costs
- **Fixed**: ~$16/month for ALB
- **Variable**: $0.008 per LCU-hour

### 2. Route 53 Costs
- **Hosted Zone**: $0.50/month
- **Queries**: $0.40 per million queries

### 3. ACM Certificate
- **Free**: SSL certificates are free with ACM

## Migration Strategy

### From Development to Production

1. **Deploy Infrastructure**: Run `./aws/deploy.sh`
2. **Setup Domain**: Run `./aws/custom-domain-setup.sh`
3. **Update Environment**: Set `ENVIRONMENT=production`
4. **Test Endpoints**: Verify all API routes work
5. **Update Frontend**: Point to `https://api.hero365.ai/v1`

### Rollback Plan

If issues occur:
1. Set `ENVIRONMENT=staging`
2. Use ALB DNS name directly
3. Revert frontend to staging URL
4. Debug and fix issues
5. Re-deploy with `ENVIRONMENT=production`

This configuration ensures Hero365 has a professional API domain in production while maintaining easy local development. 