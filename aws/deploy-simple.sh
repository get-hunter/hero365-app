#!/bin/bash

# Hero365 AWS Deployment Script (Simplified)
# This script sets up the complete AWS infrastructure for Hero365 without tagging

set -e

# Configuration
AWS_REGION="us-east-1"
DOMAIN="hero365.ai"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Starting Hero365 AWS deployment (simplified)..."
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "Domain: $DOMAIN"

# Step 1: Create ECR Repositories (already exist, skip)
echo "📦 ECR repositories already exist, continuing..."

# Step 2: Create VPC and Networking
echo "🌐 Creating VPC and networking..."
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query Vpc.VpcId --output text)
echo "VPC created: $VPC_ID"

# Create subnets
SUBNET_1=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a --query Subnet.SubnetId --output text)
SUBNET_2=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${AWS_REGION}b --query Subnet.SubnetId --output text)

echo "Subnets created: $SUBNET_1, $SUBNET_2"

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

# Create Route Table for public subnets
RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --subnet-id $SUBNET_1 --route-table-id $RT_ID
aws ec2 associate-route-table --subnet-id $SUBNET_2 --route-table-id $RT_ID

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

# Step 7: Create Application Load Balancer
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

# Step 8: Create Target Groups
echo "🎯 Creating target groups..."
BACKEND_TG_ARN=$(aws elbv2 create-target-group \
  --name hero365-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /health \
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

# Step 9: Create HTTP Listener (HTTPS will be added with custom domain)
echo "🎧 Creating ALB listeners..."
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
  --region $AWS_REGION

echo "✅ Basic AWS infrastructure setup complete!"
echo ""
echo "📋 Infrastructure Summary:"
echo "VPC ID: $VPC_ID"
echo "Subnets: $SUBNET_1, $SUBNET_2"
echo "ALB Security Group: $ALB_SG"
echo "ECS Security Group: $ECS_SG"
echo "ALB ARN: $ALB_ARN"
echo "Backend Target Group: $BACKEND_TG_ARN"
echo "Frontend Target Group: $FRONTEND_TG_ARN"
echo ""
echo "🔗 ALB DNS Name:"
aws elbv2 describe-load-balancers --names hero365-alb --query LoadBalancers[0].DNSName --output text
echo ""
echo "📋 Next steps:"
echo "1. Build and push Docker images to ECR"
echo "2. Create ECS task definitions"
echo "3. Create ECS services"
echo "4. Setup custom domain with SSL" 