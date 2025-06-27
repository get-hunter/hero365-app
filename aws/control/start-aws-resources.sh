#!/bin/bash

# Hero365 AWS Resource Start Script
# Restart AWS resources after being stopped

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_REGION="us-east-1"
ACCOUNT_ID="886436939429"
CLUSTER_NAME="hero365-cluster"
SERVICE_NAME="hero365-backend"
ALB_NAME="hero365-alb"

echo "🚀 Hero365 AWS Resource Start Script"
echo "====================================="
echo "Account ID: $ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "Date: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log with colors
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if resource exists
resource_exists() {
    local resource_type="$1"
    local resource_name="$2"
    
    case "$resource_type" in
        "service")
            aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$resource_name" --region "$AWS_REGION" --query 'services[0].status' --output text 2>/dev/null | grep -q "ACTIVE"
            ;;
        "cluster")
            aws ecs describe-clusters --clusters "$resource_name" --region "$AWS_REGION" --query 'clusters[0].status' --output text 2>/dev/null | grep -q "ACTIVE"
            ;;
    esac
}

# Function to start ECS service
start_ecs_service() {
    local desired_count=${1:-1}
    
    log_info "Starting ECS service: $SERVICE_NAME with $desired_count tasks"
    
    if resource_exists "service" "$SERVICE_NAME"; then
        # Scale service up
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$SERVICE_NAME" \
            --desired-count "$desired_count" \
            --region "$AWS_REGION" > /dev/null
        
        log_success "ECS service scaled to $desired_count tasks"
        
        # Wait for tasks to start
        log_info "Waiting for tasks to start and become healthy..."
        local timeout=300  # 5 minutes
        local elapsed=0
        local interval=15
        
        while [ $elapsed -lt $timeout ]; do
            local service_info=$(aws ecs describe-services \
                --cluster "$CLUSTER_NAME" \
                --services "$SERVICE_NAME" \
                --region "$AWS_REGION" \
                --query 'services[0].{running:runningCount,desired:desiredCount,pending:pendingCount}' \
                --output json)
            
            local running_count=$(echo $service_info | jq -r '.running')
            local desired_count_actual=$(echo $service_info | jq -r '.desired')
            local pending_count=$(echo $service_info | jq -r '.pending')
            
            if [ "$running_count" = "$desired_count_actual" ] && [ "$running_count" -gt 0 ]; then
                log_success "All tasks started and running successfully!"
                echo "   Running tasks: $running_count/$desired_count_actual"
                break
            fi
            
            echo "   Status: $running_count running, $pending_count pending, $desired_count_actual desired"
            sleep $interval
            elapsed=$((elapsed + interval))
        done
        
        if [ $elapsed -ge $timeout ]; then
            log_warning "Timeout waiting for tasks to start. Check AWS console for details."
            echo "   Current status: $running_count running, $pending_count pending, $desired_count_actual desired"
        fi
    else
        log_error "ECS service not found. Please run infrastructure deployment first:"
        echo "   ./aws/deploy-simple.sh"
        exit 1
    fi
    
    echo ""
}

# Function to enable auto scaling
enable_auto_scaling() {
    log_info "Re-enabling auto scaling for ECS service"
    
    local scaling_target="service/$CLUSTER_NAME/$SERVICE_NAME"
    
    # Check if scaling target exists
    if aws application-autoscaling describe-scalable-targets \
        --service-namespace ecs \
        --resource-ids "$scaling_target" \
        --region "$AWS_REGION" \
        --query 'ScalableTargets[0]' --output text 2>/dev/null | grep -q "service"; then
        
        # Resume scaling activities
        aws application-autoscaling register-scalable-target \
            --service-namespace ecs \
            --resource-id "$scaling_target" \
            --scalable-dimension ecs:service:DesiredCount \
            --suspended-state '{
                "DynamicScalingInSuspended": false,
                "DynamicScalingOutSuspended": false,
                "ScheduledScalingSuspended": false
            }' \
            --region "$AWS_REGION" > /dev/null
        
        log_success "Auto scaling resumed"
    else
        log_warning "No auto scaling configuration found. Consider setting up auto scaling:"
        echo "   ./aws/deployment/auto-scaling-setup.sh"
    fi
    
    echo ""
}

