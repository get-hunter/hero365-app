"""
Business Membership Domain Entity

Represents a user's membership in a business with roles and permissions.
"""

import uuid
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum

from ..exceptions.domain_exceptions import DomainValidationError


class BusinessRole(Enum):
    """Enumeration for business roles with hierarchical levels."""
    OWNER = "owner"      # Level 5 (highest permissions)
    ADMIN = "admin"      # Level 4
    MANAGER = "manager"  # Level 3
    EMPLOYEE = "employee"  # Level 2
    CONTRACTOR = "contractor"  # Level 1
    VIEWER = "viewer"    # Level 0 (lowest permissions)


class BusinessPermission(Enum):
    """Enumeration for business permissions."""
    # Contact Management
    VIEW_CONTACTS = "view_contacts"
    CREATE_CONTACTS = "create_contacts"
    EDIT_CONTACTS = "edit_contacts"
    DELETE_CONTACTS = "delete_contacts"
    
    # Job Management
    VIEW_JOBS = "view_jobs"
    CREATE_JOBS = "create_jobs"
    EDIT_JOBS = "edit_jobs"
    DELETE_JOBS = "delete_jobs"
    
    # Project Management
    VIEW_PROJECTS = "view_projects"
    CREATE_PROJECTS = "create_projects"
    EDIT_PROJECTS = "edit_projects"
    DELETE_PROJECTS = "delete_projects"
    
    # Business Management
    EDIT_BUSINESS_PROFILE = "edit_business_profile"
    VIEW_BUSINESS_SETTINGS = "view_business_settings"
    EDIT_BUSINESS_SETTINGS = "edit_business_settings"
    
    # Team Management
    INVITE_TEAM_MEMBERS = "invite_team_members"
    EDIT_TEAM_MEMBERS = "edit_team_members"
    REMOVE_TEAM_MEMBERS = "remove_team_members"
    
    # Financial Management
    VIEW_INVOICES = "view_invoices"
    CREATE_INVOICES = "create_invoices"
    EDIT_INVOICES = "edit_invoices"
    DELETE_INVOICES = "delete_invoices"
    
    VIEW_ESTIMATES = "view_estimates"
    CREATE_ESTIMATES = "create_estimates"
    EDIT_ESTIMATES = "edit_estimates"
    DELETE_ESTIMATES = "delete_estimates"
    
    # Reporting
    VIEW_REPORTS = "view_reports"
    EDIT_REPORTS = "edit_reports"
    VIEW_ACCOUNTING = "view_accounting"
    EDIT_ACCOUNTING = "edit_accounting"


# Role hierarchy mapping
ROLE_HIERARCHY = {
    BusinessRole.OWNER: 5,
    BusinessRole.ADMIN: 4,
    BusinessRole.MANAGER: 3,
    BusinessRole.EMPLOYEE: 2,
    BusinessRole.CONTRACTOR: 1,
    BusinessRole.VIEWER: 0
}

