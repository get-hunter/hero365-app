#!/bin/bash

# Hero365 AWS Deployment Script
# This script sets up the complete AWS infrastructure for Hero365
# Note: Uses Supabase for database and authentication (no RDS needed)

set -e

# Configuration
AWS_REGION="us-east-1"
DOMAIN="hero365.ai"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Starting Hero365 AWS deployment..."
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "Domain: $DOMAIN"

# Step 1: Create ECR Repositories
echo "📦 Creating ECR repositories..."
aws ecr create-repository --repository-name hero365-backend --region $AWS_REGION || echo "Repository already exists"
aws ecr create-repository --repository-name hero365-frontend --region $AWS_REGION || echo "Repository already exists"

# Step 2: Create VPC and Networking
echo "🌐 Creating VPC and networking..."
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query Vpc.VpcId --output text)
# Add tags to VPC
aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=hero365-vpc
echo "VPC created: $VPC_ID"

# Create subnets
SUBNET_1=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a --query Subnet.SubnetId --output text)
SUBNET_2=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${AWS_REGION}b --query Subnet.SubnetId --output text)
SUBNET_3=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.3.0/24 --availability-zone ${AWS_REGION}a --query Subnet.SubnetId --output text)
SUBNET_4=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.4.0/24 --availability-zone ${AWS_REGION}b --query Subnet.SubnetId --output text)

# Tag subnets
aws ec2 create-tags --resources $SUBNET_1 --tags Key=Name,Value=hero365-public-1a
aws ec2 create-tags --resources $SUBNET_2 --tags Key=Name,Value=hero365-public-1b
aws ec2 create-tags --resources $SUBNET_3 --tags Key=Name,Value=hero365-private-1a
aws ec2 create-tags --resources $SUBNET_4 --tags Key=Name,Value=hero365-private-1b

echo "Subnets created: $SUBNET_1, $SUBNET_2, $SUBNET_3, $SUBNET_4"

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
aws ec2 create-tags --resources $IGW_ID --tags Key=Name,Value=hero365-igw

# Create Route Table for public subnets
RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --subnet-id $SUBNET_1 --route-table-id $RT_ID
aws ec2 associate-route-table --subnet-id $SUBNET_2 --route-table-id $RT_ID
aws ec2 create-tags --resources $RT_ID --tags Key=Name,Value=hero365-public-rt

echo "Internet Gateway and routing configured"

# Step 3: Create Security Groups
echo "🔒 Creating security groups..."
ALB_SG=$(aws ec2 create-security-group --group-name hero365-alb-sg --description "ALB Security Group" --vpc-id $VPC_ID --query GroupId --output text)
ECS_SG=$(aws ec2 create-security-group --group-name hero365-ecs-sg --description "ECS Security Group" --vpc-id $VPC_ID --query GroupId --output text)

# Configure ALB security group
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 443 --cidr 0.0.0.0/0

# Configure ECS security group
aws ec2 authorize-security-group-ingress --group-id $ECS_SG --protocol tcp --port 8000 --source-group $ALB_SG
aws ec2 authorize-security-group-ingress --group-id $ECS_SG --protocol tcp --port 80 --source-group $ALB_SG

echo "Security groups created: ALB=$ALB_SG, ECS=$ECS_SG"

# Step 4: Create ECS Cluster
echo "🐳 Creating ECS cluster..."
aws ecs create-cluster --cluster-name hero365-cluster --region $AWS_REGION

# Step 5: Create IAM Roles
echo "👤 Creating IAM roles..."
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}' || echo "Role already exists"
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam create-role --role-name ecsTaskRole --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}' || echo "Role already exists"

# Step 6: Create CloudWatch Log Groups
echo "📊 Creating CloudWatch log groups..."
aws logs create-log-group --log-group-name /ecs/hero365-backend --region $AWS_REGION || echo "Log group already exists"
aws logs create-log-group --log-group-name /ecs/hero365-frontend --region $AWS_REGION || echo "Log group already exists"

# Step 7: Store Secrets in AWS Secrets Manager
echo "🔐 Storing secrets in AWS Secrets Manager..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

aws secretsmanager create-secret --name hero365/secret-key --secret-string "$SECRET_KEY" --region $AWS_REGION || echo "Secret already exists"
aws secretsmanager create-secret --name hero365/supabase-url --secret-string "https://your-project.supabase.co" --region $AWS_REGION || echo "Secret already exists"
aws secretsmanager create-secret --name hero365/supabase-key --secret-string "your-supabase-anon-key" --region $AWS_REGION || echo "Secret already exists"
aws secretsmanager create-secret --name hero365/supabase-service-key --secret-string "your-supabase-service-key" --region $AWS_REGION || echo "Secret already exists"

# Step 8: Create Application Load Balancer
echo "⚖️ Creating Application Load Balancer..."
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name hero365-alb \
  --subnets $SUBNET_1 $SUBNET_2 \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --region $AWS_REGION \
  --query LoadBalancers[0].LoadBalancerArn --output text)

echo "ALB created: $ALB_ARN"

# Step 9: Create Target Groups
echo "🎯 Creating target groups..."
BACKEND_TG_ARN=$(aws elbv2 create-target-group \
  --name hero365-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /api/v1/utils/health-check/ \
  --region $AWS_REGION \
  --query TargetGroups[0].TargetGroupArn --output text)

FRONTEND_TG_ARN=$(aws elbv2 create-target-group \
  --name hero365-frontend-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path / \
  --region $AWS_REGION \
  --query TargetGroups[0].TargetGroupArn --output text)

echo "Target groups created: Backend=$BACKEND_TG_ARN, Frontend=$FRONTEND_TG_ARN"

# Step 10: Create Listeners
echo "🎧 Creating ALB listeners..."
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}' \
  --region $AWS_REGION

# Note: HTTPS listener requires SSL certificate - you'll need to create this manually
echo "⚠️  HTTPS listener requires SSL certificate. Please create one in ACM and update the listener."

# Step 11: Register Task Definitions
echo "📋 Registering task definitions..."
# Update task definition files with actual values
sed -i "s/AWS_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" aws/backend-task-definition.json
sed -i "s/AWS_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" aws/frontend-task-definition.json

aws ecs register-task-definition --cli-input-json file://aws/backend-task-definition.json --region $AWS_REGION
aws ecs register-task-definition --cli-input-json file://aws/frontend-task-definition.json --region $AWS_REGION

# Step 12: Create ECS Services
echo "🚀 Creating ECS services..."
aws ecs create-service \
  --cluster hero365-cluster \
  --service-name hero365-backend \
  --task-definition hero365-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_2],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=backend,containerPort=8000" \
  --region $AWS_REGION

aws ecs create-service \
  --cluster hero365-cluster \
  --service-name hero365-frontend \
  --task-definition hero365-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_2],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=$FRONTEND_TG_ARN,containerName=frontend,containerPort=80" \
  --region $AWS_REGION

echo "✅ AWS infrastructure setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update your domain DNS to point to the ALB"
echo "2. Create SSL certificate in ACM"
echo "3. Update HTTPS listener with certificate"
echo "4. Build and push Docker images to ECR"
echo "5. Update environment variables in task definitions"
echo ""
echo "🔗 Useful commands:"
echo "ALB DNS: $(aws elbv2 describe-load-balancers --names hero365-alb --query LoadBalancers[0].DNSName --output text)"
echo "ECS Cluster: hero365-cluster"
echo "ECR Repositories: hero365-backend, hero365-frontend" 