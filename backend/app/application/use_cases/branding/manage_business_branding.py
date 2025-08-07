"""
Use case for managing centralized business branding.

This use case handles the creation, update, and retrieval of business branding
configurations that are shared across all business components.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.entities.business_branding import (
    BusinessBranding, 
    BrandingTheme,
    ColorScheme,
    Typography,
    BrandAssets
)
from app.domain.entities.business import Business
from app.domain.repositories.business_repository import BusinessRepository
from app.application.exceptions.application_exceptions import (
    ApplicationError,
    ResourceNotFoundError,
    ValidationError
)


class ManageBusinessBrandingUseCase:
    """
    Use case for managing centralized business branding.
    
    Handles creation, updates, and application of branding across
    all business components (websites, documents, emails, etc.).
    """
    
    def __init__(
        self,
        business_repository: BusinessRepository,
        branding_repository: Any  # BrandingRepository when created
    ):
        self.business_repository = business_repository
        self.branding_repository = branding_repository
    
    async def create_or_update_branding(
        self,
        business_id: UUID,
        theme: Optional[BrandingTheme] = None,
        color_scheme: Optional[Dict[str, str]] = None,
        typography: Optional[Dict[str, str]] = None,
        assets: Optional[Dict[str, str]] = None,
        apply_trade_theme: bool = True,
        created_by: Optional[str] = None
    ) -> BusinessBranding:
        """
        Create or update business branding configuration.
        
        Args:
            business_id: The business ID
            theme: Optional branding theme
            color_scheme: Optional color overrides
            typography: Optional typography overrides
            assets: Optional brand assets (logos, etc.)
            apply_trade_theme: Whether to apply trade-specific suggestions
            created_by: User creating/updating the branding
        
        Returns:
            The created or updated BusinessBranding instance
        """
        # Get the business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise ResourceNotFoundError(f"Business {business_id} not found")
        
        # Check if branding exists
        existing_branding = await self.branding_repository.get_by_business_id(business_id)
        
        if existing_branding:
            # Update existing branding
            branding = existing_branding
            
            if theme:
                branding.theme = theme
            
            if color_scheme:
                for key, value in color_scheme.items():
                    if hasattr(branding.color_scheme, key):
                        setattr(branding.color_scheme, key, value)
            
            if typography:
                for key, value in typography.items():
                    if hasattr(branding.typography, key):
                        setattr(branding.typography, key, value)
            
            if assets:
                for key, value in assets.items():
                    if hasattr(branding.assets, key):
                        setattr(branding.assets, key, value)
            
            branding.last_modified_by = created_by
            
        else:
            # Create new branding
            branding = BusinessBranding(
                business_id=business_id,
                theme=theme or BrandingTheme.PROFESSIONAL,
                theme_name=f"{business.name} Brand",
                created_by=created_by
            )
            
            # Apply custom settings if provided
            if color_scheme:
                branding.color_scheme = ColorScheme(**color_scheme)
            
            if typography:
                branding.typography = Typography(**typography)
            
            if assets:
                branding.assets = BrandAssets(**assets)
        
        # Apply trade-specific theme if requested
        if apply_trade_theme and business.get_primary_trade():
            primary_trade = business.get_primary_trade()
            trade_category = business.trade_category.value if business.trade_category else "both"
            branding = branding.apply_trade_theme(primary_trade, trade_category)
        
        # Save branding
        if existing_branding:
            branding = await self.branding_repository.update(branding)
        else:
            branding = await self.branding_repository.create(branding)
        
        return branding
    
    async def get_branding_for_component(
        self,
        business_id: UUID,
        component: str = "website"
    ) -> Dict[str, Any]:
        """
        Get branding configuration for a specific component.
        
        Args:
            business_id: The business ID
            component: Component type ('website', 'estimate', 'invoice', 'email')
        
        Returns:
            Branding configuration dictionary for the component
        """
        branding = await self.branding_repository.get_by_business_id(business_id)
        
        if not branding:
            # Return default branding if none exists
            business = await self.business_repository.get_by_id(business_id)
            if not business:
                raise ResourceNotFoundError(f"Business {business_id} not found")
            
            # Create default branding
            branding = await self.create_or_update_branding(
                business_id=business_id,
                apply_trade_theme=True
            )
        
        return branding.get_template_config(component)
    
    async def generate_css_for_website(
        self,
        business_id: UUID
    ) -> str:
        """
        Generate CSS custom properties for website.
        
        Args:
            business_id: The business ID
        
        Returns:
            CSS string with custom properties
        """
        branding = await self.branding_repository.get_by_business_id(business_id)
        
        if not branding:
            raise ResourceNotFoundError(f"No branding found for business {business_id}")
        
        return branding.get_css_variables()
    
    async def clone_branding_from_template(
        self,
        business_id: UUID,
        template_business_id: UUID,
        new_name: Optional[str] = None
    ) -> BusinessBranding:
        """
        Clone branding from another business (useful for franchises).
        
        Args:
            business_id: Target business ID
            template_business_id: Source business ID to clone from
            new_name: Optional new brand name
        
        Returns:
            Cloned BusinessBranding instance
        """
        # Get template branding
        template_branding = await self.branding_repository.get_by_business_id(
            template_business_id
        )
        
        if not template_branding:
            raise ResourceNotFoundError(
                f"No branding found for template business {template_business_id}"
            )
        
        # Get target business
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise ResourceNotFoundError(f"Business {business_id} not found")
        
        # Clone branding
        new_branding = template_branding.clone(
            new_name=new_name or f"{business.name} Brand"
        )
        new_branding.business_id = business_id
        
        # Save cloned branding
        new_branding = await self.branding_repository.create(new_branding)
        
        return new_branding
    
    async def export_branding_for_design_tools(
        self,
        business_id: UUID,
        format: str = "figma"
    ) -> Dict[str, Any]:
        """
        Export branding as design tokens for external tools.
        
        Args:
            business_id: The business ID
            format: Export format ('figma', 'sketch', 'adobe')
        
        Returns:
            Design tokens in requested format
        """
        branding = await self.branding_repository.get_by_business_id(business_id)
        
        if not branding:
            raise ResourceNotFoundError(f"No branding found for business {business_id}")
        
        if format == "figma":
            return branding.export_for_figma()
        else:
            # For now, return Figma format for all
            # Can be extended for other formats
            return branding.export_for_figma()
    
    async def suggest_trade_colors(
        self,
        business_id: UUID
    ) -> Dict[str, str]:
        """
        Suggest color scheme based on business trades.
        
        Args:
            business_id: The business ID
        
        Returns:
            Suggested color scheme
        """
        business = await self.business_repository.get_by_id(business_id)
        if not business:
            raise ResourceNotFoundError(f"Business {business_id} not found")
        
        if not business.get_primary_trade():
            raise ValidationError("Business must have at least one trade for suggestions")
        
        # Create temporary branding to get suggestions
        temp_branding = BusinessBranding(business_id=business_id)
        temp_branding = temp_branding.apply_trade_theme(
            business.get_primary_trade(),
            business.trade_category.value if business.trade_category else "both"
        )
        
        return {
            "primary_color": temp_branding.color_scheme.primary_color,
            "secondary_color": temp_branding.color_scheme.secondary_color,
            "accent_color": temp_branding.color_scheme.accent_color,
            "trade_type": business.get_primary_trade(),
            "suggested_theme": "industrial" if business.trade_category == "COMMERCIAL" else "friendly"
        }