# Default permissions for each role
DEFAULT_ROLE_PERMISSIONS = {
    BusinessRole.OWNER: [permission.value for permission in BusinessPermission],  # All permissions
    BusinessRole.ADMIN: [
        # Data Management
        BusinessPermission.VIEW_CONTACTS.value,
        BusinessPermission.CREATE_CONTACTS.value,
        BusinessPermission.EDIT_CONTACTS.value,
        BusinessPermission.DELETE_CONTACTS.value,
        BusinessPermission.VIEW_JOBS.value,
        BusinessPermission.CREATE_JOBS.value,
        BusinessPermission.EDIT_JOBS.value,
        BusinessPermission.DELETE_JOBS.value,
        BusinessPermission.VIEW_PROJECTS.value,
        BusinessPermission.CREATE_PROJECTS.value,
        BusinessPermission.EDIT_PROJECTS.value,
        BusinessPermission.DELETE_PROJECTS.value,
        BusinessPermission.VIEW_INVOICES.value,
        BusinessPermission.CREATE_INVOICES.value,
        BusinessPermission.EDIT_INVOICES.value,
        BusinessPermission.DELETE_INVOICES.value,
        BusinessPermission.VIEW_ESTIMATES.value,
        BusinessPermission.CREATE_ESTIMATES.value,
        BusinessPermission.EDIT_ESTIMATES.value,
        BusinessPermission.DELETE_ESTIMATES.value,
        # Business Management
        BusinessPermission.VIEW_BUSINESS_SETTINGS.value,
        # Team Management
        BusinessPermission.INVITE_TEAM_MEMBERS.value,
        BusinessPermission.EDIT_TEAM_MEMBERS.value,
        # Financial
        BusinessPermission.VIEW_REPORTS.value,
        BusinessPermission.EDIT_REPORTS.value,
        BusinessPermission.VIEW_ACCOUNTING.value,
        BusinessPermission.EDIT_ACCOUNTING.value
    ],
    BusinessRole.MANAGER: [
        # Data Management
        BusinessPermission.VIEW_CONTACTS.value,
        BusinessPermission.CREATE_CONTACTS.value,
        BusinessPermission.EDIT_CONTACTS.value,
        BusinessPermission.VIEW_JOBS.value,
        BusinessPermission.CREATE_JOBS.value,
        BusinessPermission.EDIT_JOBS.value,
        BusinessPermission.VIEW_PROJECTS.value,
        BusinessPermission.CREATE_PROJECTS.value,
        BusinessPermission.EDIT_PROJECTS.value,
        BusinessPermission.VIEW_INVOICES.value,
        BusinessPermission.CREATE_INVOICES.value,
        BusinessPermission.EDIT_INVOICES.value,
        BusinessPermission.VIEW_ESTIMATES.value,
        BusinessPermission.CREATE_ESTIMATES.value,
        BusinessPermission.EDIT_ESTIMATES.value,
        # Team Management
        BusinessPermission.INVITE_TEAM_MEMBERS.value,
        # Financial
        BusinessPermission.VIEW_REPORTS.value
    ],
    BusinessRole.EMPLOYEE: [
        # Data Management
        BusinessPermission.VIEW_CONTACTS.value,
        BusinessPermission.CREATE_CONTACTS.value,
        BusinessPermission.EDIT_CONTACTS.value,
        BusinessPermission.VIEW_JOBS.value,
        BusinessPermission.CREATE_JOBS.value,
        BusinessPermission.EDIT_JOBS.value,
        BusinessPermission.VIEW_PROJECTS.value,
        BusinessPermission.CREATE_PROJECTS.value,
        BusinessPermission.EDIT_PROJECTS.value,
        BusinessPermission.VIEW_INVOICES.value,
        BusinessPermission.VIEW_ESTIMATES.value
    ],
    BusinessRole.CONTRACTOR: [
        # Data Management (limited)
        BusinessPermission.VIEW_CONTACTS.value,
        BusinessPermission.VIEW_JOBS.value,
        BusinessPermission.VIEW_PROJECTS.value
    ],
    BusinessRole.VIEWER: [
        # Data Management (read-only)
        BusinessPermission.VIEW_CONTACTS.value,
        BusinessPermission.VIEW_JOBS.value,
        BusinessPermission.VIEW_PROJECTS.value
    ]
}


