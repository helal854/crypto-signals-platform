"""
CoinGecko API service for cryptocurrency market data
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CoinGeckoService:
    """Service for CoinGecko API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to CoinGecko API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        headers = {}
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"CoinGecko API error: {response.status} - {error_text}")
                    raise Exception(f"CoinGecko API error: {response.status}")
        except Exception as e:
            logger.error(f"CoinGecko API request failed: {e}")
            raise
    
    async def get_coin_price(self, coin_ids: List[str], vs_currencies: List[str] = None) -> Dict[str, Any]:
        """Get current price of coins"""
        if vs_currencies is None:
            vs_currencies = ['usd']
        
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': ','.join(vs_currencies),
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        return await self._make_request('/simple/price', params)
    
    async def get_top_cryptocurrencies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top cryptocurrencies by market cap"""
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': 'false',
            'price_change_percentage': '24h,7d'
        }
        
        return await self._make_request('/coins/markets', params)
    
    async def get_coin_details(self, coin_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific coin"""
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }
        
        return await self._make_request(f'/coins/{coin_id}', params)
    
    async def get_market_data(self) -> Dict[str, Any]:
        """Get global cryptocurrency market data"""
        return await self._make_request('/global')
    
    async def get_trending_coins(self) -> Dict[str, Any]:
        """Get trending search coins"""
        return await self._make_request('/search/trending')
    
    async def get_coin_history(self, coin_id: str, date: str) -> Dict[str, Any]:
        """Get historical data for a coin on a specific date"""
        params = {'date': date, 'localization': 'false'}
        
        return await self._make_request(f'/coins/{coin_id}/history', params)
    
    async def get_coin_market_chart(self, coin_id: str, vs_currency: str = 'usd', days: int = 7) -> Dict[str, Any]:
        """Get market chart data for a coin"""
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        return await self._make_request(f'/coins/{coin_id}/market_chart', params)
    
    async def search_coins(self, query: str) -> Dict[str, Any]:
        """Search for coins by name or symbol"""
        params = {'query': query}
        
        return await self._make_request('/search', params)
    
    async def get_exchange_rates(self) -> Dict[str, Any]:
        """Get BTC-to-Currency exchange rates"""
        return await self._make_request('/exchange_rates')
    
    async def get_supported_vs_currencies(self) -> List[str]:
        """Get list of supported vs currencies"""
        return await self._make_request('/simple/supported_vs_currencies')
    
    async def get_coins_list(self, include_platform: bool = False) -> List[Dict[str, Any]]:
        """Get list of all supported coins"""
        params = {'include_platform': str(include_platform).lower()}
        
        return await self._make_request('/coins/list', params)
    
    async def get_price_change_percentage(self, coin_ids: List[str], timeframes: List[str] = None) -> Dict[str, Any]:
        """Get price change percentage for specific timeframes"""
        if timeframes is None:
            timeframes = ['24h', '7d', '30d']
        
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'price_change_percentage': ','.join(timeframes)
        }
        
        return await self._make_request('/simple/price', params)
    
    async def get_defi_data(self) -> Dict[str, Any]:
        """Get DeFi market data"""
        return await self._make_request('/global/decentralized_finance_defi')
    
    async def get_nft_data(self) -> Dict[str, Any]:
        """Get NFT market data"""
        return await self._make_request('/nfts/markets')
    
    async def format_crypto_prices(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Get formatted crypto prices for the bot"""
        if symbols is None:
            symbols = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano', 'polkadot', 'chainlink', 'litecoin']
        
        try:
            # Get price data
            price_data = await self.get_coin_price(symbols, ['usd'])
            
            # Get market data for volume
            market_data = await self.get_top_cryptocurrencies(50)
            
            # Create symbol mapping
            symbol_map = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'binancecoin': 'BNB',
                'solana': 'SOL',
                'cardano': 'ADA',
                'polkadot': 'DOT',
                'chainlink': 'LINK',
                'litecoin': 'LTC'
            }
            
            formatted_prices = []
            
            for coin_id in symbols:
                if coin_id in price_data:
                    coin_price = price_data[coin_id]
                    
                    # Find market data for volume
                    market_info = next((item for item in market_data if item['id'] == coin_id), {})
                    
                    formatted_prices.append({
                        'symbol': symbol_map.get(coin_id, coin_id.upper()),
                        'price': coin_price.get('usd', 0),
                        'change_24h': coin_price.get('usd_24h_change', 0),
                        'volume_24h': market_info.get('total_volume', 0),
                        'market_cap': coin_price.get('usd_market_cap', 0)
                    })
            
            return formatted_prices
            
        except Exception as e:
            logger.error(f"Error formatting crypto prices: {e}")
            return []
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

