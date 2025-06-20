"""
Supabase User Repository Implementation

Repository implementation using Supabase client SDK instead of SQLModel/SQLAlchemy.
This leverages Supabase's built-in features like RLS, real-time subscriptions, and auth integration.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timedelta

from supabase import Client

from ....domain.repositories.user_repository import UserRepository
from ....domain.entities.user import User
from ....domain.value_objects.email import Email
from ....domain.value_objects.phone import Phone
from ....domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)


class SupabaseUserRepository(UserRepository):
    """
    Supabase client implementation of UserRepository.
    
    This repository uses Supabase client SDK for all database operations,
    leveraging RLS, real-time features, and built-in auth integration.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "users"
    
    async def create(self, user: User) -> User:
        """Create a new user in Supabase."""
        try:
            user_data = self._user_to_dict(user)
            
            response = self.client.table(self.table_name).insert(user_data).execute()
            
            if response.data:
                return self._dict_to_user(response.data[0])
            else:
                raise DatabaseError("Failed to create user - no data returned")
                
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"User with email {user.email} already exists")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(user_id)).execute()
            
            if response.data:
                return self._dict_to_user(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user by ID: {str(e)}")
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        try:
            response = self.client.table(self.table_name).select("*").eq("email", str(email)).execute()
            
            if response.data:
                return self._dict_to_user(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user by email: {str(e)}")
    
    async def get_by_phone(self, phone: Phone) -> Optional[User]:
        """Get user by phone."""
        try:
            response = self.client.table(self.table_name).select("*").eq("phone", str(phone)).execute()
            
            if response.data:
                return self._dict_to_user(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user by phone: {str(e)}")
    
    async def get_by_supabase_id(self, supabase_id: str) -> Optional[User]:
        """Get user by Supabase ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("supabase_id", supabase_id).execute()
            
            if response.data:
                return self._dict_to_user(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user by Supabase ID: {str(e)}")
    
    async def update(self, user: User) -> User:
        """Update user in Supabase."""
        try:
            user_data = self._user_to_dict(user)
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(user_data).eq("id", str(user.id)).execute()
            
            if response.data:
                return self._dict_to_user(response.data[0])
            else:
                raise EntityNotFoundError(f"User with ID {user.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"User data conflicts with existing user")
            raise DatabaseError(f"Failed to update user: {str(e)}")
    
    async def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user from Supabase."""
        try:
            response = self.client.table(self.table_name).delete().eq("id", str(user_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete user: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_user(user_data) for user_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get all users: {str(e)}")
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq("is_active", True).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_user(user_data) for user_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active users: {str(e)}")
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name, email, or phone."""
        try:
            # Supabase supports text search and ilike operations
            response = self.client.table(self.table_name).select("*").or_(
                f"full_name.ilike.%{query}%,email.ilike.%{query}%,phone.ilike.%{query}%"
            ).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_user(user_data) for user_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search users: {str(e)}")
    
    async def count(self) -> int:
        """Get total count of users."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count users: {str(e)}")
    
    async def count_active(self) -> int:
        """Get count of active users."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("is_active", True).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count active users: {str(e)}")
    
    async def is_email_unique(self, email: Email, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """Check if email is unique."""
        try:
            query = self.client.table(self.table_name).select("id").eq("email", str(email))
            
            if exclude_user_id:
                query = query.neq("id", str(exclude_user_id))
            
            response = query.execute()
            
            return len(response.data) == 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check email uniqueness: {str(e)}")
    
    async def is_phone_unique(self, phone: Phone, exclude_user_id: Optional[uuid.UUID] = None) -> bool:
        """Check if phone is unique."""
        try:
            query = self.client.table(self.table_name).select("id").eq("phone", str(phone))
            
            if exclude_user_id:
                query = query.neq("id", str(exclude_user_id))
            
            response = query.execute()
            
            return len(response.data) == 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check phone uniqueness: {str(e)}")
    
    async def get_recent_users(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[User]:
        """Get recently created users."""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.client.table(self.table_name).select("*").gte("created_at", cutoff_date).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
            
            return [self._dict_to_user(user_data) for user_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get recent users: {str(e)}")
    
    async def count_superusers(self) -> int:
        """Get count of superusers."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("is_superuser", True).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count superusers: {str(e)}")
    
    def _user_to_dict(self, user: User) -> dict:
        """Convert User domain entity to dictionary for Supabase."""
        return {
            "id": str(user.id),
            "email": str(user.email),
            "phone": str(user.phone) if user.phone else None,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "supabase_id": user.supabase_id,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else datetime.utcnow().isoformat(),
        }
    
    def _dict_to_user(self, data: dict) -> User:
        """Convert dictionary data from Supabase to User domain entity."""
        return User(
            id=uuid.UUID(data["id"]),
            email=Email(data["email"]),
            phone=Phone(data["phone"]) if data.get("phone") else None,
            full_name=data["full_name"],
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            supabase_id=data.get("supabase_id"),
            hashed_password=data.get("hashed_password"),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")) if data.get("updated_at") else None,
        ) 