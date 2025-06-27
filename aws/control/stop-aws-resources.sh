#!/bin/bash

# Hero365 AWS Resource Stop Script
# Stop AWS resources to save costs during development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_REGION="us-east-1"
ACCOUNT_ID="886436939429"
CLUSTER_NAME="hero365-cluster"
SERVICE_NAME="hero365-backend"
ALB_NAME="hero365-alb"

echo "🛑 Hero365 AWS Resource Stop Script"
echo "===================================="
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
        "alb")
            aws elbv2 describe-load-balancers --names "$resource_name" --region "$AWS_REGION" --query 'LoadBalancers[0].State.Code' --output text 2>/dev/null | grep -q "active"
            ;;
    esac
}

# Function to stop ECS service
stop_ecs_service() {
    log_info "Stopping ECS service: $SERVICE_NAME"
    
    if resource_exists "service" "$SERVICE_NAME"; then
        # Scale service to 0 tasks
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$SERVICE_NAME" \
            --desired-count 0 \
            --region "$AWS_REGION" > /dev/null
        
        log_success "ECS service scaled to 0 tasks"
        
        # Wait for tasks to stop
        log_info "Waiting for tasks to stop..."
        local timeout=120  # 2 minutes
        local elapsed=0
        local interval=10
        
        while [ $elapsed -lt $timeout ]; do
            local running_count=$(aws ecs describe-services \
                --cluster "$CLUSTER_NAME" \
                --services "$SERVICE_NAME" \
                --region "$AWS_REGION" \
                --query 'services[0].runningCount' \
                --output text)
            
            if [ "$running_count" = "0" ]; then
                log_success "All tasks stopped successfully"
                break
            fi
            
            echo "   Still running $running_count tasks..."
            sleep $interval
            elapsed=$((elapsed + interval))
        done
        
        if [ $elapsed -ge $timeout ]; then
            log_warning "Timeout waiting for tasks to stop. Some tasks may still be running."
        fi
    else
        log_warning "ECS service not found or not active"
    fi
    
    echo ""
}

# Function to disable auto scaling
disable_auto_scaling() {
    log_info "Disabling auto scaling for ECS service"
    
    local scaling_target="service/$CLUSTER_NAME/$SERVICE_NAME"
    
    # Check if scaling target exists
    if aws application-autoscaling describe-scalable-targets \
        --service-namespace ecs \
        --resource-ids "$scaling_target" \
        --region "$AWS_REGION" \
        --query 'ScalableTargets[0]' --output text 2>/dev/null | grep -q "service"; then
        
        # Suspend scaling activities
        aws application-autoscaling register-scalable-target \
            --service-namespace ecs \
            --resource-id "$scaling_target" \
            --scalable-dimension ecs:service:DesiredCount \
            --suspended-state '{
                "DynamicScalingInSuspended": true,
                "DynamicScalingOutSuspended": true,
                "ScheduledScalingSuspended": true
            }' \
            --region "$AWS_REGION" > /dev/null
        
        log_success "Auto scaling suspended"
    else
        log_info "No auto scaling configuration found"
    fi
    
    echo ""
}

# Function to clean up CloudWatch logs (optional - saves storage costs)
cleanup_cloudwatch_logs() {
    log_info "Cleaning up old CloudWatch logs"
    
    local log_group="/ecs/$SERVICE_NAME"
    
    # Check if log group exists
    if aws logs describe-log-groups --log-group-name-prefix "$log_group" --region "$AWS_REGION" --query 'logGroups[0].logGroupName' --output text 2>/dev/null | grep -q "$log_group"; then
        
        # Delete log streams older than 7 days
        local cutoff_date=$(date -d '7 days ago' +%s)000  # CloudWatch uses milliseconds
        
        log_streams=$(aws logs describe-log-streams \
            --log-group-name "$log_group" \
            --region "$AWS_REGION" \
            --query "logStreams[?lastEventTime<\`$cutoff_date\`].logStreamName" \
            --output text)
        
        if [ -n "$log_streams" ] && [ "$log_streams" != "None" ]; then
            for stream in $log_streams; do
                aws logs delete-log-stream \
                    --log-group-name "$log_group" \
                    --log-stream-name "$stream" \
                    --region "$AWS_REGION" 2>/dev/null || true
            done
            log_success "Cleaned up old log streams"
        else
            log_info "No old log streams to clean up"
        fi
    else
        log_info "Log group not found"
    fi
    
    echo ""
}

