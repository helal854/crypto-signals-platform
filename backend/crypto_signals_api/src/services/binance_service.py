"""
Binance API service for market data and futures leaderboard
"""

import aiohttp
import asyncio
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class BinanceService:
    """Service for Binance API integration"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com"
        self.futures_url = "https://fapi.binance.com"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _generate_signature(self, query_string: str) -> str:
        """Generate signature for authenticated requests"""
        if not self.api_secret:
            raise ValueError("API secret required for authenticated requests")
        
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _make_request(self, url: str, params: Dict = None, signed: bool = False) -> Dict[str, Any]:
        """Make HTTP request to Binance API"""
        session = await self._get_session()
        
        if params is None:
            params = {}
        
        headers = {}
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            params['signature'] = self._generate_signature(query_string)
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Binance API error: {response.status} - {error_text}")
                    raise Exception(f"Binance API error: {response.status}")
        except Exception as e:
            logger.error(f"Binance API request failed: {e}")
            raise
    
    async def get_symbol_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol"""
        url = f"{self.base_url}/api/v3/ticker/price"
        params = {'symbol': symbol.upper()}
        
        return await self._make_request(url, params)
    
    async def get_24hr_ticker(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get 24hr ticker statistics"""
        url = f"{self.base_url}/api/v3/ticker/24hr"
        params = {}
        
        if symbol:
            params['symbol'] = symbol.upper()
        
        result = await self._make_request(url, params)
        return result if isinstance(result, list) else [result]
    
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.base_url}/api/v3/klines"
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': limit
        }
        
        return await self._make_request(url, params)
    
    async def calculate_support_resistance(self, symbol: str, period: str = "1d") -> Dict[str, Any]:
        """Calculate support and resistance levels"""
        try:
            # Get recent klines data
            klines = await self.get_klines(symbol, period, 50)
            
            if not klines:
                return {'symbol': symbol, 'support_levels': [], 'resistance_levels': []}
            
            # Extract high and low prices
            highs = [float(kline[2]) for kline in klines]  # High prices
            lows = [float(kline[3]) for kline in klines]   # Low prices
            closes = [float(kline[4]) for kline in klines] # Close prices
            
            current_price = closes[-1]
            
            # Simple support/resistance calculation
            # Support: Recent significant lows
            support_levels = []
            resistance_levels = []
            
            # Find local minima for support
            for i in range(2, len(lows) - 2):
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    if lows[i] < current_price:  # Only levels below current price
                        support_levels.append(lows[i])
            
            # Find local maxima for resistance
            for i in range(2, len(highs) - 2):
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    if highs[i] > current_price:  # Only levels above current price
                        resistance_levels.append(highs[i])
            
            # Sort and get top levels
            support_levels = sorted(set(support_levels), reverse=True)[:3]
            resistance_levels = sorted(set(resistance_levels))[:3]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance for {symbol}: {e}")
            return {'symbol': symbol, 'support_levels': [], 'resistance_levels': []}
    
    async def get_futures_leaderboard(self, symbol: str = "USDT", period: str = "7d") -> List[Dict[str, Any]]:
        """Get futures leaderboard data"""
        # Note: This is a mock implementation as Binance doesn't provide public leaderboard API
        # In production, you would need to use Binance's official leaderboard or scrape data
        
        try:
            # Mock leaderboard data for demonstration
            mock_traders = [
                {
                    "nickname": "CryptoKing",
                    "uid": "D908B5DF1A83DE36",
                    "rank": 1,
                    "pnl": 15420.50,
                    "roi": 23.45,
                    "followerCount": 1250,
                    "positions": [
                        {
                            "symbol": "BTCUSDT",
                            "side": "LONG",
                            "size": 0.5,
                            "markPrice": 43250.00,
                            "pnl": 850.25,
                            "roe": 12.5
                        }
                    ]
                },
                {
                    "nickname": "FuturesGuru",
                    "uid": "A123B456C789D012",
                    "rank": 2,
                    "pnl": 12890.75,
                    "roi": 19.87,
                    "followerCount": 980,
                    "positions": [
                        {
                            "symbol": "ETHUSDT",
                            "side": "SHORT",
                            "size": 2.1,
                            "markPrice": 2650.00,
                            "pnl": -125.50,
                            "roe": -2.3
                        }
                    ]
                },
                {
                    "nickname": "TradeMaster",
                    "uid": "E456F789G012H345",
                    "rank": 3,
                    "pnl": 9876.25,
                    "roi": 16.42,
                    "followerCount": 756,
                    "positions": [
                        {
                            "symbol": "SOLUSDT",
                            "side": "LONG",
                            "size": 15.0,
                            "markPrice": 98.50,
                            "pnl": 234.75,
                            "roe": 8.9
                        }
                    ]
                }
            ]
            
            return mock_traders
            
        except Exception as e:
            logger.error(f"Error fetching futures leaderboard: {e}")
            return []
    
    async def get_trader_positions(self, trader_uid: str) -> List[Dict[str, Any]]:
        """Get specific trader's positions"""
        # Mock implementation - in production, this would require special API access
        
        try:
            # Mock trader positions
            mock_positions = [
                {
                    "symbol": "BTCUSDT",
                    "side": "LONG",
                    "size": 0.75,
                    "entryPrice": 42800.00,
                    "markPrice": 43250.00,
                    "pnl": 337.50,
                    "roe": 15.75,
                    "leverage": 5,
                    "timestamp": int(time.time() * 1000)
                },
                {
                    "symbol": "ETHUSDT",
                    "side": "SHORT",
                    "size": 1.5,
                    "entryPrice": 2680.00,
                    "markPrice": 2650.00,
                    "pnl": 45.00,
                    "roe": 2.24,
                    "leverage": 3,
                    "timestamp": int(time.time() * 1000) - 3600000
                }
            ]
            
            return mock_positions
            
        except Exception as e:
            logger.error(f"Error fetching trader positions for {trader_uid}: {e}")
            return []
    
    async def get_top_symbols(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top trading symbols by volume"""
        try:
            tickers = await self.get_24hr_ticker()
            
            # Filter USDT pairs and sort by volume
            usdt_pairs = [
                ticker for ticker in tickers 
                if ticker['symbol'].endswith('USDT') and 
                ticker['symbol'] not in ['BUSDUSDT', 'TUSDUSDT', 'USDCUSDT']
            ]
            
            # Sort by quote volume
            sorted_pairs = sorted(
                usdt_pairs, 
                key=lambda x: float(x['quoteVolume']), 
                reverse=True
            )
            
            return sorted_pairs[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching top symbols: {e}")
            return []
    
    async def get_futures_open_interest(self, symbol: str) -> Dict[str, Any]:
        """Get futures open interest data"""
        try:
            url = f"{self.futures_url}/fapi/v1/openInterest"
            params = {'symbol': symbol.upper()}
            
            return await self._make_request(url, params)
            
        except Exception as e:
            logger.error(f"Error fetching open interest for {symbol}: {e}")
            return {}
    
    async def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Get current funding rate"""
        try:
            url = f"{self.futures_url}/fapi/v1/premiumIndex"
            params = {'symbol': symbol.upper()}
            
            return await self._make_request(url, params)
            
        except Exception as e:
            logger.error(f"Error fetching funding rate for {symbol}: {e}")
            return {}
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

