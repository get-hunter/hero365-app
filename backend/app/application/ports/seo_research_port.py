"""
SEO Research Port

Interface for SEO research and analysis infrastructure services.
Defines contracts for external SEO tools and APIs.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from ...domain.entities.business import Business


@dataclass
class KeywordResearchData:
    """External keyword research data structure."""
    
    keyword: str
    search_volume: int
    competition_level: str  # LOW, MEDIUM, HIGH
    competition_score: float  # 0.0 to 1.0
    cost_per_click: float
    difficulty: int  # 1-100
    trend: str  # RISING, STABLE, DECLINING
    related_keywords: List[str]
    local_volume: Optional[int] = None
    seasonal_data: Optional[Dict[str, int]] = None


@dataclass
class RankingData:
    """Search ranking data from external sources."""
    
    keyword: str
    domain: str
    current_rank: Optional[int]
    previous_rank: Optional[int]
    rank_change: int
    page_url: str
    search_engine: str = "google"
    location: str = "US"
    device: str = "desktop"
    checked_at: datetime = None


@dataclass
class CompetitorAnalysisData:
    """Competitor analysis data from external sources."""
    
    domain: str
    business_name: Optional[str]
    estimated_traffic: int
    top_keywords: List[str]
    ranking_keywords_count: int
    domain_authority: int
    backlinks_count: int
    top_pages: List[Dict[str, Any]]
    content_topics: List[str]


@dataclass
class TechnicalSEOData:
    """Technical SEO audit data from external sources."""
    
    domain: str
    page_speed_score: int  # 1-100
    mobile_friendly: bool
    https_enabled: bool
    meta_tags_present: bool
    structured_data_present: bool
    sitemap_present: bool
    robots_txt_present: bool
    crawl_errors: List[str]
    broken_links: List[str]
    duplicate_content: List[str]


class SEOResearchPort(ABC):
    """
    Port (interface) for SEO research services.
    
    This defines the contract for external SEO tools and APIs
    without containing any business logic.
    """
    
    @abstractmethod
    async def research_keywords(
        self,
        seed_keywords: List[str],
        location: str,
        language: str = "en"
    ) -> List[KeywordResearchData]:
        """
        Research keywords using external SEO tools.
        
        Args:
            seed_keywords: Starting keywords for research
            location: Geographic location for local search data
            language: Language code for search data
            
        Returns:
            List of keyword research data from external sources
        """
        pass
    
    @abstractmethod
    async def track_keyword_rankings(
        self,
        keywords: List[str],
        domain: str,
        location: str = "US",
        device: str = "desktop"
    ) -> List[RankingData]:
        """
        Track keyword rankings for a domain.
        
        Args:
            keywords: Keywords to track
            domain: Domain to track rankings for
            location: Geographic location for search results
            device: Device type (desktop, mobile)
            
        Returns:
            List of ranking data from search engines
        """
        pass
    
    @abstractmethod
    async def analyze_competitors(
        self,
        domain: str,
        competitor_domains: List[str],
        keywords: Optional[List[str]] = None
    ) -> List[CompetitorAnalysisData]:
        """
        Analyze competitor SEO performance.
        
        Args:
            domain: Primary domain to analyze
            competitor_domains: List of competitor domains
            keywords: Optional keywords to focus analysis on
            
        Returns:
            List of competitor analysis data
        """
        pass
    
    @abstractmethod
    async def audit_technical_seo(
        self,
        domain: str,
        pages: Optional[List[str]] = None
    ) -> TechnicalSEOData:
        """
        Perform technical SEO audit of a website.
        
        Args:
            domain: Domain to audit
            pages: Optional specific pages to audit
            
        Returns:
            Technical SEO audit data
        """
        pass
    
    @abstractmethod
    async def get_search_volume(
        self,
        keywords: List[str],
        location: str = "US"
    ) -> Dict[str, int]:
        """
        Get search volume data for keywords.
        
        Args:
            keywords: Keywords to get volume for
            location: Geographic location
            
        Returns:
            Dictionary mapping keywords to search volumes
        """
        pass
    
    @abstractmethod
    async def get_serp_features(
        self,
        keyword: str,
        location: str = "US"
    ) -> Dict[str, Any]:
        """
        Get SERP features for a keyword.
        
        Args:
            keyword: Keyword to analyze
            location: Geographic location
            
        Returns:
            SERP features data (featured snippets, local pack, etc.)
        """
        pass
    
    @abstractmethod
    async def analyze_backlinks(
        self,
        domain: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Analyze backlink profile of a domain.
        
        Args:
            domain: Domain to analyze
            limit: Maximum number of backlinks to return
            
        Returns:
            List of backlink data
        """
        pass
    
    @abstractmethod
    async def get_content_suggestions(
        self,
        topic: str,
        target_audience: str,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get content suggestions for a topic.
        
        Args:
            topic: Content topic
            target_audience: Target audience description
            location: Optional geographic location
            
        Returns:
            List of content suggestions
        """
        pass
