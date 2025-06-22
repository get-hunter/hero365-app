# Hero365 AWS Deployment Guide

This guide explains how to deploy Hero365 to AWS production environment.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **AWS CLI configured** with appropriate permissions
2. **Docker** installed and running
3. **Domain registered** (hero365.ai) with access to DNS settings
4. **Supabase project** set up with database and auth
5. **Production environment variables** configured

## 🚀 Quick Deployment (First Time)

For a complete first-time deployment:

```bash
# 1. Setup environment
./scripts/setup-environment.sh setup-prod

# 2. Configure production variables
# Edit environments/production.env with your values

# 3. Validate configuration
./scripts/setup-environment.sh validate production

# 4. Deploy infrastructure
./aws/deploy-simple.sh

# 5. Build and push images
./scripts/build-and-deploy.sh

# 6. Setup custom domain and SSL
./aws/custom-domain-setup.sh
```

## 📂 Deployment Scripts Overview

### Core Deployment Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `aws/deploy-simple.sh` | Creates all AWS infrastructure | First deployment |
| `aws/deploy.sh` | Full deployment with tagging | Production with tags |
| `scripts/setup-environment.sh` | Environment management | Setup and validation |
| `aws/custom-domain-setup.sh` | SSL and domain setup | After infrastructure |

### Build and Push Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `scripts/build-push.sh` | Build and push containers | Code updates |
| Docker commands | Manual build/push | Development |

### Infrastructure Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `aws/auto-scaling-setup.sh` | Configure auto-scaling | After deployment |
| `aws/monitoring-dashboard.json` | CloudWatch dashboard | Monitoring setup |

## 🔧 Step-by-Step Deployment Process

### Step 1: Environment Setup

1. **Check current environment:**
   ```bash
   ./scripts/setup-environment.sh check
   ```

2. **Setup production environment:**
   ```bash
   ./scripts/setup-environment.sh setup-prod
   ```

3. **Edit production configuration:**
   ```bash
   nano environments/production.env
   ```
   
   Fill in these required values:
   - `SECRET_KEY` - Secure random key (auto-generated)
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Supabase anon key
   - `SUPABASE_SERVICE_KEY` - Supabase service role key
   - `FIRST_SUPERUSER` - Admin email
   - `FIRST_SUPERUSER_PASSWORD` - Admin password

4. **Validate configuration:**
   ```bash
   ./scripts/setup-environment.sh validate production
   ```

### Step 2: AWS Infrastructure Deployment

1. **Deploy infrastructure:**
   ```bash
   ./aws/deploy-simple.sh
   ```
   
   This creates:
   - VPC and networking
   - Security groups
   - ECS cluster
   - Application Load Balancer
   - Target groups
   - IAM roles
   - CloudWatch log groups

2. **Note the output values** (VPC ID, subnet IDs, security group IDs, etc.)

### Step 3: Build and Deploy Application

1. **Build and push Docker images:**
   ```bash
   # Backend only (current setup)
   docker buildx build --platform linux/amd64 -t $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/hero365-backend:latest -f backend/Dockerfile backend/ --push
   ```

2. **Register ECS task definitions:**
   ```bash
   aws ecs register-task-definition --cli-input-json file://aws/backend-task-definition.json --region us-east-1
   ```

3. **Create ECS services:**
   ```bash
   # Backend service
   aws ecs create-service \
     --cluster hero365-cluster \
     --service-name hero365-backend \
     --task-definition hero365-backend:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
     --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/hero365-backend-tg/xxx,containerName=backend,containerPort=8000" \
     --region us-east-1
   ```

### Step 4: Domain and SSL Setup

1. **Setup custom domain:**
   ```bash
   ./aws/custom-domain-setup.sh
   ```
   
   This handles:
   - Route 53 hosted zone creation
   - SSL certificate request
   - DNS validation
   - HTTPS listener setup
   - Domain DNS records

2. **Update nameservers** in your domain registrar with the Route 53 nameservers

### Step 5: Verification

1. **Check service health:**
   ```bash
   curl https://api.hero365.ai/health
   ```

2. **Test API endpoints:**
   ```bash
   curl https://api.hero365.ai/v1/utils/test-email/ -X POST -H "Content-Type: application/json" -d '{"email_to": "test@example.com"}'
   ```

## 🔄 Regular Deployment (Updates)

For code updates after initial deployment:

```bash
# 1. Build and push new image
docker buildx build --platform linux/amd64 -t $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/hero365-backend:latest -f backend/Dockerfile backend/ --push

# 2. Force new deployment
aws ecs update-service --cluster hero365-cluster --service hero365-backend --force-new-deployment --region us-east-1

# 3. Monitor deployment
aws ecs describe-services --cluster hero365-cluster --services hero365-backend --region us-east-1
```

## 📊 Monitoring and Scaling

### Auto-scaling Setup
```bash
./aws/auto-scaling-setup.sh
```

### CloudWatch Dashboard
The monitoring dashboard is automatically created with key metrics for:
- ECS service health
- ALB performance
- Error rates
- Response times

## 🔒 Security Considerations

1. **AWS Secrets Manager** stores sensitive configuration
2. **IAM roles** follow least privilege principle
3. **Security groups** restrict network access
4. **SSL/TLS** encryption for all traffic
5. **VPC** provides network isolation

## 🚨 Troubleshooting

### Common Issues

1. **Tasks failing to start:**
   - Check CloudWatch logs: `/ecs/hero365-backend`
   - Verify Secrets Manager permissions
   - Check image architecture (must be linux/amd64)

2. **Health checks failing:**
   - Verify health endpoint: `/health`
   - Check target group configuration
   - Review security group rules

3. **DNS not resolving:**
   - Verify nameservers updated at registrar
   - Check Route 53 hosted zone
   - Wait for DNS propagation (up to 48 hours)

### Useful Commands

```bash
# Check service status
aws ecs describe-services --cluster hero365-cluster --services hero365-backend --region us-east-1

# View logs
aws logs tail /ecs/hero365-backend --follow --region us-east-1

# Check target group health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/hero365-backend-tg/xxx --region us-east-1
```

## 📋 Environment Variables Reference

### Required Production Variables
```bash
ENVIRONMENT=production
PROJECT_NAME=Hero365
API_DOMAIN=api.hero365.ai
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
SECRET_KEY=your-generated-secret-key
FIRST_SUPERUSER=admin@hero365.ai
FIRST_SUPERUSER_PASSWORD=secure-password
```

### Optional Variables
```bash
SENTRY_DSN=https://xxx@sentry.io/xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=xxx
SMTP_PASSWORD=xxx
```

## 🎯 Production Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Domain nameservers updated
- [ ] SSL certificate validated
- [ ] Health checks passing
- [ ] API endpoints tested
- [ ] Monitoring dashboard configured
- [ ] Auto-scaling policies set
- [ ] Backup and disaster recovery planned
- [ ] Security review completed

## 💰 Cost Optimization

Current AWS resources and estimated costs:
- **ECS Fargate**: ~$25-50/month (2 tasks)
- **Application Load Balancer**: ~$18/month
- **Route 53**: ~$1/month
- **CloudWatch**: ~$5-10/month
- **Data Transfer**: Variable

Total estimated: **$50-80/month** for production workload.

## 📞 Support

For deployment issues:
1. Check CloudWatch logs
2. Review this guide
3. Consult AWS documentation
4. Check Hero365 project documentation 