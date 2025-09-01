# Interactive Business Website Deployer - Usage Guide

## Quick Start

The easiest way to deploy a business website is using the interactive script:

```bash
# Run the interactive deployer
./scripts/deploy-business-website.sh

# Or with specific options
./scripts/deploy-business-website.sh --env staging --build-only
```

## What the Script Does

1. **Connects to Database**: Automatically connects to your Supabase database
2. **Fetches Businesses**: Retrieves all active businesses and displays them in a beautiful table
3. **Interactive Selection**: Lets you choose which business to deploy
4. **Automated Deployment**: Builds and deploys the website to Cloudflare Workers

## Example Session

```
🚀 Interactive Website Deployer
Environment: staging
Mode: Build & Deploy

✅ Found 3 active businesses

                           🏢 Available Businesses                            
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Business Name        ┃ Trade         ┃ Location           ┃ Contact                 ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ Elite HVAC Services  │ HVAC          │ Austin, TX         │ contact@elitehvac.com   │
│    │                      │               │                    │ (512) 555-0123          │
│ 2  │ Pro Plumbing Co      │ Plumbing      │ Dallas, TX         │ info@proplumbing.com    │
│    │                      │               │                    │ (214) 555-0456          │
│ 3  │ Ace Electrical       │ Electrical    │ Houston, TX        │ service@aceelectric.com │
│    │                      │               │                    │ (713) 555-0789          │
└────┴──────────────────────┴───────────────┴────────────────────┴─────────────────────────┘

📋 Select a business to deploy:
Enter business number (1-3) or 'q' to quit [1]: 1

┌─ Selected Business ─────────────────────────────────────────────────────────┐
│ Elite HVAC Services                                                         │
│ Trade: HVAC                                                                 │
│ Location: Austin, TX                                                        │
│ Email: contact@elitehvac.com                                                │
│ Phone: (512) 555-0123                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

Deploy website for this business? [Y/n]: y

🚀 Starting website deployment for Elite HVAC Services
Environment: staging
Build Only: False

[Deployment process begins...]
```

## Available Options

- `--env staging|production|development`: Target environment (default: staging)
- `--build-only`: Only build the website, don't deploy to Cloudflare
- `--help`: Show help information

## Prerequisites

1. **Environment Variables**: Ensure your `environments/.env` file contains:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

2. **Dependencies**: All required dependencies are automatically managed through the backend environment

3. **Cloudflare Setup**: For actual deployment (not build-only), ensure Cloudflare is configured

## Troubleshooting

### "Missing required environment variables"
- Check your `environments/.env` file
- Ensure SUPABASE_URL and SUPABASE_KEY are properly set

### "No active businesses found"
- Verify businesses exist in your database
- Check that businesses have `is_active = true`

### Build/Deployment Errors
- The website builder may need additional configuration for Edge Runtime
- Check the detailed logs in the terminal output
- Use `--build-only` flag to test without deployment

## Integration with Existing Workflow

This script integrates seamlessly with the existing Hero365 infrastructure:

- Uses the same Supabase database
- Leverages existing website-builder configuration
- Follows the same deployment patterns
- Maintains all existing business data relationships

The script is designed to be the primary way to deploy business websites, replacing manual business ID entry with an intuitive selection interface.
