"""
Cloudflare Pages Deployment Service

Service for deploying static websites to Cloudflare Pages.
Handles project creation, deployment via Wrangler CLI, and deployment status tracking.
"""

import json
import uuid
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...domain.entities.website_template import (
    WebsiteDeployment, DeploymentType, BuildStatus
)
from ..exceptions.application_exceptions import DeploymentError, ConfigurationError


class CloudflarePagesDeploymentService:
    """Service for deploying websites to Cloudflare Pages."""
    
    def __init__(
        self, 
        api_token: Optional[str] = None,
        account_id: Optional[str] = None,
        default_project_prefix: str = "hero365"
    ):
        self.api_token = api_token
        self.account_id = account_id
        self.default_project_prefix = default_project_prefix
        
        # Verify Wrangler is available
        self._verify_wrangler_available()
    
    def _verify_wrangler_available(self):
        """Verify that Wrangler CLI is available."""
        try:
            result = subprocess.run(
                ["wrangler", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ConfigurationError("Wrangler CLI not available or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise ConfigurationError("Wrangler CLI not found. Please install Wrangler.")
    
    async def deploy_to_pages(
        self,
        build_dir: Path,
        business_name: str,
        deployment_type: DeploymentType = DeploymentType.PRODUCTION,
        custom_domain: Optional[str] = None
    ) -> WebsiteDeployment:
        """
        Deploy a built website to Cloudflare Pages.
        
        Args:
            build_dir: Path to the built website (containing 'out' directory)
            business_name: Business name for project naming
            deployment_type: Type of deployment
            custom_domain: Optional custom domain
            
        Returns:
            WebsiteDeployment: Deployment record with URLs and status
            
        Raises:
            DeploymentError: If deployment fails
        """
        try:
            # Generate project name
            project_name = self._generate_project_name(business_name, deployment_type)
            
            # Ensure out directory exists
            out_dir = build_dir / "out"
            if not out_dir.exists():
                raise DeploymentError(f"Build output directory not found: {out_dir}")
            
            # Authenticate with Cloudflare if token provided
            if self.api_token:
                await self._authenticate_wrangler()
            
            # Deploy to Cloudflare Pages
            deployment_result = await self._deploy_with_wrangler(
                out_dir, project_name, deployment_type
            )
            
            # Create deployment record
            deployment = WebsiteDeployment(
                id=uuid.uuid4(),
                business_id=uuid.uuid4(),  # This will be set by the caller
                template_name="professional",  # This will be set by the caller
                deployment_type=deployment_type,
                project_name=project_name,
                deploy_url=deployment_result["url"],
                custom_domain=custom_domain,
                build_id=deployment_result.get("deployment_id"),
                build_status=BuildStatus.SUCCESS,
                build_log=deployment_result.get("log"),
                is_current=True,
                deployed_by="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Set up custom domain if provided
            if custom_domain:
                await self._setup_custom_domain(project_name, custom_domain)
                deployment.custom_domain = custom_domain
            
            return deployment
            
        except Exception as e:
            # Create failed deployment record
            return WebsiteDeployment(
                id=uuid.uuid4(),
                business_id=uuid.uuid4(),
                template_name="professional",
                deployment_type=deployment_type,
                project_name=project_name if 'project_name' in locals() else "unknown",
                deploy_url="",
                build_status=BuildStatus.FAILED,
                error_message=str(e),
                deployed_by="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
    
    def _generate_project_name(self, business_name: str, deployment_type: DeploymentType) -> str:
        """Generate Cloudflare Pages project name."""
        # Sanitize business name for URL
        sanitized_name = business_name.lower()
        sanitized_name = "".join(c if c.isalnum() or c in "-" else "-" for c in sanitized_name)
        sanitized_name = "-".join(part for part in sanitized_name.split("-") if part)
        
        # Truncate if too long
        if len(sanitized_name) > 30:
            sanitized_name = sanitized_name[:30].rstrip("-")
        
        # Add deployment type suffix for non-production
        if deployment_type != DeploymentType.PRODUCTION:
            suffix = deployment_type.value
            return f"{self.default_project_prefix}-{sanitized_name}-{suffix}"
        
        return f"{self.default_project_prefix}-{sanitized_name}"
    
    async def _authenticate_wrangler(self):
        """Authenticate Wrangler with API token."""
        if not self.api_token:
            return
        
        try:
            # Set environment variable for authentication
            env = {"CLOUDFLARE_API_TOKEN": self.api_token}
            
            # Verify authentication
            result = subprocess.run(
                ["wrangler", "whoami"],
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode != 0:
                raise DeploymentError(f"Wrangler authentication failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise DeploymentError("Wrangler authentication timed out")
    
    async def _deploy_with_wrangler(
        self, 
        out_dir: Path, 
        project_name: str,
        deployment_type: DeploymentType
    ) -> Dict[str, Any]:
        """Deploy using Wrangler CLI."""
        try:
            # Prepare environment
            env = {}
            if self.api_token:
                env["CLOUDFLARE_API_TOKEN"] = self.api_token
            
            # Build wrangler command
            cmd = [
                "wrangler", "pages", "deploy", str(out_dir),
                "--project-name", project_name
            ]
            
            # Add production flag for production deployments
            if deployment_type == DeploymentType.PRODUCTION:
                cmd.append("--production")
            
            # Execute deployment
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise DeploymentError(f"Wrangler deployment failed: {result.stderr}")
            
            # Parse deployment URL from output
            deploy_url = self._parse_deploy_url_from_output(result.stdout, project_name)
            
            return {
                "url": deploy_url,
                "deployment_id": self._parse_deployment_id_from_output(result.stdout),
                "log": result.stdout
            }
            
        except subprocess.TimeoutExpired:
            raise DeploymentError("Wrangler deployment timed out after 5 minutes")
        except Exception as e:
            raise DeploymentError(f"Deployment failed: {str(e)}")
    
    def _parse_deploy_url_from_output(self, output: str, project_name: str) -> str:
        """Parse deployment URL from Wrangler output."""
        lines = output.split("\n")
        
        # Look for URL in output
        for line in lines:
            if "https://" in line and "pages.dev" in line:
                # Extract URL
                parts = line.split()
                for part in parts:
                    if part.startswith("https://") and "pages.dev" in part:
                        return part.strip()
        
        # Fallback to constructed URL
        return f"https://{project_name}.pages.dev"
    
    def _parse_deployment_id_from_output(self, output: str) -> Optional[str]:
        """Parse deployment ID from Wrangler output."""
        lines = output.split("\n")
        
        for line in lines:
            if "deployment id" in line.lower() or "deployment:" in line.lower():
                # Try to extract ID-like string
                parts = line.split()
                for part in parts:
                    if len(part) > 10 and (part.isalnum() or "-" in part):
                        return part
        
        return None
    
    async def _setup_custom_domain(self, project_name: str, custom_domain: str):
        """Set up custom domain for the project."""
        try:
            env = {}
            if self.api_token:
                env["CLOUDFLARE_API_TOKEN"] = self.api_token
            
            # Add custom domain
            result = subprocess.run([
                "wrangler", "pages", "domain", "add",
                custom_domain, "--project-name", project_name
            ], capture_output=True, text=True, env=env, timeout=60)
            
            if result.returncode != 0:
                raise DeploymentError(f"Failed to set up custom domain: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise DeploymentError("Custom domain setup timed out")
    
    async def get_deployment_status(self, project_name: str) -> Dict[str, Any]:
        """Get deployment status for a project."""
        try:
            env = {}
            if self.api_token:
                env["CLOUDFLARE_API_TOKEN"] = self.api_token
            
            result = subprocess.run([
                "wrangler", "pages", "deployment", "list",
                "--project-name", project_name, "--format", "json"
            ], capture_output=True, text=True, env=env, timeout=30)
            
            if result.returncode != 0:
                raise DeploymentError(f"Failed to get deployment status: {result.stderr}")
            
            # Parse JSON output
            try:
                deployments = json.loads(result.stdout)
                if deployments and len(deployments) > 0:
                    latest = deployments[0]  # Most recent deployment
                    return {
                        "status": latest.get("stage", "unknown"),
                        "url": latest.get("url"),
                        "created_on": latest.get("created_on"),
                        "deployment_id": latest.get("id")
                    }
            except json.JSONDecodeError:
                pass
            
            return {"status": "unknown"}
            
        except subprocess.TimeoutExpired:
            raise DeploymentError("Deployment status check timed out")
    
    async def delete_project(self, project_name: str):
        """Delete a Cloudflare Pages project."""
        try:
            env = {}
            if self.api_token:
                env["CLOUDFLARE_API_TOKEN"] = self.api_token
            
            result = subprocess.run([
                "wrangler", "pages", "project", "delete",
                project_name, "--yes"
            ], capture_output=True, text=True, env=env, timeout=60)
            
            if result.returncode != 0:
                raise DeploymentError(f"Failed to delete project: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise DeploymentError("Project deletion timed out")
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all Cloudflare Pages projects."""
        try:
            env = {}
            if self.api_token:
                env["CLOUDFLARE_API_TOKEN"] = self.api_token
            
            result = subprocess.run([
                "wrangler", "pages", "project", "list", "--format", "json"
            ], capture_output=True, text=True, env=env, timeout=30)
            
            if result.returncode != 0:
                raise DeploymentError(f"Failed to list projects: {result.stderr}")
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
                
        except subprocess.TimeoutExpired:
            raise DeploymentError("Project listing timed out")
    
    def validate_project_name(self, project_name: str) -> bool:
        """Validate Cloudflare Pages project name."""
        # Project names must be lowercase, alphanumeric, and hyphens only
        # Must be between 1 and 58 characters
        if not project_name:
            return False
        
        if len(project_name) > 58:
            return False
        
        if not project_name.replace("-", "").isalnum():
            return False
        
        if project_name.startswith("-") or project_name.endswith("-"):
            return False
        
        return True
