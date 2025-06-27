# Hero365 AWS Cost Control Scripts

This directory contains scripts to help manage AWS costs during development by stopping and starting resources as needed.

## Available Scripts

### 🛑 `stop-aws-resources.sh`
**Purpose**: Stop AWS resources to save costs during development

**What it does**:
- Scales ECS service to 0 tasks
- Disables auto scaling
- Cleans up old CloudWatch logs (7+ days old)
- Shows cost savings estimate
- Provides restart instructions

**Usage**:
```bash
# Interactive mode (with confirmation)
./aws/control/stop-aws-resources.sh

# Force mode (skip confirmation) 
./aws/control/stop-aws-resources.sh --force

# Dry run (see what would be done)
./aws/control/stop-aws-resources.sh --dry-run

# Help
./aws/control/stop-aws-resources.sh --help
```

**💰 Expected Savings**: ~$34-53/month

### 🚀 `start-aws-resources.sh`
**Purpose**: Restart AWS resources after they've been stopped

**What it does**:
- Scales ECS service back up (default: 1 task)
- Re-enables auto scaling
- Verifies deployment health
- Shows service status and endpoints

**Usage**:
```bash
# Start with 1 task (default)
./aws/control/start-aws-resources.sh

# Start with specific number of tasks
./aws/control/start-aws-resources.sh --count 2

# Dry run
./aws/control/start-aws-resources.sh --dry-run

# Help
./aws/control/start-aws-resources.sh --help
```

### 💰 `check-costs.sh`
**Purpose**: Monitor current AWS costs and usage

**Usage**:
```bash
./aws/control/check-costs.sh
```

### 🔧 `setup-cost-controls.sh`
**Purpose**: Set up billing alerts and budgets

**Usage**:
```bash
./aws/control/setup-cost-controls.sh
```

## Quick Reference

### Stop Infrastructure (Development Break)
```bash
# Quick stop with confirmation
./aws/control/stop-aws-resources.sh

# Force stop (no confirmation)
./aws/control/stop-aws-resources.sh --force
```

### Start Infrastructure (Back to Work)
```bash
# Start with default settings
./aws/control/start-aws-resources.sh

# Start with more capacity
./aws/control/start-aws-resources.sh --count 2
```

### Check Current Status
```bash
# Check costs
./aws/control/check-costs.sh

# Check ECS service status
aws ecs describe-services --cluster hero365-cluster --services hero365-backend --region us-east-1
```

## Manual Commands (If Scripts Fail)

### Stop Resources Manually
```bash
# Scale ECS service to 0
aws ecs update-service --cluster hero365-cluster --service hero365-backend --desired-count 0 --region us-east-1

# Disable auto scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id "service/hero365-cluster/hero365-backend" \
    --scalable-dimension ecs:service:DesiredCount \
    --suspended-state '{"DynamicScalingInSuspended": true, "DynamicScalingOutSuspended": true, "ScheduledScalingSuspended": true}' \
    --region us-east-1
```

### Start Resources Manually
```bash
# Scale ECS service back up
aws ecs update-service --cluster hero365-cluster --service hero365-backend --desired-count 1 --region us-east-1

# Re-enable auto scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id "service/hero365-cluster/hero365-backend" \
    --scalable-dimension ecs:service:DesiredCount \
    --suspended-state '{"DynamicScalingInSuspended": false, "DynamicScalingOutSuspended": false, "ScheduledScalingSuspended": false}' \
    --region us-east-1
```

## Cost Breakdown

When stopped, you save costs on:
- **ECS Fargate**: ~$15-25/month (CPU/Memory allocation)
- **CloudWatch Logs**: ~$2-5/month (reduced ingestion)
- **Data Transfer**: ~$1-3/month (reduced outbound traffic)

**Note**: ALB costs (~$16-20/month) continue even when no traffic is routed. Consider deleting ALB for extended breaks (>1 week).

## Best Practices

1. **Daily Development**: Use stop/start scripts for overnight and weekend breaks
2. **Weekly Breaks**: Consider keeping infrastructure running for short breaks
3. **Extended Breaks**: (>1 week) Consider tearing down ALB and other persistent resources
4. **Monitor Costs**: Run `check-costs.sh` weekly to track spending
5. **Set Budgets**: Run `setup-cost-controls.sh` to get billing alerts

## Troubleshooting

### Script Fails to Stop/Start
- Check AWS credentials: `aws sts get-caller-identity`
- Verify permissions: Ensure your AWS user has ECS, Application Auto Scaling, and CloudWatch permissions
- Check resources exist: `aws ecs describe-services --cluster hero365-cluster --services hero365-backend --region us-east-1`

### Service Won't Start
- Check task definition exists
- Verify ECR image is available
- Check CloudWatch logs: `/ecs/hero365-backend`
- Ensure Secrets Manager secrets exist

### Health Checks Fail
- Service may still be starting (wait 2-3 minutes)
- Check task logs in CloudWatch
- Verify ALB configuration
- Test endpoints manually with curl

## Contact

For issues with these scripts, check the AWS Console or contact the development team. 