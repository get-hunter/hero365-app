"""
Content Generation Factory

Factory for creating content generation adapters based on configuration.
Allows switching between different LLM providers (OpenAI, Claude, Gemini).
"""

import logging
from typing import Dict, Type

from ...application.ports.content_generation_port import ContentGenerationPort
from ...core.config import settings
from .openai_content_adapter import OpenAIContentAdapter
from .claude_content_adapter import ClaudeContentAdapter
from .gemini_content_adapter import GeminiContentAdapter

logger = logging.getLogger(__name__)


class ContentGenerationFactory:
    """
    Factory for creating content generation adapters.
    
    This factory allows switching between different LLM providers
    based on configuration without changing application code.
    """
    
    # Registry of available adapters
    _adapters: Dict[str, Type[ContentGenerationPort]] = {
        "openai": OpenAIContentAdapter,
        "claude": ClaudeContentAdapter,
        "gemini": GeminiContentAdapter,
    }
    
    @classmethod
    def create_adapter(self, provider: str = None) -> ContentGenerationPort:
        """
        Create a content generation adapter for the specified provider.
        
        Args:
            provider: LLM provider name ("openai", "claude", "gemini")
                     If None, uses the configured default provider
        
        Returns:
            ContentGenerationPort implementation for the provider
            
        Raises:
            ValueError: If provider is not supported or not configured
        """
        
        # Use configured default if no provider specified
        if provider is None:
            provider = settings.CONTENT_GENERATION_PROVIDER
        
        # Validate provider is supported
        if provider not in self._adapters:
            available = ", ".join(self._adapters.keys())
            raise ValueError(f"Unsupported content generation provider: {provider}. Available: {available}")
        
        # Validate provider is configured
        self._validate_provider_configuration(provider)
        
        # Create and return adapter
        adapter_class = self._adapters[provider]
        
        try:
            adapter = adapter_class()
            logger.info(f"Created {provider} content generation adapter")
            return adapter
        except Exception as e:
            logger.error(f"Failed to create {provider} adapter: {str(e)}")
            raise ValueError(f"Failed to initialize {provider} content generation: {str(e)}")
    
    @classmethod
    def get_available_providers(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about available content generation providers.
        
        Returns:
            Dictionary with provider info including availability and configuration status
        """
        
        providers = {}
        
        for provider_name in self._adapters.keys():
            is_configured = self._is_provider_configured(provider_name)
            
            providers[provider_name] = {
                "name": provider_name,
                "configured": is_configured,
                "adapter_class": self._adapters[provider_name].__name__,
                "description": self._get_provider_description(provider_name)
            }
        
        return providers
    
    @classmethod
    def register_adapter(self, provider_name: str, adapter_class: Type[ContentGenerationPort]):
        """
        Register a new content generation adapter.
        
        Args:
            provider_name: Name of the provider
            adapter_class: Adapter class implementing ContentGenerationPort
        """
        
        if not issubclass(adapter_class, ContentGenerationPort):
            raise ValueError(f"Adapter class must implement ContentGenerationPort")
        
        self._adapters[provider_name] = adapter_class
        logger.info(f"Registered content generation adapter: {provider_name}")
    
    @classmethod
    def _validate_provider_configuration(self, provider: str):
        """Validate that the provider is properly configured."""
        
        if not self._is_provider_configured(provider):
            raise ValueError(f"{provider} content generation is not configured. Check API keys and settings.")
    
    @classmethod
    def _is_provider_configured(self, provider: str) -> bool:
        """Check if a provider is properly configured."""
        
        config_checks = {
            "openai": lambda: bool(settings.OPENAI_API_KEY),
            "claude": lambda: bool(settings.CLAUDE_API_KEY),
            "gemini": lambda: bool(settings.GEMINI_API_KEY),
        }
        
        check_func = config_checks.get(provider)
        if check_func is None:
            return False
        
        try:
            return check_func()
        except Exception:
            return False
    
    @classmethod
    def _get_provider_description(self, provider: str) -> str:
        """Get description for a provider."""
        
        descriptions = {
            "openai": "OpenAI GPT-4 - Versatile content generation with strong general capabilities",
            "claude": "Anthropic Claude - Excellent for code generation and detailed, structured content",
            "gemini": "Google Gemini - Advanced multimodal capabilities and competitive performance",
        }
        
        return descriptions.get(provider, f"Content generation using {provider}")


# Convenience function for creating the default adapter
def create_content_adapter(provider: str = None) -> ContentGenerationPort:
    """
    Convenience function to create a content generation adapter.
    
    Args:
        provider: Optional provider name. Uses configured default if None.
        
    Returns:
        ContentGenerationPort implementation
    """
    return ContentGenerationFactory.create_adapter(provider)


# Convenience function for getting provider info
def get_provider_info() -> Dict[str, Dict[str, any]]:
    """
    Convenience function to get available provider information.
    
    Returns:
        Dictionary with provider information
    """
    return ContentGenerationFactory.get_available_providers()
