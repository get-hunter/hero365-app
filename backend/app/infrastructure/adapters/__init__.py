"""
Infrastructure Adapters

Clean Architecture adapters that implement application ports.
These adapters handle external service integration while keeping
business logic separate in domain services.
"""

from .openai_content_adapter import OpenAIContentAdapter
from .claude_content_adapter import ClaudeContentAdapter
from .gemini_content_adapter import GeminiContentAdapter
from .content_generation_factory import create_content_adapter, get_provider_info

from .seo_tools_adapter import SEOToolsAdapter
from .cloudflare_domain_adapter import CloudflareDomainAdapter
from .aws_hosting_adapter import AWSHostingAdapter
from .google_business_profile_adapter import GoogleBusinessProfileAdapter
from .hero365_subdomain_adapter import Hero365SubdomainAdapter

__all__ = [
    # Content Generation Adapters
    "OpenAIContentAdapter",
    "ClaudeContentAdapter", 
    "GeminiContentAdapter",
    "create_content_adapter",
    "get_provider_info",
    
    # Website Builder Adapters
    "SEOToolsAdapter",
    "CloudflareDomainAdapter",
    "AWSHostingAdapter",
    "GoogleBusinessProfileAdapter",
    "Hero365SubdomainAdapter",
]
