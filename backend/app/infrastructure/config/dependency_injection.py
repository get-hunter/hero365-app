"""
Dependency Injection Container

Manages the wiring of dependencies for the clean architecture implementation.
"""

import os
from typing import Dict, Any, Optional
from supabase import create_client, Client

from ...core.config import settings

# Domain Repositories
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.item_repository import ItemRepository

# Application Ports
from ...application.ports.auth_service import AuthServicePort
from ...application.ports.email_service import EmailServicePort
from ...application.ports.sms_service import SMSServicePort

# Infrastructure Implementations
from ..database.repositories.supabase_user_repository import SupabaseUserRepository
from ..database.repositories.supabase_item_repository import SupabaseItemRepository
from ..external_services.supabase_auth_adapter import SupabaseAuthAdapter
from ..external_services.smtp_email_adapter import SMTPEmailAdapter
from ..external_services.twilio_sms_adapter import TwilioSMSAdapter

# Application Use Cases
from ...application.use_cases.user.create_user import CreateUserUseCase
from ...application.use_cases.user.get_user import GetUserUseCase
from ...application.use_cases.user.update_user import UpdateUserUseCase
from ...application.use_cases.user.delete_user import DeleteUserUseCase

from ...application.use_cases.auth.authenticate_user import AuthenticateUserUseCase
from ...application.use_cases.auth.register_user import RegisterUserUseCase
from ...application.use_cases.auth.reset_password import ResetPasswordUseCase

from ...application.use_cases.item.create_item import CreateItemUseCase
from ...application.use_cases.item.get_items import GetItemsUseCase
from ...application.use_cases.item.update_item import UpdateItemUseCase
from ...application.use_cases.item.delete_item import DeleteItemUseCase


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
        self._repositories['user_repository'] = SupabaseUserRepository(supabase_client=supabase_client)
        self._repositories['item_repository'] = SupabaseItemRepository(supabase_client=supabase_client)
    
    def _setup_services(self):
        """Initialize external service adapters."""
        # Authentication service
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            self._services['auth_service'] = SupabaseAuthAdapter(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY
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
        # User use cases (create first since it's needed by register_user)
        self._use_cases['create_user'] = CreateUserUseCase(
            user_repository=self.get_repository('user_repository')
        )
        
        self._use_cases['get_user'] = GetUserUseCase(
            user_repository=self.get_repository('user_repository')
        )
        
        self._use_cases['update_user'] = UpdateUserUseCase(
            user_repository=self.get_repository('user_repository')
        )
        
        self._use_cases['delete_user'] = DeleteUserUseCase(
            user_repository=self.get_repository('user_repository'),
            item_repository=self.get_repository('item_repository')
        )
        
        # Auth use cases (register_user needs create_user to be already created)
        self._use_cases['authenticate_user'] = AuthenticateUserUseCase(
            user_repository=self.get_repository('user_repository')
        )
        
        self._use_cases['register_user'] = RegisterUserUseCase(
            create_user_use_case=self._use_cases['create_user']
        )
        
        self._use_cases['reset_password'] = ResetPasswordUseCase(
            user_repository=self.get_repository('user_repository')
        )
        
        # Item use cases
        self._use_cases['create_item'] = CreateItemUseCase(
            item_repository=self.get_repository('item_repository'),
            user_repository=self.get_repository('user_repository')
        )
        
        self._use_cases['get_items'] = GetItemsUseCase(
            item_repository=self.get_repository('item_repository')
        )
        
        self._use_cases['update_item'] = UpdateItemUseCase(
            item_repository=self.get_repository('item_repository')
        )
        
        self._use_cases['delete_item'] = DeleteItemUseCase(
            item_repository=self.get_repository('item_repository')
        )
    
    def _get_supabase_client(self) -> Client:
        """Get Supabase client."""
        if not self._supabase_client:
            self._supabase_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY
            )
        return self._supabase_client
    
    def get_repository(self, name: str) -> Any:
        """Get repository by name."""
        if name not in self._repositories:
            raise ValueError(f"Repository '{name}' not found")
        return self._repositories[name]
    
    def get_service(self, name: str) -> Any:
        """Get service by name."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
        return self._services[name]
    
    def get_use_case(self, name: str) -> Any:
        """Get use case by name."""
        if name not in self._use_cases:
            raise ValueError(f"Use case '{name}' not found")
        return self._use_cases[name]
    
    def get_user_repository(self) -> UserRepository:
        """Get user repository."""
        return self.get_repository('user_repository')
    
    def get_item_repository(self) -> ItemRepository:
        """Get item repository."""
        return self.get_repository('item_repository')
    
    def get_auth_service(self) -> AuthServicePort:
        """Get authentication service."""
        return self.get_service('auth_service')
    
    def get_email_service(self) -> EmailServicePort:
        """Get email service."""
        return self.get_service('email_service')
    
    def get_sms_service(self) -> Optional[SMSServicePort]:
        """Get SMS service (may be None if not configured)."""
        return self.get_service('sms_service')
    
    # User Use Cases
    def get_create_user_use_case(self) -> CreateUserUseCase:
        """Get create user use case."""
        return self.get_use_case('create_user')
    
    def get_get_user_use_case(self) -> GetUserUseCase:
        """Get get user use case."""
        return self.get_use_case('get_user')
    
    def get_update_user_use_case(self) -> UpdateUserUseCase:
        """Get update user use case."""
        return self.get_use_case('update_user')
    
    def get_delete_user_use_case(self) -> DeleteUserUseCase:
        """Get delete user use case."""
        return self.get_use_case('delete_user')
    
    # Auth Use Cases
    def get_authenticate_user_use_case(self) -> AuthenticateUserUseCase:
        """Get authenticate user use case."""
        return self.get_use_case('authenticate_user')
    
    def get_register_user_use_case(self) -> RegisterUserUseCase:
        """Get register user use case."""
        return self.get_use_case('register_user')
    
    def get_reset_password_use_case(self) -> ResetPasswordUseCase:
        """Get reset password use case."""
        return self.get_use_case('reset_password')
    
    # Item Use Cases
    def get_create_item_use_case(self) -> CreateItemUseCase:
        """Get create item use case."""
        return self.get_use_case('create_item')
    
    def get_get_items_use_case(self) -> GetItemsUseCase:
        """Get get items use case."""
        return self.get_use_case('get_items')
    
    def get_update_item_use_case(self) -> UpdateItemUseCase:
        """Get update item use case."""
        return self.get_use_case('update_item')
    
    def get_delete_item_use_case(self) -> DeleteItemUseCase:
        """Get delete item use case."""
        return self.get_use_case('delete_item')
    
    def close(self):
        """Clean up resources."""
        if self._supabase_client:
            # Supabase client doesn't need explicit cleanup
            self._supabase_client = None


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def reset_container():
    """Reset the global container (useful for testing)."""
    global _container
    if _container:
        _container.close()
    _container = None


# Convenience functions for common dependencies
def get_user_repository() -> UserRepository:
    """Get user repository."""
    return get_container().get_user_repository()


def get_item_repository() -> ItemRepository:
    """Get item repository."""
    return get_container().get_item_repository()


def get_auth_service() -> AuthServicePort:
    """Get authentication service."""
    return get_container().get_auth_service()


def get_email_service() -> EmailServicePort:
    """Get email service."""
    return get_container().get_email_service()


def get_sms_service() -> Optional[SMSServicePort]:
    """Get SMS service."""
    return get_container().get_sms_service() 