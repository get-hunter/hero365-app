"""
Website Deployment Domain Entity

Represents a website deployment run with status tracking and metadata.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class DeploymentStatus(str, Enum):
    """Website deployment status enumeration."""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BuildStatus(str, Enum):
    """Build status enumeration."""
    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class WebsiteDeployment:
    """
    Website deployment entity representing a single deployment run.
    
    Tracks the complete lifecycle of a website deployment from initiation
    to completion, including build status, deployment URLs, and metadata.
    """
    
    # Primary identifiers
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    business_id: uuid.UUID = field(default=None)
    website_id: Optional[uuid.UUID] = field(default=None)
    
    # Deployment configuration
    project_name: str = field(default="")
    subdomain: Optional[str] = field(default=None)
    
    # Status tracking
    status: DeploymentStatus = field(default=DeploymentStatus.PENDING)
    build_status: BuildStatus = field(default=BuildStatus.PENDING)
    progress: int = field(default=0)  # 0-100 percentage
    current_step: str = field(default="Initializing deployment")
    
    # URLs and identifiers
    deploy_url: Optional[str] = field(default=None)
    build_id: Optional[str] = field(default=None)
    
    # Metadata and configuration
    build_config: Dict[str, Any] = field(default_factory=dict)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Error handling
    error_message: Optional[str] = field(default=None)
    build_logs: List[str] = field(default_factory=list)
    
    # Performance metrics
    lighthouse_score: Optional[int] = field(default=None)
    build_time_seconds: Optional[int] = field(default=None)
    deploy_time_seconds: Optional[int] = field(default=None)
    
    # Flags
    is_current: bool = field(default=False)
    is_production: bool = field(default=True)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = field(default=None)
    completed_at: Optional[datetime] = field(default=None)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if self.business_id is None:
            raise ValueError("business_id is required")
        
        if not self.project_name:
            # Generate project name from business_id if not provided
            self.project_name = f"hero365-{str(self.business_id)[:8]}"
    
    def start_deployment(self) -> None:
        """Mark deployment as started."""
        self.status = DeploymentStatus.BUILDING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, progress: int, step: str) -> None:
        """Update deployment progress."""
        self.progress = max(0, min(100, progress))
        self.current_step = step
        self.updated_at = datetime.utcnow()
    
    def mark_building(self, step: str = "Building website") -> None:
        """Mark deployment as building."""
        self.status = DeploymentStatus.BUILDING
        self.build_status = BuildStatus.BUILDING
        self.current_step = step
        self.updated_at = datetime.utcnow()
    
    def mark_deploying(self, step: str = "Deploying to Cloudflare") -> None:
        """Mark deployment as deploying."""
        self.status = DeploymentStatus.DEPLOYING
        self.current_step = step
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self, deploy_url: str, lighthouse_score: Optional[int] = None) -> None:
        """Mark deployment as completed successfully."""
        self.status = DeploymentStatus.COMPLETED
        self.build_status = BuildStatus.SUCCESS
        self.progress = 100
        self.current_step = "Deployment completed successfully"
        self.deploy_url = deploy_url
        self.lighthouse_score = lighthouse_score
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark deployment as failed."""
        self.status = DeploymentStatus.FAILED
        self.build_status = BuildStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_cancelled(self) -> None:
        """Mark deployment as cancelled."""
        self.status = DeploymentStatus.CANCELLED
        self.current_step = "Deployment cancelled"
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_log_entry(self, log_entry: str) -> None:
        """Add a log entry to the deployment."""
        self.build_logs.append(f"{datetime.utcnow().isoformat()}: {log_entry}")
        self.updated_at = datetime.utcnow()
    
    def set_as_current(self) -> None:
        """Mark this deployment as the current active deployment."""
        self.is_current = True
        self.updated_at = datetime.utcnow()
    
    def is_terminal_status(self) -> bool:
        """Check if deployment is in a terminal status."""
        return self.status in [
            DeploymentStatus.COMPLETED,
            DeploymentStatus.FAILED,
            DeploymentStatus.CANCELLED
        ]
    
    def is_active(self) -> bool:
        """Check if deployment is currently active (not terminal)."""
        return not self.is_terminal_status()
    
    def get_duration_seconds(self) -> Optional[int]:
        """Get deployment duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "website_id": str(self.website_id) if self.website_id else None,
            "project_name": self.project_name,
            "subdomain": self.subdomain,
            "status": self.status.value,
            "build_status": self.build_status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "deploy_url": self.deploy_url,
            "build_id": self.build_id,
            "build_config": self.build_config,
            "deployment_config": self.deployment_config,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "build_logs": self.build_logs,
            "lighthouse_score": self.lighthouse_score,
            "build_time_seconds": self.build_time_seconds,
            "deploy_time_seconds": self.deploy_time_seconds,
            "is_current": self.is_current,
            "is_production": self.is_production,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class BusinessWebsite:
    """
    Business website entity representing the main website configuration.
    
    Links to the business and tracks the current deployment status,
    domain configuration, and website metadata.
    """
    
    # Primary identifiers
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    business_id: uuid.UUID = field(default=None)
    
    # Domain configuration
    subdomain: Optional[str] = field(default=None)
    custom_domain: Optional[str] = field(default=None)
    
    # Website configuration
    status: str = field(default="draft")  # draft, building, deployed, error
    website_url: Optional[str] = field(default=None)
    
    # Build and deployment metadata
    build_config: Dict[str, Any] = field(default_factory=dict)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    seo_config: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    lighthouse_score: Optional[int] = field(default=None)
    last_lighthouse_check: Optional[datetime] = field(default=None)
    
    # Timestamps
    last_build_at: Optional[datetime] = field(default=None)
    last_deploy_at: Optional[datetime] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.business_id is None:
            raise ValueError("business_id is required")
        
        if not self.subdomain and not self.custom_domain:
            raise ValueError("Either subdomain or custom_domain must be provided")
    
    def update_deployment_status(self, status: str, website_url: Optional[str] = None) -> None:
        """Update website deployment status."""
        self.status = status
        if website_url:
            self.website_url = website_url
        if status == "deployed":
            self.last_deploy_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_lighthouse_score(self, score: int) -> None:
        """Update Lighthouse performance score."""
        self.lighthouse_score = score
        self.last_lighthouse_check = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "subdomain": self.subdomain,
            "custom_domain": self.custom_domain,
            "status": self.status,
            "website_url": self.website_url,
            "build_config": self.build_config,
            "deployment_config": self.deployment_config,
            "seo_config": self.seo_config,
            "lighthouse_score": self.lighthouse_score,
            "last_lighthouse_check": self.last_lighthouse_check.isoformat() if self.last_lighthouse_check else None,
            "last_build_at": self.last_build_at.isoformat() if self.last_build_at else None,
            "last_deploy_at": self.last_deploy_at.isoformat() if self.last_deploy_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
