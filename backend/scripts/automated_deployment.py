#!/usr/bin/env python3
"""
Fully automated website deployment using Cloudflare Pages API directly.
This bypasses Wrangler's interactive prompts by using the REST API.
"""

import json
import subprocess
import shutil
import os
import zipfile
import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime
import uuid
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cloudflare credentials
CLOUDFLARE_API_TOKEN = "muGRINW0SuRdhq5otaMRwMf0piAn24wFdRgrGiXl"
CLOUDFLARE_ACCOUNT_ID = "4e131688804526ec202c7d530e635307"


async def create_zip_file(build_path: Path) -> Path:
    """Create a zip file of the build output for upload."""
    
    zip_path = build_path.parent / f"{build_path.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in build_path.rglob('*'):
            if file_path.is_file():
                # Get relative path from build directory
                relative_path = file_path.relative_to(build_path)
                zipf.write(file_path, relative_path)
    
    print(f"✅ Created zip file: {zip_path} ({zip_path.stat().st_size // 1024} KB)")
    return zip_path


async def deploy_to_cloudflare_api(build_path: Path, project_name: str) -> str:
    """Deploy using Cloudflare Pages API directly."""
    
    print(f"🚀 Deploying '{project_name}' using Cloudflare Pages API...")
    
    # Create zip file
    zip_path = await create_zip_file(build_path)
    
    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Create or get project
        project_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects"
        
        # Check if project exists
        async with session.get(project_url, headers=headers) as response:
            if response.status == 200:
                projects_data = await response.json()
                existing_project = None
                
                for project in projects_data.get('result', []):
                    if project['name'] == project_name:
                        existing_project = project
                        break
                
                if not existing_project:
                    # Create new project
                    project_data = {
                        'name': project_name,
                        'production_branch': 'main',
                        'build_config': {
                            'build_command': '',
                            'destination_dir': '/',
                            'root_dir': '/'
                        }
                    }
                    
                    async with session.post(project_url, headers=headers, json=project_data) as create_response:
                        if create_response.status == 200:
                            project_info = await create_response.json()
                            project_id = project_info['result']['name']
                            print(f"✅ Created new project: {project_id}")
                        else:
                            error_text = await create_response.text()
                            print(f"❌ Failed to create project: {error_text}")
                            return None
                else:
                    project_id = existing_project['name']
                    print(f"✅ Using existing project: {project_id}")
        
        # Step 2: Create deployment
        deployment_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{project_id}/deployments"
        
        # Prepare form data
        data = aiohttp.FormData()
        
        # Add the zip file
        with open(zip_path, 'rb') as f:
            data.add_field('file', f, filename='site.zip', content_type='application/zip')
        
        # Add metadata
        manifest = {
            '/index.html': {
                'hash': 'dummy-hash',
                'content_type': 'text/html'
            }
        }
        data.add_field('manifest', json.dumps(manifest))
        
        # Deploy
        async with session.post(deployment_url, headers=headers, data=data) as deploy_response:
            if deploy_response.status == 200:
                deployment_info = await deploy_response.json()
                deployment_url = deployment_info['result']['url']
                print(f"✅ Deployment successful!")
                print(f"🌐 Website URL: {deployment_url}")
                
                # Clean up zip file
                zip_path.unlink()
                
                return deployment_url
            else:
                error_text = await deploy_response.text()
                print(f"❌ Deployment failed: {error_text}")
                
                # Clean up zip file
                zip_path.unlink()
                
                return None


