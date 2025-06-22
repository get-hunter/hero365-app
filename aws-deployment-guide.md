# Hero365 AWS Deployment Guide

This guide will help you deploy Hero365 on AWS using ECS Fargate and Application Load Balancer, with Supabase as your database and authentication provider.

## Architecture Overview

```
Internet → Route 53 → Application Load Balancer → ECS Fargate Services
                                    ↓
                              Supabase (Database + Auth)
```

## Prerequisites

1. AWS CLI installed and configured
2. Domain name with DNS managed by Route 53
3. AWS credits ($5000) - this setup will cost ~$50-100/month

## AWS Services Used

- **ECS Fargate**: Container orchestration (serverless)
- **Application Load Balancer**: Traffic distribution and SSL termination
- **Route 53**: DNS management
- **ACM**: SSL certificates
- **ECR**: Container registry
- **CloudWatch**: Logging and monitoring
- **IAM**: Security and permissions
- **Supabase**: External database and authentication service

## Step 1: AWS Infrastructure Setup

### 1.1 Create ECR Repositories

```bash
# Create repositories for your containers
aws ecr create-repository --repository-name hero365-backend
aws ecr create-repository --repository-name hero365-frontend
```

### 1.2 Create VPC and Networking

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications ResourceType=vpc,Tags=[{Key=Name,Value=hero365-vpc}]

# Create subnets
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.3.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.4.0/24 --availability-zone us-east-1b
```

### 1.3 Create Security Groups

```bash
# ALB Security Group
aws ec2 create-security-group --group-name hero365-alb-sg --description "ALB Security Group" --vpc-id vpc-xxxxx
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# ECS Security Group
aws ec2 create-security-group --group-name hero365-ecs-sg --description "ECS Security Group" --vpc-id vpc-xxxxx
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 8000 --source-group sg-xxxxx
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 80 --source-group sg-xxxxx
```

## Step 2: Container Registry Setup

### 2.1 Build and Push Images

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag images
docker build -t hero365-backend ./backend
docker build -t hero365-frontend ./frontend

# Tag for ECR
docker tag hero365-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hero365-backend:latest
docker tag hero365-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hero365-frontend:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hero365-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hero365-frontend:latest
```

## Step 3: ECS Cluster and Services

