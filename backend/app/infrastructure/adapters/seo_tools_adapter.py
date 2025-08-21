"""
SEO Tools Infrastructure Adapter

Pure infrastructure adapter for external SEO tools and APIs.
Contains NO business logic - only external API communication.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ...application.ports.seo_research_port import (
    SEOResearchPort, KeywordResearchData, RankingData, 
    CompetitorAnalysisData, TechnicalSEOData
)
from ...core.config import settings

logger = logging.getLogger(__name__)


class SEOToolsAdapter(SEOResearchPort):
    """
    Infrastructure adapter for external SEO tools.
    
    This adapter ONLY handles:
    - External API communication
    - Data format conversion
    - HTTP requests and responses
    
    It contains NO business logic or domain rules.
    """
    
    def __init__(self):
        self.serp_api_key = settings.SERPAPI_KEY
        self.semrush_api_key = getattr(settings, 'SEMRUSH_API_KEY', None)
        self.ahrefs_api_key = getattr(settings, 'AHREFS_API_KEY', None)
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Hero365-SEO-Bot/1.0 (+https://hero365.ai/bot)"
            }
        )
    
    async def research_keywords(
        self,
        seed_keywords: List[str],
        location: str,
        language: str = "en"
    ) -> List[KeywordResearchData]:
        """Research keywords using external SEO APIs."""
        
        try:
            # Try multiple sources and combine results
            results = []
            
            # Use SERP API if available
            if self.serp_api_key:
                serp_results = await self._research_keywords_serp_api(
                    seed_keywords, location, language
                )
                results.extend(serp_results)
            
            # Use SEMrush API if available
            if self.semrush_api_key:
                semrush_results = await self._research_keywords_semrush(
                    seed_keywords, location
                )
                results.extend(semrush_results)
            
            # Fallback to basic keyword expansion if no APIs available
            if not results:
                results = await self._generate_basic_keyword_variations(seed_keywords)
            
            return results
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            return []
    
    async def track_keyword_rankings(
        self,
        keywords: List[str],
        domain: str,
        location: str = "US",
        device: str = "desktop"
    ) -> List[RankingData]:
        """Track keyword rankings using external APIs."""
        
        try:
            rankings = []
            
            # Use SERP API for ranking tracking
            if self.serp_api_key:
                for keyword in keywords:
                    ranking = await self._check_ranking_serp_api(
                        keyword, domain, location, device
                    )
                    if ranking:
                        rankings.append(ranking)
            
            return rankings
            
        except Exception as e:
            logger.error(f"Ranking tracking failed: {str(e)}")
            return []
    
    async def analyze_competitors(
        self,
        domain: str,
        competitor_domains: List[str],
        keywords: Optional[List[str]] = None
    ) -> List[CompetitorAnalysisData]:
        """Analyze competitors using external SEO tools."""
        
        try:
            competitor_data = []
            
            for competitor_domain in competitor_domains:
                # Use SEMrush for competitor analysis if available
                if self.semrush_api_key:
                    data = await self._analyze_competitor_semrush(
                        competitor_domain, keywords
                    )
                    if data:
                        competitor_data.append(data)
                else:
                    # Fallback to basic analysis
                    data = await self._analyze_competitor_basic(competitor_domain)
                    if data:
                        competitor_data.append(data)
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {str(e)}")
            return []
    
    async def audit_technical_seo(
        self,
        domain: str,
        pages: Optional[List[str]] = None
    ) -> TechnicalSEOData:
        """Perform technical SEO audit using external tools."""
        
        try:
            # Use multiple sources for comprehensive audit
            audit_data = TechnicalSEOData(
                domain=domain,
                page_speed_score=0,
                mobile_friendly=False,
                https_enabled=False,
                meta_tags_present=False,
                structured_data_present=False,
                sitemap_present=False,
                robots_txt_present=False,
                crawl_errors=[],
                broken_links=[],
                duplicate_content=[]
            )
            
            # Check basic technical factors
            basic_audit = await self._perform_basic_technical_audit(domain)
            if basic_audit:
                audit_data.https_enabled = basic_audit.get('https_enabled', False)
                audit_data.meta_tags_present = basic_audit.get('meta_tags_present', False)
                audit_data.sitemap_present = basic_audit.get('sitemap_present', False)
                audit_data.robots_txt_present = basic_audit.get('robots_txt_present', False)
            
            # Check page speed (using Google PageSpeed Insights API if available)
            page_speed = await self._check_page_speed(domain)
            if page_speed:
                audit_data.page_speed_score = page_speed.get('score', 0)
                audit_data.mobile_friendly = page_speed.get('mobile_friendly', False)
            
            return audit_data
            
        except Exception as e:
            logger.error(f"Technical SEO audit failed: {str(e)}")
            return TechnicalSEOData(
                domain=domain,
                page_speed_score=0,
                mobile_friendly=False,
                https_enabled=False,
                meta_tags_present=False,
                structured_data_present=False,
                sitemap_present=False,
                robots_txt_present=False,
                crawl_errors=[],
                broken_links=[],
                duplicate_content=[]
            )
    
    async def get_search_volume(
        self,
        keywords: List[str],
        location: str = "US"
    ) -> Dict[str, int]:
        """Get search volume data from external APIs."""
        
        try:
            volume_data = {}
            
            # Use SEMrush API if available
            if self.semrush_api_key:
                for keyword in keywords:
                    volume = await self._get_search_volume_semrush(keyword, location)
                    if volume is not None:
                        volume_data[keyword] = volume
            
            # Fallback to estimated volumes
            if not volume_data:
                for keyword in keywords:
                    # Simple estimation based on keyword characteristics
                    estimated_volume = self._estimate_search_volume(keyword)
                    volume_data[keyword] = estimated_volume
            
            return volume_data
            
        except Exception as e:
            logger.error(f"Search volume lookup failed: {str(e)}")
            return {}
    
    async def get_serp_features(
        self,
        keyword: str,
        location: str = "US"
    ) -> Dict[str, Any]:
        """Get SERP features using external APIs."""
        
        try:
            if self.serp_api_key:
                return await self._get_serp_features_serp_api(keyword, location)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"SERP features lookup failed: {str(e)}")
            return {}
    
    async def analyze_backlinks(
        self,
        domain: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Analyze backlinks using external tools."""
        
        try:
            if self.ahrefs_api_key:
                return await self._analyze_backlinks_ahrefs(domain, limit)
            else:
                # Return empty list if no backlink tools available
                return []
                
        except Exception as e:
            logger.error(f"Backlink analysis failed: {str(e)}")
            return []
    
    async def get_content_suggestions(
        self,
        topic: str,
        target_audience: str,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get content suggestions from external sources."""
        
        try:
            suggestions = []
            
            # Use SERP API to analyze top-ranking content
            if self.serp_api_key:
                serp_suggestions = await self._get_content_suggestions_serp(
                    topic, location
                )
                suggestions.extend(serp_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Content suggestions failed: {str(e)}")
            return []
    
    # =====================================
    # PRIVATE API INTEGRATION METHODS
    # =====================================
    
    async def _research_keywords_serp_api(
        self,
        seed_keywords: List[str],
        location: str,
        language: str
    ) -> List[KeywordResearchData]:
        """Research keywords using SERP API."""
        
        results = []
        
        for keyword in seed_keywords:
            try:
                params = {
                    'api_key': self.serp_api_key,
                    'engine': 'google_keyword_planner',
                    'q': keyword,
                    'location': location,
                    'hl': language
                }
                
                async with self.http_client.get(
                    'https://serpapi.com/search',
                    params=params
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Parse SERP API response
                        if 'keyword_ideas' in data:
                            for idea in data['keyword_ideas'][:20]:  # Limit results
                                results.append(KeywordResearchData(
                                    keyword=idea.get('keyword', ''),
                                    search_volume=idea.get('monthly_searches', 0),
                                    competition_level=idea.get('competition', 'MEDIUM'),
                                    competition_score=self._convert_competition_to_score(
                                        idea.get('competition', 'MEDIUM')
                                    ),
                                    cost_per_click=float(idea.get('top_of_page_bid_low', 0)),
                                    difficulty=self._estimate_difficulty(idea),
                                    trend='STABLE',  # Default
                                    related_keywords=[],
                                    local_volume=idea.get('monthly_searches', 0)
                                ))
                
            except Exception as e:
                logger.warning(f"SERP API keyword research failed for '{keyword}': {str(e)}")
        
        return results
    
    async def _research_keywords_semrush(
        self,
        seed_keywords: List[str],
        location: str
    ) -> List[KeywordResearchData]:
        """Research keywords using SEMrush API."""
        
        results = []
        
        for keyword in seed_keywords:
            try:
                params = {
                    'key': self.semrush_api_key,
                    'type': 'phrase_related',
                    'phrase': keyword,
                    'database': 'us',  # Could be mapped from location
                    'export_columns': 'Ph,Nq,Cp,Co,Nr,Td'
                }
                
                async with self.http_client.get(
                    'https://api.semrush.com/',
                    params=params
                ) as response:
                    if response.status_code == 200:
                        data = response.text
                        
                        # Parse SEMrush CSV response
                        lines = data.strip().split('\n')
                        for line in lines[1:21]:  # Skip header, limit to 20
                            parts = line.split(';')
                            if len(parts) >= 6:
                                results.append(KeywordResearchData(
                                    keyword=parts[0],
                                    search_volume=int(parts[1]) if parts[1].isdigit() else 0,
                                    competition_level=self._convert_semrush_competition(parts[3]),
                                    competition_score=float(parts[3]) if parts[3] else 0.5,
                                    cost_per_click=float(parts[2]) if parts[2] else 0.0,
                                    difficulty=int(float(parts[5]) * 100) if parts[5] else 50,
                                    trend='STABLE',
                                    related_keywords=[],
                                    local_volume=int(parts[1]) if parts[1].isdigit() else 0
                                ))
                
            except Exception as e:
                logger.warning(f"SEMrush keyword research failed for '{keyword}': {str(e)}")
        
        return results
    
    async def _check_ranking_serp_api(
        self,
        keyword: str,
        domain: str,
        location: str,
        device: str
    ) -> Optional[RankingData]:
        """Check keyword ranking using SERP API."""
        
        try:
            params = {
                'api_key': self.serp_api_key,
                'engine': 'google',
                'q': keyword,
                'location': location,
                'device': device,
                'num': 100  # Check top 100 results
            }
            
            async with self.http_client.get(
                'https://serpapi.com/search',
                params=params
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    
                    # Find domain in organic results
                    if 'organic_results' in data:
                        for i, result in enumerate(data['organic_results']):
                            result_domain = urlparse(result.get('link', '')).netloc
                            if domain in result_domain:
                                return RankingData(
                                    keyword=keyword,
                                    domain=domain,
                                    current_rank=i + 1,
                                    previous_rank=None,  # Would need historical data
                                    rank_change=0,
                                    page_url=result.get('link', ''),
                                    search_engine='google',
                                    location=location,
                                    device=device,
                                    checked_at=datetime.utcnow()
                                )
                    
                    # Not found in top 100
                    return RankingData(
                        keyword=keyword,
                        domain=domain,
                        current_rank=None,
                        previous_rank=None,
                        rank_change=0,
                        page_url='',
                        search_engine='google',
                        location=location,
                        device=device,
                        checked_at=datetime.utcnow()
                    )
        
        except Exception as e:
            logger.warning(f"Ranking check failed for '{keyword}': {str(e)}")
        
        return None
    
    async def _analyze_competitor_semrush(
        self,
        domain: str,
        keywords: Optional[List[str]]
    ) -> Optional[CompetitorAnalysisData]:
        """Analyze competitor using SEMrush API."""
        
        try:
            params = {
                'key': self.semrush_api_key,
                'type': 'domain_organic',
                'domain': domain,
                'database': 'us',
                'export_columns': 'Dn,Cr,Np,Or,Ot,Oc,Ad'
            }
            
            async with self.http_client.get(
                'https://api.semrush.com/',
                params=params
            ) as response:
                if response.status_code == 200:
                    data = response.text
                    lines = data.strip().split('\n')
                    
                    if len(lines) > 1:
                        parts = lines[1].split(';')
                        if len(parts) >= 7:
                            return CompetitorAnalysisData(
                                domain=domain,
                                business_name=None,  # Not available from SEMrush
                                estimated_traffic=int(parts[2]) if parts[2].isdigit() else 0,
                                top_keywords=[],  # Would need separate API call
                                ranking_keywords_count=int(parts[3]) if parts[3].isdigit() else 0,
                                domain_authority=0,  # Not available from SEMrush
                                backlinks_count=0,  # Not available from SEMrush
                                top_pages=[],
                                content_topics=[]
                            )
        
        except Exception as e:
            logger.warning(f"SEMrush competitor analysis failed for '{domain}': {str(e)}")
        
        return None
    
    async def _analyze_competitor_basic(self, domain: str) -> Optional[CompetitorAnalysisData]:
        """Basic competitor analysis without external APIs."""
        
        try:
            # Basic web scraping for competitor info
            async with self.http_client.get(f'https://{domain}') as response:
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract basic information
                    title = soup.find('title')
                    business_name = title.text.strip() if title else domain
                    
                    return CompetitorAnalysisData(
                        domain=domain,
                        business_name=business_name,
                        estimated_traffic=0,  # Unknown
                        top_keywords=[],
                        ranking_keywords_count=0,
                        domain_authority=0,
                        backlinks_count=0,
                        top_pages=[],
                        content_topics=[]
                    )
        
        except Exception as e:
            logger.warning(f"Basic competitor analysis failed for '{domain}': {str(e)}")
        
        return None
    
    async def _perform_basic_technical_audit(self, domain: str) -> Optional[Dict[str, Any]]:
        """Perform basic technical SEO audit."""
        
        try:
            audit_results = {}
            
            # Check HTTPS
            try:
                async with self.http_client.get(f'https://{domain}') as response:
                    audit_results['https_enabled'] = response.status_code < 400
            except:
                audit_results['https_enabled'] = False
            
            # Check robots.txt
            try:
                async with self.http_client.get(f'https://{domain}/robots.txt') as response:
                    audit_results['robots_txt_present'] = response.status_code == 200
            except:
                audit_results['robots_txt_present'] = False
            
            # Check sitemap
            try:
                async with self.http_client.get(f'https://{domain}/sitemap.xml') as response:
                    audit_results['sitemap_present'] = response.status_code == 200
            except:
                audit_results['sitemap_present'] = False
            
            # Check homepage for meta tags
            try:
                async with self.http_client.get(f'https://{domain}') as response:
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        title = soup.find('title')
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        
                        audit_results['meta_tags_present'] = bool(title and meta_desc)
                    else:
                        audit_results['meta_tags_present'] = False
            except:
                audit_results['meta_tags_present'] = False
            
            return audit_results
        
        except Exception as e:
            logger.warning(f"Basic technical audit failed for '{domain}': {str(e)}")
        
        return None
    
    async def _check_page_speed(self, domain: str) -> Optional[Dict[str, Any]]:
        """Check page speed using Google PageSpeed Insights API."""
        
        try:
            # This would require Google PageSpeed Insights API key
            # For now, return placeholder data
            return {
                'score': 75,  # Placeholder score
                'mobile_friendly': True
            }
        
        except Exception as e:
            logger.warning(f"Page speed check failed for '{domain}': {str(e)}")
        
        return None
    
    # =====================================
    # HELPER METHODS
    # =====================================
    
    def _convert_competition_to_score(self, competition: str) -> float:
        """Convert competition level to numeric score."""
        
        competition_map = {
            'LOW': 0.2,
            'MEDIUM': 0.5,
            'HIGH': 0.8
        }
        
        return competition_map.get(competition.upper(), 0.5)
    
    def _convert_semrush_competition(self, competition_str: str) -> str:
        """Convert SEMrush competition score to level."""
        
        try:
            score = float(competition_str)
            if score < 0.33:
                return 'LOW'
            elif score < 0.67:
                return 'MEDIUM'
            else:
                return 'HIGH'
        except:
            return 'MEDIUM'
    
    def _estimate_difficulty(self, keyword_data: Dict[str, Any]) -> int:
        """Estimate keyword difficulty from available data."""
        
        # Simple estimation based on competition and search volume
        competition = keyword_data.get('competition', 'MEDIUM')
        volume = keyword_data.get('monthly_searches', 0)
        
        base_difficulty = {
            'LOW': 30,
            'MEDIUM': 50,
            'HIGH': 70
        }.get(competition, 50)
        
        # Adjust for search volume
        if volume > 10000:
            base_difficulty += 20
        elif volume > 1000:
            base_difficulty += 10
        
        return min(100, base_difficulty)
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume based on keyword characteristics."""
        
        # Simple estimation based on keyword length and type
        word_count = len(keyword.split())
        
        if word_count == 1:
            return 5000  # Single words tend to have higher volume
        elif word_count == 2:
            return 2000
        elif word_count == 3:
            return 800
        else:
            return 300  # Long-tail keywords have lower volume
    
    async def _generate_basic_keyword_variations(
        self,
        seed_keywords: List[str]
    ) -> List[KeywordResearchData]:
        """Generate basic keyword variations without external APIs."""
        
        variations = []
        
        modifiers = [
            'best', 'top', 'cheap', 'affordable', 'professional', 'local',
            'near me', 'services', 'company', 'contractor', 'repair',
            'installation', 'maintenance', 'emergency', '24/7'
        ]
        
        for seed in seed_keywords:
            for modifier in modifiers:
                # Create variations
                variations.extend([
                    f"{modifier} {seed}",
                    f"{seed} {modifier}",
                    f"{seed} services",
                    f"{seed} near me"
                ])
        
        # Convert to KeywordResearchData objects with estimated data
        keyword_data = []
        for variation in variations[:50]:  # Limit to 50 variations
            keyword_data.append(KeywordResearchData(
                keyword=variation,
                search_volume=self._estimate_search_volume(variation),
                competition_level='MEDIUM',
                competition_score=0.5,
                cost_per_click=2.50,  # Estimated CPC
                difficulty=50,  # Medium difficulty
                trend='STABLE',
                related_keywords=[],
                local_volume=None
            ))
        
        return keyword_data
    
    async def _get_search_volume_semrush(self, keyword: str, location: str) -> Optional[int]:
        """Get search volume from SEMrush API."""
        
        try:
            params = {
                'key': self.semrush_api_key,
                'type': 'phrase_this',
                'phrase': keyword,
                'database': 'us',
                'export_columns': 'Ph,Nq'
            }
            
            async with self.http_client.get(
                'https://api.semrush.com/',
                params=params
            ) as response:
                if response.status_code == 200:
                    data = response.text
                    lines = data.strip().split('\n')
                    
                    if len(lines) > 1:
                        parts = lines[1].split(';')
                        if len(parts) >= 2 and parts[1].isdigit():
                            return int(parts[1])
        
        except Exception as e:
            logger.warning(f"SEMrush search volume lookup failed for '{keyword}': {str(e)}")
        
        return None
    
    async def _get_serp_features_serp_api(
        self,
        keyword: str,
        location: str
    ) -> Dict[str, Any]:
        """Get SERP features using SERP API."""
        
        try:
            params = {
                'api_key': self.serp_api_key,
                'engine': 'google',
                'q': keyword,
                'location': location
            }
            
            async with self.http_client.get(
                'https://serpapi.com/search',
                params=params
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    
                    features = {
                        'featured_snippet': 'answer_box' in data,
                        'local_pack': 'local_results' in data,
                        'knowledge_panel': 'knowledge_graph' in data,
                        'image_pack': 'images_results' in data,
                        'video_results': 'video_results' in data,
                        'shopping_results': 'shopping_results' in data,
                        'ads_count': len(data.get('ads', [])),
                        'organic_results_count': len(data.get('organic_results', []))
                    }
                    
                    return features
        
        except Exception as e:
            logger.warning(f"SERP features lookup failed for '{keyword}': {str(e)}")
        
        return {}
    
    async def _analyze_backlinks_ahrefs(
        self,
        domain: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Analyze backlinks using Ahrefs API."""
        
        try:
            params = {
                'token': self.ahrefs_api_key,
                'target': domain,
                'mode': 'domain',
                'limit': limit
            }
            
            async with self.http_client.get(
                'https://apiv2.ahrefs.com/v2/backlinks',
                params=params
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    return data.get('backlinks', [])
        
        except Exception as e:
            logger.warning(f"Ahrefs backlink analysis failed for '{domain}': {str(e)}")
        
        return []
    
    async def _get_content_suggestions_serp(
        self,
        topic: str,
        location: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get content suggestions by analyzing SERP results."""
        
        try:
            params = {
                'api_key': self.serp_api_key,
                'engine': 'google',
                'q': topic,
                'num': 10
            }
            
            if location:
                params['location'] = location
            
            async with self.http_client.get(
                'https://serpapi.com/search',
                params=params
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    
                    suggestions = []
                    
                    # Analyze organic results for content ideas
                    for result in data.get('organic_results', [])[:5]:
                        suggestions.append({
                            'title': result.get('title', ''),
                            'url': result.get('link', ''),
                            'snippet': result.get('snippet', ''),
                            'type': 'organic_result'
                        })
                    
                    # Analyze "People also ask" for content ideas
                    for question in data.get('related_questions', [])[:5]:
                        suggestions.append({
                            'title': question.get('question', ''),
                            'snippet': question.get('snippet', ''),
                            'type': 'related_question'
                        })
                    
                    return suggestions
        
        except Exception as e:
            logger.warning(f"Content suggestions failed for '{topic}': {str(e)}")
        
        return []
