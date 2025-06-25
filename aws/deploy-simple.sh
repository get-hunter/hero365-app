#!/bin/bash

# Hero365 Simple AWS Infrastructure Deployment
# This script sets up the basic AWS infrastructure needed for Hero365

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_REGION="us-east-1"
ACCOUNT_ID="886436939429"
CLUSTER_NAME="hero365-cluster"
SERVICE_NAME="hero365-backend"
REPO_NAME="hero365-backend"

echo "🚀 Hero365 Infrastructure Setup"
echo "==============================="
echo "Account ID: $ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo ""

# Function to check if resource exists
resource_exists() {
    local resource_type="$1"
    local resource_name="$2"
    
    case "$resource_type" in
        "cluster")
            aws ecs describe-clusters --clusters "$resource_name" --region "$AWS_REGION" --query 'clusters[0].status' --output text 2>/dev/null | grep -q "ACTIVE"
            ;;
        "repository")
            aws ecr describe-repositories --repository-names "$resource_name" --region "$AWS_REGION" >/dev/null 2>&1
            ;;
        "service")
            aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$resource_name" --region "$AWS_REGION" --query 'services[0].status' --output text 2>/dev/null | grep -q "ACTIVE"
            ;;
    esac
}

# Create ECR repository
create_ecr_repository() {
    echo "📦 Creating ECR repository..."
    
    if resource_exists "repository" "$REPO_NAME"; then
        echo "✅ ECR repository already exists"
    else
        aws ecr create-repository \
            --repository-name "$REPO_NAME" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        
        echo "✅ ECR repository created"
    fi
}

# Create ECS cluster
create_ecs_cluster() {
    echo "🏗️  Creating ECS cluster..."
    
    if resource_exists "cluster" "$CLUSTER_NAME"; then
        echo "✅ ECS cluster already exists"
    else
        aws ecs create-cluster \
            --cluster-name "$CLUSTER_NAME" \
            --capacity-providers FARGATE \
            --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
            --region "$AWS_REGION"
        
        echo "✅ ECS cluster created"
    fi
}

# Create CloudWatch log group
create_log_group() {
    echo "📝 Creating CloudWatch log group..."
    
    local log_group="/ecs/$SERVICE_NAME"
    
    if aws logs describe-log-groups --log-group-name-prefix "$log_group" --region "$AWS_REGION" --query 'logGroups[0].logGroupName' --output text 2>/dev/null | grep -q "$log_group"; then
        echo "✅ Log group already exists"
    else
        aws logs create-log-group \
            --log-group-name "$log_group" \
            --region "$AWS_REGION"
        
        # Set retention policy
        aws logs put-retention-policy \
            --log-group-name "$log_group" \
            --retention-in-days 30 \
            --region "$AWS_REGION"
        
        echo "✅ Log group created"
    fi
}

# Create IAM roles
create_iam_roles() {
    echo "🔐 Creating IAM roles..."
    
    # ECS Task Execution Role
    if aws iam get-role --role-name ecsTaskExecutionRole >/dev/null 2>&1; then
        echo "✅ ECS Task Execution Role already exists"
    else
        # Create trust policy
        cat > /tmp/ecs-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
        
        aws iam create-role \
            --role-name ecsTaskExecutionRole \
            --assume-role-policy-document file:///tmp/ecs-trust-policy.json
        
        aws iam attach-role-policy \
            --role-name ecsTaskExecutionRole \
            --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
        
        aws iam attach-role-policy \
            --role-name ecsTaskExecutionRole \
            --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
        
        echo "✅ ECS Task Execution Role created"
    fi
    
    # ECS Task Role
    if aws iam get-role --role-name ecsTaskRole >/dev/null 2>&1; then
        echo "✅ ECS Task Role already exists"
    else
        aws iam create-role \
            --role-name ecsTaskRole \
            --assume-role-policy-document file:///tmp/ecs-trust-policy.json
        
        # Create policy for task role
        cat > /tmp/ecs-task-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "*"
        }
    ]
}
EOF
        
        aws iam put-role-policy \
            --role-name ecsTaskRole \
            --policy-name SecretsManagerAccess \
            --policy-document file:///tmp/ecs-task-policy.json
        
        echo "✅ ECS Task Role created"
    fi
    
    # Clean up temp files
    rm -f /tmp/ecs-trust-policy.json /tmp/ecs-task-policy.json
}

# Create secrets in AWS Secrets Manager
create_secrets() {
    echo "🔒 Creating secrets in AWS Secrets Manager..."
    
    local prod_env="$SCRIPT_DIR/../environments/production.env"
    
    if [ ! -f "$prod_env" ]; then
        echo "❌ Production environment file not found: $prod_env"
        exit 1
    fi
    
    # Extract values from production.env
    SECRET_KEY=$(grep "^SECRET_KEY=" "$prod_env" | cut -d'=' -f2)
    SUPABASE_URL=$(grep "^SUPABASE_URL=" "$prod_env" | cut -d'=' -f2)
    SUPABASE_KEY=$(grep "^SUPABASE_KEY=" "$prod_env" | cut -d'=' -f2)
    SUPABASE_SERVICE_KEY=$(grep "^SUPABASE_SERVICE_KEY=" "$prod_env" | cut -d'=' -f2)
    
    # Create individual secrets
    create_secret "hero365/secret-key" "$SECRET_KEY"
    create_secret "hero365/supabase-url" "$SUPABASE_URL"
    create_secret "hero365/supabase-key" "$SUPABASE_KEY"
    create_secret "hero365/supabase-service-key" "$SUPABASE_SERVICE_KEY"
}

create_secret() {
    local secret_name="$1"
    local secret_value="$2"
    
    if aws secretsmanager describe-secret --secret-id "$secret_name" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "✅ Secret $secret_name already exists"
    else
        aws secretsmanager create-secret \
            --name "$secret_name" \
            --secret-string "$secret_value" \
            --region "$AWS_REGION" >/dev/null
        
        echo "✅ Secret $secret_name created"
    fi
}

# Register task definition
register_task_definition() {
    echo "📋 Registering ECS task definition..."
    
    local task_def_file="$SCRIPT_DIR/deployment/backend-task-definition.json"
    
    if [ ! -f "$task_def_file" ]; then
        echo "❌ Task definition file not found: $task_def_file"
        exit 1
    fi
    
    aws ecs register-task-definition \
        --cli-input-json file://"$task_def_file" \
        --region "$AWS_REGION" >/dev/null
    
    echo "✅ Task definition registered"
}

# Main deployment flow
main() {
    echo "Starting infrastructure setup..."
    echo ""
    
    create_ecr_repository
    create_ecs_cluster
    create_log_group
    create_iam_roles
    create_secrets
    register_task_definition
    
    echo ""
    echo "🎉 Infrastructure setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Run: ./aws/deployment/deploy-production.sh"
    echo "2. Configure your domain DNS to point to the load balancer"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    "ecr")
        create_ecr_repository
        ;;
    "cluster")
        create_ecs_cluster
        ;;
    "logs")
        create_log_group
        ;;
    "roles")
        create_iam_roles
        ;;
    "secrets")
        create_secrets
        ;;
    "task-def")
        register_task_definition
        ;;
    *)
        main
        ;;
esac 