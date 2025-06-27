"""
Contact Use Cases Package

Exports all contact management use cases.
"""

from .create_contact_use_case import CreateContactUseCase
from .get_contact_use_case import GetContactUseCase
from .update_contact_use_case import UpdateContactUseCase
from .delete_contact_use_case import DeleteContactUseCase
from .list_contacts_use_case import ListContactsUseCase
from .search_contacts_use_case import SearchContactsUseCase
from .contact_statistics_use_case import ContactStatisticsUseCase
from .contact_interaction_use_case import ContactInteractionUseCase
from .contact_status_management_use_case import ContactStatusManagementUseCase
from .bulk_contact_operations_use_case import BulkContactOperationsUseCase

__all__ = [
    "CreateContactUseCase",
    "GetContactUseCase", 
    "UpdateContactUseCase",
    "DeleteContactUseCase",
    "ListContactsUseCase",
    "SearchContactsUseCase",
    "ContactStatisticsUseCase",
    "ContactInteractionUseCase",
    "ContactStatusManagementUseCase",
    "BulkContactOperationsUseCase"
] 