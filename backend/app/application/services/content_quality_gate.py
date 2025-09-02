"""
Content quality validation for LLM-generated content.
"""

from typing import Dict, List, Any


class ContentQualityGate:
    """Quality gate for generated content."""
    
    MIN_WORD_COUNT = 100
    MAX_WORD_COUNT = 2000
    MIN_SENTENCES = 3
    MAX_KEYWORD_DENSITY = 0.05  # 5%
    
    @classmethod
    def validate_content(cls, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """Validate content quality and return metrics."""
        words = content.split()
        sentences = content.split('.')
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Keyword density check
        keyword_issues = []
        if target_keywords:
            content_lower = content.lower()
            for keyword in target_keywords:
                keyword_count = content_lower.count(keyword.lower())
                density = keyword_count / word_count if word_count > 0 else 0
                if density > cls.MAX_KEYWORD_DENSITY:
                    keyword_issues.append(f"Keyword '{keyword}' density too high: {density:.2%}")
        
        # Quality checks
        issues = []
        if word_count < cls.MIN_WORD_COUNT:
            issues.append(f"Content too short: {word_count} words (min: {cls.MIN_WORD_COUNT})")
        if word_count > cls.MAX_WORD_COUNT:
            issues.append(f"Content too long: {word_count} words (max: {cls.MAX_WORD_COUNT})")
        if sentence_count < cls.MIN_SENTENCES:
            issues.append(f"Too few sentences: {sentence_count} (min: {cls.MIN_SENTENCES})")
        
        issues.extend(keyword_issues)
        
        return {
            "valid": len(issues) == 0,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "issues": issues,
            "metrics": {
                "readability_score": None,  # Could add textstat here
                "keyword_density": {kw: content_lower.count(kw.lower()) / word_count 
                                  for kw in (target_keywords or [])}
            }
        }
