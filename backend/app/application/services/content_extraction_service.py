"""
Content Extraction Service

Service for extracting meaningful content from different entity types
for embedding generation and change detection.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from ..dto.contact_dto import ContactDto
from ..dto.job_dto import JobDto
from ..dto.estimate_dto import EstimateDto
from ..dto.invoice_dto import InvoiceDto
from ..dto.product_dto import ProductDto
from ..dto.project_dto import ProjectDto
# EntityType enum not yet defined, using string literals


class ContentExtractionService:
    """
    Service for extracting searchable content from entity objects.
    
    This service knows how to extract meaningful textual content from each
    entity type for embedding generation and provides change detection
    through content hashing.
    """
    
    def extract_contact_content(self, contact: ContactDto) -> str:
        """
        Extract meaningful content from a contact entity.
        
        Args:
            contact: The contact DTO object
            
        Returns:
            Combined textual content for embedding
        """
        content_parts = []
        
        # Basic identification
        if contact.first_name:
            content_parts.append(f"First name: {contact.first_name}")
        if contact.last_name:
            content_parts.append(f"Last name: {contact.last_name}")
        if contact.company_name:
            content_parts.append(f"Company: {contact.company_name}")
        if contact.job_title:
            content_parts.append(f"Job title: {contact.job_title}")
        
        # Contact information
        if contact.email:
            content_parts.append(f"Email: {contact.email}")
        if contact.phone:
            content_parts.append(f"Phone: {contact.phone}")
        if contact.mobile_phone:
            content_parts.append(f"Mobile: {contact.mobile_phone}")
        if contact.website:
            content_parts.append(f"Website: {contact.website}")
        
        # Address information
        if contact.address:
            content_parts.append(f"Address: {contact.address}")
        if contact.city:
            content_parts.append(f"City: {contact.city}")
        if contact.state:
            content_parts.append(f"State: {contact.state}")
        if contact.postal_code:
            content_parts.append(f"Postal code: {contact.postal_code}")
        if contact.country:
            content_parts.append(f"Country: {contact.country}")
        
        # Business context
        if contact.contact_type:
            content_parts.append(f"Contact type: {contact.contact_type}")
        if contact.source:
            content_parts.append(f"Source: {contact.source}")
        if contact.status:
            content_parts.append(f"Status: {contact.status}")
        if contact.lifecycle_stage:
            content_parts.append(f"Lifecycle stage: {contact.lifecycle_stage}")
        if contact.priority:
            content_parts.append(f"Priority: {contact.priority}")
        if contact.relationship_status:
            content_parts.append(f"Relationship status: {contact.relationship_status}")
        
        # Additional information
        if contact.notes:
            content_parts.append(f"Notes: {contact.notes}")
        if contact.tags:
            tags_str = ", ".join(str(tag) for tag in contact.tags)
            content_parts.append(f"Tags: {tags_str}")
        
        # Combine all parts
        return " | ".join(content_parts)
    
    def extract_job_content(self, job: JobDto) -> str:
        """Extract meaningful content from a job entity."""
        content_parts = []
        
        # Basic information
        if job.job_number:
            content_parts.append(f"Job number: {job.job_number}")
        if job.title:
            content_parts.append(f"Title: {job.title}")
        if job.description:
            content_parts.append(f"Description: {job.description}")
        
        # Job classification
        if job.job_type:
            content_parts.append(f"Job type: {job.job_type}")
        if job.status:
            content_parts.append(f"Status: {job.status}")
        if job.priority:
            content_parts.append(f"Priority: {job.priority}")
        if job.source:
            content_parts.append(f"Source: {job.source}")
        
        # Location information
        if job.location_address:
            content_parts.append(f"Location: {job.location_address}")
        if job.location_city:
            content_parts.append(f"City: {job.location_city}")
        if job.location_state:
            content_parts.append(f"State: {job.location_state}")
        if job.location_postal_code:
            content_parts.append(f"Postal code: {job.location_postal_code}")
        
        # Time and cost estimates
        if job.estimated_duration_hours:
            content_parts.append(f"Estimated duration: {job.estimated_duration_hours} hours")
        if job.estimated_cost:
            content_parts.append(f"Estimated cost: ${job.estimated_cost}")
        
        # Additional information
        if job.special_instructions:
            content_parts.append(f"Special instructions: {job.special_instructions}")
        if job.internal_notes:
            content_parts.append(f"Internal notes: {job.internal_notes}")
        
        return " | ".join(content_parts)
    
    def extract_estimate_content(self, estimate: EstimateDto) -> str:
        """Extract meaningful content from an estimate entity."""
        content_parts = []
        
        # Basic information
        if estimate.estimate_number:
            content_parts.append(f"Estimate number: {estimate.estimate_number}")
        if estimate.title:
            content_parts.append(f"Title: {estimate.title}")
        if estimate.description:
            content_parts.append(f"Description: {estimate.description}")
        
        # Status and classification
        if estimate.status:
            content_parts.append(f"Status: {estimate.status}")
        if estimate.assigned_to:
            content_parts.append(f"Assigned to: {estimate.assigned_to}")
        
        # Client information
        if estimate.client_name:
            content_parts.append(f"Client: {estimate.client_name}")
        if estimate.client_email:
            content_parts.append(f"Client email: {estimate.client_email}")
        if estimate.client_phone:
            content_parts.append(f"Client phone: {estimate.client_phone}")
        
        # Financial information
        if estimate.currency:
            content_parts.append(f"Currency: {estimate.currency}")
        if estimate.subtotal:
            content_parts.append(f"Subtotal: {estimate.subtotal}")
        if estimate.total_amount:
            content_parts.append(f"Total: {estimate.total_amount}")
        if estimate.discount_type and estimate.discount_type != 'none':
            content_parts.append(f"Discount type: {estimate.discount_type}")
        if estimate.tax_rate:
            content_parts.append(f"Tax rate: {estimate.tax_rate}%")
        
        # Dates
        if estimate.valid_until:
            content_parts.append(f"Valid until: {estimate.valid_until}")
        if estimate.issue_date:
            content_parts.append(f"Issue date: {estimate.issue_date}")
        
        # Additional information
        if estimate.notes:
            content_parts.append(f"Notes: {estimate.notes}")
        if estimate.terms_and_conditions:
            content_parts.append(f"Terms: {estimate.terms_and_conditions}")
        
        return " | ".join(content_parts)
    
    def extract_invoice_content(self, invoice: InvoiceDto) -> str:
        """Extract meaningful content from an invoice entity."""
        content_parts = []
        
        # Basic information
        if invoice.invoice_number:
            content_parts.append(f"Invoice number: {invoice.invoice_number}")
        if invoice.title:
            content_parts.append(f"Title: {invoice.title}")
        if invoice.description:
            content_parts.append(f"Description: {invoice.description}")
        
        # Status and classification
        if invoice.status:
            content_parts.append(f"Status: {invoice.status}")
        if invoice.assigned_to:
            content_parts.append(f"Assigned to: {invoice.assigned_to}")
        
        # Client information
        if invoice.client_name:
            content_parts.append(f"Client: {invoice.client_name}")
        if invoice.client_email:
            content_parts.append(f"Client email: {invoice.client_email}")
        if invoice.client_phone:
            content_parts.append(f"Client phone: {invoice.client_phone}")
        
        # Financial information
        if invoice.currency:
            content_parts.append(f"Currency: {invoice.currency}")
        if invoice.subtotal:
            content_parts.append(f"Subtotal: {invoice.subtotal}")
        if invoice.total_amount:
            content_parts.append(f"Total: {invoice.total_amount}")
        if invoice.amount_paid:
            content_parts.append(f"Amount paid: {invoice.amount_paid}")
        if invoice.discount_type and invoice.discount_type != 'none':
            content_parts.append(f"Discount type: {invoice.discount_type}")
        if invoice.tax_rate:
            content_parts.append(f"Tax rate: {invoice.tax_rate}%")
        
        # Dates
        if invoice.due_date:
            content_parts.append(f"Due date: {invoice.due_date}")
        if invoice.issue_date:
            content_parts.append(f"Issue date: {invoice.issue_date}")
        if invoice.paid_date:
            content_parts.append(f"Paid date: {invoice.paid_date}")
        
        # Additional information
        if invoice.notes:
            content_parts.append(f"Notes: {invoice.notes}")
        if invoice.terms_and_conditions:
            content_parts.append(f"Terms: {invoice.terms_and_conditions}")
        
        return " | ".join(content_parts)
    
    def extract_product_content(self, product: ProductDto) -> str:
        """Extract meaningful content from a product entity."""
        content_parts = []
        
        # Basic information
        if product.sku:
            content_parts.append(f"SKU: {product.sku}")
        if product.name:
            content_parts.append(f"Name: {product.name}")
        if product.description:
            content_parts.append(f"Description: {product.description}")
        if product.long_description:
            content_parts.append(f"Long description: {product.long_description}")
        
        # Classification
        if product.product_type:
            content_parts.append(f"Product type: {product.product_type}")
        if product.status:
            content_parts.append(f"Status: {product.status}")
        if product.pricing_model:
            content_parts.append(f"Pricing model: {product.pricing_model}")
        
        # Pricing information
        if product.unit_price:
            content_parts.append(f"Unit price: ${product.unit_price}")
        if product.cost_price:
            content_parts.append(f"Cost price: ${product.cost_price}")
        if product.unit_of_measure:
            content_parts.append(f"Unit of measure: {product.unit_of_measure}")
        
        # Inventory information
        if product.current_stock is not None:
            content_parts.append(f"Current stock: {product.current_stock}")
        if product.reorder_point:
            content_parts.append(f"Reorder point: {product.reorder_point}")
        
        # Additional information
        if product.barcode:
            content_parts.append(f"Barcode: {product.barcode}")
        if product.notes:
            content_parts.append(f"Notes: {product.notes}")
        if product.tags:
            tags_str = ", ".join(str(tag) for tag in product.tags)
            content_parts.append(f"Tags: {tags_str}")
        
        return " | ".join(content_parts)
    
    def extract_project_content(self, project: ProjectDto) -> str:
        """Extract meaningful content from a project entity."""
        content_parts = []
        
        # Basic information
        if project.name:
            content_parts.append(f"Name: {project.name}")
        if project.description:
            content_parts.append(f"Description: {project.description}")
        if project.client_name:
            content_parts.append(f"Client: {project.client_name}")
        
        # Classification
        if project.project_type:
            content_parts.append(f"Project type: {project.project_type}")
        if project.status:
            content_parts.append(f"Status: {project.status}")
        if project.priority:
            content_parts.append(f"Priority: {project.priority}")
        
        # People and management
        if project.created_by:
            content_parts.append(f"Created by: {project.created_by}")
        if project.manager:
            content_parts.append(f"Manager: {project.manager}")
        if project.team_members:
            members_str = ", ".join(str(member) for member in project.team_members)
            content_parts.append(f"Team members: {members_str}")
        
        # Location
        if project.client_address:
            content_parts.append(f"Client address: {project.client_address}")
        
        # Timeline and budget
        if project.start_date:
            content_parts.append(f"Start date: {project.start_date}")
        if project.end_date:
            content_parts.append(f"End date: {project.end_date}")
        if project.estimated_budget:
            content_parts.append(f"Estimated budget: ${project.estimated_budget}")
        if project.actual_cost:
            content_parts.append(f"Actual cost: ${project.actual_cost}")
        
        # Additional information
        if project.notes:
            content_parts.append(f"Notes: {project.notes}")
        if project.tags:
            tags_str = ", ".join(str(tag) for tag in project.tags)
            content_parts.append(f"Tags: {tags_str}")
        
        return " | ".join(content_parts)
    
    def extract_content_for_entity(self, entity_type: str, entity_data: Dict[str, Any]) -> str:
        """
        Extract content for any entity type using unified interface.
        
        Args:
            entity_type: The type of entity (contact, job, estimate, etc.)
            entity_data: The entity data as a dictionary
            
        Returns:
            Extracted content string
            
        Raises:
            ValueError: If entity type is not supported
        """
        if entity_type == 'contact':
            contact = ContactDto(**entity_data)
            return self.extract_contact_content(contact)
        elif entity_type == 'job':
            job = JobDto(**entity_data)
            return self.extract_job_content(job)
        elif entity_type == 'estimate':
            estimate = EstimateDto(**entity_data)
            return self.extract_estimate_content(estimate)
        elif entity_type == 'invoice':
            invoice = InvoiceDto(**entity_data)
            return self.extract_invoice_content(invoice)
        elif entity_type == 'product':
            product = ProductDto(**entity_data)
            return self.extract_product_content(product)
        elif entity_type == 'project':
            project = ProjectDto(**entity_data)
            return self.extract_project_content(project)
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")
    
    def calculate_content_hash(self, content: str) -> str:
        """
        Calculate SHA256 hash of content for change detection.
        
        Args:
            content: The content string to hash
            
        Returns:
            SHA256 hash as hexadecimal string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def has_content_changed(self, new_content: str, existing_hash: Optional[str]) -> bool:
        """
        Check if content has changed by comparing hashes.
        
        Args:
            new_content: The new content to check
            existing_hash: The existing content hash (None if no previous hash)
            
        Returns:
            True if content has changed, False otherwise
        """
        if existing_hash is None:
            return True  # No previous hash means it's new content
        
        new_hash = self.calculate_content_hash(new_content)
        return new_hash != existing_hash
    
    def get_content_preview(self, content: str, max_length: int = 200) -> str:
        """
        Get a preview of the content for storage/debugging.
        
        Args:
            content: The full content string
            max_length: Maximum length of preview
            
        Returns:
            Truncated content preview
        """
        if len(content) <= max_length:
            return content
        
        return content[:max_length - 3] + "..."
    
    def extract_content_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata about the content.
        
        Args:
            content: The content string
            
        Returns:
            Dictionary containing content metadata
        """
        return {
            "character_count": len(content),
            "word_count": len(content.split()),
            "hash": self.calculate_content_hash(content),
            "preview": self.get_content_preview(content),
            "extracted_at": datetime.now().isoformat(),
            "is_empty": len(content.strip()) == 0
        } 