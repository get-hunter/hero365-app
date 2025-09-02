"""
LLM Content Orchestrator - Enhanced with RAG retrieval.
"""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Any

from app.domain.entities.service_page_content import (
    ServicePageContent, ContentBlock, ContentSource, ContentBlockType
)
from app.application.services.rag_retrieval_service import RAGRetrievalService
from app.application.services.content_template_service import ContentTemplateService
from app.application.services.content_quality_gate import ContentQualityGateService
from app.application.services.schema_generator_service import SchemaGeneratorService

logger = logging.getLogger(__name__)


class LLMContentOrchestrator:
    """Orchestrates LLM content generation with RAG retrieval."""
    
    def __init__(self, rag_service: Optional[RAGRetrievalService] = None):
        self.providers = []
        self.rag_service = rag_service
        self.template_service = ContentTemplateService()
        self.quality_gate = ContentQualityGateService()
        self.schema_generator = SchemaGeneratorService()
    
    async def generate_content_block(
        self,
        block_type: ContentBlockType,
        context: Dict[str, Any],
        target_keywords: List[str] = None
    ) -> Optional[ContentBlock]:
        """Generate a content block (placeholder for now)."""
        
        # For now, return template-based content
        # Will be replaced with actual LLM calls
        
        content = self._get_template_content(block_type, context)
        
        return ContentBlock(
            type=block_type,
            content=content,
            source=ContentSource.TEMPLATE
        )
    
    def _get_template_content(self, block_type: ContentBlockType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get template content for block type, enhanced with RAG data and category-specific templates."""
        
        business_name = context.get('business_name', 'Elite HVAC Austin')
        service_name = context.get('service_name', 'HVAC Service')
        city = context.get('city', 'Austin')
        
        # Debug logging
        logger.info(f"Template context - service_name: {service_name} (type: {type(service_name)}), business_name: {business_name}, city: {city}")
        
        # Extract RAG context if available
        rag_context = context.get('rag_context', {})
        business_info = rag_context.get('business_info', {})
        testimonials = rag_context.get('testimonials', [])
        featured_projects = rag_context.get('featured_projects', [])
        target_service = rag_context.get('target_service', {})
        
        # Use RAG data to enhance business info
        if business_info:
            business_name = business_info.get('display_name') or business_info.get('name', business_name)
            city = business_info.get('city', city)
            years_in_business = business_info.get('years_in_business')
            license_number = business_info.get('license_number')
            certifications = business_info.get('certifications', [])
        
        # Get service category for template selection
        service_category = target_service.get('category') if target_service else None
        if not service_category:
            service_category = 'general'
        template_category = self.template_service.get_category_template(service_category)
        
        # Create enhanced context with RAG data
        enhanced_context = context.copy()
        enhanced_context.update({
            'business_name': business_name,
            'city': city,
            'service_name': service_name,  # Ensure service_name is preserved
            'years_in_business': years_in_business if 'years_in_business' in locals() else None,
            'license_number': license_number if 'license_number' in locals() else None,
            'certifications': certifications if 'certifications' in locals() else [],
            'rag_context': rag_context
        })
        
        # Use category-specific templates
        try:
            if block_type == ContentBlockType.HERO:
                logger.info(f"Calling get_hero_template with category: {template_category}")
                return self.template_service.get_hero_template(template_category, enhanced_context)
            elif block_type == ContentBlockType.BENEFITS:
                logger.info(f"Calling get_benefits_template with category: {template_category}")
                return self.template_service.get_benefits_template(template_category, enhanced_context)
            elif block_type == ContentBlockType.PROCESS_STEPS:
                logger.info(f"Calling get_process_steps_template with category: {template_category}")
                return self.template_service.get_process_steps_template(template_category, enhanced_context)
            elif block_type == ContentBlockType.FAQ:
                logger.info(f"Calling get_faq_template with category: {template_category}")
                return self.template_service.get_faq_template(template_category, enhanced_context)
        except Exception as e:
            logger.error(f"Template error in {block_type} with category {template_category}: {e}")
            logger.error(f"Enhanced context keys: {list(enhanced_context.keys())}")
            logger.error(f"Enhanced context values: {enhanced_context}")
            raise
        
        # Fallback for unsupported block types
        return {"content": f"Template content for {block_type}"}
    
    async def generate_service_page_content(
        self,
        business_id: str,
        service_slug: str,
        location_slug: Optional[str] = None,
        context: Dict[str, Any] = None,
        target_keywords: List[str] = None
    ) -> ServicePageContent:
        """Generate complete service page content with RAG enhancement."""
        
        context = context or {}
        target_keywords = target_keywords or []
        
        # Retrieve RAG context if service is available
        if self.rag_service:
            try:
                rag_context = await self.rag_service.get_service_specific_context(
                    business_id, service_slug, location_slug
                )
                context['rag_context'] = rag_context
                logger.info(f"Retrieved RAG context for {business_id}/{service_slug}")
            except Exception as e:
                logger.warning(f"Failed to retrieve RAG context: {e}")
        
        # Initialize page content
        content_source = ContentSource.RAG_ENHANCED if self.rag_service else ContentSource.TEMPLATE
        page_content = ServicePageContent(
            business_id=business_id,
            service_slug=service_slug,
            location_slug=location_slug,
            target_keywords=target_keywords,
            content_source=content_source
        )
        
        logger.info(f"Initialized page content for {service_slug}, starting content generation...")
        
        # Generate content blocks
        block_types = [
            ContentBlockType.HERO,
            ContentBlockType.BENEFITS,
            ContentBlockType.PROCESS_STEPS,
            ContentBlockType.FAQ
        ]
        
        for i, block_type in enumerate(block_types):
            try:
                logger.info(f"Generating {block_type} block...")
                block = await self.generate_content_block(
                    block_type=block_type,
                    context=context,
                    target_keywords=target_keywords
                )
                if block:
                    block.order = i
                    page_content.add_block(block)
                    logger.info(f"Added {block_type} block to page - content length: {len(str(block.content))}")
                else:
                    logger.warning(f"No block generated for {block_type}")
            except Exception as e:
                logger.error(f"Error generating {block_type}: {e}")
        
        # Generate JSON-LD schemas
        try:
            schema_context = context.copy()
            schema_context['service_slug'] = service_slug
            schemas = self.schema_generator.generate_all_schemas(schema_context, page_content.content_blocks)
            
            for schema in schemas:
                page_content.add_schema_block(schema)
            
            logger.info(f"Generated {len(schemas)} schema blocks")
        except Exception as e:
            logger.error(f"Error generating schemas: {e}")
        
        # Calculate metrics
        page_content.calculate_metrics()
        
        # Run quality gate validation
        quality_result = self.quality_gate.validate_content(page_content)
        logger.info(f"Content quality: {quality_result.summary}")
        
        # Store quality metrics in page content
        if hasattr(page_content, 'quality_metrics'):
            page_content.quality_metrics = {
                "overall_score": quality_result.overall_score,
                "overall_level": quality_result.overall_level,
                "passed": quality_result.passed,
                "summary": quality_result.summary
            }
        
        # Final debug log before returning
        logger.info(f"Returning page content with {len(page_content.content_blocks)} content blocks and {len(page_content.schema_blocks)} schema blocks")
        
        return page_content
