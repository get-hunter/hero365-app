# 🚀 Hero365 Quick Deployment Reference

## 📋 What You Need to Deploy

When you want to deploy Hero365, here's exactly what to do:

### ✅ Prerequisites Check
```bash
./scripts/deploy-production.sh check
```

### 🚀 Quick Deploy (Code Updates)
```bash
./scripts/deploy-production.sh
```

That's it! This single command will:
- ✅ Build your Docker image with correct architecture
- ✅ Push to AWS ECR
- ✅ Deploy to ECS Fargate
- ✅ Wait for deployment to complete
- ✅ Verify everything is working
- ✅ Show you the results

## 🔧 Individual Steps (if needed)

| Command | What it does |
|---------|-------------|
| `./scripts/deploy-production.sh check` | Check if everything is ready |
| `./scripts/deploy-production.sh build` | Just build and push images |
| `./scripts/deploy-production.sh deploy` | Just deploy (no build) |
| `./scripts/deploy-production.sh verify` | Just test endpoints |

## 🆕 First Time Setup (Only Once)

If this is your first deployment ever:

```bash
# 1. Setup environment
./scripts/setup-environment.sh setup-prod

# 2. Edit production config (add your Supabase keys, etc.)
nano environments/production.env

# 3. Validate config
./scripts/setup-environment.sh validate production

# 4. Create AWS infrastructure (only once!)
./aws/deploy-simple.sh

# 5. Setup domain and SSL (only once!)
./aws/custom-domain-setup.sh

# 6. Now you can use regular deployment
./scripts/deploy-production.sh
```

## 🌐 Your Live URLs

After deployment:
- **Main Site**: https://hero365.ai
- **API**: https://api.hero365.ai/v1/
- **Health Check**: https://api.hero365.ai/health

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Service not found" | Run `./aws/deploy-simple.sh` first |
| "Docker not running" | Start Docker Desktop |
| "AWS credentials not configured" | Run `aws configure` |
| "Health check failed" | Check logs: `aws logs tail /ecs/hero365-backend --follow` |

## ⚡ Super Quick Deploy

For regular code updates, just run:
```bash
./scripts/deploy-production.sh
```

Wait 2-3 minutes, and your changes are live! 🎉 