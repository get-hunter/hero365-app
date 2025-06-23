"""
Dependency Injection Container

Manages the wiring of dependencies for the clean architecture implementation.
"""

import os
from typing import Dict, Any, Optional
from supabase import create_client, Client

from ...core.config import settings

# Domain Repositories
from ...domain.repositories.business_repository import BusinessRepository
from ...domain.repositories.business_membership_repository import BusinessMembershipRepository
from ...domain.repositories.business_invitation_repository import BusinessInvitationRepository
from ...domain.repositories.contact_repository import ContactRepository
from ...domain.repositories.job_repository import JobRepository
from ...domain.repositories.activity_repository import ActivityRepository

# Application Ports
from ...application.ports.auth_service import AuthServicePort
from ...application.ports.email_service import EmailServicePort
from ...application.ports.sms_service import SMSServicePort

# Infrastructure Implementations
from ..database.repositories.supabase_business_repository import SupabaseBusinessRepository
from ..database.repositories.supabase_business_membership_repository import SupabaseBusinessMembershipRepository
from ..database.repositories.supabase_business_invitation_repository import SupabaseBusinessInvitationRepository
from ..database.repositories.supabase_contact_repository import SupabaseContactRepository
from ..database.repositories.supabase_job_repository import SupabaseJobRepository
from ..database.repositories.supabase_activity_repository import SupabaseActivityRepository, SupabaseActivityTemplateRepository
from ..external_services.supabase_auth_adapter import SupabaseAuthAdapter
from ..external_services.smtp_email_adapter import SMTPEmailAdapter
from ..external_services.twilio_sms_adapter import TwilioSMSAdapter

# Application Use Cases
from ...application.use_cases.auth.authenticate_user import AuthenticateUserUseCase
from ...application.use_cases.auth.register_user import RegisterUserUseCase
from ...application.use_cases.auth.reset_password import ResetPasswordUseCase

from ...application.use_cases.user.manage_onboarding import ManageOnboardingUseCase

from ...application.use_cases.business.create_business import CreateBusinessUseCase
from ...application.use_cases.business.invite_team_member import InviteTeamMemberUseCase
from ...application.use_cases.business.accept_invitation import AcceptInvitationUseCase
from ...application.use_cases.business.get_user_businesses import GetUserBusinessesUseCase
from ...application.use_cases.business.get_business_detail import GetBusinessDetailUseCase
from ...application.use_cases.business.update_business import UpdateBusinessUseCase
from ...application.use_cases.business.manage_team_member import ManageTeamMemberUseCase
from ...application.use_cases.business.manage_invitations import ManageInvitationsUseCase

# Contact Use Cases
from ...application.use_cases.contact.manage_contacts import ManageContactsUseCase

# Job Use Cases
from ...application.use_cases.job.manage_jobs import ManageJobsUseCase

# Activity Use Cases
from ...application.use_cases.activity.manage_activities import ManageActivitiesUseCase


