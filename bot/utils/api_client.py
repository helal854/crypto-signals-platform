"""
API Client for communicating with the backend
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import logging

from config.settings import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

class APIClient:
    """Client for backend API communication"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    raise Exception(f"API request failed with status {response.status}")
        except Exception as e:
            logger.error(f"API request error: {e}")
            raise
    
    # User Management
    async def register_telegram_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new Telegram user"""
        return await self._make_request('POST', '/telegram-users', json=user_data)
    
    async def get_telegram_user(self, user_id: int) -> Dict[str, Any]:
        """Get Telegram user by ID"""
        return await self._make_request('GET', f'/telegram-users/{user_id}')
    
    async def get_telegram_users(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of Telegram users"""
        return await self._make_request('GET', f'/telegram-users?limit={limit}')
    
    async def update_telegram_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update Telegram user"""
        return await self._make_request('PUT', f'/telegram-users/{user_id}', json=data)
    
    async def delete_telegram_user(self, user_id: int) -> Dict[str, Any]:
        """Delete Telegram user"""
        return await self._make_request('DELETE', f'/telegram-users/{user_id}')
    
    async def toggle_user_notifications(self, user_id: int) -> Dict[str, Any]:
        """Toggle user notifications"""
        return await self._make_request('POST', f'/telegram-users/{user_id}/toggle-notifications')
    
    # Subscription Management
    async def activate_subscription(self, user_id: int, plan: str) -> Dict[str, Any]:
        """Activate user subscription"""
        data = {'user_id': user_id, 'plan': plan}
        return await self._make_request('POST', '/subscriptions/activate', json=data)
    
    async def get_user_subscription(self, user_id: int) -> Dict[str, Any]:
        """Get user subscription details"""
        return await self._make_request('GET', f'/subscriptions/user/{user_id}')
    
    # Payment Management
    async def create_payment_invoice(self, user_id: int, plan: str, payment_method: str, amount: float) -> Dict[str, Any]:
        """Create payment invoice"""
        data = {
            'user_id': user_id,
            'plan': plan,
            'payment_method': payment_method,
            'amount': amount
        }
        return await self._make_request('POST', '/payments/create-invoice', json=data)
    
    async def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check payment status"""
        return await self._make_request('GET', f'/payments/status/{invoice_id}')
    
    async def get_user_payments(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user payment history"""
        return await self._make_request('GET', f'/payments/user/{user_id}')
    
    async def get_recent_payments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent payments for admin"""
        return await self._make_request('GET', f'/payments/recent?limit={limit}')
    
    # Signals Management
    async def get_spot_signals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get Spot signals"""
        return await self._make_request('GET', f'/signals/spot?limit={limit}')
    
    async def get_futures_signals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get Futures signals"""
        return await self._make_request('GET', f'/signals/futures?limit={limit}')
    
    async def get_signal_details(self, signal_id: str) -> Dict[str, Any]:
        """Get signal details"""
        return await self._make_request('GET', f'/signals/{signal_id}')
    
    async def get_signal_statistics(self) -> Dict[str, Any]:
        """Get signal statistics"""
        return await self._make_request('GET', '/signals/statistics')
    
    # Futures Management
    async def get_futures_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Futures leaderboard"""
        return await self._make_request('GET', f'/futures/leaderboard?limit={limit}')
    
    async def get_futures_traders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get Futures traders"""
        return await self._make_request('GET', f'/futures/traders?limit={limit}')
    
    # Market Data
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """Get Fear & Greed index"""
        return await self._make_request('GET', '/market/fear-greed')
    
    async def get_support_resistance_levels(self) -> List[Dict[str, Any]]:
        """Get support and resistance levels"""
        return await self._make_request('GET', '/market/support-resistance')
    
    async def get_economic_calendar(self) -> List[Dict[str, Any]]:
        """Get economic calendar"""
        return await self._make_request('GET', '/market/economic-calendar')
    
    async def get_crypto_prices(self) -> List[Dict[str, Any]]:
        """Get cryptocurrency prices"""
        return await self._make_request('GET', '/market/crypto-prices')
    
    async def get_market_analysis(self) -> Dict[str, Any]:
        """Get market analysis"""
        return await self._make_request('GET', '/market/analysis')
    
    # Admin Functions
    async def get_admin_statistics(self) -> Dict[str, Any]:
        """Get admin statistics"""
        return await self._make_request('GET', '/admin/statistics')
    
    async def send_broadcast_message(self, message: str, sender_id: int) -> Dict[str, Any]:
        """Send broadcast message"""
        data = {'message': message, 'sender_id': sender_id}
        return await self._make_request('POST', '/admin/broadcast', json=data)
    
    async def get_system_settings(self) -> Dict[str, Any]:
        """Get system settings"""
        return await self._make_request('GET', '/admin/settings')
    
    async def update_system_setting(self, key: str, value: Any) -> Dict[str, Any]:
        """Update system setting"""
        data = {'key': key, 'value': value}
        return await self._make_request('PUT', '/admin/settings', json=data)
    
    async def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit logs"""
        return await self._make_request('GET', f'/admin/logs?limit={limit}')
    
    # Dashboard Data
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return await self._make_request('GET', '/dashboard')
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

