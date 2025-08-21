"""
Google Business Profile Domain Service

Contains pure business logic for Google Business Profile operations.
No external dependencies - only domain rules and calculations.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..entities.business import Business
from ..entities.website import GoogleBusinessProfile, ReviewData


class GoogleBusinessProfileDomainService:
    """
    Domain service containing pure business logic for Google Business Profile operations.
    
    This service handles:
    - Profile matching algorithms
    - Review sentiment analysis
    - Response generation rules
    - Business hours formatting
    - Trade-to-category mapping
    """
    
    def calculate_profile_match_score(
        self, 
        business: Business, 
        profile_data: Dict[str, Any]
    ) -> float:
        """
        Calculate how well a Google Business Profile matches our business.
        
        Uses weighted scoring algorithm:
        - Name similarity: 40%
        - Phone match: 30%
        - Address similarity: 20%
        - Category relevance: 10%
        """
        
        score = 0.0
        
        # Name similarity (40% weight)
        name_similarity = self._calculate_string_similarity(
            business.name.lower(),
            profile_data.get("name", "").lower()
        )
        score += name_similarity * 0.4
        
        # Phone number match (30% weight)
        if business.phone and profile_data.get("phone"):
            phone_match = 1.0 if business.phone in profile_data["phone"] else 0.0
            score += phone_match * 0.3
        
        # Address similarity (20% weight)
        if business.city and profile_data.get("address", {}).get("locality"):
            city_match = 1.0 if business.city.lower() in profile_data["address"]["locality"].lower() else 0.0
            score += city_match * 0.2
        
        # Category relevance (10% weight)
        business_trades = [business.get_primary_trade()] + business.get_secondary_trades()
        profile_categories = [cat.get("displayName", "").lower() for cat in profile_data.get("categories", [])]
        
        category_match = 0.0
        for trade in business_trades:
            trade_category = self.get_google_category_for_trade(trade).lower()
            if any(trade_category in cat for cat in profile_categories):
                category_match = 1.0
                break
        
        score += category_match * 0.1
        
        return min(score, 1.0)
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using Jaccard similarity.
        
        Business rule: Uses word-level Jaccard index for name matching.
        """
        
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_google_category_for_trade(self, trade: str) -> str:
        """
        Map Hero365 trade to Google Business category.
        
        Business rule: Standardized mapping between internal trades
        and Google's business category taxonomy.
        """
        
        trade_category_mapping = {
            # Commercial
            "mechanical": "HVAC Contractor",
            "refrigeration": "Commercial Refrigeration Service",
            "plumbing": "Plumber",
            "electrical": "Electrician",
            "security_systems": "Security System Installer",
            "landscaping": "Landscaper",
            "roofing": "Roofing Contractor",
            "kitchen_equipment": "Commercial Kitchen Equipment Service",
            "water_treatment": "Water Treatment Service",
            "pool_spa": "Pool & Spa Service",
            
            # Residential
            "hvac": "HVAC Contractor",
            "chimney": "Chimney Service",
            "garage_door": "Garage Door Service",
            "septic": "Septic Tank Service",
            "pest_control": "Pest Control Service",
            "irrigation": "Irrigation System Service",
            "painting": "Painter"
        }
        
        return trade_category_mapping.get(trade.lower(), "Home Services")
    
    def get_google_category_id_for_trade(self, trade: str) -> str:
        """
        Get Google category ID for trade.
        
        Business rule: Maps trades to Google's category ID system.
        """
        
        # Business rule: For now, all home services use generic ID
        # This would be expanded with specific category IDs from Google's taxonomy
        return "gcid:home_services"
    
    def format_business_hours(self, hours_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format business hours according to Google Business Profile requirements.
        
        Business rule: Default to standard business hours (8 AM - 5 PM, Mon-Fri)
        if no specific hours provided.
        """
        
        if not hours_data:
            # Business rule: Default hours for home service businesses
            return {
                "periods": [
                    {
                        "openDay": "MONDAY",
                        "openTime": {"hours": 8, "minutes": 0},
                        "closeDay": "MONDAY", 
                        "closeTime": {"hours": 17, "minutes": 0}
                    },
                    {
                        "openDay": "TUESDAY",
                        "openTime": {"hours": 8, "minutes": 0},
                        "closeDay": "TUESDAY",
                        "closeTime": {"hours": 17, "minutes": 0}
                    },
                    {
                        "openDay": "WEDNESDAY",
                        "openTime": {"hours": 8, "minutes": 0},
                        "closeDay": "WEDNESDAY",
                        "closeTime": {"hours": 17, "minutes": 0}
                    },
                    {
                        "openDay": "THURSDAY",
                        "openTime": {"hours": 8, "minutes": 0},
                        "closeDay": "THURSDAY",
                        "closeTime": {"hours": 17, "minutes": 0}
                    },
                    {
                        "openDay": "FRIDAY",
                        "openTime": {"hours": 8, "minutes": 0},
                        "closeDay": "FRIDAY",
                        "closeTime": {"hours": 17, "minutes": 0}
                    }
                ]
            }
        
        return hours_data
    
    def analyze_review_sentiment(self, review_text: str) -> float:
        """
        Analyze sentiment of review text.
        
        Business rule: Simple keyword-based sentiment analysis
        returning score between -1.0 (negative) and 1.0 (positive).
        """
        
        if not review_text:
            return 0.0
        
        # Business rule: Predefined positive and negative keywords
        positive_words = [
            "great", "excellent", "amazing", "professional", "recommend", 
            "fast", "quality", "satisfied", "outstanding", "fantastic",
            "reliable", "trustworthy", "efficient", "courteous", "helpful"
        ]
        negative_words = [
            "terrible", "awful", "slow", "expensive", "rude", "unprofessional", 
            "disappointed", "poor", "bad", "worst", "horrible", "incompetent",
            "unreliable", "overpriced", "delayed", "unsatisfied"
        ]
        
        text_lower = review_text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def generate_review_response(
        self,
        review_data: ReviewData,
        business: Business,
        response_tone: str = "professional"
    ) -> str:
        """
        Generate appropriate response to a customer review.
        
        Business rules:
        - Positive reviews (4-5 stars): Thank and encourage
        - Neutral reviews (3 stars): Acknowledge and invite discussion
        - Negative reviews (1-2 stars): Apologize and offer resolution
        - Always personalize with reviewer name and business context
        """
        
        try:
            reviewer_name = review_data.reviewer_name or "valued customer"
            primary_trade = business.get_primary_trade() or "services"
            business_name = business.name
            
            if review_data.rating >= 4:
                # Business rule: Positive review responses
                responses = [
                    f"Thank you {reviewer_name} for your wonderful review! We're thrilled that you were satisfied with our {primary_trade} services. We appreciate your business and look forward to serving you again.",
                    f"We're so grateful for your kind words, {reviewer_name}! Providing excellent {primary_trade} service is our top priority. Thank you for choosing {business_name}!",
                    f"Thank you for the 5-star review, {reviewer_name}! We're delighted that our team exceeded your expectations. We appreciate your trust in {business_name} for your {primary_trade} needs.",
                    f"What a fantastic review, {reviewer_name}! We're proud to have delivered exceptional {primary_trade} service. Your recommendation means the world to us at {business_name}."
                ]
            elif review_data.rating >= 3:
                # Business rule: Neutral review responses
                responses = [
                    f"Thank you for your feedback, {reviewer_name}. We appreciate you taking the time to share your experience. We're always working to improve our {primary_trade} services and would welcome the opportunity to discuss your experience further.",
                    f"Hi {reviewer_name}, thank you for your review. We value all feedback as it helps us improve our services. Please feel free to contact us directly if there's anything specific we can address.",
                    f"We appreciate your honest feedback, {reviewer_name}. At {business_name}, we're committed to continuous improvement in our {primary_trade} services. We'd love to hear more about your experience."
                ]
            else:
                # Business rule: Negative review responses
                responses = [
                    f"Thank you for your feedback, {reviewer_name}. We sincerely apologize that our service didn't meet your expectations. We take all concerns seriously and would appreciate the opportunity to make this right. Please contact us directly so we can resolve this matter.",
                    f"We're sorry to hear about your experience, {reviewer_name}. This doesn't reflect the quality of service we strive to provide. We'd like to discuss this with you directly and find a solution. Please reach out to us at your earliest convenience.",
                    f"We apologize for falling short of your expectations, {reviewer_name}. Your feedback is valuable to us at {business_name}, and we're committed to making this right. Please contact us so we can address your concerns personally."
                ]
            
            # Business rule: Consistent response selection based on review content hash
            response_index = int(
                hashlib.md5(review_data.review_text.encode()).hexdigest(), 16
            ) % len(responses)
            
            return responses[response_index]
            
        except Exception as e:
            # Business rule: Fallback response for any errors
            return f"Thank you for your review, {reviewer_name}. We appreciate your feedback and will use it to improve our services."
    
    def determine_profile_verification_priority(
        self, 
        business: Business, 
        profile_data: Dict[str, Any]
    ) -> int:
        """
        Determine priority level for profile verification.
        
        Business rule: Higher priority for businesses with:
        - Better match scores
        - More complete profiles
        - Active review engagement
        """
        
        priority = 0
        
        # Base priority on match score
        match_score = self.calculate_profile_match_score(business, profile_data)
        priority += int(match_score * 50)  # 0-50 points
        
        # Bonus for complete profiles
        if profile_data.get("phone"):
            priority += 10
        if profile_data.get("website"):
            priority += 10
        if profile_data.get("address", {}).get("locality"):
            priority += 10
        
        # Bonus for verification status
        verification_status = profile_data.get("verification_status", "")
        if verification_status == "VERIFIED":
            priority += 20
        elif verification_status == "PENDING":
            priority += 10
        
        return min(priority, 100)  # Cap at 100
    
    def calculate_profile_completeness_score(self, profile_data: Dict[str, Any]) -> float:
        """
        Calculate how complete a Google Business Profile is.
        
        Business rule: Score based on presence of key profile elements.
        """
        
        score = 0.0
        total_elements = 8
        
        # Essential elements (weighted scoring)
        if profile_data.get("name"):
            score += 1.0
        if profile_data.get("phone"):
            score += 1.0
        if profile_data.get("address", {}).get("locality"):
            score += 1.0
        if profile_data.get("website"):
            score += 1.0
        if profile_data.get("categories"):
            score += 1.0
        if profile_data.get("verification_status") == "VERIFIED":
            score += 1.0
        
        # Business hours
        hours = profile_data.get("regularHours", {}).get("periods", [])
        if hours:
            score += 1.0
        
        # Description/about section
        if profile_data.get("profile", {}).get("description"):
            score += 1.0
        
        return score / total_elements
    
    def should_auto_respond_to_review(
        self, 
        review_data: ReviewData, 
        business_settings: Dict[str, Any]
    ) -> bool:
        """
        Determine if a review should receive an automatic response.
        
        Business rules:
        - Only respond if auto-response is enabled
        - Don't respond to reviews older than 30 days
        - Don't respond if already responded
        - Always respond to negative reviews (1-2 stars)
        - Respond to positive reviews based on settings
        """
        
        if not business_settings.get("auto_respond_reviews", False):
            return False
        
        if review_data.is_responded:
            return False
        
        # Don't respond to very old reviews
        days_old = (datetime.utcnow() - review_data.review_date).days
        if days_old > 30:
            return False
        
        # Always respond to negative reviews
        if review_data.rating <= 2:
            return True
        
        # Respond to positive reviews based on settings
        if review_data.rating >= 4:
            return business_settings.get("auto_respond_positive", True)
        
        # Neutral reviews - respond based on settings
        return business_settings.get("auto_respond_neutral", False)
