"""
Get User Use Case

Business logic for retrieving user information.
"""

import uuid
from typing import Optional

from ...dto.user_dto import UserDTO, UserSearchDTO, UserListDTO
from ...exceptions.application_exceptions import UserNotFoundError, PermissionDeniedError
from ....domain.repositories.user_repository import UserRepository
from ....domain.entities.user import User


class GetUserUseCase:
    """
    Use case for retrieving user information.
    
    This use case handles the business logic for fetching users,
    including permission checks and data formatting.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_by_id(self, user_id: uuid.UUID, requesting_user_id: Optional[uuid.UUID] = None,
                       is_superuser: bool = False) -> UserDTO:
        """
        Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            UserDTO containing user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        # Fetch user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        
        # Check permissions
        if not self._can_view_user(user, requesting_user_id, is_superuser):
            raise PermissionDeniedError("view_user", str(user_id))
        
        return self._entity_to_dto(user)
    
    async def get_by_email(self, email: str, requesting_user_id: Optional[uuid.UUID] = None,
                          is_superuser: bool = False) -> UserDTO:
        """
        Get a user by email address.
        
        Args:
            email: Email address to search for
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            UserDTO containing user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        from ....domain.value_objects.email import Email
        
        try:
            email_obj = Email.create(email)
        except Exception:
            raise UserNotFoundError(f"email:{email}")
        
        user = await self.user_repository.get_by_email(email_obj)
        if not user:
            raise UserNotFoundError(f"email:{email}")
        
        # Check permissions
        if not self._can_view_user(user, requesting_user_id, is_superuser):
            raise PermissionDeniedError("view_user", f"email:{email}")
        
        return self._entity_to_dto(user)
    
    async def get_by_phone(self, phone: str, requesting_user_id: Optional[uuid.UUID] = None,
                          is_superuser: bool = False) -> UserDTO:
        """
        Get a user by phone number.
        
        Args:
            phone: Phone number to search for
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            UserDTO containing user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            PermissionDeniedError: If user lacks permission
        """
        from ....domain.value_objects.phone import Phone
        
        try:
            phone_obj = Phone.create(phone)
        except Exception:
            raise UserNotFoundError(f"phone:{phone}")
        
        user = await self.user_repository.get_by_phone(phone_obj)
        if not user:
            raise UserNotFoundError(f"phone:{phone}")
        
        # Check permissions
        if not self._can_view_user(user, requesting_user_id, is_superuser):
            raise PermissionDeniedError("view_user", f"phone:{phone}")
        
        return self._entity_to_dto(user)
    
    async def get_users(self, search_dto: UserSearchDTO, requesting_user_id: Optional[uuid.UUID] = None,
                       is_superuser: bool = False) -> UserListDTO:
        """
        Get users with search and pagination.
        
        Args:
            search_dto: Search parameters
            requesting_user_id: ID of the user making the request
            is_superuser: Whether the requesting user is a superuser
            
        Returns:
            UserListDTO with paginated results
            
        Raises:
            PermissionDeniedError: If user lacks permission to list users
        """
        # Only superusers can list all users
        if not is_superuser:
            raise PermissionDeniedError("list_users")
        
        # Get users based on search criteria
        if search_dto.query:
            users = await self.user_repository.search_users(
                search_dto.query, search_dto.skip, search_dto.limit
            )
        elif search_dto.is_active is not None:
            if search_dto.is_active:
                users = await self.user_repository.get_active_users(
                    search_dto.skip, search_dto.limit
                )
            else:
                # Get all users and filter inactive ones
                all_users = await self.user_repository.get_all(
                    search_dto.skip, search_dto.limit
                )
                users = [user for user in all_users if not user.is_active]
        elif search_dto.is_superuser is not None:
            if search_dto.is_superuser:
                users = await self.user_repository.get_superusers(
                    search_dto.skip, search_dto.limit
                )
            else:
                # Get all users and filter non-superusers
                all_users = await self.user_repository.get_all(
                    search_dto.skip, search_dto.limit
                )
                users = [user for user in all_users if not user.is_superuser]
        else:
            users = await self.user_repository.get_all(search_dto.skip, search_dto.limit)
        
        # Get total count
        total_count = await self.user_repository.count()
        
        # Convert to DTOs
        user_dtos = [self._entity_to_dto(user) for user in users]
        
        # Calculate pagination info
        page = (search_dto.skip // search_dto.limit) + 1
        has_next = (search_dto.skip + search_dto.limit) < total_count
        has_previous = search_dto.skip > 0
        
        return UserListDTO(
            users=user_dtos,
            total_count=total_count,
            page=page,
            page_size=search_dto.limit,
            has_next=has_next,
            has_previous=has_previous
        )
    
    async def get_active_users_count(self) -> int:
        """
        Get count of active users.
        
        Returns:
            Number of active users
        """
        return await self.user_repository.count_active_users()
    
    async def get_superusers_count(self) -> int:
        """
        Get count of superusers.
        
        Returns:
            Number of superusers
        """
        return await self.user_repository.count_superusers()
    
    def _can_view_user(self, user: User, requesting_user_id: Optional[uuid.UUID],
                      is_superuser: bool) -> bool:
        """
        Check if the requesting user can view the target user.
        
        Args:
            user: User to view
            requesting_user_id: ID of requesting user
            is_superuser: Whether requesting user is superuser
            
        Returns:
            True if user can be viewed, False otherwise
        """
        # Superusers can view any user
        if is_superuser:
            return True
        
        # Users can view their own profile
        if requesting_user_id and user.id == requesting_user_id:
            return True
        
        # By default, users cannot view other users
        return False
    
    def _entity_to_dto(self, user: User) -> UserDTO:
        """
        Convert User entity to UserDTO.
        
        Args:
            user: User entity
            
        Returns:
            UserDTO
        """
        return UserDTO(
            id=user.id,
            email=str(user.email) if user.email else None,
            phone=str(user.phone) if user.phone else None,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            supabase_id=user.supabase_id
        ) 