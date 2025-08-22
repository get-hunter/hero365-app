#!/usr/bin/env python3
"""
Test integration between backend and Next.js template system.
This script demonstrates the full flow:
1. Generate content for a template
2. Build the Next.js site with that content
3. Deploy to Cloudflare Pages
"""

import json
import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime
import uuid
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.entities.business import Business, CompanySize
from app.domain.entities.business_branding import BusinessBranding


def create_test_business():
    """Create a test business for the website."""
    return {
        "name": "ProComfort HVAC Solutions",
        "phone_number": "(512) 555-HVAC",
        "business_email": "service@procomforthvac.com",
        "business_address": "789 Commerce Blvd, Austin, TX 78745",
        "description": "Austin's premier HVAC service provider",
        "industry": "HVAC Services",
        "service_areas": ["Austin", "Round Rock", "Cedar Park", "Pflugerville", "Georgetown"]
    }


def generate_content_for_template(business):
    """Generate content for the HVAC template."""
    return {
        "business": {
            "name": business["name"],
            "phone": business["phone_number"],
            "email": business["business_email"],
            "address": business["business_address"],
            "hours": "Mon-Fri 7AM-7PM, Sat 8AM-5PM, Sun Emergency Only",
            "description": business["description"],
            "serviceAreas": business["service_areas"]
        },
        "hero": {
            "headline": f"Austin's Most Trusted HVAC Experts",
            "subtitle": "24/7 Emergency Service • Same-Day Repairs • 100% Satisfaction Guaranteed",
            "ctaButtons": [
                {"text": "Get Free Quote", "action": "open_quote", "style": "primary"},
                {"text": "Call Now", "action": "call", "style": "secondary"}
            ],
            "trustIndicators": ["Licensed & Insured", "20+ Years Experience", "5-Star Rated"],
            "showEmergencyBanner": True,
            "emergencyMessage": "🔥 Heating Emergency? ❄️ AC Down? Call Now for Immediate Service!"
        },
        "services": [
            {
                "title": "Air Conditioning Repair",
                "description": "Fast, reliable AC repair service for all makes and models",
                "price": "From $89",
                "features": ["Same-day service", "All brands", "Warranty included"],
                "isPopular": True
            },
            {
                "title": "Heating System Service",
                "description": "Keep your home warm with our expert heating services",
                "price": "From $99",
                "features": ["24/7 emergency", "Energy efficient", "Safety certified"]
            },
            {
                "title": "HVAC Installation",
                "description": "New system installation with energy-efficient options",
                "price": "Free Quote",
                "features": ["Top brands", "Financing available", "10-year warranty"]
            },
            {
                "title": "Maintenance Plans",
                "description": "Preventive maintenance to extend system life",
                "price": "$19/month",
                "features": ["Bi-annual service", "Priority scheduling", "15% off repairs"]
            }
        ],
        "contact": {
            "title": "Get Your Free HVAC Quote Today",
            "subtitle": "Professional service, transparent pricing, no surprises",
            "services": ["AC Repair", "Heating Repair", "New Installation", "Maintenance", "Emergency Service"],
            "urgencyOptions": ["Emergency (Within 1 hour)", "Today", "Tomorrow", "This Week", "Just Planning"]
        },
        "booking": {
            "title": "Schedule Your HVAC Service",
            "subtitle": "Pick a time that works for you",
            "services": ["AC Repair", "Heating Service", "Installation Consultation", "Maintenance Check"],
            "showPricing": True
        },
        "seo": {
            "title": f"{business['name']} - HVAC Repair & Installation in Austin, TX",
            "description": f"Professional HVAC services in Austin. 24/7 emergency AC and heating repair, installation, and maintenance. Licensed & insured. Call {business['phone_number']} for same-day service.",
            "keywords": ["hvac austin", "ac repair austin", "heating repair austin", "hvac installation", "emergency hvac service"]
        }
    }


