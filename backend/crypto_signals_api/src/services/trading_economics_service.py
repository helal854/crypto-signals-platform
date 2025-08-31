"""
TradingEconomics API service for economic calendar
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TradingEconomicsService:
    """Service for TradingEconomics API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "guest:guest"  # Default guest credentials
        self.base_url = "https://api.tradingeconomics.com"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Any:
        """Make HTTP request to TradingEconomics API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        # Add API key to params
        if ':' in self.api_key:
            # Guest credentials format
            params['c'] = self.api_key
        else:
            # API key format
            params['key'] = self.api_key
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("TradingEconomics API rate limit reached")
                    return []
                else:
                    error_text = await response.text()
                    logger.error(f"TradingEconomics API error: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"TradingEconomics API request failed: {e}")
            return []
    
    async def get_economic_calendar(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get economic calendar events"""
        try:
            # Calculate date range
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            endpoint = f"/calendar"
            params = {
                'f': 'json',
                'd1': start_date,
                'd2': end_date
            }
            
            events = await self._make_request(endpoint, params)
            
            if not events:
                # Return mock data if API fails
                return self._get_mock_economic_events()
            
            # Filter and format important events
            important_events = []
            
            for event in events:
                if isinstance(event, dict):
                    # Filter by importance (High impact events)
                    importance = event.get('Importance', 1)
                    if importance >= 2:  # Medium to High importance
                        
                        formatted_event = {
                            'title': event.get('Event', 'Unknown Event'),
                            'country': event.get('Country', 'Unknown'),
                            'date': event.get('Date', ''),
                            'time': event.get('Time', ''),
                            'impact': self._get_impact_level(importance),
                            'forecast': event.get('Forecast', ''),
                            'previous': event.get('Previous', ''),
                            'actual': event.get('Actual', ''),
                            'currency': event.get('Currency', ''),
                            'category': event.get('Category', '')
                        }
                        
                        important_events.append(formatted_event)
            
            # Sort by date and time
            important_events.sort(key=lambda x: f"{x['date']} {x['time']}")
            
            return important_events[:20]  # Return top 20 events
            
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return self._get_mock_economic_events()
    
    def _get_impact_level(self, importance: int) -> str:
        """Convert importance number to impact level"""
        if importance >= 3:
            return 'high'
        elif importance >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _get_mock_economic_events(self) -> List[Dict[str, Any]]:
        """Get mock economic events as fallback"""
        base_date = datetime.now()
        
        mock_events = [
            {
                'title': 'Federal Reserve Interest Rate Decision',
                'country': 'United States',
                'date': (base_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'impact': 'high',
                'forecast': '5.25%',
                'previous': '5.25%',
                'actual': '',
                'currency': 'USD',
                'category': 'Interest Rate'
            },
            {
                'title': 'Non-Farm Payrolls',
                'country': 'United States',
                'date': (base_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '13:30',
                'impact': 'high',
                'forecast': '200K',
                'previous': '187K',
                'actual': '',
                'currency': 'USD',
                'category': 'Employment'
            },
            {
                'title': 'Consumer Price Index (CPI)',
                'country': 'United States',
                'date': (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '13:30',
                'impact': 'high',
                'forecast': '3.2%',
                'previous': '3.1%',
                'actual': '',
                'currency': 'USD',
                'category': 'Inflation'
            },
            {
                'title': 'European Central Bank Interest Rate Decision',
                'country': 'European Union',
                'date': (base_date + timedelta(days=4)).strftime('%Y-%m-%d'),
                'time': '12:15',
                'impact': 'high',
                'forecast': '4.50%',
                'previous': '4.50%',
                'actual': '',
                'currency': 'EUR',
                'category': 'Interest Rate'
            },
            {
                'title': 'GDP Growth Rate',
                'country': 'China',
                'date': (base_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                'time': '02:00',
                'impact': 'medium',
                'forecast': '5.2%',
                'previous': '5.3%',
                'actual': '',
                'currency': 'CNY',
                'category': 'GDP'
            },
            {
                'title': 'Bank of Japan Interest Rate Decision',
                'country': 'Japan',
                'date': (base_date + timedelta(days=6)).strftime('%Y-%m-%d'),
                'time': '03:00',
                'impact': 'medium',
                'forecast': '-0.10%',
                'previous': '-0.10%',
                'actual': '',
                'currency': 'JPY',
                'category': 'Interest Rate'
            }
        ]
        
        return mock_events
    
    async def get_country_indicators(self, country: str) -> List[Dict[str, Any]]:
        """Get economic indicators for a specific country"""
        try:
            endpoint = f"/country/{country.lower()}"
            
            indicators = await self._make_request(endpoint)
            
            if not indicators:
                return []
            
            # Format indicators
            formatted_indicators = []
            
            for indicator in indicators[:10]:  # Top 10 indicators
                if isinstance(indicator, dict):
                    formatted_indicators.append({
                        'category': indicator.get('Category', ''),
                        'title': indicator.get('Title', ''),
                        'latest_value': indicator.get('LatestValue', ''),
                        'latest_value_date': indicator.get('LatestValueDate', ''),
                        'previous_value': indicator.get('PreviousValue', ''),
                        'unit': indicator.get('Unit', ''),
                        'frequency': indicator.get('Frequency', '')
                    })
            
            return formatted_indicators
            
        except Exception as e:
            logger.error(f"Error fetching country indicators for {country}: {e}")
            return []
    
    async def get_market_forecasts(self, category: str = None) -> List[Dict[str, Any]]:
        """Get market forecasts"""
        try:
            endpoint = "/forecasts"
            params = {}
            
            if category:
                params['category'] = category
            
            forecasts = await self._make_request(endpoint, params)
            
            if not forecasts:
                return []
            
            # Format forecasts
            formatted_forecasts = []
            
            for forecast in forecasts[:15]:  # Top 15 forecasts
                if isinstance(forecast, dict):
                    formatted_forecasts.append({
                        'country': forecast.get('Country', ''),
                        'category': forecast.get('Category', ''),
                        'title': forecast.get('Title', ''),
                        'forecast_value': forecast.get('ForecastValue', ''),
                        'forecast_date': forecast.get('ForecastDate', ''),
                        'trading_economics_forecast': forecast.get('TEForecast', ''),
                        'trading_economics_forecast_min': forecast.get('TEForecastMin', ''),
                        'trading_economics_forecast_max': forecast.get('TEForecastMax', '')
                    })
            
            return formatted_forecasts
            
        except Exception as e:
            logger.error(f"Error fetching market forecasts: {e}")
            return []
    
    async def get_formatted_calendar(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get formatted economic calendar for the bot"""
        try:
            events = await self.get_economic_calendar(days_ahead)
            
            formatted_events = []
            
            for event in events:
                # Parse date and time
                try:
                    event_datetime = datetime.strptime(f"{event['date']} {event['time']}", '%Y-%m-%d %H:%M')
                except:
                    event_datetime = datetime.now()
                
                # Translate impact to Arabic
                impact_arabic = {
                    'high': 'عالي',
                    'medium': 'متوسط',
                    'low': 'منخفض'
                }.get(event['impact'], 'متوسط')
                
                # Translate country names to Arabic
                country_arabic = {
                    'United States': 'الولايات المتحدة',
                    'European Union': 'الاتحاد الأوروبي',
                    'China': 'الصين',
                    'Japan': 'اليابان',
                    'United Kingdom': 'المملكة المتحدة',
                    'Germany': 'ألمانيا',
                    'France': 'فرنسا',
                    'Canada': 'كندا',
                    'Australia': 'أستراليا'
                }.get(event['country'], event['country'])
                
                formatted_events.append({
                    'title': event['title'],
                    'country': country_arabic,
                    'date': event_datetime.strftime('%Y-%m-%d'),
                    'time': event_datetime.strftime('%H:%M'),
                    'impact': event['impact'],
                    'impact_arabic': impact_arabic,
                    'forecast': event['forecast'],
                    'previous': event['previous'],
                    'currency': event['currency'],
                    'category': event['category'],
                    'datetime': event_datetime.isoformat()
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error formatting economic calendar: {e}")
            return []
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

