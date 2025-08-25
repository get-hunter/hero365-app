#!/usr/bin/env python3
"""
Deploy Simple Professional Website to Cloudflare Pages

This script creates and deploys a simplified professional website template to Cloudflare Pages.
"""

import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

class SimpleWebsiteDeployer:
    """Deploy simple professional websites to Cloudflare Pages."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.output_dir = self.project_root / "build_output"
    
    def create_sample_business(self, business_type: str = "comprehensive") -> dict:
        """Create sample business data for deployment."""
        
        base_id = str(uuid.uuid4())
        
        if business_type == "hvac_specialist":
            return {
                "id": base_id,
                "name": "Arctic Air HVAC Specialists",
                "industry": "HVAC Services",
                "phone_number": "(512) 555-COOL",
                "address": "1234 Cool Air Drive",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78745",
                "trades": ["HVAC"],
                "service_areas": ["Austin", "South Austin", "Kyle", "Buda", "Dripping Springs"],
                "description": "Your trusted HVAC specialists in Austin. We provide professional heating, cooling, and air quality solutions with 24/7 emergency service."
            }
        else:  # comprehensive
            return {
                "id": base_id,
                "name": "Elite Home Services Austin",
                "industry": "Home Services", 
                "phone_number": "(512) 555-ELITE",
                "address": "4567 Professional Blvd",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78731",
                "trades": ["HVAC", "Plumbing", "Electrical"],
                "service_areas": [
                    "Austin", "Round Rock", "Cedar Park", "Pflugerville", 
                    "Georgetown", "Leander", "Liberty Hill", "Lago Vista"
                ],
                "description": "Austin's premier home services provider specializing in HVAC, plumbing, and electrical solutions. Licensed, insured, and committed to excellence since 2018."
            }
    
    def create_simple_nextjs_site(self, deployment_id: str, business: dict) -> Path:
        """Create a simple Next.js site structure."""
        
        build_dir = self.output_dir / deployment_id
        
        # Clean existing build directory
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Next.js project structure
        self.create_package_json(build_dir)
        self.create_next_config(build_dir)
        self.create_tsconfig(build_dir)
        self.create_tailwind_config(build_dir)
        self.create_postcss_config(build_dir)
        
        # Create pages
        self.create_homepage(build_dir, business)
        self.create_about_page(build_dir, business)
        self.create_contact_page(build_dir, business)
        self.create_layout(build_dir, business)
        
        # Create styles
        self.create_globals_css(build_dir)
        
        return build_dir
    
    def create_package_json(self, build_dir: Path):
        """Create package.json for the Next.js project."""
        
        package_json = {
            "name": "professional-website",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "export": "next build"
            },
            "dependencies": {
                "clsx": "^2.1.1",
                "lucide-react": "^0.541.0",
                "next": "15.5.0",
                "react": "19.1.0",
                "react-dom": "19.1.0"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^19",
                "@types/react-dom": "^19",
                "tailwindcss": "^3.4.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0",
                "typescript": "^5"
            }
        }
        
        with open(build_dir / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
    
    def create_next_config(self, build_dir: Path):
        """Create next.config.js for static export."""
        
        config = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  typescript: {
    ignoreBuildErrors: true
  }
}

module.exports = nextConfig
'''
        
        with open(build_dir / "next.config.js", 'w') as f:
            f.write(config)
    
    def create_tsconfig(self, build_dir: Path):
        """Create tsconfig.json."""
        
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [
                    {
                        "name": "next"
                    }
                ],
                "paths": {
                    "@/*": ["./*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        with open(build_dir / "tsconfig.json", 'w') as f:
            json.dump(tsconfig, f, indent=2)
    
    def create_tailwind_config(self, build_dir: Path):
        """Create tailwind.config.js."""
        
        config = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        
        with open(build_dir / "tailwind.config.js", 'w') as f:
            f.write(config)
    
    def create_postcss_config(self, build_dir: Path):
        """Create postcss.config.js for Tailwind processing."""
        
        config = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
        
        with open(build_dir / "postcss.config.js", 'w') as f:
            f.write(config)
    
    def create_globals_css(self, build_dir: Path):
        """Create global CSS file."""
        
        css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-start-rgb: 0, 0, 0;
    --background-end-rgb: 0, 0, 0;
  }
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}
'''
        
        app_dir = build_dir / "app"
        app_dir.mkdir(exist_ok=True)
        
        with open(app_dir / "globals.css", 'w') as f:
            f.write(css)
    
    def create_layout(self, build_dir: Path, business: dict):
        """Create root layout."""
        
        trades_str = ", ".join(business["trades"])
        # Escape single quotes in strings for JavaScript
        escaped_name = business["name"].replace("'", "\\'")
        escaped_description = business["description"].replace("'", "\\'")
        
        layout = f'''import './globals.css'
import type {{ Metadata }} from 'next'

export const metadata: Metadata = {{
  title: '{escaped_name} - Professional {trades_str} Services',
  description: '{escaped_description}',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body>
        <nav className="bg-blue-900 text-white p-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <h1 className="text-xl font-bold">{business["name"]}</h1>
            <div className="space-x-4">
              <a href="/" className="hover:text-blue-200">Home</a>
              <a href="/about" className="hover:text-blue-200">About</a>
              <a href="/contact" className="hover:text-blue-200">Contact</a>
            </div>
          </div>
        </nav>
        {{children}}
        <footer className="bg-gray-900 text-white p-8 mt-16">
          <div className="max-w-7xl mx-auto text-center">
            <p>&copy; 2024 {business["name"]}. All rights reserved.</p>
            <p className="mt-2">📞 {business["phone_number"]} | 📧 Contact us for all your {trades_str} needs</p>
          </div>
        </footer>
      </body>
    </html>
  )
}}
'''
        
        app_dir = build_dir / "app"
        app_dir.mkdir(exist_ok=True)
        
        with open(app_dir / "layout.tsx", 'w') as f:
            f.write(layout)
    
    def create_homepage(self, build_dir: Path, business: dict):
        """Create homepage."""
        
        # Generate service cards
        service_cards = []
        for trade in business["trades"]:
            service_cards.append(f'''
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-2xl font-bold text-blue-900 mb-4">{trade} Services</h3>
              <ul className="space-y-2">
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Installation & Repair
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Emergency Service
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Maintenance Plans
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Free Estimates
                </li>
              </ul>
              <button className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                Learn More
              </button>
            </div>''')
        
        # Generate service area cards
        area_cards = []
        for area in business["service_areas"]:
            area_cards.append(f'''
              <div className="bg-blue-50 p-4 rounded-lg">
                <span className="font-semibold text-blue-900">{area}</span>
              </div>''')
        
        trades_str = ", ".join(business["trades"])
        escaped_description = business["description"].replace("'", "\\'")
        
        homepage = f'''export default function Home() {{
  return (
    <div className="min-h-screen">
      {{/* Hero Section */}}
      <section className="bg-gradient-to-r from-blue-900 to-blue-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Quality {trades_str} Services in {business["city"]}, {business["state"]}
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            {escaped_description}
          </p>
          <div className="space-x-4">
            <button className="bg-yellow-500 hover:bg-yellow-600 text-blue-900 font-bold py-3 px-8 rounded-lg text-lg">
              Get Free Quote
            </button>
            <button className="border-2 border-white hover:bg-white hover:text-blue-900 text-white font-bold py-3 px-8 rounded-lg text-lg">
              Call {business["phone_number"]}
            </button>
          </div>
        </div>
      </section>

      {{/* Features */}}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div className="p-6">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🛡️</span>
              </div>
              <h3 className="font-bold text-lg">Licensed & Insured</h3>
              <p className="text-gray-600">Fully licensed and insured for your peace of mind</p>
            </div>
            <div className="p-6">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🚨</span>
              </div>
              <h3 className="font-bold text-lg">24/7 Emergency</h3>
              <p className="text-gray-600">Emergency services available around the clock</p>
            </div>
            <div className="p-6">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="font-bold text-lg">Same-Day Service</h3>
              <p className="text-gray-600">Fast response times for urgent repairs</p>
            </div>
            <div className="p-6">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✅</span>
              </div>
              <h3 className="font-bold text-lg">Satisfaction Guaranteed</h3>
              <p className="text-gray-600">100% satisfaction guarantee on all work</p>
            </div>
          </div>
        </div>
      </section>

      {{/* Services */}}
      <section className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Our Services</h2>
            <p className="text-xl text-gray-600">Professional {trades_str.lower()} services you can trust</p>
          </div>
          
          <div className="grid md:grid-cols-{min(3, len(business["trades"]))} gap-8">
            {''.join(service_cards)}
          </div>
        </div>
      </section>

      {{/* Service Areas */}}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-8">Service Areas</h2>
          <p className="text-xl text-gray-600 mb-8">Proudly serving customers throughout the {business["city"]} area</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {''.join(area_cards)}
          </div>
        </div>
      </section>
    </div>
  )
}}'''
        
        app_dir = build_dir / "app"
        app_dir.mkdir(exist_ok=True)
        
        with open(app_dir / "page.tsx", 'w') as f:
            f.write(homepage)
    
    def create_about_page(self, build_dir: Path, business: dict):
        """Create about page."""
        
        trades_str = ", ".join(business["trades"])
        area_items = []
        for area in business["service_areas"]:
            area_items.append(f'<div className="text-blue-600 font-medium">{area}</div>')
        
        escaped_name = business["name"].replace("'", "\\'")
        escaped_description = business["description"].replace("'", "\\'")
        
        about_page = f'''export default function About() {{
  return (
    <div className="min-h-screen py-16">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">About {escaped_name}</h1>
        
        <div className="prose max-w-none">
          <p className="text-xl text-gray-600 mb-6">
            {escaped_description}
          </p>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Services</h2>
          <p className="text-gray-600 mb-6">
            We specialize in {trades_str.lower()} services and have been serving the {business["city"]} area with pride and professionalism.
          </p>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Why Choose Us?</h2>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start">
              <span className="text-green-500 mr-2 mt-1">✓</span>
              Licensed and insured professionals
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2 mt-1">✓</span>
              24/7 emergency service available
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2 mt-1">✓</span>
              Competitive pricing with no hidden fees
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2 mt-1">✓</span>
              100% satisfaction guarantee
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2 mt-1">✓</span>
              Local family-owned business
            </li>
          </ul>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-4 mt-8">Service Areas</h2>
          <p className="text-gray-600 mb-4">We proudly serve customers in:</p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {''.join(area_items)}
          </div>
        </div>
      </div>
    </div>
  )
}}'''
        
        about_dir = build_dir / "app" / "about"
        about_dir.mkdir(parents=True, exist_ok=True)
        
        with open(about_dir / "page.tsx", 'w') as f:
            f.write(about_page)
    
    def create_contact_page(self, build_dir: Path, business: dict):
        """Create contact page."""
        
        service_options = []
        for trade in business["trades"]:
            service_options.append(f'<option value="{trade}">{trade}</option>')
        
        contact_page = f'''export default function Contact() {{
  return (
    <div className="min-h-screen py-16">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">Contact Us</h1>
        
        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Get in Touch</h2>
            <p className="text-gray-600 mb-6">
              Ready to schedule service or have a question? Contact us today!
            </p>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <span className="text-2xl mr-4">📞</span>
                <div>
                  <div className="font-semibold">Phone</div>
                  <div className="text-blue-600 font-bold text-lg">{business["phone_number"]}</div>
                </div>
              </div>
              
              <div className="flex items-center">
                <span className="text-2xl mr-4">📍</span>
                <div>
                  <div className="font-semibold">Address</div>
                  <div className="text-gray-600">
                    {business["address"]}<br/>
                    {business["city"]}, {business["state"]} {business["zip_code"]}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center">
                <span className="text-2xl mr-4">🕒</span>
                <div>
                  <div className="font-semibold">Hours</div>
                  <div className="text-gray-600">
                    24/7 Emergency Service Available<br/>
                    Regular Hours: Mon-Fri 8AM-6PM
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="text-red-800 font-bold mb-2">Emergency Service</h3>
              <p className="text-red-700">
                Need immediate assistance? Call us now at {business["phone_number"]} for 24/7 emergency service.
              </p>
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Request Service</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input type="text" className="w-full px-3 py-2 border border-gray-300 rounded-md" required />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                <input type="tel" className="w-full px-3 py-2 border border-gray-300 rounded-md" required />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Service Needed</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option>Select Service...</option>
                  {''.join(service_options)}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                <textarea rows={{4}} className="w-full px-3 py-2 border border-gray-300 rounded-md"></textarea>
              </div>
              
              <button type="submit" className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 font-semibold">
                Request Service
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}}'''
        
        contact_dir = build_dir / "app" / "contact"
        contact_dir.mkdir(parents=True, exist_ok=True)
        
        with open(contact_dir / "page.tsx", 'w') as f:
            f.write(contact_page)
    
    def build_nextjs_website(self, build_dir: Path) -> bool:
        """Build the Next.js website for static export."""
        
        print(f"📦 Building Next.js website...")
        
        try:
            # Install dependencies
            print(f"   Installing dependencies...")
            result = subprocess.run(
                ['npm', 'install'], 
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"❌ npm install failed: {result.stderr}")
                return False
            
            # Build the website
            print(f"   Building website...")
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"❌ Build failed: {result.stderr}")
                return False
                
            print(f"✅ Website built successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"❌ Build timed out")
            return False
        except Exception as e:
            print(f"❌ Build failed: {str(e)}")
            return False
    
    def deploy_to_cloudflare_pages(self, build_dir: Path, deployment_id: str, project_name: str = None) -> dict:
        """Deploy the built website to Cloudflare Pages."""
        
        out_dir = build_dir / "out"
        
        if not out_dir.exists():
            return {"success": False, "error": "Build output directory not found"}
        
        # Use deployment_id as project name if not specified
        cf_project_name = project_name or f"hero365-{deployment_id[:8]}"
        
        print(f"🚀 Deploying to Cloudflare Pages...")
        print(f"   Project: {cf_project_name}")
        
        try:
            # Check if wrangler is authenticated
            auth_check = subprocess.run(
                ['wrangler', 'whoami'],
                capture_output=True,
                text=True
            )
            
            if auth_check.returncode != 0:
                print(f"⚠️  Wrangler not authenticated. Please run: wrangler login")
                return {"success": False, "error": "Wrangler authentication required"}
            
            # Deploy to Cloudflare Pages
            deploy_result = subprocess.run([
                'wrangler', 'pages', 'deploy', str(out_dir),
                '--project-name', cf_project_name
            ], capture_output=True, text=True, timeout=300)
            
            if deploy_result.returncode == 0:
                # Parse deployment URL from output
                output = deploy_result.stdout
                url = None
                
                # Look for deployment URL in output
                for line in output.split('\n'):
                    if 'https://' in line and '.pages.dev' in line:
                        # Extract URL from the line
                        words = line.split()
                        for word in words:
                            if 'https://' in word and '.pages.dev' in word:
                                url = word
                                break
                        if url:
                            break
                
                if not url:
                    # Construct expected URL
                    url = f"https://{cf_project_name}.pages.dev"
                
                print(f"✅ Deployment successful!")
                print(f"   🌐 Website URL: {url}")
                
                return {
                    "success": True,
                    "url": url,
                    "project_name": cf_project_name,
                    "deployment_id": deployment_id
                }
            else:
                error_msg = deploy_result.stderr or deploy_result.stdout
                print(f"❌ Cloudflare deployment failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Deployment timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "wrangler command not found. Please install Cloudflare Wrangler CLI"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def deploy_simple_website(self, business_type: str = "comprehensive", project_name: str = None) -> dict:
        """Deploy a complete simple professional website to Cloudflare Pages."""
        
        deployment_id = str(uuid.uuid4())
        
        print(f"🚀 Deploying Simple Professional Website")
        print(f"=" * 60)
        print(f"Business Type: {business_type.title()}")
        print(f"Deployment ID: {deployment_id}")
        
        try:
            # Step 1: Create sample business
            print(f"\n1️⃣ Creating business data...")
            business = self.create_sample_business(business_type)
            
            print(f"   Business: {business['name']}")
            print(f"   Location: {business['city']}, {business['state']}")
            print(f"   Services: {', '.join(business['trades'])}")
            print(f"   Service Areas: {len(business['service_areas'])} locations")
            
            # Step 2: Create Next.js site
            print(f"\n2️⃣ Creating Next.js site...")
            build_dir = self.create_simple_nextjs_site(deployment_id, business)
            print(f"   Build directory: {build_dir}")
            
            # Step 3: Build website
            print(f"\n3️⃣ Building website...")
            build_success = self.build_nextjs_website(build_dir)
            
            if not build_success:
                return {
                    "success": False,
                    "error": "Website build failed",
                    "deployment_id": deployment_id
                }
            
            # Step 4: Deploy to Cloudflare
            print(f"\n4️⃣ Deploying to Cloudflare Pages...")
            deployment_result = self.deploy_to_cloudflare_pages(build_dir, deployment_id, project_name)
            
            if deployment_result["success"]:
                print(f"\n🎉 Deployment Complete!")
                print(f"=" * 60)
                print(f"✅ Simple professional website deployed successfully")
                print(f"🌐 Website URL: {deployment_result['url']}")
                print(f"📋 Project: {deployment_result['project_name']}")
                print(f"🏢 Business: {business['name']}")
                print(f"📍 Location: {business['city']}, {business['state']}")
                print(f"🔧 Services: {', '.join(business['trades'])}")
                
                return {
                    "success": True,
                    "url": deployment_result["url"],
                    "project_name": deployment_result["project_name"],
                    "deployment_id": deployment_id,
                    "business": business
                }
            else:
                print(f"\n❌ Deployment failed: {deployment_result['error']}")
                return deployment_result
                
        except Exception as e:
            print(f"\n❌ Deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "deployment_id": deployment_id
            }
        finally:
            # Optional: Clean up build directory
            if '--keep-build' not in sys.argv:
                try:
                    if 'build_dir' in locals():
                        shutil.rmtree(build_dir)
                        print(f"🧹 Cleaned up build directory")
                except:
                    pass


def main():
    """Main deployment function."""
    
    deployer = SimpleWebsiteDeployer()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        business_type = sys.argv[1]
        project_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"🎯 Single deployment: {business_type}")
        result = deployer.deploy_simple_website(business_type, project_name)
        
        if result["success"]:
            print(f"\n✅ Success! Visit: {result['url']}")
            return True
        else:
            print(f"\n❌ Failed: {result['error']}")
            return False
    else:
        print(f"🔄 Deploying comprehensive business website...")
        result = deployer.deploy_simple_website("comprehensive")
        
        if result["success"]:
            print(f"\n🎉 Website deployed successfully!")
            return True
        else:
            print(f"\n❌ Deployment failed")
            return False


if __name__ == "__main__":
    print(f"☁️ Simple Cloudflare Pages Professional Website Deployment")
    print(f"Usage:")
    print(f"  python scripts/deploy_simple_website.py                        # Deploy comprehensive business")
    print(f"  python scripts/deploy_simple_website.py comprehensive          # Deploy comprehensive business")
    print(f"  python scripts/deploy_simple_website.py hvac_specialist        # Deploy HVAC specialist")
    print(f"  python scripts/deploy_simple_website.py comprehensive my-site  # Deploy with custom project name")
    print(f"")
    
    success = main()
    sys.exit(0 if success else 1)