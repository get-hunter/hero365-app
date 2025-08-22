#!/usr/bin/env python3
"""
Test script to deploy a professional website using real data from the API endpoints.
This script demonstrates the full integration between the professional data APIs
and the website deployment system.
"""

import asyncio
import httpx
import json
import subprocess
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.application.services.professional_data_service import ProfessionalDataService

async def test_real_data_deployment():
    """Test deploying a website with real data from the professional APIs."""
    
    print("🚀 Testing Professional Website Deployment with Real Data")
    print("=" * 60)
    
    # Configuration
    api_base_url = "http://localhost:8000"
    business_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    
    # Initialize the professional data service
    data_service = ProfessionalDataService(api_base_url)
    
    try:
        print("📊 Step 1: Fetching professional data from APIs...")
        
        # Fetch all data in parallel
        profile_task = data_service.get_professional_profile(business_id)
        services_task = data_service.get_professional_services(business_id)
        products_task = data_service.get_professional_products(business_id)
        
        profile, services, products = await asyncio.gather(
            profile_task, services_task, products_task
        )
        
        if not profile:
            print("❌ Failed to fetch professional profile")
            return
        
        print(f"✅ Profile fetched: {profile['business_name']}")
        print(f"✅ Services fetched: {len(services)} services")
        print(f"✅ Products fetched: {len(products)} products")
        
        print("\n📝 Step 2: Generating website content...")
        
        # Generate enhanced content using the real data
        website_content = {
            "hero": {
                "headline": f"{profile['business_name']} - {profile['description'][:50]}...",
                "subtitle": f"Serving {', '.join(profile['service_areas'][:3])} with {profile['years_in_business']}+ years of experience",
                "cta_text": "Get Free Estimate" if profile['emergency_service'] else "Schedule Service",
                "background_image": "/images/hvac-hero.jpg",
                "phone": profile['phone'],
                "rating": profile['average_rating'],
                "reviews": profile['total_reviews']
            },
            "services": {
                "title": f"Our {profile['trade_type'].upper()} Services",
                "subtitle": f"Professional {profile['trade_type']} services in {profile['service_areas'][0]}",
                "services": [
                    {
                        "name": service['name'],
                        "description": service['description'],
                        "price": f"From ${service['base_price']}" if service['base_price'] else "Free Estimate",
                        "features": [
                            f"{service['duration_minutes']} min service" if service['duration_minutes'] else "Quick response",
                            "Licensed professionals",
                            "Warranty included"
                        ],
                        "emergency": service['is_emergency']
                    }
                    for service in services[:4]  # Limit to 4 services
                ]
            },
            "products": {
                "title": "Featured Products",
                "subtitle": "High-quality products from trusted brands",
                "products": [
                    {
                        "name": product['name'],
                        "description": product['description'],
                        "price": product['price'],
                        "brand": product['brand'],
                        "in_stock": product['in_stock'],
                        "warranty": f"{product['warranty_years']} year warranty"
                    }
                    for product in products[:3]  # Limit to 3 products
                ]
            },
            "contact": {
                "business_name": profile['business_name'],
                "phone": profile['phone'],
                "email": profile['email'],
                "address": profile['address'],
                "service_areas": profile['service_areas'],
                "emergency_service": profile['emergency_service'],
                "certifications": profile['certifications']
            },
            "seo": {
                "title": f"{profile['business_name']} - Professional {profile['trade_type'].upper()} Services in {profile['service_areas'][0]}",
                "description": f"{profile['description']} Serving {', '.join(profile['service_areas'])}. {profile['average_rating']} stars from {profile['total_reviews']} reviews.",
                "keywords": [
                    f"{profile['trade_type']} {profile['service_areas'][0]}",
                    f"{profile['trade_type']} repair",
                    f"{profile['trade_type']} installation",
                    f"emergency {profile['trade_type']}",
                    profile['business_name'].lower()
                ]
            }
        }
        
        print("✅ Website content generated with real data")
        
        print("\n🏗️  Step 3: Building and deploying website...")
        
        # Save the content to a temporary file for the deployment script
        content_file = backend_dir / "temp_website_content.json"
        with open(content_file, 'w') as f:
            json.dump(website_content, f, indent=2)
        
        # Run the automated deployment script
        deployment_script = backend_dir / "scripts" / "automated_deployment.py"
        
        print("Running deployment script...")
        result = subprocess.run([
            sys.executable, str(deployment_script)
        ], capture_output=True, text=True, cwd=str(backend_dir.parent))
        
        if result.returncode == 0:
            print("✅ Website deployed successfully!")
            print(f"🌐 Website URL: https://hero365-websites.pages.dev/")
            
            # Parse deployment output for any URLs
            if "https://" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "https://" in line:
                        print(f"🔗 {line.strip()}")
        else:
            print("❌ Deployment failed:")
            print(result.stderr)
            print(result.stdout)
        
        # Clean up
        if content_file.exists():
            content_file.unlink()
        
        print("\n📊 Step 4: Deployment Summary")
        print(f"Business: {profile['business_name']}")
        print(f"Trade: {profile['trade_type'].upper()}")
        print(f"Services: {len(services)} services integrated")
        print(f"Products: {len(products)} products integrated")
        print(f"Service Areas: {', '.join(profile['service_areas'])}")
        print(f"Rating: {profile['average_rating']}/5.0 ({profile['total_reviews']} reviews)")
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # No cleanup needed - aiohttp sessions are closed automatically
        pass

if __name__ == "__main__":
    asyncio.run(test_real_data_deployment())
