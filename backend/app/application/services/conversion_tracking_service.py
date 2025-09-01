"""
Conversion Tracking Service - 10X Revenue Focus
Tracks website conversions and calculates ROI
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from supabase import Client


class ConversionTrackingService:
    """10X approach: Simple conversion tracking with powerful analytics"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def track_conversion(
        self,
        business_id: UUID,
        conversion_data: Dict
    ) -> Dict:
        """
        Track a conversion event from the website
        """
        conversion_record = {
            'business_id': str(business_id),
            'conversion_type': conversion_data.get('type', 'contact'),
            'conversion_value': conversion_data.get('value', 0.0),
            'source_page': conversion_data.get('page', '/'),
            'visitor_data': conversion_data.get('visitor', {}),
            'conversion_data': conversion_data.get('details', {}),
            'created_at': datetime.utcnow().isoformat()
        }
        
        response = self.db.table('website_conversions').insert(conversion_record).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise Exception("Failed to track conversion")
    
    async def get_conversion_analytics(
        self,
        business_id: UUID,
        days: int = 30
    ) -> Dict:
        """
        Get conversion analytics for ROI dashboard
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get conversions for the period
        response = self.db.table('website_conversions').select('*').eq('business_id', str(business_id)).gte('created_at', start_date.isoformat()).execute()
        
        conversions = response.data if response.data else []
        
        # Calculate metrics
        total_conversions = len(conversions)
        total_value = sum(c.get('conversion_value', 0) for c in conversions)
        
        # Group by type
        conversion_by_type = {}
        for conversion in conversions:
            conv_type = conversion.get('conversion_type', 'unknown')
            if conv_type not in conversion_by_type:
                conversion_by_type[conv_type] = {'count': 0, 'value': 0}
            conversion_by_type[conv_type]['count'] += 1
            conversion_by_type[conv_type]['value'] += conversion.get('conversion_value', 0)
        
        # Group by page
        conversion_by_page = {}
        for conversion in conversions:
            page = conversion.get('source_page', '/')
            if page not in conversion_by_page:
                conversion_by_page[page] = {'count': 0, 'value': 0}
            conversion_by_page[page]['count'] += 1
            conversion_by_page[page]['value'] += conversion.get('conversion_value', 0)
        
        return {
            'period_days': days,
            'total_conversions': total_conversions,
            'total_value': total_value,
            'average_conversion_value': total_value / max(total_conversions, 1),
            'conversions_by_type': conversion_by_type,
            'conversions_by_page': conversion_by_page,
            'daily_conversions': self._get_daily_conversions(conversions)
        }
    
    def _get_daily_conversions(
        self,
        conversions: List[Dict]
    ) -> List[Dict]:
        """
        Get daily conversion breakdown for charts
        """
        # Group by day
        daily_data = {}
        for conversion in conversions:
            # Parse the created_at timestamp
            created_at_str = conversion.get('created_at', datetime.utcnow().isoformat())
            if isinstance(created_at_str, str):
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            else:
                created_at = created_at_str
            
            date_str = created_at.strftime('%Y-%m-%d')
            if date_str not in daily_data:
                daily_data[date_str] = {'count': 0, 'value': 0}
            daily_data[date_str]['count'] += 1
            daily_data[date_str]['value'] += conversion.get('conversion_value', 0)
        
        # Convert to list format for charts
        return [
            {
                'date': date,
                'conversions': data['count'],
                'value': data['value']
            }
            for date, data in sorted(daily_data.items())
        ]
    
    async def get_roi_metrics(
        self,
        business_id: UUID,
        days: int = 30
    ) -> Dict:
        """
        Calculate ROI metrics for the website
        """
        analytics = await self.get_conversion_analytics(business_id, days)
        
        # Estimate website cost (simplified - could be more sophisticated)
        estimated_monthly_cost = 50.0  # Base Hero365 subscription
        daily_cost = estimated_monthly_cost / 30
        period_cost = daily_cost * days
        
        total_revenue = analytics['total_value']
        roi_percentage = ((total_revenue - period_cost) / max(period_cost, 1)) * 100
        
        return {
            'period_days': days,
            'total_revenue': total_revenue,
            'estimated_cost': period_cost,
            'net_profit': total_revenue - period_cost,
            'roi_percentage': roi_percentage,
            'cost_per_conversion': period_cost / max(analytics['total_conversions'], 1),
            'revenue_per_conversion': analytics['average_conversion_value']
        }