### 3.1 Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name hero365-cluster
```

### 3.2 Create Task Definitions

Create `backend-task-definition.json`:

```json
{
  "family": "hero365-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hero365-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "PROJECT_NAME", "value": "Hero365"},
        {"name": "FRONTEND_HOST", "value": "https://dashboard.yourdomain.com"}
      ],
      "secrets": [
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:$AWS_ACCOUNT_ID:secret:hero365/secret-key"},
        {"name": "SUPABASE_URL", "valueFrom": "arn:aws:secretsmanager:us-east-1:$AWS_ACCOUNT_ID:secret:hero365/supabase-url"},
        {"name": "SUPABASE_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:$AWS_ACCOUNT_ID:secret:hero365/supabase-key"},
        {"name": "SUPABASE_SERVICE_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:$AWS_ACCOUNT_ID:secret:hero365/supabase-service-key"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hero365-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/utils/health-check/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

Create `frontend-task-definition.json`:

```json
{
  "family": "hero365-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hero365-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hero365-frontend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 3.3 Register Task Definitions

```bash
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json
```

## Step 4: Application Load Balancer

### 4.1 Create ALB

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name hero365-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx \
  --scheme internet-facing \
  --type application

# Create target groups
aws elbv2 create-target-group \
  --name hero365-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --target-type ip \
  --health-check-path /api/v1/utils/health-check/

aws elbv2 create-target-group \
  --name hero365-frontend-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-xxxxx \
  --target-type ip \
  --health-check-path /
```

### 4.2 Create Listeners

```bash
# HTTP listener (redirect to HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:$AWS_ACCOUNT_ID:loadbalancer/app/hero365-alb/xxxxx \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'

# HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:$AWS_ACCOUNT_ID:loadbalancer/app/hero365-alb/xxxxx \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:$AWS_ACCOUNT_ID:certificate/xxxxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:$AWS_ACCOUNT_ID:targetgroup/hero365-frontend-tg/xxxxx
```

## Step 5: ECS Services

### 5.1 Create Backend Service

```bash
aws ecs create-service \
  --cluster hero365-cluster \
  --service-name hero365-backend \
  --task-definition hero365-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx,subnet-yyyyy],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:$AWS_ACCOUNT_ID:targetgroup/hero365-backend-tg/xxxxx,containerName=backend,containerPort=8000"
```

### 5.2 Create Frontend Service

```bash
aws ecs create-service \
  --cluster hero365-cluster \
  --service-name hero365-frontend \
  --task-definition hero365-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx,subnet-yyyyy],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:$AWS_ACCOUNT_ID:targetgroup/hero365-frontend-tg/xxxxx,containerName=frontend,containerPort=80"
```

## Step 6: Route 53 and SSL

### 6.1 Create Hosted Zone

```bash
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)
```

### 6.2 Request SSL Certificate

```bash
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names "*.yourdomain.com" \
  --validation-method DNS
```

### 6.3 Create DNS Records

```bash
# Create A record for ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "yourdomain.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "dualstack.hero365-alb-xxxxx.us-east-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }
    ]
  }'
```

## Step 7: AWS Secrets Manager

### 7.1 Store Secrets

```bash
# Store sensitive configuration
aws secretsmanager create-secret --name hero365/secret-key --secret-string "your-generated-secret-key"
aws secretsmanager create-secret --name hero365/supabase-url --secret-string "https://your-project.supabase.co"
aws secretsmanager create-secret --name hero365/supabase-key --secret-string "your-supabase-anon-key"
aws secretsmanager create-secret --name hero365/supabase-service-key --secret-string "your-supabase-service-key"
```

## Step 8: CloudWatch Logs

### 8.1 Create Log Groups

```bash
aws logs create-log-group --log-group-name /ecs/hero365-backend
aws logs create-log-group --log-group-name /ecs/hero365-frontend
```

## Step 9: IAM Roles

### 9.1 Create ECS Task Execution Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step 10: GitHub Actions for AWS Deployment

Create `.github/workflows/deploy-aws.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY_BACKEND: hero365-backend
  ECR_REPOSITORY_FRONTEND: hero365-frontend
  ECS_CLUSTER: hero365-cluster
  ECS_SERVICE_BACKEND: hero365-backend
  ECS_SERVICE_FRONTEND: hero365-frontend

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
        
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2
      
    - name: Build and push backend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG ./backend
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG
        
    - name: Build and push frontend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG ./frontend
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG
        
    - name: Update ECS services
      run: |
        aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE_BACKEND --force-new-deployment
        aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE_FRONTEND --force-new-deployment
```

## Cost Estimation (Monthly)

- **ECS Fargate**: ~$30-50 (2 services, 2 tasks each)
- **Application Load Balancer**: ~$20
- **CloudWatch Logs**: ~$5-10
- **Route 53**: ~$1
- **Data Transfer**: ~$5-15
- **Total**: ~$60-100/month

**Note**: Supabase costs are separate (free tier available, then $25/month for Pro)

With $5000 AWS credits, this will last you **50-80 months** (4-6 years) for the AWS infrastructure!

## URLs After Deployment

- **Frontend**: `https://yourdomain.com`
- **API**: `https://api.yourdomain.com`
- **API Docs**: `https://api.yourdomain.com/docs`

## Monitoring and Scaling

### Auto Scaling

```bash
# Create auto scaling policies
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/hero365-cluster/hero365-backend \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/hero365-cluster/hero365-backend \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{"TargetValue": 70.0, "PredefinedMetricSpecification": {"PredefinedMetricType": "ECSServiceAverageCPUUtilization"}}'
```

### CloudWatch Alarms

```bash
# Create CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name hero365-backend-cpu-high \
  --alarm-description "High CPU utilization for backend service" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

## Security Best Practices

1. **Use IAM roles** instead of access keys
2. **Enable VPC Flow Logs** for network monitoring
3. **Use AWS WAF** for web application firewall
4. **Enable CloudTrail** for API logging
5. **Regular security updates** for container images
6. **Use AWS Secrets Manager** for sensitive data
7. **Enable encryption at rest** for all data
8. **Supabase RLS**: Enable Row Level Security policies in Supabase
9. **Supabase API keys**: Rotate Supabase keys regularly

## Troubleshooting

### Common Issues

1. **Service not starting**: Check ECS task logs in CloudWatch
2. **Health check failures**: Verify health check endpoint
3. **Container not reachable**: Check security groups and target groups
4. **SSL certificate issues**: Verify ACM certificate validation

### Useful Commands

```bash
# Check service status
aws ecs describe-services --cluster hero365-cluster --services hero365-backend

# View task logs
aws logs tail /ecs/hero365-backend --follow

# Scale service
aws ecs update-service --cluster hero365-cluster --service hero365-backend --desired-count 3
```

This AWS deployment provides a production-ready, scalable infrastructure for Hero365 with high availability, automatic scaling, and comprehensive monitoring. By using Supabase for database and authentication, you get a fully managed backend service while keeping your application logic on AWS ECS Fargate for maximum control and scalability. 