# Function to show current costs
show_current_costs() {
    log_info "Checking current AWS costs..."
    
    # Run the cost check script if it exists
    local cost_script="$SCRIPT_DIR/check-costs.sh"
    
    if [ -f "$cost_script" ]; then
        chmod +x "$cost_script"
        "$cost_script" | head -20  # Show first 20 lines to avoid too much output
    else
        log_warning "Cost check script not found. Run it manually: ./aws/control/check-costs.sh"
    fi
    
    echo ""
}

# Function to show restart instructions
show_restart_instructions() {
    echo "🔄 To restart your Hero365 infrastructure:"
    echo "=========================================="
    echo ""
    echo "1. Scale ECS service back up:"
    echo "   aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --desired-count 1 --region $AWS_REGION"
    echo ""
    echo "2. Or use the deployment script:"
    echo "   ./aws/deployment/deploy-production.sh"
    echo ""
    echo "3. Re-enable auto scaling (if needed):"
    echo "   ./aws/deployment/auto-scaling-setup.sh"
    echo ""
    echo "4. Check service status:"
    echo "   aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION"
    echo ""
}

# Function to show cost savings estimate
show_cost_savings() {
    log_info "Estimated cost savings by stopping resources:"
    echo ""
    echo "💰 Potential Monthly Savings:"
    echo "   • ECS Fargate (512 CPU, 1GB RAM): ~\$15-25/month"
    echo "   • ALB (if unused): ~\$16-20/month"
    echo "   • CloudWatch Logs (reduced): ~\$2-5/month"
    echo "   • Data Transfer (reduced): ~\$1-3/month"
    echo ""
    echo "   📊 Total estimated savings: ~\$34-53/month"
    echo ""
    echo "Note: ALB costs continue even when no traffic is routed to it."
    echo "Consider deleting ALB if stopping for extended periods (>1 week)."
    echo ""
}

# Main execution
main() {
    log_info "Starting AWS resource shutdown process..."
    echo ""
    
    # Confirm action
    read -p "⚠️  This will stop your Hero365 infrastructure. Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operation cancelled by user"
        exit 0
    fi
    echo ""
    
    # Show current costs first
    show_current_costs
    
    # Stop resources
    disable_auto_scaling
    stop_ecs_service
    cleanup_cloudwatch_logs
    
    # Show summary
    log_success "AWS resources stopped successfully!"
    echo ""
    
    show_cost_savings
    show_restart_instructions
    
    log_info "💡 Pro tip: Set up billing alerts to monitor costs: ./aws/control/setup-cost-controls.sh"
    echo ""
    log_success "Done! Your AWS resources are now stopped to save costs."
}

# Script options
case "${1:-}" in
    "--help"|"-h")
        echo "Hero365 AWS Resource Stop Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --force        Skip confirmation prompt"
        echo "  --dry-run      Show what would be done without making changes"
        echo ""
        echo "This script will:"
        echo "  • Scale ECS service to 0 tasks"
        echo "  • Disable auto scaling"
        echo "  • Clean up old CloudWatch logs"
        echo "  • Show cost savings estimate"
        echo "  • Provide restart instructions"
        echo ""
        exit 0
        ;;
    "--force")
        log_info "Force mode enabled - skipping confirmation"
        echo ""
        # Modify main function to skip confirmation
        disable_auto_scaling
        stop_ecs_service
        cleanup_cloudwatch_logs
        show_cost_savings
        show_restart_instructions
        log_success "Done! Your AWS resources are now stopped to save costs."
        ;;
    "--dry-run")
        log_info "DRY RUN MODE - No changes will be made"
        echo ""
        echo "Would perform the following actions:"
        echo "  • Stop ECS service: $SERVICE_NAME"
        echo "  • Disable auto scaling for: service/$CLUSTER_NAME/$SERVICE_NAME"
        echo "  • Clean up CloudWatch logs in: /ecs/$SERVICE_NAME"
        echo ""
        show_cost_savings
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 