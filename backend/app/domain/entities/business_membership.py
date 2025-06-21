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
    BusinessRole.OWNER: [
        # Data Management
        "view_contacts", "edit_contacts", "delete_contacts",
        "view_jobs", "edit_jobs", "delete_jobs",
        "view_projects", "edit_projects", "delete_projects",
        "view_invoices", "edit_invoices", "delete_invoices",
        "view_estimates", "edit_estimates", "delete_estimates",
        # Business Management
        "edit_business_profile",
        "view_business_settings", "edit_business_settings",
        # Team Management
        "invite_team_members", "edit_team_members", "remove_team_members",
        # Financial
        "view_reports", "edit_reports",
        "view_accounting", "edit_accounting"
    ],
    BusinessRole.ADMIN: [
        # Data Management
        "view_contacts", "edit_contacts", "delete_contacts",
        "view_jobs", "edit_jobs", "delete_jobs",
        "view_projects", "edit_projects", "delete_projects",
        "view_invoices", "edit_invoices", "delete_invoices",
        "view_estimates", "edit_estimates", "delete_estimates",
        # Business Management
        "view_business_settings",
        # Team Management
        "invite_team_members", "edit_team_members",
        # Financial
        "view_reports", "edit_reports",
        "view_accounting", "edit_accounting"
    ],
    BusinessRole.MANAGER: [
        # Data Management
        "view_contacts", "edit_contacts",
        "view_jobs", "edit_jobs",
        "view_projects", "edit_projects",
        "view_invoices", "edit_invoices",
        "view_estimates", "edit_estimates",
        # Team Management
        "invite_team_members",
        # Financial
        "view_reports"
    ],
    BusinessRole.EMPLOYEE: [
        # Data Management
        "view_contacts", "edit_contacts",
        "view_jobs", "edit_jobs",
        "view_projects", "edit_projects",
        "view_invoices",
        "view_estimates"
    ],
    BusinessRole.CONTRACTOR: [
        # Data Management
        "view_contacts",
        "view_jobs",
        "view_projects"
    ],
    BusinessRole.VIEWER: [
        # Data Management
        "view_contacts",
        "view_jobs",
        "view_projects"
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
    
    def can_invite_members(self) -> bool:
        """Check if membership can invite new team members."""
        return self.has_permission("invite_team_members")
    
    def can_edit_team_members(self) -> bool:
        """Check if membership can edit team member roles."""
        return self.has_permission("edit_team_members")
    
    def can_remove_team_members(self) -> bool:
        """Check if membership can remove team members."""
        return self.has_permission("remove_team_members")
    
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
    
    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the membership."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def activate(self) -> None:
        """Activate the membership."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the membership."""
        if self.role == BusinessRole.OWNER:
            raise DomainValidationError("Cannot deactivate business owner membership")
        self.is_active = False
    
    def is_owner(self) -> bool:
        """Check if this is an owner membership."""
        return self.role == BusinessRole.OWNER
    
    def is_admin(self) -> bool:
        """Check if this is an admin membership."""
        return self.role == BusinessRole.ADMIN
    
    def get_display_role(self) -> str:
        """Get a human-readable role name."""
        role_names = {
            BusinessRole.OWNER: "Owner",
            BusinessRole.ADMIN: "Administrator",
            BusinessRole.MANAGER: "Manager",
            BusinessRole.EMPLOYEE: "Employee",
            BusinessRole.CONTRACTOR: "Contractor",
            BusinessRole.VIEWER: "Viewer"
        }
        return role_names.get(self.role, "Unknown")
    
    def __str__(self) -> str:
        return f"BusinessMembership({self.user_id} as {self.get_display_role()} in {self.business_id})"
    
    def __repr__(self) -> str:
        return (f"BusinessMembership(id={self.id}, business_id={self.business_id}, "
                f"user_id='{self.user_id}', role={self.role}, is_active={self.is_active})") 