#!/usr/bin/env python3
"""
Deploy Professional Website using Hero365 Website Builder System
Creates a real professional HVAC contractor website using our templates and system.
"""

import asyncio
import sys
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add the backend app to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.entities.website import WebsiteStatus
from app.domain.entities.business import Business, TradeCategory, ResidentialTrade, CompanySize


async def create_professional_business() -> Business:
    """Create a real HVAC professional business."""
    return Business(
        id=uuid4(),
        name="Elite HVAC Solutions",
        industry="HVAC Services",
        company_size=CompanySize.SMALL,
        business_email="contact@elitehvacsolutions.com",
        phone_number="+1-555-HVAC-PRO",
        business_address="1234 Industrial Blvd, Austin, TX 78704",
        trade_category=TradeCategory.RESIDENTIAL,
        residential_trades=[ResidentialTrade.HVAC],
        service_areas=["Austin", "Round Rock", "Cedar Park", "Georgetown", "Pflugerville"],
        description="Professional HVAC services with over 15 years of experience. We specialize in residential heating, cooling, and air quality solutions.",
        website="https://elitehvacsolutions.com"
    )


async def create_professional_branding(business_id) -> dict:
    """Create professional branding for the HVAC business."""
    return {
        "id": str(uuid4()),
        "business_id": str(business_id),
        "logo_url": "https://example.com/elite-hvac-logo.png",
        "primary_color": "#1E3A8A",  # Professional blue
        "secondary_color": "#3B82F6",  # Lighter blue
        "accent_color": "#EF4444",  # Emergency red
        "font_family": "Inter"
    }


async def create_hvac_template() -> dict:
    """Create a professional HVAC template."""
    return {
        "id": str(uuid4()),
        "trade_type": ResidentialTrade.HVAC.value,
        "trade_category": TradeCategory.RESIDENTIAL,
        "name": "Professional HVAC Contractor",
        "description": "Modern, conversion-optimized template for HVAC professionals",
        "variant": "modern",
        "structure": {
            "pages": [
                {
                    "path": "/",
                    "name": "Home",
                    "sections": [
                        {"type": "hero", "order": 1},
                        {"type": "services", "order": 2},
                        {"type": "emergency", "order": 3},
                        {"type": "about", "order": 4},
                        {"type": "contact", "order": 5}
                    ]
                }
            ]
        },
        "content_fields": {
            "hero": ["headline", "subheadline", "cta_text"],
            "services": ["service_description"],
            "about": ["body_text"],
            "meta": ["meta_title", "meta_description"]
        },
        "default_content": {
            "hero": {
                "headline": "Austin's Most Trusted HVAC Professionals",
                "subheadline": "Expert heating, cooling, and air quality solutions for your home. Licensed, insured, and available 24/7 for emergencies.",
                "cta_text": "Get Free Estimate"
            },
            "services": {
                "heating": "Professional heating system installation, repair, and maintenance",
                "cooling": "Expert air conditioning services and energy-efficient solutions",
                "air_quality": "Indoor air quality testing and improvement systems",
                "emergency": "24/7 emergency HVAC services when you need us most"
            },
            "about": {
                "description": "Elite HVAC Solutions has been serving the Austin area for over 15 years. Our certified technicians provide reliable, professional service with a focus on customer satisfaction and energy efficiency."
            }
        },
        "seo_config": {
            "meta_title_template": "{business_name} - Professional HVAC Services in {service_area}",
            "meta_description_template": "Expert HVAC services in {service_area}. {business_name} provides heating, cooling, and air quality solutions. Licensed, insured, and available 24/7.",
            "schema_types": ["LocalBusiness", "HVACBusiness", "Service"]
        }
    }


async def create_professional_website(business_id, template_id) -> dict:
    """Create a professional website entity."""
    return {
        "id": str(uuid4()),
        "business_id": str(business_id),
        "template_id": str(template_id),
        "hostname": None,
        "subdomain": "elite-hvac-solutions.hero365.ai",
        "status": WebsiteStatus.DRAFT,
        "theme_config": {
            "primary_color": "#1E3A8A",
            "secondary_color": "#3B82F6",
            "accent_color": "#EF4444",
            "font_family": "Inter"
        },
        "content_overrides": {
            "hero": {
                "headline": "Austin's Most Trusted HVAC Professionals",
                "subheadline": "Expert heating, cooling, and air quality solutions for your home. Licensed, insured, and available 24/7 for emergencies."
            }
        },
        "primary_trade": ResidentialTrade.HVAC.value,
        "service_areas": ["Austin", "Round Rock", "Cedar Park", "Georgetown", "Pflugerville"],
        "seo_settings": {
            "meta_title": "Elite HVAC Solutions - Professional HVAC Services in Austin, TX",
            "meta_description": "Expert HVAC services in Austin, TX. Elite HVAC Solutions provides heating, cooling, and air quality solutions. Licensed, insured, and available 24/7.",
            "keywords": ["HVAC Austin", "heating repair", "air conditioning", "Austin HVAC contractor", "emergency HVAC"]
        }
    }