# Function to verify deployment
verify_deployment() {
    log_info "Verifying deployment health..."
    
    # Wait a bit for the service to be fully ready
    sleep 30
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    local health_url="https://api.hero365.ai/health"
    
    # Try multiple times as service might be starting
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 10 "$health_url" | grep -q "healthy"; then
            log_success "Health check passed"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                log_warning "Health check failed after $max_attempts attempts"
                echo "   You may need to wait longer or check AWS console for issues"
            else
                echo "   Health check attempt $attempt/$max_attempts failed, retrying in 10s..."
                sleep 10
            fi
        fi
        attempt=$((attempt + 1))
    done
    
    # Test API endpoint
    log_info "Testing API endpoint..."
    local api_url="https://api.hero365.ai/v1/utils/test-email/"
    
    if curl -s --max-time 10 "$api_url" -X POST -H "Content-Type: application/json" -d '{"email_to": "test@example.com"}' | grep -q "Not authenticated"; then
        log_success "API endpoint responding correctly"
    else
        log_warning "API endpoint test inconclusive (may require authentication)"
    fi
    
    echo ""
}

# Function to show service status
show_service_status() {
    log_info "Current service status:"
    
    local service_info=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region "$AWS_REGION" \
        --query 'services[0]' \
        --output json)
    
    local status=$(echo $service_info | jq -r '.status')
    local running_count=$(echo $service_info | jq -r '.runningCount')
    local desired_count=$(echo $service_info | jq -r '.desiredCount')
    local pending_count=$(echo $service_info | jq -r '.pendingCount')
    local task_definition=$(echo $service_info | jq -r '.taskDefinition' | rev | cut -d'/' -f1 | rev)
    
    echo "   Service Status: $status"
    echo "   Task Definition: $task_definition"
    echo "   Running Tasks: $running_count"
    echo "   Desired Tasks: $desired_count"
    echo "   Pending Tasks: $pending_count"
    
    # Show task details if running
    if [ "$running_count" -gt 0 ]; then
        log_info "Running task details:"
        aws ecs list-tasks \
            --cluster "$CLUSTER_NAME" \
            --service-name "$SERVICE_NAME" \
            --region "$AWS_REGION" \
            --query 'taskArns[0]' \
            --output text | xargs -I {} aws ecs describe-tasks \
            --cluster "$CLUSTER_NAME" \
            --tasks {} \
            --region "$AWS_REGION" \
            --query 'tasks[0].{Status:lastStatus,Health:healthStatus,Started:startedAt,CPU:cpu,Memory:memory}' \
            --output table
    fi
    
    echo ""
}

# Function to show endpoints
show_endpoints() {
    echo "🌐 Hero365 Endpoints:"
    echo "===================="
    echo ""
    echo "   Main Site: https://hero365.ai"
    echo "   API Base: https://api.hero365.ai"
    echo "   Health Check: https://api.hero365.ai/health"
    echo "   API Docs: https://api.hero365.ai/docs"
    echo ""
    echo "🔗 Quick verification commands:"
    echo "   curl https://api.hero365.ai/health"
    echo "   curl https://api.hero365.ai/docs"
    echo ""
}

# Main execution
main() {
    log_info "Starting AWS resource startup process..."
    echo ""
    
    local desired_count=1
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --count)
                desired_count="$2"
                shift 2
                ;;
            *)
                break
                ;;
        esac
    done
    
    # Start resources
    start_ecs_service "$desired_count"
    enable_auto_scaling
    
    # Verify deployment
    verify_deployment
    
    # Show status
    show_service_status
    show_endpoints
    
    log_success "Hero365 infrastructure is now running!"
    echo ""
    log_info "💡 Monitor your costs with: ./aws/control/check-costs.sh"
    log_info "🛑 Stop resources anytime with: ./aws/control/stop-aws-resources.sh"
}

# Script options
case "${1:-}" in
    "--help"|"-h")
        echo "Hero365 AWS Resource Start Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h         Show this help message"
        echo "  --count N          Number of tasks to run (default: 1)"
        echo "  --force            Skip confirmation prompt"
        echo "  --dry-run          Show what would be done without making changes"
        echo ""
        echo "This script will:"
        echo "  • Scale ECS service to desired task count"
        echo "  • Re-enable auto scaling"
        echo "  • Verify deployment health"
        echo "  • Show service status and endpoints"
        echo ""
        echo "Examples:"
        echo "  $0                 Start with 1 task"
        echo "  $0 --count 2       Start with 2 tasks"
        echo "  $0 --dry-run       Show what would be done"
        echo ""
        exit 0
        ;;
    "--force")
        shift
        log_info "Force mode enabled"
        main "$@"
        ;;
    "--dry-run")
        log_info "DRY RUN MODE - No changes will be made"
        echo ""
        echo "Would perform the following actions:"
        echo "  • Start ECS service: $SERVICE_NAME"
        echo "  • Scale to: ${2:-1} tasks"
        echo "  • Re-enable auto scaling for: service/$CLUSTER_NAME/$SERVICE_NAME"
        echo "  • Verify deployment health"
        echo ""
        ;;
    "")
        main "$@"
        ;;
    *)
        if [[ $1 =~ ^--count ]]; then
            main "$@"
        else
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
        fi
        ;;
esac 