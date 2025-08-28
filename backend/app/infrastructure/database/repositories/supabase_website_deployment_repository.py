"""
Supabase Website Deployment Repository Implementation

Implements website deployment data access operations using Supabase.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from supabase import Client

from ....domain.entities.website_deployment import WebsiteDeployment, BusinessWebsite, DeploymentStatus, BuildStatus
from ....domain.repositories.website_deployment_repository import WebsiteDeploymentRepository, BusinessWebsiteRepository
from ....core.db import get_supabase_client
from ....domain.exceptions.domain_exceptions import DatabaseError, EntityNotFoundError, DuplicateEntityError

logger = logging.getLogger(__name__)


class SupabaseWebsiteDeploymentRepository(WebsiteDeploymentRepository):
    """
    Supabase implementation of WebsiteDeploymentRepository.
    
    Handles website deployment data operations using Supabase database.
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize repository with Supabase client.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or get_supabase_client()
        self.table_name = "website_deployments"
    
    async def create(self, deployment: WebsiteDeployment) -> WebsiteDeployment:
        """Create a new website deployment."""
        try:
            deployment_data = {
                "id": str(deployment.id),
                "business_id": str(deployment.business_id),
                "website_id": str(deployment.website_id) if deployment.website_id else None,
                "project_name": deployment.project_name,
                "subdomain": deployment.subdomain,
                "status": deployment.status.value,
                "build_status": deployment.build_status.value,
                "progress": deployment.progress,
                "current_step": deployment.current_step,
                "deploy_url": deployment.deploy_url,
                "build_id": deployment.build_id,
                "build_config": deployment.build_config,
                "deployment_config": deployment.deployment_config,
                "metadata": deployment.metadata,
                "error_message": deployment.error_message,
                "build_logs": deployment.build_logs,
                "lighthouse_score": deployment.lighthouse_score,
                "build_time_seconds": deployment.build_time_seconds,
                "deploy_time_seconds": deployment.deploy_time_seconds,
                "is_current": deployment.is_current,
                "is_production": deployment.is_production,
                "created_at": deployment.created_at.isoformat(),
                "started_at": deployment.started_at.isoformat() if deployment.started_at else None,
                "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None,
                "updated_at": deployment.updated_at.isoformat()
            }
            
            result = self.supabase.table(self.table_name).insert(deployment_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create website deployment")
            
            logger.info(f"Created website deployment: {deployment.id}")
            return deployment
            
        except Exception as e:
            logger.error(f"Failed to create website deployment: {str(e)}")
            raise DatabaseError(f"Failed to create website deployment: {str(e)}")
    
    async def get_by_id(self, deployment_id: uuid.UUID) -> Optional[WebsiteDeployment]:
        """Get deployment by ID."""
        try:
            result = self.supabase.table(self.table_name).select("*").eq("id", str(deployment_id)).execute()
            
            if not result.data:
                return None
            
            return self._map_to_entity(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get deployment by ID {deployment_id}: {str(e)}")
            raise DatabaseError(f"Failed to get deployment: {str(e)}")
    
    async def get_by_business_id(
        self, 
        business_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[WebsiteDeployment]:
        """Get deployments for a specific business."""
        try:
            query = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .order("created_at", desc=True)
                .range(skip, skip + limit - 1)
            )
            
            result = query.execute()
            
            return [self._map_to_entity(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get deployments for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to get deployments: {str(e)}")
    
    async def get_active_deployment(self, business_id: uuid.UUID) -> Optional[WebsiteDeployment]:
        """Get the currently active (non-terminal) deployment for a business."""
        try:
            active_statuses = [
                DeploymentStatus.PENDING.value,
                DeploymentStatus.BUILDING.value,
                DeploymentStatus.DEPLOYING.value
            ]
            
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .in_("status", active_statuses)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if not result.data:
                return None
            
            return self._map_to_entity(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get active deployment for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to get active deployment: {str(e)}")
    
    async def get_current_deployment(self, business_id: uuid.UUID) -> Optional[WebsiteDeployment]:
        """Get the current live deployment for a business."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .eq("is_current", True)
                .limit(1)
                .execute()
            )
            
            if not result.data:
                return None
            
            return self._map_to_entity(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get current deployment for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to get current deployment: {str(e)}")
    
    async def get_by_idempotency_key(
        self, 
        business_id: uuid.UUID, 
        idempotency_key: str
    ) -> Optional[WebsiteDeployment]:
        """Get deployment by idempotency key for a business."""
        try:
            # Check metadata for idempotency_key
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .contains("metadata", {"idempotency_key": idempotency_key})
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if not result.data:
                return None
            
            return self._map_to_entity(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get deployment by idempotency key: {str(e)}")
            raise DatabaseError(f"Failed to get deployment by idempotency key: {str(e)}")
    
    async def update(self, deployment: WebsiteDeployment) -> WebsiteDeployment:
        """Update an existing deployment."""
        try:
            deployment.updated_at = datetime.utcnow()
            
            update_data = {
                "status": deployment.status.value,
                "build_status": deployment.build_status.value,
                "progress": deployment.progress,
                "current_step": deployment.current_step,
                "deploy_url": deployment.deploy_url,
                "build_id": deployment.build_id,
                "build_config": deployment.build_config,
                "deployment_config": deployment.deployment_config,
                "metadata": deployment.metadata,
                "error_message": deployment.error_message,
                "build_logs": deployment.build_logs,
                "lighthouse_score": deployment.lighthouse_score,
                "build_time_seconds": deployment.build_time_seconds,
                "deploy_time_seconds": deployment.deploy_time_seconds,
                "is_current": deployment.is_current,
                "started_at": deployment.started_at.isoformat() if deployment.started_at else None,
                "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None,
                "updated_at": deployment.updated_at.isoformat()
            }
            
            result = (
                self.supabase.table(self.table_name)
                .update(update_data)
                .eq("id", str(deployment.id))
                .execute()
            )
            
            if not result.data:
                raise EntityNotFoundError(f"Deployment {deployment.id} not found")
            
            logger.info(f"Updated website deployment: {deployment.id}")
            return deployment
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update deployment {deployment.id}: {str(e)}")
            raise DatabaseError(f"Failed to update deployment: {str(e)}")
    
    async def update_status(
        self, 
        deployment_id: uuid.UUID, 
        status: DeploymentStatus,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None,
        website_url: Optional[str] = None
    ) -> bool:
        """Update deployment status and progress, optionally setting the deploy URL."""
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if progress is not None:
                update_data["progress"] = progress
            
            if current_step is not None:
                update_data["current_step"] = current_step
            
            if error_message is not None:
                update_data["error_message"] = error_message
            
            # If we received a website URL, persist it
            if website_url:
                update_data["deploy_url"] = website_url
                # If we have a URL and status is completed, mark as current
                if status == DeploymentStatus.COMPLETED:
                    update_data["is_current"] = True

            if status in [DeploymentStatus.COMPLETED, DeploymentStatus.FAILED, DeploymentStatus.CANCELLED]:
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            result = (
                self.supabase.table(self.table_name)
                .update(update_data)
                .eq("id", str(deployment_id))
                .execute()
            )
            
            success = bool(result.data)
            if success:
                logger.info(f"Updated deployment {deployment_id} status to {status.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update deployment status: {str(e)}")
            raise DatabaseError(f"Failed to update deployment status: {str(e)}")
    
    async def set_current_deployment(
        self, 
        business_id: uuid.UUID, 
        deployment_id: uuid.UUID
    ) -> bool:
        """Set a deployment as the current live deployment for a business."""
        try:
            # First, unset any existing current deployment
            self.supabase.table(self.table_name).update({
                "is_current": False,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("is_current", True).execute()
            
            # Then set the new current deployment
            result = (
                self.supabase.table(self.table_name)
                .update({
                    "is_current": True,
                    "updated_at": datetime.utcnow().isoformat()
                })
                .eq("id", str(deployment_id))
                .eq("business_id", str(business_id))
                .execute()
            )
            
            success = bool(result.data)
            if success:
                logger.info(f"Set deployment {deployment_id} as current for business {business_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to set current deployment: {str(e)}")
            raise DatabaseError(f"Failed to set current deployment: {str(e)}")
    
    async def cancel_deployment(self, deployment_id: uuid.UUID) -> bool:
        """Cancel a pending or in-progress deployment."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .update({
                    "status": DeploymentStatus.CANCELLED.value,
                    "current_step": "Deployment cancelled",
                    "completed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                })
                .eq("id", str(deployment_id))
                .in_("status", [
                    DeploymentStatus.PENDING.value,
                    DeploymentStatus.BUILDING.value,
                    DeploymentStatus.DEPLOYING.value
                ])
                .execute()
            )
            
            success = bool(result.data)
            if success:
                logger.info(f"Cancelled deployment {deployment_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to cancel deployment: {str(e)}")
            raise DatabaseError(f"Failed to cancel deployment: {str(e)}")
    
    async def get_deployments_by_status(
        self, 
        status: DeploymentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[WebsiteDeployment]:
        """Get deployments by status across all businesses."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("status", status.value)
                .order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )
            
            return [self._map_to_entity(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get deployments by status {status}: {str(e)}")
            raise DatabaseError(f"Failed to get deployments by status: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Get count of deployments for a business."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("id", count="exact")
                .eq("business_id", str(business_id))
                .execute()
            )
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Failed to count deployments for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to count deployments: {str(e)}")
    
    async def delete(self, deployment_id: uuid.UUID) -> bool:
        """Delete a deployment record."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .delete()
                .eq("id", str(deployment_id))
                .execute()
            )
            
            success = bool(result.data)
            if success:
                logger.info(f"Deleted deployment {deployment_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete deployment: {str(e)}")
            raise DatabaseError(f"Failed to delete deployment: {str(e)}")
    
    def _map_to_entity(self, row: Dict[str, Any]) -> WebsiteDeployment:
        """Map database row to WebsiteDeployment entity."""
        return WebsiteDeployment(
            id=uuid.UUID(row["id"]),
            business_id=uuid.UUID(row["business_id"]),
            website_id=uuid.UUID(row["website_id"]) if row["website_id"] else None,
            project_name=row["project_name"],
            subdomain=row["subdomain"],
            status=DeploymentStatus(row["status"]),
            build_status=BuildStatus(row["build_status"]),
            progress=row["progress"],
            current_step=row["current_step"],
            deploy_url=row["deploy_url"],
            build_id=row["build_id"],
            build_config=row["build_config"] or {},
            deployment_config=row["deployment_config"] or {},
            metadata=row["metadata"] or {},
            error_message=row["error_message"],
            build_logs=row["build_logs"] or [],
            lighthouse_score=row["lighthouse_score"],
            build_time_seconds=row["build_time_seconds"],
            deploy_time_seconds=row["deploy_time_seconds"],
            is_current=row["is_current"],
            is_production=row["is_production"],
            created_at=datetime.fromisoformat(row["created_at"].replace('Z', '+00:00')),
            started_at=datetime.fromisoformat(row["started_at"].replace('Z', '+00:00')) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"].replace('Z', '+00:00')) if row["completed_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"].replace('Z', '+00:00'))
        )


class SupabaseBusinessWebsiteRepository(BusinessWebsiteRepository):
    """
    Supabase implementation of BusinessWebsiteRepository.
    
    Handles business website configuration data operations using Supabase database.
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize repository with Supabase client.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or get_supabase_client()
        self.table_name = "business_websites"
    
    async def create(self, website: BusinessWebsite) -> BusinessWebsite:
        """Create a new business website configuration."""
        try:
            website_data = {
                "id": str(website.id),
                "business_id": str(website.business_id),
                "subdomain": website.subdomain,
                "custom_domain": website.custom_domain,
                "status": website.status,
                "website_url": website.website_url,
                "build_config": website.build_config,
                "deployment_config": website.deployment_config,
                "seo_config": website.seo_config,
                "lighthouse_score": website.lighthouse_score,
                "last_lighthouse_check": website.last_lighthouse_check.isoformat() if website.last_lighthouse_check else None,
                "last_build_at": website.last_build_at.isoformat() if website.last_build_at else None,
                "last_deploy_at": website.last_deploy_at.isoformat() if website.last_deploy_at else None,
                "created_at": website.created_at.isoformat(),
                "updated_at": website.updated_at.isoformat()
            }
            
            result = self.supabase.table(self.table_name).insert(website_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create business website")
            
            logger.info(f"Created business website: {website.id}")
            return website
            
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise DuplicateEntityError(f"Subdomain '{website.subdomain}' already exists")
            logger.error(f"Failed to create business website: {str(e)}")
            raise DatabaseError(f"Failed to create business website: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID) -> Optional[BusinessWebsite]:
        """Get website configuration for a business."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("business_id", str(business_id))
                .limit(1)
                .execute()
            )
            
            if not result.data:
                return None
            
            return self._map_to_entity(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get website for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to get website: {str(e)}")
    
    async def get_by_subdomain(self, subdomain: str) -> Optional[BusinessWebsite]:
        """Get website by subdomain."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("subdomain", subdomain)
                .limit(1)
                .execute()
            )
            
            if not result.data:
                return None
            
            return self._map_to_entity(result.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get website by subdomain {subdomain}: {str(e)}")
            raise DatabaseError(f"Failed to get website by subdomain: {str(e)}")
    
    async def update(self, website: BusinessWebsite) -> BusinessWebsite:
        """Update an existing website configuration."""
        try:
            website.updated_at = datetime.utcnow()
            
            update_data = {
                "subdomain": website.subdomain,
                "custom_domain": website.custom_domain,
                "status": website.status,
                "website_url": website.website_url,
                "build_config": website.build_config,
                "deployment_config": website.deployment_config,
                "seo_config": website.seo_config,
                "lighthouse_score": website.lighthouse_score,
                "last_lighthouse_check": website.last_lighthouse_check.isoformat() if website.last_lighthouse_check else None,
                "last_build_at": website.last_build_at.isoformat() if website.last_build_at else None,
                "last_deploy_at": website.last_deploy_at.isoformat() if website.last_deploy_at else None,
                "updated_at": website.updated_at.isoformat()
            }
            
            result = (
                self.supabase.table(self.table_name)
                .update(update_data)
                .eq("id", str(website.id))
                .execute()
            )
            
            if not result.data:
                raise EntityNotFoundError(f"Website {website.id} not found")
            
            logger.info(f"Updated business website: {website.id}")
            return website
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise DuplicateEntityError(f"Subdomain '{website.subdomain}' already exists")
            logger.error(f"Failed to update website {website.id}: {str(e)}")
            raise DatabaseError(f"Failed to update website: {str(e)}")
    
    async def upsert_by_business_id(self, website: BusinessWebsite) -> BusinessWebsite:
        """Create or update website configuration for a business."""
        try:
            existing = await self.get_by_business_id(website.business_id)
            
            if existing:
                # Update existing website
                website.id = existing.id
                website.created_at = existing.created_at
                return await self.update(website)
            else:
                # Create new website
                return await self.create(website)
                
        except Exception as e:
            logger.error(f"Failed to upsert website for business {website.business_id}: {str(e)}")
            raise DatabaseError(f"Failed to upsert website: {str(e)}")
    
    async def is_subdomain_available(
        self, 
        subdomain: str, 
        exclude_business_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a subdomain is available."""
        try:
            query = self.supabase.table(self.table_name).select("id").eq("subdomain", subdomain)
            
            if exclude_business_id:
                query = query.neq("business_id", str(exclude_business_id))
            
            result = query.limit(1).execute()
            
            return len(result.data) == 0
            
        except Exception as e:
            logger.error(f"Failed to check subdomain availability: {str(e)}")
            raise DatabaseError(f"Failed to check subdomain availability: {str(e)}")
    
    async def delete(self, business_id: uuid.UUID) -> bool:
        """Delete website configuration for a business."""
        try:
            result = (
                self.supabase.table(self.table_name)
                .delete()
                .eq("business_id", str(business_id))
                .execute()
            )
            
            success = bool(result.data)
            if success:
                logger.info(f"Deleted website for business {business_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete website: {str(e)}")
            raise DatabaseError(f"Failed to delete website: {str(e)}")
    
    def _map_to_entity(self, row: Dict[str, Any]) -> BusinessWebsite:
        """Map database row to BusinessWebsite entity."""
        return BusinessWebsite(
            id=uuid.UUID(row["id"]),
            business_id=uuid.UUID(row["business_id"]),
            subdomain=row["subdomain"],
            custom_domain=row["custom_domain"],
            status=row["status"],
            website_url=row["website_url"],
            build_config=row["build_config"] or {},
            deployment_config=row["deployment_config"] or {},
            seo_config=row["seo_config"] or {},
            lighthouse_score=row["lighthouse_score"],
            last_lighthouse_check=datetime.fromisoformat(row["last_lighthouse_check"].replace('Z', '+00:00')) if row["last_lighthouse_check"] else None,
            last_build_at=datetime.fromisoformat(row["last_build_at"].replace('Z', '+00:00')) if row["last_build_at"] else None,
            last_deploy_at=datetime.fromisoformat(row["last_deploy_at"].replace('Z', '+00:00')) if row["last_deploy_at"] else None,
            created_at=datetime.fromisoformat(row["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(row["updated_at"].replace('Z', '+00:00'))
        )
