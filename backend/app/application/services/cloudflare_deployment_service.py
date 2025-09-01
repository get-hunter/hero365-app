"""
Cloudflare Deployment Service - 10X Engineer Approach
Deploy websites to Cloudflare Workers/Pages in under 60 seconds
"""

import asyncio
import aiohttp
import zipfile
import tempfile
import os
from typing import Dict, Optional
from pathlib import Path
import json

from app.core.config import get_settings

settings = get_settings()


class CloudflareDeploymentService:
    """
    Ultra-fast deployment to Cloudflare
    """
    
    def __init__(self):
        self.api_token = settings.CLOUDFLARE_API_TOKEN
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.zone_id = settings.CLOUDFLARE_ZONE_ID
        self.base_url = "https://api.cloudflare.com/client/v4"
        
    async def deploy_website(
        self,
        build_path: str,
        subdomain: str,
        custom_domain: Optional[str] = None
    ) -> Dict:
        """
        Deploy website to Cloudflare Pages
        """
        try:
            # 1. Create deployment package
            deployment_package = await self._create_deployment_package(build_path)
            
            # 2. Upload to Cloudflare Pages
            deployment_result = await self._deploy_to_pages(
                deployment_package, subdomain
            )
            
            # 3. Configure custom domain if provided
            if custom_domain:
                await self._configure_custom_domain(custom_domain, subdomain)
            
            # 4. Setup redirects and optimization
            await self._configure_optimization(subdomain)
            
            return {
                'url': f"https://{subdomain}.hero365.app",
                'custom_url': f"https://{custom_domain}" if custom_domain else None,
                'deployment_id': deployment_result['id'],
                'status': 'deployed',
                'cdn_enabled': True
            }
            
        except Exception as e:
            raise Exception(f"Cloudflare deployment failed: {str(e)}")
    
    async def _create_deployment_package(self, build_path: str) -> str:
        """
        Create optimized deployment package
        """
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                build_dir = Path(build_path)
                
                for file_path in build_dir.rglob('*'):
                    if file_path.is_file():
                        # Skip unnecessary files
                        if self._should_include_file(file_path):
                            arc_name = file_path.relative_to(build_dir)
                            zip_file.write(file_path, arc_name)
            
            return temp_file.name
    
    def _should_include_file(self, file_path: Path) -> bool:
        """
        Filter files for deployment
        """
        # Skip source maps, logs, and other dev files
        skip_extensions = {'.map', '.log', '.tmp'}
        skip_dirs = {'node_modules', '.git', '.next/cache'}
        
        if file_path.suffix in skip_extensions:
            return False
            
        for skip_dir in skip_dirs:
            if skip_dir in file_path.parts:
                return False
                
        return True
    
    async def _deploy_to_pages(self, package_path: str, subdomain: str) -> Dict:
        """
        Deploy to Cloudflare Pages
        """
        url = f"{self.base_url}/accounts/{self.account_id}/pages/projects/{subdomain}/deployments"
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
        }
        
        async with aiohttp.ClientSession() as session:
            with open(package_path, 'rb') as package_file:
                data = aiohttp.FormData()
                data.add_field('file', package_file, filename='deployment.zip')
                
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['result']
                    else:
                        error_text = await response.text()
                        raise Exception(f"Cloudflare API error: {error_text}")
    
    async def _configure_custom_domain(self, custom_domain: str, subdomain: str):
        """
        Configure custom domain with SSL
        """
        # Add custom domain to Pages project
        url = f"{self.base_url}/accounts/{self.account_id}/pages/projects/{subdomain}/domains"
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'name': custom_domain
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Custom domain setup failed: {error_text}")
    
    async def _configure_optimization(self, subdomain: str):
        """
        Configure Cloudflare optimization settings
        """
        # Enable auto-minification, Brotli compression, etc.
        optimizations = [
            self._enable_auto_minify(),
            self._enable_brotli_compression(),
            self._configure_caching_rules(),
            self._setup_security_headers()
        ]
        
        await asyncio.gather(*optimizations)
    
    async def _enable_auto_minify(self):
        """
        Enable automatic minification
        """
        url = f"{self.base_url}/zones/{self.zone_id}/settings/minify"
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'value': {
                'css': 'on',
                'html': 'on',
                'js': 'on'
            }
        }
        
        async with aiohttp.ClientSession() as session:
            await session.patch(url, headers=headers, json=data)
    
    async def _enable_brotli_compression(self):
        """
        Enable Brotli compression for better performance
        """
        url = f"{self.base_url}/zones/{self.zone_id}/settings/brotli"
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {'value': 'on'}
        
        async with aiohttp.ClientSession() as session:
            await session.patch(url, headers=headers, json=data)
    
    async def _configure_caching_rules(self):
        """
        Configure aggressive caching for static assets
        """
        # Cache static assets for 1 year
        # Cache HTML for 1 hour with revalidation
        pass  # Implementation would set up page rules
    
    async def _setup_security_headers(self):
        """
        Setup security headers for better security score
        """
        # HSTS, CSP, X-Frame-Options, etc.
        pass  # Implementation would configure security headers
    
    async def get_deployment_status(self, subdomain: str, deployment_id: str) -> Dict:
        """
        Check deployment status
        """
        url = f"{self.base_url}/accounts/{self.account_id}/pages/projects/{subdomain}/deployments/{deployment_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['result']
                else:
                    raise Exception(f"Failed to get deployment status")
    
    async def run_lighthouse_audit(self, url: str) -> Dict:
        """
        Run Lighthouse audit on deployed website
        """
        # This would integrate with Lighthouse CI or PageSpeed Insights API
        lighthouse_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        params = {
            'url': url,
            'key': settings.GOOGLE_PAGESPEED_API_KEY,
            'category': ['performance', 'accessibility', 'best-practices', 'seo'],
            'strategy': 'mobile'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(lighthouse_url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract scores
                    lighthouse_result = result['lighthouseResult']
                    categories = lighthouse_result['categories']
                    
                    return {
                        'performance': int(categories['performance']['score'] * 100),
                        'accessibility': int(categories['accessibility']['score'] * 100),
                        'best_practices': int(categories['best-practices']['score'] * 100),
                        'seo': int(categories['seo']['score'] * 100),
                        'overall': int(sum([
                            categories['performance']['score'],
                            categories['accessibility']['score'],
                            categories['best-practices']['score'],
                            categories['seo']['score']
                        ]) / 4 * 100)
                    }
                else:
                    return {'error': 'Lighthouse audit failed'}
    
    async def invalidate_cache(self, subdomain: str):
        """
        Invalidate Cloudflare cache for website
        """
        url = f"{self.base_url}/zones/{self.zone_id}/purge_cache"
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Purge all files for the subdomain
        data = {
            'hosts': [f"{subdomain}.hero365.app"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return response.status == 200