async def generate_professional_website_html(business: Business, branding: dict, template: dict, website: dict) -> str:
    """Generate professional HTML for the HVAC contractor using our template system."""
    
    # This simulates our content generation service
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{website['seo_settings']['meta_title']}</title>
    <meta name="description" content="{website['seo_settings']['meta_description']}">
    <meta name="keywords" content="{', '.join(website['seo_settings']['keywords'])}"
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{website['seo_settings']['meta_title']}">
    <meta property="og:description" content="{website['seo_settings']['meta_description']}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://{website['subdomain']}"
    
    <!-- Local Business Schema -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": "https://{website['subdomain']}",
        "name": "{business.name}",
        "description": "{business.description}",
        "url": "https://{website['subdomain']}",
        "telephone": "{business.phone_number}",
        "email": "{business.business_email}",
        "address": {{
            "@type": "PostalAddress",
            "streetAddress": "{business.business_address.split(',')[0]}",
            "addressLocality": "{business.business_address.split(',')[1].strip()}",
            "addressRegion": "{business.business_address.split(',')[2].strip().split()[0]}",
            "postalCode": "{business.business_address.split(',')[2].strip().split()[1]}"
        }},
        "areaServed": {business.service_areas},
        "serviceType": ["HVAC Services", "Heating Repair", "Air Conditioning", "Indoor Air Quality"],
        "priceRange": "$$",
        "openingHours": "Mo-Fr 08:00-18:00, Sa 09:00-17:00",
        "hasOfferCatalog": {{
            "@type": "OfferCatalog",
            "name": "HVAC Services",
            "itemListElement": [
                {{
                    "@type": "Offer",
                    "itemOffered": {{
                        "@type": "Service",
                        "name": "Heating System Repair",
                        "description": "Professional heating system diagnosis and repair"
                    }}
                }},
                {{
                    "@type": "Offer",
                    "itemOffered": {{
                        "@type": "Service",
                        "name": "Air Conditioning Installation",
                        "description": "Expert AC installation and replacement services"
                    }}
                }}
            ]
        }}
    }}
    </script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: {website['theme_config']['font_family']}, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        .hero {{
            background: linear-gradient(135deg, {website['theme_config']['primary_color']} 0%, {website['theme_config']['secondary_color']} 100%);
            color: white;
            padding: 100px 20px;
            text-align: center;
            min-height: 70vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .hero-content {{
            max-width: 800px;
        }}
        
        .hero h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .hero p {{
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.95;
        }}
        
        .cta-button {{
            background: {website['theme_config']['accent_color']};
            color: white;
            padding: 18px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
        }}
        
        .emergency-banner {{
            background: {website['theme_config']['accent_color']};
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        
        .services {{
            padding: 80px 20px;
            background: #f8fafc;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .section-title {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: {website['theme_config']['primary_color']};
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .service-card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            border-left: 4px solid {website.theme_config['primary_color']};
        }}
        
        .service-card:hover {{
            transform: translateY(-5px);
        }}
        
        .service-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
            color: {website.theme_config['primary_color']};
        }}
        
        .about {{
            padding: 80px 20px;
            background: white;
        }}
        
        .about-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }}
        
        .contact {{
            background: {website.theme_config['primary_color']};
            color: white;
            padding: 80px 20px;
            text-align: center;
        }}
        
        .contact-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}
        
        .contact-item {{
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 10px;
        }}
        
        .contact-item h3 {{
            margin-bottom: 1rem;
            color: #fbbf24;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2.5rem; }}
            .about-content {{ grid-template-columns: 1fr; }}
            .services-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="emergency-banner">
        🚨 24/7 Emergency HVAC Services Available - Call {business.phone_number} 🚨
    </div>
    
    <section class="hero">
        <div class="hero-content">
            <h1>{website.content_overrides['hero']['headline']}</h1>
            <p>{website.content_overrides['hero']['subheadline']}</p>
            <a href="tel:{business.phone_number}" class="cta-button">Call Now for Free Estimate</a>
        </div>
    </section>
    
    <section class="services">
        <div class="container">
            <h2 class="section-title">Our Professional HVAC Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">🔥</div>
                    <h3>Heating Systems</h3>
                    <p>Expert furnace repair, installation, and maintenance. We service all major brands and provide energy-efficient solutions.</p>
                    <ul>
                        <li>Furnace repair & replacement</li>
                        <li>Heat pump services</li>
                        <li>Ductwork installation</li>
                        <li>Energy efficiency upgrades</li>
                    </ul>
                </div>
                
                <div class="service-card">
                    <div class="service-icon">❄️</div>
                    <h3>Air Conditioning</h3>
                    <p>Complete AC services from installation to emergency repairs. Stay cool with our reliable cooling solutions.</p>
                    <ul>
                        <li>AC installation & replacement</li>
                        <li>Emergency AC repair</li>
                        <li>Preventive maintenance</li>
                        <li>Duct cleaning services</li>
                    </ul>
                </div>
                
                <div class="service-card">
                    <div class="service-icon">🌬️</div>
                    <h3>Indoor Air Quality</h3>
                    <p>Improve your home's air quality with our advanced filtration and purification systems.</p>
                    <ul>
                        <li>Air purification systems</li>
                        <li>Humidity control</li>
                        <li>UV light installation</li>
                        <li>Air quality testing</li>
                    </ul>
                </div>
                
                <div class="service-card">
                    <div class="service-icon">⚡</div>
                    <h3>Emergency Services</h3>
                    <p>24/7 emergency HVAC services when you need us most. Fast response times guaranteed.</p>
                    <ul>
                        <li>24/7 emergency repairs</li>
                        <li>Same-day service</li>
                        <li>Weekend availability</li>
                        <li>Holiday emergency service</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>
    
    <section class="about">
        <div class="container">
            <div class="about-content">
                <div>
                    <h2 class="section-title">Why Choose Elite HVAC Solutions?</h2>
                    <p>{business.description}</p>
                    <br>
                    <ul>
                        <li>✅ Licensed & Insured Technicians</li>
                        <li>✅ 15+ Years of Experience</li>
                        <li>✅ 24/7 Emergency Service</li>
                        <li>✅ Upfront Pricing - No Hidden Fees</li>
                        <li>✅ 100% Satisfaction Guarantee</li>
                        <li>✅ Energy-Efficient Solutions</li>
                    </ul>
                </div>
                <div>
                    <h3>Service Areas</h3>
                    <p>We proudly serve the following areas:</p>
                    <ul>
                        {"".join([f"<li>{area}</li>" for area in business.service_areas])}
                    </ul>
                    <br>
                    <h3>Certifications</h3>
                    <ul>
                        <li>NATE Certified Technicians</li>
                        <li>EPA Certified</li>
                        <li>Texas State Licensed</li>
                        <li>Better Business Bureau A+ Rating</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>
    
    <section class="contact">
        <div class="container">
            <h2>Ready to Get Started?</h2>
            <p>Contact Elite HVAC Solutions today for professional HVAC services you can trust.</p>
            
            <div class="contact-info">
                <div class="contact-item">
                    <h3>📞 Call Us</h3>
                    <p><strong>{business.phone_number}</strong></p>
                    <p>Available 24/7 for emergencies</p>
                </div>
                
                <div class="contact-item">
                    <h3>📧 Email Us</h3>
                    <p>{business.business_email}</p>
                    <p>Get a free estimate</p>
                </div>
                
                <div class="contact-item">
                    <h3>📍 Service Area</h3>
                    <p>{business.business_address}</p>
                    <p>Serving {", ".join(business.service_areas)}</p>
                </div>
                
                <div class="contact-item">
                    <h3>⏰ Hours</h3>
                    <p>Mon-Fri: 8:00 AM - 6:00 PM</p>
                    <p>Sat: 9:00 AM - 5:00 PM</p>
                    <p>Emergency: 24/7</p>
                </div>
            </div>
        </div>
    </section>
</body>
</html>"""
    
    return html_content


async def deploy_professional_website():
    """Deploy a professional HVAC contractor website using our system."""
    
    print("🏗️  Hero365 Professional Website Deployment")
    print("=" * 60)
    
    try:
        # 1. Create professional business entities
        print("1. Creating professional business entities...")
        business = await create_professional_business()
        branding = await create_professional_branding(business.id)
        template = await create_hvac_template()
        website = await create_professional_website(business.id, template["id"])
        
        print(f"   ✅ Business: {business.name}")
        print(f"   ✅ Industry: {business.industry}")
        print(f"   ✅ Service Areas: {', '.join(business.service_areas)}")
        print(f"   ✅ Template: {template['name']}")
        print(f"   ✅ Website ID: {website['id']}")
        
        # 2. Generate professional website content
        print(f"\n2. Generating professional website content...")
        html_content = await generate_professional_website_html(business, branding, template, website)
        
        # Create build directory
        build_dir = Path(__file__).parent.parent / "build_output" / "professional-hvac-site"
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Write HTML file
        with open(build_dir / "index.html", "w") as f:
            f.write(html_content)
        
        # Create robots.txt
        robots_txt = f"""User-agent: *
Allow: /

Sitemap: https://{website.subdomain}/sitemap.xml"""
        
        with open(build_dir / "robots.txt", "w") as f:
            f.write(robots_txt)
        
        # Create sitemap.xml
        sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://{website.subdomain}/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
        
        with open(build_dir / "sitemap.xml", "w") as f:
            f.write(sitemap_xml)
        
        file_count = len(list(build_dir.rglob('*')))
        build_size = sum(f.stat().st_size for f in build_dir.rglob('*') if f.is_file()) // 1024
        
        print(f"   ✅ Professional website generated")
        print(f"   📊 Files: {file_count}, Size: {build_size} KB")
        print(f"   📁 Build path: {build_dir}")
        
        # 3. Deploy using Wrangler CLI directly
        print(f"\n3. Deploying to Cloudflare Pages...")
        
        # Create a unique project name
        project_name = f"elite-hvac-{str(uuid4())[:8]}"
        
        # Deploy using Wrangler
        import subprocess
        import os
        
        env = os.environ.copy()
        env['CLOUDFLARE_API_TOKEN'] = "muGRINW0SuRdhq5otaMRwMf0piAn24wFdRgrGiXl"
        env['CLOUDFLARE_ACCOUNT_ID'] = "4e131688804526ec202c7d530e635307"
        
        cmd = [
            'wrangler', 'pages', 'deploy', str(build_dir),
            '--project-name', project_name,
            '--commit-dirty=true'
        ]
        
        print(f"   🚀 Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse output to get deployment URL
            output_lines = result.stdout.split('\n')
            deployment_url = None
            
            for line in output_lines:
                if 'https://' in line and '.pages.dev' in line:
                    import re
                    url_match = re.search(r'https://[a-zA-Z0-9\-\.]+\.pages\.dev', line)
                    if url_match:
                        deployment_url = url_match.group(0)
                        break
            
            if not deployment_url:
                deployment_url = f"https://{project_name}.pages.dev"
            
            deployment_info = {
                'url': deployment_url,
                'project_name': project_name,
                'status': 'deployed'
            }
            
            website['status'] = 'deployed'
            website['hostname'] = deployment_url.replace('https://', '')
            website['deployment_info'] = deployment_info
        else:
            raise Exception(f"Deployment failed: {result.stderr}")
        
        print(f"   ✅ Deployment successful!")
        print(f"   🌐 Live URL: {deployment_info.get('url')}")
        print(f"   📋 Project: {deployment_info.get('project_name')}")
        
        # 4. Summary
        print(f"\n" + "=" * 60)
        print(f"🎉 PROFESSIONAL WEBSITE DEPLOYED SUCCESSFULLY!")
        print(f"=" * 60)
        print(f"Business: {business.name}")
        print(f"Industry: {business.industry} ({business.trade_category.value.title()})")
        print(f"Service Areas: {', '.join(business.service_areas)}")
        print(f"Website URL: {deployment_info.get('url')}")
        print(f"Template: {template['name']} ({template['variant']})")
        print(f"Deployment: {datetime.utcnow()}")
        
        print(f"\n🎯 Website Features:")
        print(f"✅ Professional design with business branding")
        print(f"✅ SEO optimized with local business schema")
        print(f"✅ Mobile responsive and fast loading")
        print(f"✅ Emergency contact prominently displayed")
        print(f"✅ Service area targeting")
        print(f"✅ Call-to-action buttons for conversions")
        
        print(f"\n💰 Revenue Potential:")
        print(f"This website could generate $199-299/month in recurring revenue")
        print(f"The Hero365 Website Builder successfully created a professional contractor website!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DEPLOYMENT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(deploy_professional_website())
    
    if success:
        print(f"\n🚀 Professional website deployment completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Professional website deployment failed.")
        sys.exit(1)
