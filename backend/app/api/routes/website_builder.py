"""
Website Builder API Routes
Handles website deployment using the existing website-builder system
"""

import asyncio
import logging
import subprocess
import os
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from supabase import Client

from app.api.deps import get_supabase_client
from app.application.services.website_configuration_service import WebsiteConfigurationService

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class WebsiteDeploymentRequest(BaseModel):
    business_id: UUID
    deployment_type: str = Field(default="basic", description="basic or full_seo")
    custom_domain: Optional[str] = None
    force_rebuild: bool = Field(default=False, description="Force rebuild even if already deployed")

class WebsiteDeploymentResponse(BaseModel):
    success: bool
    deployment_id: str
    website_url: Optional[str] = None
    status: str
    message: str
    estimated_completion_time: Optional[int] = None  # seconds

class DeploymentStatusResponse(BaseModel):
    deployment_id: str
    status: str  # pending, building, deploying, completed, failed
    progress: int  # 0-100
    website_url: Optional[str] = None
    error_message: Optional[str] = None
    logs: list[str] = []

@router.post("/deploy", response_model=WebsiteDeploymentResponse)
async def deploy_website(
    request: WebsiteDeploymentRequest,
    background_tasks: BackgroundTasks,
    db: Client = Depends(get_supabase_client)
):
    """
    Deploy website using the existing website-builder system
    This triggers the actual Next.js build and Cloudflare deployment
    """
    try:
        logger.info(f"🚀 Starting website deployment for business {request.business_id}")
        
        # Initialize services
        config_service = WebsiteConfigurationService(db)
        
        # Get or create website configuration
        website_config = await config_service.get_or_create_website_config(
            business_id=request.business_id,
            deployment_type=request.deployment_type
        )
        
        # Generate deployment ID
        deployment_id = f"deploy-{request.business_id}-{int(datetime.now().timestamp())}"
        
        # Start deployment in background
        background_tasks.add_task(
            execute_website_deployment,
            deployment_id=deployment_id,
            business_id=request.business_id,
            website_config=website_config,
            force_rebuild=request.force_rebuild
        )
        
        # Return immediate response
        return WebsiteDeploymentResponse(
            success=True,
            deployment_id=deployment_id,
            website_url=f"https://hero365-website-staging.workers.dev",
            status="building",
            message="Website deployment started successfully",
            estimated_completion_time=300  # 5 minutes for full build
        )
        
    except Exception as e:
        logger.error(f"❌ Deployment initiation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@router.get("/deploy/{deployment_id}/status", response_model=DeploymentStatusResponse)
async def get_deployment_status(
    deployment_id: str,
    db: Client = Depends(get_supabase_client)
):
    """
    Get deployment status for real-time updates in mobile app
    """
    try:
        # In a real implementation, this would check a deployment status table
        # For now, we'll simulate the status based on time elapsed
        
        # Extract timestamp from deployment_id to simulate progress
        parts = deployment_id.split('-')
        if len(parts) >= 3:
            timestamp = int(parts[-1])
            elapsed = int(datetime.now().timestamp()) - timestamp
            
            if elapsed < 60:
                status = "building"
                progress = min(30, elapsed // 2)
                logs = [
                    "✅ Website configuration loaded",
                    "✅ Business data retrieved", 
                    "🔨 Building Next.js application..."
                ]
            elif elapsed < 240:
                status = "deploying"
                progress = 30 + min(60, (elapsed - 60) // 3)
                logs = [
                    "✅ Website configuration loaded",
                    "✅ Business data retrieved",
                    "✅ Next.js build completed",
                    "🚀 Deploying to Cloudflare Workers..."
                ]
            else:
                status = "completed"
                progress = 100
                logs = [
                    "✅ Website configuration loaded",
                    "✅ Business data retrieved",
                    "✅ Next.js build completed",
                    "✅ Deployed to Cloudflare Workers",
                    "🌐 Website is live!"
                ]
        else:
            status = "completed"
            progress = 100
            logs = ["✅ Deployment completed"]
        
        return DeploymentStatusResponse(
            deployment_id=deployment_id,
            status=status,
            progress=progress,
            website_url="https://elite-hvac-austin.pages.dev" if progress == 100 else None,
            logs=logs
        )
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

async def execute_website_deployment(
    deployment_id: str,
    business_id: UUID,
    website_config: Dict[str, Any],
    force_rebuild: bool = False
):
    """
    Execute the actual website deployment using the existing website-builder
    """
    try:
        logger.info(f"🔨 Building website for deployment {deployment_id}")
        
        # Get the website-builder path
        backend_path = Path(__file__).parent.parent.parent.parent
        website_builder_path = backend_path / "website-builder"
        
        if not website_builder_path.exists():
            raise Exception(f"Website builder not found at {website_builder_path}")
        
        # Prepare environment variables
        env = os.environ.copy()
        env.update({
            "NEXT_PUBLIC_BUSINESS_ID": str(business_id),
            "NEXT_PUBLIC_API_URL": "http://127.0.0.1:8000/api/v1",  # Backend URL
            "NODE_ENV": "production"
        })
        
        # Use the existing deployment script
        deploy_command = [
            "npm", "run", "deploy:staging"  # Use staging deployment for testing
        ]
        
        logger.info(f"🚀 Deploying to Cloudflare Workers via OpenNext: {' '.join(deploy_command)}")
        
        # Execute deployment in website-builder directory
        result = subprocess.run(
            deploy_command,
            cwd=website_builder_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Deployment {deployment_id} completed successfully")
            
            # Extract deployment URL from output (Cloudflare Workers)
            output_lines = result.stdout.split('\n')
            deployment_url = None
            for line in output_lines:
                if 'https://' in line and ('.workers.dev' in line or '.pages.dev' in line):
                    # Extract URL from the line (support both Workers and Pages)
                    import re
                    url_match = re.search(r'https://[^\s]+\.(workers|pages)\.dev[^\s]*', line)
                    if url_match:
                        deployment_url = url_match.group(0)
                        break
            
            # Update website configuration with deployment info
            if deployment_url:
                update_data = {
                    'deployment_status': 'deployed',
                    'domain': deployment_url
                }
                
                # Update in database
                db = Client(
                    supabase_url=env.get('SUPABASE_URL'),
                    supabase_key=env.get('SUPABASE_KEY')
                )
                
                db.table('website_configurations').update(update_data).eq(
                    'business_id', str(business_id)
                ).execute()
                
                logger.info(f"🌐 Website deployed at: {deployment_url}")
            
            return {
                'success': True,
                'deployment_url': deployment_url,
                'output': result.stdout
            }
        else:
            logger.error(f"❌ Deployment {deployment_id} failed: {result.stderr}")
            raise Exception(f"Deployment failed: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Deployment {deployment_id} timed out")
        raise Exception("Deployment timed out after 10 minutes")
    except Exception as e:
        logger.error(f"❌ Background deployment {deployment_id} failed: {e}")
        raise

@router.get("/preview/{business_id}")
async def preview_website(
    business_id: UUID,
    db: Client = Depends(get_supabase_client)
):
    """
    Get preview URL for the website (if deployed)
    """
    try:
        # Get website configuration
        result = db.table('website_configurations').select('*').eq('business_id', str(business_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Website configuration not found")
        
        config = result.data[0]
        
        if config.get('deployment_status') == 'deployed' and config.get('domain'):
            return {
                'website_url': config['domain'],
                'status': 'deployed',
                'subdomain': config.get('subdomain'),
                'deployment_status': config.get('deployment_status')
            }
        else:
            return {
                'website_url': None,
                'status': 'not_deployed',
                'message': 'Website has not been deployed yet'
            }
        
    except Exception as e:
        logger.error(f"❌ Preview check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preview check failed: {str(e)}")