def deploy_using_existing_project(build_path: Path) -> str:
    """Deploy to an existing Cloudflare Pages project to avoid prompts."""
    
    print("🚀 Deploying to existing Cloudflare Pages project...")
    
    # Use an existing project name that we know exists
    existing_project = "hero365-websites"  # We can create this once manually
    
    env = os.environ.copy()
    env['CLOUDFLARE_API_TOKEN'] = CLOUDFLARE_API_TOKEN
    env['CLOUDFLARE_ACCOUNT_ID'] = CLOUDFLARE_ACCOUNT_ID
    
    # Deploy to existing project (no prompts)
    cmd = [
        'npx', 'wrangler', 'pages', 'deploy', str(build_path),
        '--project-name', existing_project,
        '--commit-dirty=true'
    ]
    
    print(f"   Running: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        # Parse URL from output
        for line in result.stdout.split('\n'):
            if 'https://' in line and '.pages.dev' in line:
                # Extract just the URL
                import re
                url_match = re.search(r'https://[^\s]+\.pages\.dev[^\s]*', line)
                if url_match:
                    url = url_match.group(0)
                    print(f"✅ Deployed successfully!")
                    print(f"🌐 Website URL: {url}")
                    return url
        
        print("✅ Deployment completed but couldn't extract URL")
        return "https://hero365-websites.pages.dev"
    else:
        print(f"❌ Deployment failed: {result.stderr}")
        return None


def create_test_business():
    """Create a test business for the website."""
    return {
        "name": "Austin Elite HVAC",
        "phone_number": "(512) 555-COOL",
        "business_email": "service@austinelitehvac.com",
        "business_address": "456 Tech Ridge Blvd, Austin, TX 78753",
        "description": "Premier HVAC services for Austin homes and businesses",
        "service_areas": ["Austin", "Round Rock", "Cedar Park", "Leander", "Georgetown"]
    }


def generate_content_for_template(business):
    """Generate content for the HVAC template."""
    return {
        "business": {
            "name": business["name"],
            "phone": business["phone_number"],
            "email": business["business_email"],
            "address": business["business_address"],
            "hours": "Mon-Fri 7AM-8PM, Sat-Sun 8AM-6PM, 24/7 Emergency Service",
            "description": f"{business['name']} is Austin's premier HVAC service provider, delivering exceptional heating, cooling, and air quality solutions since 1999. Our NATE-certified technicians combine decades of experience with cutting-edge technology.",
            "serviceAreas": business["service_areas"] + ["Lakeway", "Bee Cave", "Dripping Springs", "Manor", "Hutto"]
        },
        "hero": {
            "headline": "Austin's Most Trusted HVAC Experts",
            "subtitle": "24/7 Emergency Service • Same-Day Repairs • 100% Satisfaction Guaranteed • NATE Certified Technicians",
            "ctaButtons": [
                {"text": "Get Free Quote", "action": "open_quote", "style": "primary"},
                {"text": "Call Now", "action": "call", "style": "secondary"}
            ],
            "trustIndicators": ["Licensed & Insured", "25+ Years Experience", "A+ BBB Rating", "NATE Certified", "5-Star Reviews"],
            "showEmergencyBanner": True,
            "emergencyMessage": "🚨 HVAC Emergency? We're Available 24/7 - No Overtime Charges!"
        },
        "services": [
            {
                "title": "Emergency AC Repair",
                "description": "24/7 emergency air conditioning repair throughout Austin metro. Fast response, expert diagnosis, and reliable repairs for all AC brands and models.",
                "price": "From $99",
                "features": ["Same-day service", "All major brands", "Parts warranty", "Upfront pricing"],
                "isPopular": True
            },
            {
                "title": "Heating System Repair",
                "description": "Expert furnace and heating system repair",
                "price": "From $89",
                "features": ["Safety inspection", "Energy efficiency check", "Emergency service"]
            },
            {
                "title": "New HVAC Installation",
                "description": "Complete HVAC system installation and replacement",
                "price": "Free Quote",
                "features": ["Energy-efficient systems", "Financing available", "10-year warranty"]
            },
            {
                "title": "Maintenance Plans",
                "description": "Preventive maintenance to keep your system running",
                "price": "$25/month",
                "features": ["Bi-annual tune-ups", "Priority service", "20% off repairs"]
            }
        ],
        "seo": {
            "title": f"{business['name']} - Professional HVAC Services in Austin, TX | 24/7 Emergency Repair",
            "description": f"Expert HVAC services in Austin, TX. 24/7 emergency AC & heating repair, installation, and maintenance. Licensed & insured NATE-certified technicians. Call {business['phone_number']} for same-day service and free estimates.",
            "keywords": ["hvac austin tx", "ac repair austin", "heating repair austin", "hvac installation austin", "emergency hvac austin", "austin hvac contractor", "nate certified hvac austin", "hvac maintenance austin"]
        }
    }


def inject_content_into_template(content, website_builder_path):
    """Inject the generated content into the Next.js template."""
    
    template_file = website_builder_path / "app" / "page.tsx"
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return False
    
    # Read the template
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Convert content to JavaScript format
    content_js = json.dumps(content, indent=2)
    
    # Find the defaultContent declaration and replace it
    start_marker = "const defaultContent = {"
    end_marker = "export default function Home()"
    
    start_idx = template_content.find(start_marker)
    end_idx = template_content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ Could not find content markers in template")
        return False
    
    # Find the end of the defaultContent object
    brace_count = 0
    i = start_idx + len(start_marker) - 1
    while i < end_idx:
        if template_content[i] == '{':
            brace_count += 1
        elif template_content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
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
    
    print("✅ Content injected into template")
    return True


def build_nextjs_site(website_builder_path, output_path):
    """Build the Next.js site to static files."""
    
    print("🔨 Building Next.js site...")
    
    original_dir = os.getcwd()
    os.chdir(website_builder_path)
    
    try:
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
        
        # Copy the output
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


def main():
    """Main execution flow with automated deployment."""
    
    print("=" * 70)
    print("Hero365 Automated Website Deployment")
    print("=" * 70)
    
    # Paths
    backend_path = Path(__file__).parent.parent
    website_builder_path = backend_path.parent / "website-builder"
    build_output_path = backend_path / "build_output" / f"automated-{uuid.uuid4().hex[:8]}"
    
    # 1. Create test business
    print("\n1. Creating test business...")
    business = create_test_business()
    print(f"   Business: {business['name']}")
    
    # 2. Generate content
    print("\n2. Generating content...")
    content = generate_content_for_template(business)
    print(f"   Generated content for {len(content)} sections")
    
    # 3. Inject content
    print("\n3. Injecting content into template...")
    if not inject_content_into_template(content, website_builder_path):
        return 1
    
    # 4. Build the site
    print("\n4. Building static site...")
    build_result = build_nextjs_site(website_builder_path, build_output_path)
    if not build_result:
        return 1
    
    # Count files
    html_files = list(build_output_path.rglob("*.html"))
    total_files = list(build_output_path.rglob("*"))
    print(f"   Generated {len(html_files)} HTML pages")
    print(f"   Total files: {len([f for f in total_files if f.is_file()])}")
    
    # 5. Deploy (try existing project first, then API)
    print("\n5. Deploying to Cloudflare Pages...")
    
    # Try deploying to existing project first (fastest)
    url = deploy_using_existing_project(build_output_path)
    
    if not url:
        print("   Existing project deployment failed, trying API...")
        # Fallback to API deployment
        project_name = f"hvac-auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        url = asyncio.run(deploy_to_cloudflare_api(build_output_path, project_name))
    
    if url:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Automated deployment completed")
        print(f"🌐 Live Website: {url}")
        print("=" * 70)
        return 0
    else:
        print("\n❌ All deployment methods failed")
        return 1


if __name__ == "__main__":
    exit(main())
