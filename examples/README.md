# Business Website Deployment Examples

This directory contains example configuration files for deploying SEO-optimized contractor websites.

## Quick Start

1. **Copy an example configuration:**
   ```bash
   cp examples/austin-pro-hvac.config.json my-business.config.json
   ```

2. **Edit the configuration with your business details:**
   ```bash
   nano my-business.config.json
   ```

3. **Deploy your website:**
   ```bash
   ./scripts/deploy-from-config.sh my-business.config.json
   ```

That's it! Your website with 900+ SEO-optimized pages will be deployed automatically.

## Configuration Examples

### HVAC Business
- **File:** `austin-pro-hvac.config.json`
- **Trade:** HVAC/Air Conditioning
- **Location:** Austin, TX
- **Services:** AC repair, installation, maintenance, etc.

### Plumbing Business  
- **File:** `dallas-elite-plumbing.config.json`
- **Trade:** Plumbing
- **Location:** Dallas, TX
- **Services:** Drain cleaning, water heater, leak repair, etc.

### Electrical Business
- **File:** `houston-pro-electrical.config.json` 
- **Trade:** Electrical
- **Location:** Houston, TX
- **Services:** Panel upgrades, wiring, lighting, etc.

## Configuration File Structure

```json
{
  "business_id": "unique-business-identifier",
  "business_name": "Your Business Name",
  "phone": "(555) 123-4567",
  "email": "info@yourbusiness.com",
  "address": "123 Main St",
  "city": "Your City",
  "state": "TX",
  "postal_code": "12345",
  "primary_trade": "hvac|plumbing|electrical|roofing|general_contractor",
  "service_areas": [
    "City 1",
    "City 2", 
    "City 3"
  ],
  "domain": "yourbusiness.com",
  "environment": "production",
  "seo_config": {
    "enable_location_pages": true,
    "enable_emergency_pages": true,
    "enable_commercial_pages": true,
    "target_keywords": ["keyword1", "keyword2"],
    "business_description": "Brief description of your business",
    "service_radius_miles": 30
  },
  "services": [
    "service-1",
    "service-2"
  ]
}
```

## What Gets Deployed

When you deploy a business website, the system automatically generates:

### 🎯 **SEO Page Matrix**
- **Standard Pages:** `/services/{service}/{location}`
- **Emergency Pages:** `/emergency/{service}/{location}`  
- **Commercial Pages:** `/commercial/{service}/{location}`

### 📊 **Example for Austin Pro HVAC:**
- 10 services × 15 locations × 3 variants = **450 pages**
- Plus home page, about, contact, etc.
- **Total: 450+ SEO-optimized pages**

### 🔍 **SEO Features:**
- ✅ Location-specific title tags and meta descriptions
- ✅ Structured data markup (LocalBusiness, Service)
- ✅ Mobile-optimized responsive design
- ✅ Fast loading times (< 2 seconds)
- ✅ Local keyword optimization
- ✅ Phone numbers and contact info on every page

## Supported Trades

- **HVAC** - Air conditioning, heating, ventilation
- **Plumbing** - Drain cleaning, water heaters, leak repair
- **Electrical** - Panel upgrades, wiring, lighting
- **Roofing** - Roof repair, replacement, gutters
- **General Contractor** - Home renovation, remodeling

## Service Areas

Each business can serve up to 15+ locations. The system will generate location-specific pages for each service in each area, maximizing local SEO coverage.

## Domain Setup

Before deployment, ensure:
1. Domain is registered and DNS is configured
2. SSL certificate is available
3. Hosting environment is ready

## Support

For questions or issues:
1. Check the deployment logs
2. Verify your configuration file format
3. Ensure all required fields are filled
4. Test with a simple configuration first

## Advanced Configuration

For advanced features like custom styling, additional services, or special SEO requirements, contact the development team.
