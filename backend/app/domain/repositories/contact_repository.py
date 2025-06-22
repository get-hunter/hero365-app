"""
Contact Repository Interface

Defines the contract for contact data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..entities.contact import Contact, ContactType, ContactStatus, ContactPriority, ContactSource


class ContactRepository(ABC):
    """
    Repository interface for Contact entity operations.
    
    This interface defines the contract for all contact data access operations,
    following the Repository pattern to abstract database implementation details.
    """
    
    @abstractmethod
    async def create(self, contact: Contact) -> Contact:
        """
        Create a new contact.
        
        Args:
            contact: Contact entity to create
            
        Returns:
            Created contact entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If contact with same email/phone exists in business
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, contact_id: uuid.UUID) -> Optional[Contact]:
        """
        Get contact by ID.
        
        Args:
            contact_id: Unique identifier of the contact
            
        Returns:
            Contact entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts by business ID.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities for the business
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, business_id: uuid.UUID, email: str) -> Optional[Contact]:
        """
        Get contact by email within a business.
        
        Args:
            business_id: ID of the business
            email: Email address to search for
            
        Returns:
            Contact entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_phone(self, business_id: uuid.UUID, phone: str) -> Optional[Contact]:
        """
        Get contact by phone within a business.
        
        Args:
            business_id: ID of the business
            phone: Phone number to search for
            
        Returns:
            Contact entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_type(self, business_id: uuid.UUID, contact_type: ContactType, 
                         skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts by type within a business.
        
        Args:
            business_id: ID of the business
            contact_type: Type of contacts to retrieve
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities of the specified type
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, business_id: uuid.UUID, status: ContactStatus,
                           skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts by status within a business.
        
        Args:
            business_id: ID of the business
            status: Status of contacts to retrieve
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities with the specified status
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_priority(self, business_id: uuid.UUID, priority: ContactPriority,
                             skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts by priority within a business.
        
        Args:
            business_id: ID of the business
            priority: Priority of contacts to retrieve
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities with the specified priority
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts assigned to a specific user within a business.
        
        Args:
            business_id: ID of the business
            user_id: ID of the assigned user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities assigned to the user
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_tag(self, business_id: uuid.UUID, tag: str,
                        skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts with a specific tag within a business.
        
        Args:
            business_id: ID of the business
            tag: Tag to search for
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities with the specified tag
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def search_contacts(self, business_id: uuid.UUID, search_term: str,
                             skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Search contacts within a business by name, email, phone, or company.
        
        Args:
            business_id: ID of the business
            search_term: Term to search for
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities matching the search term
            
        Raises:
            DatabaseError: If search fails
        """
        pass
    
    @abstractmethod
    async def get_recently_contacted(self, business_id: uuid.UUID, days: int = 30,
                                   skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts that were recently contacted within a business.
        
        Args:
            business_id: ID of the business
            days: Number of days to look back
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities recently contacted
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_never_contacted(self, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts that have never been contacted within a business.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities never contacted
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_high_value_contacts(self, business_id: uuid.UUID, min_value: float,
                                    skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts with estimated value above threshold within a business.
        
        Args:
            business_id: ID of the business
            min_value: Minimum estimated value
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Contact entities with high estimated value
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, contact: Contact) -> Contact:
        """
        Update an existing contact.
        
        Args:
            contact: Contact entity with updated information
            
        Returns:
            Updated contact entity
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(self, contact_id: uuid.UUID) -> bool:
        """
        Delete a contact by ID.
        
        Args:
            contact_id: ID of the contact to delete
            
        Returns:
            True if contact was deleted, False if not found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                               status: ContactStatus) -> int:
        """
        Update status for multiple contacts.
        
        Args:
            business_id: ID of the business
            contact_ids: List of contact IDs to update
            status: New status to set
            
        Returns:
            Number of contacts updated
            
        Raises:
            DatabaseError: If bulk update fails
        """
        pass
    
    @abstractmethod
    async def bulk_assign_contacts(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                                 user_id: str) -> int:
        """
        Assign multiple contacts to a user.
        
        Args:
            business_id: ID of the business
            contact_ids: List of contact IDs to assign
            user_id: ID of the user to assign contacts to
            
        Returns:
            Number of contacts assigned
            
        Raises:
            DatabaseError: If bulk assignment fails
        """
        pass
    
    @abstractmethod
    async def bulk_add_tag(self, business_id: uuid.UUID, contact_ids: List[uuid.UUID],
                          tag: str) -> int:
        """
        Add a tag to multiple contacts.
        
        Args:
            business_id: ID of the business
            contact_ids: List of contact IDs to tag
            tag: Tag to add
            
        Returns:
            Number of contacts tagged
            
        Raises:
            DatabaseError: If bulk tagging fails
        """
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """
        Get total count of contacts for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Total number of contacts
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_by_type(self, business_id: uuid.UUID, contact_type: ContactType) -> int:
        """
        Get count of contacts by type for a business.
        
        Args:
            business_id: ID of the business
            contact_type: Type of contacts to count
            
        Returns:
            Number of contacts of the specified type
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, business_id: uuid.UUID, status: ContactStatus) -> int:
        """
        Get count of contacts by status for a business.
        
        Args:
            business_id: ID of the business
            status: Status of contacts to count
            
        Returns:
            Number of contacts with the specified status
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def get_contact_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive contact statistics for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Dictionary with contact statistics (counts by type, status, priority, etc.)
            
        Raises:
            DatabaseError: If statistics retrieval fails
        """
        pass
    
    @abstractmethod
    async def exists(self, contact_id: uuid.UUID) -> bool:
        """
        Check if a contact exists.
        
        Args:
            contact_id: ID of the contact to check
            
        Returns:
            True if contact exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def has_duplicate_email(self, business_id: uuid.UUID, email: str, 
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if email already exists for another contact in the business.
        
        Args:
            business_id: ID of the business
            email: Email to check
            exclude_id: Contact ID to exclude from check (for updates)
            
        Returns:
            True if duplicate exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def has_duplicate_phone(self, business_id: uuid.UUID, phone: str,
                                exclude_id: Optional[uuid.UUID] = None) -> bool:
        """
        Check if phone already exists for another contact in the business.
        
        Args:
            business_id: ID of the business
            phone: Phone to check
            exclude_id: Contact ID to exclude from check (for updates)
            
        Returns:
            True if duplicate exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass 