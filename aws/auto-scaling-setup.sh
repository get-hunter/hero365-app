#!/bin/bash

# Hero365 Auto-Scaling Setup Script
# Sets up auto-scaling policies for ECS Fargate services

set -e

AWS_REGION="us-east-1"
ECS_CLUSTER="hero365-cluster"
BACKEND_SERVICE="hero365-backend"
FRONTEND_SERVICE="hero365-frontend"

echo "🚀 Setting up auto-scaling for Hero365..."

# Function to create auto-scaling target
create_scaling_target() {
    local service_name=$1
    local min_capacity=$2
    local max_capacity=$3
    
    echo "Creating scaling target for $service_name..."
    
    aws application-autoscaling register-scalable-target \
        --service-namespace ecs \
        --scalable-dimension ecs:service:DesiredCount \
        --resource-id "service/$ECS_CLUSTER/$service_name" \
        --min-capacity $min_capacity \
        --max-capacity $max_capacity \
        --region $AWS_REGION
}

# Function to create CPU scaling policy
create_cpu_scaling_policy() {
    local service_name=$1
    local target_value=$2
    
    echo "Creating CPU scaling policy for $service_name..."
    
    aws application-autoscaling put-scaling-policy \
        --service-namespace ecs \
        --scalable-dimension ecs:service:DesiredCount \
        --resource-id "service/$ECS_CLUSTER/$service_name" \
        --policy-name "${service_name}-cpu-scaling" \
        --policy-type TargetTrackingScaling \
        --target-tracking-scaling-policy-configuration "{
            \"TargetValue\": $target_value,
            \"PredefinedMetricSpecification\": {
                \"PredefinedMetricType\": \"ECSServiceAverageCPUUtilization\"
            },
            \"ScaleOutCooldown\": 300,
            \"ScaleInCooldown\": 300
        }" \
        --region $AWS_REGION
}

# Function to create memory scaling policy
create_memory_scaling_policy() {
    local service_name=$1
    local target_value=$2
    
    echo "Creating memory scaling policy for $service_name..."
    
    aws application-autoscaling put-scaling-policy \
        --service-namespace ecs \
        --scalable-dimension ecs:service:DesiredCount \
        --resource-id "service/$ECS_CLUSTER/$service_name" \
        --policy-name "${service_name}-memory-scaling" \
        --policy-type TargetTrackingScaling \
        --target-tracking-scaling-policy-configuration "{
            \"TargetValue\": $target_value,
            \"PredefinedMetricSpecification\": {
                \"PredefinedMetricType\": \"ECSServiceAverageMemoryUtilization\"
            },
            \"ScaleOutCooldown\": 300,
            \"ScaleInCooldown\": 300
        }" \
        --region $AWS_REGION
}

# Function to create request-based scaling policy
create_request_scaling_policy() {
    local service_name=$1
    local target_group_arn=$2
    local target_value=$3
    
    echo "Creating request-based scaling policy for $service_name..."
    
    aws application-autoscaling put-scaling-policy \
        --service-namespace ecs \
        --scalable-dimension ecs:service:DesiredCount \
        --resource-id "service/$ECS_CLUSTER/$service_name" \
        --policy-name "${service_name}-request-scaling" \
        --policy-type TargetTrackingScaling \
        --target-tracking-scaling-policy-configuration "{
            \"TargetValue\": $target_value,
            \"PredefinedMetricSpecification\": {
                \"PredefinedMetricType\": \"ALBRequestCountPerTarget\",
                \"ResourceLabel\": \"$target_group_arn\"
            },
            \"ScaleOutCooldown\": 300,
            \"ScaleInCooldown\": 300
        }" \
        --region $AWS_REGION
}

# Get target group ARNs
echo "Getting target group ARNs..."
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
    --names hero365-backend-tg \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text \
    --region $AWS_REGION)

FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups \
    --names hero365-frontend-tg \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text \
    --region $AWS_REGION)

echo "Backend TG ARN: $BACKEND_TG_ARN"
echo "Frontend TG ARN: $FRONTEND_TG_ARN"

# Set up auto-scaling for backend service
echo "🔧 Setting up backend auto-scaling..."
create_scaling_target $BACKEND_SERVICE 2 20
create_cpu_scaling_policy $BACKEND_SERVICE 70.0
create_memory_scaling_policy $BACKEND_SERVICE 80.0
create_request_scaling_policy $BACKEND_SERVICE $BACKEND_TG_ARN 1000.0

# Set up auto-scaling for frontend service  
echo "🔧 Setting up frontend auto-scaling..."
create_scaling_target $FRONTEND_SERVICE 2 10
create_cpu_scaling_policy $FRONTEND_SERVICE 60.0
create_memory_scaling_policy $FRONTEND_SERVICE 70.0
create_request_scaling_policy $FRONTEND_SERVICE $FRONTEND_TG_ARN 2000.0

# Create CloudWatch alarms for monitoring
echo "📊 Creating CloudWatch alarms..."

# Backend CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Hero365-Backend-HighCPU" \
    --alarm-description "Backend CPU utilization > 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=ServiceName,Value=$BACKEND_SERVICE Name=ClusterName,Value=$ECS_CLUSTER \
    --region $AWS_REGION

# Backend memory alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Hero365-Backend-HighMemory" \
    --alarm-description "Backend memory utilization > 85%" \
    --metric-name MemoryUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=ServiceName,Value=$BACKEND_SERVICE Name=ClusterName,Value=$ECS_CLUSTER \
    --region $AWS_REGION

# Backend response time alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Hero365-Backend-HighResponseTime" \
    --alarm-description "Backend response time > 2 seconds" \
    --metric-name TargetResponseTime \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 300 \
    --threshold 2 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=TargetGroup,Value=$BACKEND_TG_ARN \
    --region $AWS_REGION

# Frontend CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Hero365-Frontend-HighCPU" \
    --alarm-description "Frontend CPU utilization > 70%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 70 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=ServiceName,Value=$FRONTEND_SERVICE Name=ClusterName,Value=$ECS_CLUSTER \
    --region $AWS_REGION

echo "✅ Auto-scaling setup complete!"
echo ""
echo "📊 Scaling Configuration Summary:"
echo "Backend Service:"
echo "  - Min Capacity: 2 tasks"
echo "  - Max Capacity: 20 tasks"
echo "  - CPU Target: 70%"
echo "  - Memory Target: 80%"
echo "  - Requests per task: 1000/min"
echo ""
echo "Frontend Service:"
echo "  - Min Capacity: 2 tasks"
echo "  - Max Capacity: 10 tasks"
echo "  - CPU Target: 60%"
echo "  - Memory Target: 70%"
echo "  - Requests per task: 2000/min"
echo ""
echo "🔔 CloudWatch Alarms Created:"
echo "  - Hero365-Backend-HighCPU (>80%)"
echo "  - Hero365-Backend-HighMemory (>85%)"
echo "  - Hero365-Backend-HighResponseTime (>2s)"
echo "  - Hero365-Frontend-HighCPU (>70%)"
echo ""
echo "📈 Monitor scaling at:"
echo "https://console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/$ECS_CLUSTER/services" 