@dataclass
class BusinessMembership:
    """
    Business Membership entity representing a user's relationship with a business.
    
    This entity contains business logic for role-based access control,
    permission management, and membership lifecycle.
    """
    
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    role: BusinessRole
    permissions: List[str]
    joined_date: datetime
    invited_date: Optional[datetime] = None
    invited_by: Optional[str] = None
    is_active: bool = True
    department_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = None
    
    def __post_init__(self):
        """Validate business rules after initialization."""
        self._validate_membership_rules()
    
    def _validate_membership_rules(self) -> None:
        """Validate core membership business rules."""
        if not self.business_id:
            raise DomainValidationError("Business membership must have a business ID")
        
        if not self.user_id:
            raise DomainValidationError("Business membership must have a user ID")
        
        if not self.permissions:
            raise DomainValidationError("Business membership must have permissions")
        
        # Validate permissions are consistent with role
        self._validate_role_permissions()
    
    def _validate_role_permissions(self) -> None:
        """Validate that permissions are appropriate for the role."""
        default_permissions = DEFAULT_ROLE_PERMISSIONS.get(self.role, [])
        
        # Check that all assigned permissions are valid for the role
        for permission in self.permissions:
            if permission not in default_permissions and self.role != BusinessRole.OWNER:
                # Owners can have any permission, others must stick to role defaults
                pass  # For now, allow custom permissions
    
    def get_role_level(self) -> int:
        """Get the numerical level of the role for hierarchy comparisons."""
        return ROLE_HIERARCHY.get(self.role, 0)
    
    def can_manage_role(self, target_role: BusinessRole) -> bool:
        """Check if this membership can manage another role."""
        if not self.is_active:
            return False
        
        # Can only manage roles lower in hierarchy
        return self.get_role_level() > ROLE_HIERARCHY.get(target_role, 0)
    
    def can_manage_membership(self, target_membership: 'BusinessMembership') -> bool:
        """Check if this membership can manage another membership."""
        if not self.is_active:
            return False
        
        # Cannot manage yourself (except owners can)
        if self.user_id == target_membership.user_id and self.role != BusinessRole.OWNER:
            return False
        
        # Must be in same business
        if self.business_id != target_membership.business_id:
            return False
        
        # Can manage if role is higher
        return self.can_manage_role(target_membership.role)
    
    def has_permission(self, permission: str) -> bool:
        """Check if membership has a specific permission."""
        return self.is_active and permission in self.permissions
    
    def has_business_permission(self, permission: BusinessPermission) -> bool:
        """Check if membership has a specific business permission."""
        return self.has_permission(permission.value)
    
    def can_view_contacts(self) -> bool:
        """Check if membership can view contacts."""
        return self.has_business_permission(BusinessPermission.VIEW_CONTACTS)
    
    def can_create_contacts(self) -> bool:
        """Check if membership can create contacts."""
        return self.has_business_permission(BusinessPermission.CREATE_CONTACTS)
    
    def can_edit_contacts(self) -> bool:
        """Check if membership can edit contacts."""
        return self.has_business_permission(BusinessPermission.EDIT_CONTACTS)
    
    def can_delete_contacts(self) -> bool:
        """Check if membership can delete contacts."""
        return self.has_business_permission(BusinessPermission.DELETE_CONTACTS)
    
    def can_view_jobs(self) -> bool:
        """Check if membership can view jobs."""
        return self.has_business_permission(BusinessPermission.VIEW_JOBS)
    
    def can_create_jobs(self) -> bool:
        """Check if membership can create jobs."""
        return self.has_business_permission(BusinessPermission.CREATE_JOBS)
    
    def can_edit_jobs(self) -> bool:
        """Check if membership can edit jobs."""
        return self.has_business_permission(BusinessPermission.EDIT_JOBS)
    
    def can_delete_jobs(self) -> bool:
        """Check if membership can delete jobs."""
        return self.has_business_permission(BusinessPermission.DELETE_JOBS)
    
    def can_invite_members(self) -> bool:
        """Check if membership can invite new team members."""
        return self.has_business_permission(BusinessPermission.INVITE_TEAM_MEMBERS)
    
    def can_edit_team_members(self) -> bool:
        """Check if membership can edit team member roles."""
        return self.has_business_permission(BusinessPermission.EDIT_TEAM_MEMBERS)
    
    def can_remove_team_members(self) -> bool:
        """Check if membership can remove team members."""
        return self.has_business_permission(BusinessPermission.REMOVE_TEAM_MEMBERS)
    
    def update_role(self, new_role: BusinessRole) -> None:
        """
        Update the membership role and adjust permissions accordingly.
        
        Args:
            new_role: The new role to assign
            
        Raises:
            DomainValidationError: If role update is invalid
        """
        if self.role == BusinessRole.OWNER and new_role != BusinessRole.OWNER:
            raise DomainValidationError("Cannot change owner role")
        
        old_role = self.role
        self.role = new_role
        
        # Update permissions to match new role
        self.permissions = DEFAULT_ROLE_PERMISSIONS.get(new_role, []).copy()
        
        try:
            self._validate_membership_rules()
        except DomainValidationError:
            # Rollback on validation failure
            self.role = old_role
            self.permissions = DEFAULT_ROLE_PERMISSIONS.get(old_role, []).copy()
            raise
    
    def add_permission(self, permission: str) -> None:
        """Add a custom permission to the membership."""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def add_business_permission(self, permission: BusinessPermission) -> None:
        """Add a business permission to the membership."""
        self.add_permission(permission.value)
    
    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the membership."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def remove_business_permission(self, permission: BusinessPermission) -> None:
        """Remove a business permission from the membership."""
        self.remove_permission(permission.value)
    
    def activate(self) -> None:
        """Activate the membership."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the membership."""
        self.is_active = False
    
    def to_dict(self) -> dict:
        """Convert membership to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "user_id": self.user_id,
            "role": self.role.value,
            "role_level": self.get_role_level(),
            "permissions": self.permissions,
            "joined_date": self.joined_date.isoformat() if self.joined_date else None,
            "invited_date": self.invited_date.isoformat() if self.invited_date else None,
            "invited_by": self.invited_by,
            "is_active": self.is_active,
            "department_id": str(self.department_id) if self.department_id else None,
            "job_title": self.job_title
        }
    
    def __str__(self) -> str:
        return f"BusinessMembership({self.user_id} - {self.role.value} in {self.business_id})"
    
    def __repr__(self) -> str:
        return (f"BusinessMembership(id={self.id}, business_id={self.business_id}, "
                f"user_id='{self.user_id}', role={self.role.value}, "
                f"is_active={self.is_active})") 