def inject_content_into_template(content, website_builder_path):
    """Inject the generated content into the Next.js template."""
    
    # Target the HVAC template file
    template_file = website_builder_path / "app" / "templates" / "residential" / "hvac" / "page.tsx"
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return False
    
    # Read the template
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Convert content to JavaScript format
    # We need to escape backslashes in the JSON for JavaScript
    content_js = json.dumps(content, indent=2)
    
    # Find the defaultContent declaration
    import re
    
    # Find where defaultContent starts and ends
    start_marker = "const defaultContent = {"
    end_marker = "export default function HVACTemplate()"
    
    start_idx = template_content.find(start_marker)
    end_idx = template_content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ Could not find content markers in template")
        return False
    
    # Find the end of the defaultContent object
    # Count braces to find the matching closing brace
    brace_count = 0
    i = start_idx + len(start_marker) - 1
    while i < end_idx:
        if template_content[i] == '{':
            brace_count += 1
        elif template_content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                # Found the closing brace
                end_of_content = i + 2  # Include the semicolon
                break
        i += 1
    
    # Build the new template
    new_template = (
        template_content[:start_idx] +
        f"const defaultContent = {content_js};\n\n" +
        template_content[end_of_content:]
    )
    
    # Write back
    with open(template_file, 'w') as f:
        f.write(new_template)
    
    print(f"✅ Content injected into template")
    return True


def build_nextjs_site(website_builder_path, output_path):
    """Build the Next.js site to static files."""
    
    print("🔨 Building Next.js site...")
    
    # Ensure we're in the website-builder directory
    original_dir = os.getcwd()
    os.chdir(website_builder_path)
    
    try:
        # Run the build command
        result = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return None
        
        print("✅ Build completed successfully")
        
        # Copy the output to our desired location
        out_dir = website_builder_path / "out"
        if out_dir.exists():
            if output_path.exists():
                shutil.rmtree(output_path)
            shutil.copytree(out_dir, output_path)
            print(f"✅ Static files copied to {output_path}")
            return output_path
        else:
            print("❌ Output directory not found")
            return None
            
    finally:
        os.chdir(original_dir)


def deploy_to_cloudflare(build_path, project_name):
    """Deploy the built site to Cloudflare Pages."""
    
    print(f"🚀 Deploying to Cloudflare Pages as '{project_name}'...")
    
    # Set up environment
    env = os.environ.copy()
    env['CLOUDFLARE_API_TOKEN'] = "muGRINW0SuRdhq5otaMRwMf0piAn24wFdRgrGiXl"
    env['CLOUDFLARE_ACCOUNT_ID'] = "4e131688804526ec202c7d530e635307"
    
    # Deploy using Wrangler
    # Use echo to auto-confirm project creation
    cmd = f"echo 'y' | npx wrangler pages deploy {build_path} --project-name {project_name} --commit-dirty=true"
    
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        shell=True
    )
    
    if result.returncode == 0:
        # Parse the URL from output
        for line in result.stdout.split('\n'):
            if 'https://' in line and '.pages.dev' in line:
                url = line.strip()
                if url.startswith('https://'):
                    print(f"✅ Deployed successfully!")
                    print(f"🌐 Website URL: {url}")
                    return url
    else:
        print(f"❌ Deployment failed: {result.stderr}")
    
    return None


def main():
    """Main execution flow."""
    
    print("=" * 60)
    print("Hero365 Next.js Template Integration Test")
    print("=" * 60)
    
    # Paths
    backend_path = Path(__file__).parent.parent
    website_builder_path = backend_path.parent / "website-builder"
    build_output_path = backend_path / "build_output" / f"nextjs-test-{uuid.uuid4().hex[:8]}"
    
    # 1. Create test business
    print("\n1. Creating test business...")
    business = create_test_business()
    print(f"   Business: {business['name']}")
    
    # 2. Generate content
    print("\n2. Generating content for template...")
    content = generate_content_for_template(business)
    print(f"   Generated content for {len(content)} sections")
    
    # 3. Inject content into template
    print("\n3. Injecting content into Next.js template...")
    if not inject_content_into_template(content, website_builder_path):
        print("❌ Failed to inject content")
        return 1
    
    # 4. Build the site
    print("\n4. Building static site...")
    build_result = build_nextjs_site(website_builder_path, build_output_path)
    if not build_result:
        print("❌ Build failed")
        return 1
    
    # Count files
    html_files = list(build_output_path.rglob("*.html"))
    total_files = list(build_output_path.rglob("*"))
    print(f"   Generated {len(html_files)} HTML pages")
    print(f"   Total files: {len([f for f in total_files if f.is_file()])}")
    
    # 5. Deploy to Cloudflare
    print("\n5. Deploying to Cloudflare Pages...")
    project_name = f"hvac-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    url = deploy_to_cloudflare(build_output_path, project_name)
    
    if url:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Full integration test completed")
        print(f"🌐 Live Website: {url}")
        print("=" * 60)
        return 0
    else:
        print("\n❌ Deployment failed")
        return 1


if __name__ == "__main__":
    exit(main())
