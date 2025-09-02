"""
Content Quality Gate Service - Validates SEO content quality.
"""

from typing import Dict, List, Any
from pydantic import BaseModel
import logging
from enum import Enum

from app.domain.entities.service_page_content import ServicePageContent, ContentBlockType

logger = logging.getLogger(__name__)


class QualityLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


class QualityMetric(BaseModel):
    name: str
    score: float
    level: QualityLevel
    message: str
    suggestions: List[str] = []


class QualityGateResult(BaseModel):
    overall_score: float
    overall_level: QualityLevel
    passed: bool
    metrics: List[QualityMetric]
    summary: str


class ContentQualityGateService:
    """Service for validating content quality against SEO best practices."""
    
    def __init__(self):
        self.min_passing_score = 70.0
    
    def validate_content(self, page_content: ServicePageContent) -> QualityGateResult:
        """Validate service page content against quality standards."""
        try:
            metrics = [
                self._check_word_count(page_content),
                self._check_content_structure(page_content),
                self._check_faq_presence(page_content)
            ]
            
            overall_score = sum(m.score for m in metrics) / len(metrics)
            overall_level = self._score_to_level(overall_score)
            passed = overall_score >= self.min_passing_score
            
            summary = f"Content quality: {overall_level.value} (score: {overall_score:.1f})"
            
            return QualityGateResult(
                overall_score=round(overall_score, 1),
                overall_level=overall_level,
                passed=passed,
                metrics=metrics,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error validating content quality: {e}")
            return QualityGateResult(
                overall_score=0.0,
                overall_level=QualityLevel.FAILED,
                passed=False,
                metrics=[],
                summary="Quality validation failed"
            )
    
    def _check_word_count(self, page_content: ServicePageContent) -> QualityMetric:
        """Check word count for SEO."""
        total_words = 0
        
        for block in page_content.content_blocks:
            if isinstance(block.content, dict):
                total_words += self._count_words_in_dict(block.content)
        
        if total_words >= 600:
            score, level = 100, QualityLevel.EXCELLENT
            suggestions = []
        elif total_words >= 400:
            score, level = 80, QualityLevel.GOOD
            suggestions = ["Consider adding more content for better SEO"]
        elif total_words >= 200:
            score, level = 60, QualityLevel.ACCEPTABLE
            suggestions = ["Add more detailed content sections"]
        else:
            score, level = 30, QualityLevel.POOR
            suggestions = ["Content is too short - add substantial content"]
        
        return QualityMetric(
            name="word_count",
            score=score,
            level=level,
            message=f"Word count: {total_words} words",
            suggestions=suggestions
        )
    
    def _check_content_structure(self, page_content: ServicePageContent) -> QualityMetric:
        """Check content structure and completeness."""
        block_types = set(block.type for block in page_content.content_blocks)
        
        required_blocks = {
            ContentBlockType.HERO,
            ContentBlockType.BENEFITS,
            ContentBlockType.PROCESS_STEPS
        }
        
        present_required = len(block_types & required_blocks)
        total_required = len(required_blocks)
        
        score = (present_required / total_required) * 100
        level = self._score_to_level(score)
        
        missing = required_blocks - block_types
        suggestions = []
        if missing:
            suggestions.append(f"Add missing sections: {', '.join(missing)}")
        
        return QualityMetric(
            name="content_structure",
            score=score,
            level=level,
            message=f"Content structure: {present_required}/{total_required} required sections",
            suggestions=suggestions
        )
    
    def _check_faq_presence(self, page_content: ServicePageContent) -> QualityMetric:
        """Check for FAQ section."""
        faq_blocks = [b for b in page_content.content_blocks if b.type == ContentBlockType.FAQ]
        
        if not faq_blocks:
            return QualityMetric(
                name="faq_presence",
                score=30,
                level=QualityLevel.POOR,
                message="No FAQ section found",
                suggestions=["Add FAQ section for better SEO"]
            )
        
        faq_content = faq_blocks[0].content
        faqs = faq_content.get("faqs", []) if isinstance(faq_content, dict) else []
        
        if len(faqs) >= 5:
            score, level = 100, QualityLevel.EXCELLENT
            suggestions = []
        elif len(faqs) >= 3:
            score, level = 80, QualityLevel.GOOD
            suggestions = ["Consider adding more FAQ items"]
        else:
            score, level = 50, QualityLevel.ACCEPTABLE
            suggestions = ["Add more comprehensive FAQ content"]
        
        return QualityMetric(
            name="faq_presence",
            score=score,
            level=level,
            message=f"FAQ section with {len(faqs)} questions",
            suggestions=suggestions
        )
    
    def _count_words_in_dict(self, content: Dict[str, Any]) -> int:
        """Count words in dictionary content."""
        word_count = 0
        for key, value in content.items():
            if isinstance(value, str):
                word_count += len(value.split())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        word_count += self._count_words_in_dict(item)
                    elif isinstance(item, str):
                        word_count += len(item.split())
            elif isinstance(value, dict):
                word_count += self._count_words_in_dict(value)
        return word_count
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert score to quality level."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 70:
            return QualityLevel.ACCEPTABLE
        elif score >= 50:
            return QualityLevel.POOR
        else:
            return QualityLevel.FAILED