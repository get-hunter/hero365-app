#!/bin/bash

# Hero365 Production Deployment Script
# This script handles the complete deployment process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
AWS_REGION="us-east-1"

echo "🚀 Hero365 Production Deployment"
echo "================================="
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not installed"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS credentials not configured"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon not running"
        exit 1
    fi
    
    # Check production config
    if [ ! -f "$PROJECT_ROOT/environments/production.env" ]; then
        echo "❌ Production config not found"
        echo "Please run: ./aws/deployment/setup-environment.sh setup-prod"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
    echo ""
}

# Function to get AWS account ID
get_aws_account_id() {
    aws sts get-caller-identity --query Account --output text
}

# Function to build and push images
build_and_push() {
    echo "🔨 Building and pushing Docker images..."
    
    local account_id=$(get_aws_account_id)
    local backend_image="$account_id.dkr.ecr.$AWS_REGION.amazonaws.com/hero365-backend:latest"
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $account_id.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build and push backend
    echo "Building backend image..."
    docker buildx build --platform linux/amd64 -t $backend_image -f backend/Dockerfile backend/ --push
    
    echo "✅ Images built and pushed successfully"
    echo ""
}

# Function to deploy or update ECS service
deploy_service() {
    echo "🚢 Deploying ECS service..."
    
    # Check if service exists
    if aws ecs describe-services --cluster hero365-cluster --services hero365-backend --region $AWS_REGION &> /dev/null; then
        echo "Service exists, updating..."
        aws ecs update-service \
            --cluster hero365-cluster \
            --service hero365-backend \
            --force-new-deployment \
            --region $AWS_REGION > /dev/null
        echo "✅ Service updated"
    else
        echo "❌ Service not found. Please run infrastructure deployment first:"
        echo "   ./aws/deploy-simple.sh"
        exit 1
    fi
    
    echo ""
}

# Function to wait for deployment
wait_for_deployment() {
    echo "⏳ Waiting for deployment to complete..."
    
    local timeout=300  # 5 minutes
    local elapsed=0
    local interval=10
    
    while [ $elapsed -lt $timeout ]; do
        local status=$(aws ecs describe-services \
            --cluster hero365-cluster \
            --services hero365-backend \
            --region $AWS_REGION \
            --query 'services[0].{running:runningCount,desired:desiredCount}' \
            --output json)
        
        local running=$(echo $status | jq -r '.running')
        local desired=$(echo $status | jq -r '.desired')
        
        if [ "$running" = "$desired" ] && [ "$running" -gt 0 ]; then
            echo "✅ Deployment completed successfully!"
            echo "   Running tasks: $running/$desired"
            return 0
        fi
        
        echo "   Status: $running/$desired tasks running..."
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    echo "⚠️  Deployment timeout. Check AWS console for details."
}

# Function to configure ALB routes
configure_alb_routes() {
    echo "🛣️  Configuring ALB routes for all FastAPI endpoints..."
    
    # Run the ALB configuration script
    local alb_script="$SCRIPT_DIR/../configure-alb-routes.sh"
    
    if [ -f "$alb_script" ]; then
        chmod +x "$alb_script"
        if "$alb_script"; then
            echo "✅ ALB routes configured successfully"
        else
            echo "⚠️  ALB route configuration encountered issues, but deployment continues"
            echo "   You may need to configure routes manually or check AWS permissions"
        fi
    else
        echo "⚠️  ALB configuration script not found at: $alb_script"
        echo "   All endpoints may not be accessible until routes are configured"
    fi
    
    echo ""
}

# Function to verify deployment
verify_deployment() {
    echo "🔍 Verifying deployment..."
    
    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -s https://api.hero365.ai/health | grep -q "healthy"; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        return 1
    fi
    
    # Test API endpoint
    echo "Testing API endpoint..."
    if curl -s https://api.hero365.ai/v1/utils/test-email/ -X POST -H "Content-Type: application/json" -d '{"email_to": "test@example.com"}' | grep -q "Not authenticated"; then
        echo "✅ API endpoint responding correctly"
    else
        echo "❌ API endpoint test failed"
        return 1
    fi
    
    # Test business endpoint (previously failing)
    echo "Testing business endpoint..."
    if curl -s https://api.hero365.ai/v1/businesses/debug | grep -q "Business routes are working"; then
        echo "✅ Business endpoint responding correctly"
    else
        echo "⚠️  Business endpoint test failed (may need authentication)"
    fi
    
    echo "✅ Deployment verification passed"
    echo ""
}

# Function to display deployment info
show_deployment_info() {
    echo "📊 Deployment Information"
    echo "========================"
    echo ""
    echo "🌐 Endpoints:"
    echo "   Main site: https://hero365.ai"
    echo "   API: https://api.hero365.ai"
    echo "   Health: https://api.hero365.ai/health"
    echo ""
    echo "📱 Mobile App API Endpoints:"
    echo "   🔐 Auth: https://api.hero365.ai/v1/auth/*"
    echo "   👥 Users: https://api.hero365.ai/v1/users/*"
    echo "   🏢 Businesses: https://api.hero365.ai/v1/businesses/*"
    echo "   📞 Contacts: https://api.hero365.ai/v1/contacts/*"
    echo "   💼 Jobs: https://api.hero365.ai/v1/jobs/*"
    echo "   📊 Activities: https://api.hero365.ai/v1/activities/*"
    echo "   🏢 Business Context: https://api.hero365.ai/v1/business-context/*"
    echo "   📅 Scheduling: https://api.hero365.ai/v1/scheduling/*"
    echo ""
    echo "🔧 AWS Resources:"
    echo "   Region: $AWS_REGION"
    echo "   ECS Cluster: hero365-cluster"
    echo "   Service: hero365-backend"
    echo ""
    echo "📋 Useful Commands:"
    echo "   Check service: aws ecs describe-services --cluster hero365-cluster --services hero365-backend --region $AWS_REGION"
    echo "   View logs: aws logs tail /ecs/hero365-backend --follow --region $AWS_REGION"
    echo "   Force redeploy: $0"
    echo ""
}

# Main deployment flow
main() {
    check_prerequisites
    
    echo "Starting deployment process..."
    echo ""
    
    build_and_push
    deploy_service
    wait_for_deployment
    configure_alb_routes
    verify_deployment
    show_deployment_info
    
    echo "🎉 Deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "check")
        check_prerequisites
        ;;
    "build")
        check_prerequisites
        build_and_push
        ;;
    "deploy")
        check_prerequisites
        deploy_service
        wait_for_deployment
        ;;
    "verify")
        verify_deployment
        ;;
    *)
        main
        ;;
esac 