class DependencyContainer:
    """
    Dependency Injection Container for Clean Architecture.
    
    Manages the creation and wiring of all application dependencies.
    """
    
    def __init__(self):
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._use_cases: Dict[str, Any] = {}
        self._supabase_client: Optional[Client] = None
        
        # Initialize dependencies
        self._setup_repositories()
        self._setup_services()
        self._setup_use_cases()
    
    def _setup_repositories(self):
        """Initialize repository implementations."""
        # Database repositories using Supabase client
        supabase_client = self._get_supabase_client()
        self._repositories['business_repository'] = SupabaseBusinessRepository(supabase_client=supabase_client)
        self._repositories['business_membership_repository'] = SupabaseBusinessMembershipRepository(supabase_client=supabase_client)
        self._repositories['business_invitation_repository'] = SupabaseBusinessInvitationRepository(supabase_client=supabase_client)
        self._repositories['contact_repository'] = SupabaseContactRepository(client=supabase_client)
        self._repositories['job_repository'] = SupabaseJobRepository(client=supabase_client)
        self._repositories['activity_repository'] = SupabaseActivityRepository(client=supabase_client)
        self._repositories['activity_template_repository'] = SupabaseActivityTemplateRepository(client=supabase_client)
    
    def _setup_services(self):
        """Initialize external service adapters."""
        # Authentication service
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            self._services['auth_service'] = SupabaseAuthAdapter(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY,
                supabase_service_key=settings.SUPABASE_SERVICE_KEY
            )
        
        # Email service
        self._services['email_service'] = SMTPEmailAdapter(
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            use_tls=True
        )
        
        # SMS service (optional - only if Twilio credentials are provided)
        if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
            try:
                self._services['sms_service'] = TwilioSMSAdapter(
                    account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
                    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
                    phone_number=os.getenv("TWILIO_PHONE_NUMBER")
                )
            except ImportError:
                # Twilio not installed, SMS service unavailable
                self._services['sms_service'] = None
        else:
            self._services['sms_service'] = None
    
    def _setup_use_cases(self):
        """Initialize use case implementations."""
        # Auth use cases (simplified without user management)
        self._use_cases['authenticate_user'] = AuthenticateUserUseCase()
        self._use_cases['register_user'] = RegisterUserUseCase()
        self._use_cases['reset_password'] = ResetPasswordUseCase()
        
        # User use cases
        self._use_cases['manage_onboarding'] = ManageOnboardingUseCase()
        
        # Business use cases
        self._use_cases['create_business'] = CreateBusinessUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository')
        )
        
        self._use_cases['invite_team_member'] = InviteTeamMemberUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository'),
            invitation_repository=self.get_repository('business_invitation_repository'),
            email_service=self.get_service('email_service')
        )
        
        self._use_cases['accept_invitation'] = AcceptInvitationUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository'),
            invitation_repository=self.get_repository('business_invitation_repository')
        )
        
        self._use_cases['get_user_businesses'] = GetUserBusinessesUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository'),
            invitation_repository=self.get_repository('business_invitation_repository')
        )
        
        self._use_cases['get_business_detail'] = GetBusinessDetailUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository'),
            invitation_repository=self.get_repository('business_invitation_repository')
        )
        
        self._use_cases['update_business'] = UpdateBusinessUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository')
        )
        
        self._use_cases['manage_team_member'] = ManageTeamMemberUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository')
        )
        
        self._use_cases['manage_invitations'] = ManageInvitationsUseCase(
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository'),
            invitation_repository=self.get_repository('business_invitation_repository')
        )
        
        # Contact use cases
        self._use_cases['manage_contacts'] = ManageContactsUseCase(
            contact_repository=self.get_repository('contact_repository'),
            business_repository=self.get_repository('business_repository'),
            membership_repository=self.get_repository('business_membership_repository')
        )
        
        # Job use cases
        self._use_cases['manage_jobs'] = ManageJobsUseCase(
            job_repository=self.get_repository('job_repository'),
            business_membership_repository=self.get_repository('business_membership_repository'),
            contact_repository=self.get_repository('contact_repository')
        )
        
        # Activity use cases
        self._use_cases['manage_activities'] = ManageActivitiesUseCase(
            activity_repository=self.get_repository('activity_repository'),
            template_repository=self.get_repository('activity_template_repository'),
            contact_repository=self.get_repository('contact_repository'),
            membership_repository=self.get_repository('business_membership_repository')
        )

    def _get_supabase_client(self) -> Client:
        """Get or create Supabase client."""
        if self._supabase_client is None:
            # Use service key for database operations (bypasses RLS and has full access)
            self._supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        return self._supabase_client

    def get_repository(self, name: str) -> Any:
        """Get repository by name."""
        return self._repositories.get(name)

    def get_service(self, name: str) -> Any:
        """Get service by name."""
        return self._services.get(name)

    def get_use_case(self, name: str) -> Any:
        """Get use case by name."""
        return self._use_cases.get(name)

    def get_auth_service(self) -> AuthServicePort:
        """Get authentication service."""
        return self.get_service('auth_service')

    def get_email_service(self) -> EmailServicePort:
        """Get email service."""
        return self.get_service('email_service')

    def get_sms_service(self) -> Optional[SMSServicePort]:
        """Get SMS service."""
        return self.get_service('sms_service')

    def get_authenticate_user_use_case(self) -> AuthenticateUserUseCase:
        """Get authenticate user use case."""
        return self.get_use_case('authenticate_user')

    def get_register_user_use_case(self) -> RegisterUserUseCase:
        """Get register user use case."""
        return self.get_use_case('register_user')

    def get_reset_password_use_case(self) -> ResetPasswordUseCase:
        """Get reset password use case."""
        return self.get_use_case('reset_password')

    def get_manage_onboarding_use_case(self) -> ManageOnboardingUseCase:
        """Get manage onboarding use case."""
        return self.get_use_case('manage_onboarding')

    def get_business_repository(self) -> BusinessRepository:
        """Get business repository."""
        return self.get_repository('business_repository')

    def get_business_membership_repository(self) -> BusinessMembershipRepository:
        """Get business membership repository."""
        return self.get_repository('business_membership_repository')

    def get_business_invitation_repository(self) -> BusinessInvitationRepository:
        """Get business invitation repository."""
        return self.get_repository('business_invitation_repository')

    def get_create_business_use_case(self) -> CreateBusinessUseCase:
        """Get create business use case."""
        return self.get_use_case('create_business')

    def get_invite_team_member_use_case(self) -> InviteTeamMemberUseCase:
        """Get invite team member use case."""
        return self.get_use_case('invite_team_member')

    def get_accept_invitation_use_case(self) -> AcceptInvitationUseCase:
        """Get accept invitation use case."""
        return self.get_use_case('accept_invitation')

    def get_get_user_businesses_use_case(self) -> GetUserBusinessesUseCase:
        """Get user businesses use case."""
        return self.get_use_case('get_user_businesses')

    def get_get_business_detail_use_case(self) -> GetBusinessDetailUseCase:
        """Get business detail use case."""
        return self.get_use_case('get_business_detail')

    def get_update_business_use_case(self) -> UpdateBusinessUseCase:
        """Get update business use case."""
        return self.get_use_case('update_business')

    def get_manage_team_member_use_case(self) -> ManageTeamMemberUseCase:
        """Get manage team member use case."""
        return self.get_use_case('manage_team_member')

    def get_manage_invitations_use_case(self) -> ManageInvitationsUseCase:
        """Get manage invitations use case."""
        return self.get_use_case('manage_invitations')

    def get_contact_repository(self) -> ContactRepository:
        """Get contact repository."""
        return self.get_repository('contact_repository')

    def get_manage_contacts_use_case(self) -> ManageContactsUseCase:
        """Get manage contacts use case."""
        return self.get_use_case('manage_contacts')
    
    def get_job_repository(self) -> JobRepository:
        """Get job repository."""
        return self.get_repository('job_repository')
    
    def get_manage_jobs_use_case(self) -> ManageJobsUseCase:
        """Get manage jobs use case."""
        return self.get_use_case('manage_jobs')

    def close(self):
        """Close all connections and cleanup resources."""
        # Close Supabase connection if exists
        if self._supabase_client:
            # Supabase client doesn't need explicit closing
            self._supabase_client = None
        
        # Clear all dependencies
        self._repositories.clear()
        self._services.clear()
        self._use_cases.clear()


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def reset_container():
    """Reset the global container (mainly for testing)."""
    global _container
    if _container:
        _container.close()
    _container = None


def get_auth_service() -> AuthServicePort:
    """Get auth service from container."""
    return get_container().get_auth_service()


def get_email_service() -> EmailServicePort:
    """Get email service from container."""
    return get_container().get_email_service()


def get_sms_service() -> Optional[SMSServicePort]:
    """Get SMS service from container."""
    return get_container().get_sms_service()


# Contact dependencies
def get_contact_repository() -> ContactRepository:
    """Get contact repository from container."""
    return get_container().get_contact_repository()


def get_manage_contacts_use_case() -> ManageContactsUseCase:
    """Get manage contacts use case from container."""
    return get_container().get_manage_contacts_use_case()


# Job dependencies
def get_job_repository() -> JobRepository:
    """Get job repository from container."""
    return get_container().get_job_repository()


def get_manage_jobs_use_case() -> ManageJobsUseCase:
    """Get manage jobs use case from container."""
    return get_container().get_manage_jobs_use_case()


# Activity dependencies
def get_activity_repository() -> ActivityRepository:
    """Get activity repository from container."""
    return get_container().get_repository('activity_repository')


def get_manage_activities_use_case() -> ManageActivitiesUseCase:
    """Get manage activities use case from container."""
    return get_container().get_use_case('manage_activities')