"""
Fear & Greed Index service using Alternative.me API
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FearGreedService:
    """Service for Fear & Greed Index from Alternative.me"""
    
    def __init__(self):
        self.base_url = "https://api.alternative.me"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to Alternative.me API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Fear & Greed API error: {response.status} - {error_text}")
                    raise Exception(f"Fear & Greed API error: {response.status}")
        except Exception as e:
            logger.error(f"Fear & Greed API request failed: {e}")
            raise
    
    async def get_current_index(self) -> Dict[str, Any]:
        """Get current Fear & Greed Index"""
        try:
            response = await self._make_request('/fng/')
            
            if response and 'data' in response and response['data']:
                data = response['data'][0]
                
                return {
                    'value': int(data['value']),
                    'value_classification': data['value_classification'],
                    'timestamp': data['timestamp'],
                    'time_until_update': data.get('time_until_update')
                }
            else:
                # Fallback data if API fails
                return {
                    'value': 50,
                    'value_classification': 'Neutral',
                    'timestamp': str(int(datetime.now().timestamp())),
                    'time_until_update': None
                }
                
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            # Return neutral value as fallback
            return {
                'value': 50,
                'value_classification': 'Neutral',
                'timestamp': str(int(datetime.now().timestamp())),
                'time_until_update': None
            }
    
    async def get_historical_index(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get historical Fear & Greed Index data"""
        try:
            params = {'limit': limit}
            response = await self._make_request('/fng/', params)
            
            if response and 'data' in response:
                return [
                    {
                        'value': int(item['value']),
                        'value_classification': item['value_classification'],
                        'timestamp': item['timestamp'],
                        'date': datetime.fromtimestamp(int(item['timestamp'])).strftime('%Y-%m-%d')
                    }
                    for item in response['data']
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching historical Fear & Greed Index: {e}")
            return []
    
    async def get_index_trend(self, days: int = 7) -> Dict[str, Any]:
        """Get Fear & Greed Index trend analysis"""
        try:
            historical_data = await self.get_historical_index(days)
            
            if not historical_data:
                return {
                    'trend': 'neutral',
                    'average': 50,
                    'change': 0,
                    'volatility': 0
                }
            
            values = [item['value'] for item in historical_data]
            current_value = values[0] if values else 50
            
            # Calculate trend
            if len(values) >= 2:
                recent_avg = sum(values[:3]) / min(3, len(values))
                older_avg = sum(values[3:]) / max(1, len(values) - 3)
                change = recent_avg - older_avg
            else:
                change = 0
            
            # Determine trend direction
            if change > 5:
                trend = 'increasing'
            elif change < -5:
                trend = 'decreasing'
            else:
                trend = 'neutral'
            
            # Calculate volatility (standard deviation)
            if len(values) > 1:
                avg = sum(values) / len(values)
                variance = sum((x - avg) ** 2 for x in values) / len(values)
                volatility = variance ** 0.5
            else:
                volatility = 0
            
            return {
                'trend': trend,
                'average': sum(values) / len(values) if values else 50,
                'change': change,
                'volatility': volatility,
                'current_value': current_value,
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Error calculating Fear & Greed trend: {e}")
            return {
                'trend': 'neutral',
                'average': 50,
                'change': 0,
                'volatility': 0
            }
    
    def classify_fear_greed_level(self, value: int) -> Dict[str, str]:
        """Classify Fear & Greed level with Arabic translation"""
        
        if value <= 20:
            return {
                'level': 'Extreme Fear',
                'arabic': 'خوف شديد',
                'emoji': '😱',
                'color': '#FF4444',
                'description': 'السوق في حالة خوف شديد - قد تكون فرصة شراء'
            }
        elif value <= 40:
            return {
                'level': 'Fear',
                'arabic': 'خوف',
                'emoji': '😰',
                'color': '#FF8800',
                'description': 'السوق في حالة خوف - الحذر مطلوب'
            }
        elif value <= 60:
            return {
                'level': 'Neutral',
                'arabic': 'محايد',
                'emoji': '😐',
                'color': '#FFDD00',
                'description': 'السوق في حالة محايدة - انتظار إشارات أوضح'
            }
        elif value <= 80:
            return {
                'level': 'Greed',
                'arabic': 'طمع',
                'emoji': '😊',
                'color': '#88DD00',
                'description': 'السوق في حالة طمع - الحذر من الشراء'
            }
        else:
            return {
                'level': 'Extreme Greed',
                'arabic': 'طمع شديد',
                'emoji': '🤑',
                'color': '#00DD44',
                'description': 'السوق في حالة طمع شديد - خطر تصحيح قريب'
            }
    
    async def get_formatted_index(self) -> Dict[str, Any]:
        """Get formatted Fear & Greed Index for the bot"""
        try:
            current_data = await self.get_current_index()
            trend_data = await self.get_index_trend()
            
            value = current_data['value']
            classification = self.classify_fear_greed_level(value)
            
            return {
                'value': value,
                'classification': current_data['value_classification'],
                'arabic_classification': classification['arabic'],
                'emoji': classification['emoji'],
                'color': classification['color'],
                'description': classification['description'],
                'timestamp': current_data['timestamp'],
                'trend': trend_data['trend'],
                'trend_change': trend_data['change'],
                'volatility': trend_data['volatility'],
                'weekly_average': trend_data['average']
            }
            
        except Exception as e:
            logger.error(f"Error formatting Fear & Greed Index: {e}")
            # Return fallback data
            return {
                'value': 50,
                'classification': 'Neutral',
                'arabic_classification': 'محايد',
                'emoji': '😐',
                'color': '#FFDD00',
                'description': 'السوق في حالة محايدة',
                'timestamp': str(int(datetime.now().timestamp())),
                'trend': 'neutral',
                'trend_change': 0,
                'volatility': 0,
                'weekly_average': 50
            }
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

