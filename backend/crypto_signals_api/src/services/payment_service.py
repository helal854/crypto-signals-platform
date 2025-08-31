"""
Payment service for cryptocurrency payments
"""

import aiohttp
import asyncio
import hashlib
import hmac
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for cryptocurrency payment processing"""
    
    def __init__(self, nowpayments_api_key: str = None, btcpay_api_key: str = None, btcpay_url: str = None):
        self.nowpayments_api_key = nowpayments_api_key
        self.btcpay_api_key = btcpay_api_key
        self.btcpay_url = btcpay_url
        self.nowpayments_url = "https://api.nowpayments.io/v1"
        self.session = None
        
        # Wallet addresses from knowledge
        self.wallet_addresses = {
            'BTC': '14MxL4x95TRTYJroWe8bWy4wSLq6c4WCr5',
            'USDT_TRC20': 'TJkLFH53mJUzaTMxLtYqa28jzL9CppJotV',
            'USDT_ERC20': '0xdd3a7fd3a23c7bf18a9956ca1a1cc8f35d4fce25'
        }
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_nowpayments_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Make request to NowPayments API"""
        session = await self._get_session()
        url = f"{self.nowpayments_url}{endpoint}"
        
        headers = {
            'x-api-key': self.nowpayments_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                async with session.get(url, headers=headers) as response:
                    return await self._handle_response(response)
            elif method == 'POST':
                async with session.post(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)
        except Exception as e:
            logger.error(f"NowPayments API request failed: {e}")
            raise
    
    async def _make_btcpay_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Make request to BTCPay Server API"""
        if not self.btcpay_url or not self.btcpay_api_key:
            raise ValueError("BTCPay Server configuration missing")
        
        session = await self._get_session()
        url = f"{self.btcpay_url}{endpoint}"
        
        headers = {
            'Authorization': f'token {self.btcpay_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                async with session.get(url, headers=headers) as response:
                    return await self._handle_response(response)
            elif method == 'POST':
                async with session.post(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)
        except Exception as e:
            logger.error(f"BTCPay Server API request failed: {e}")
            raise
    
    async def _handle_response(self, response) -> Dict[str, Any]:
        """Handle API response"""
        if response.status == 200:
            return await response.json()
        else:
            error_text = await response.text()
            logger.error(f"API error: {response.status} - {error_text}")
            raise Exception(f"API error: {response.status}")
    
    async def create_payment_invoice(self, amount: float, currency: str, order_id: str, description: str = None) -> Dict[str, Any]:
        """Create payment invoice"""
        try:
            # Try NowPayments first
            if self.nowpayments_api_key:
                return await self._create_nowpayments_invoice(amount, currency, order_id, description)
            
            # Fallback to BTCPay Server
            elif self.btcpay_api_key and self.btcpay_url:
                return await self._create_btcpay_invoice(amount, currency, order_id, description)
            
            # Fallback to manual payment
            else:
                return await self._create_manual_invoice(amount, currency, order_id, description)
                
        except Exception as e:
            logger.error(f"Error creating payment invoice: {e}")
            # Return manual payment as fallback
            return await self._create_manual_invoice(amount, currency, order_id, description)
    
    async def _create_nowpayments_invoice(self, amount: float, currency: str, order_id: str, description: str) -> Dict[str, Any]:
        """Create invoice using NowPayments"""
        data = {
            'price_amount': amount,
            'price_currency': 'USD',
            'pay_currency': currency.upper(),
            'order_id': order_id,
            'order_description': description or f'Subscription payment - {order_id}',
            'ipn_callback_url': f'https://your-domain.com/api/payments/callback',
            'success_url': f'https://your-domain.com/payment/success',
            'cancel_url': f'https://your-domain.com/payment/cancel'
        }
        
        response = await self._make_nowpayments_request('/invoice', 'POST', data)
        
        return {
            'invoice_id': response.get('id'),
            'payment_url': response.get('invoice_url'),
            'address': response.get('pay_address'),
            'amount': response.get('pay_amount'),
            'currency': response.get('pay_currency'),
            'status': 'pending',
            'expires_at': response.get('created_at'),  # Add expiry logic
            'provider': 'nowpayments'
        }
    
    async def _create_btcpay_invoice(self, amount: float, currency: str, order_id: str, description: str) -> Dict[str, Any]:
        """Create invoice using BTCPay Server"""
        data = {
            'amount': amount,
            'currency': 'USD',
            'orderId': order_id,
            'itemDesc': description or f'Subscription payment - {order_id}',
            'notificationURL': f'https://your-domain.com/api/payments/btcpay-callback',
            'redirectURL': f'https://your-domain.com/payment/success'
        }
        
        response = await self._make_btcpay_request('/api/v1/invoices', 'POST', data)
        
        return {
            'invoice_id': response.get('id'),
            'payment_url': response.get('url'),
            'address': response.get('addresses', {}).get(currency.upper()),
            'amount': response.get('cryptoInfo', [{}])[0].get('cryptoAmount'),
            'currency': currency.upper(),
            'status': 'pending',
            'expires_at': response.get('expirationTime'),
            'provider': 'btcpay'
        }
    
    async def _create_manual_invoice(self, amount: float, currency: str, order_id: str, description: str) -> Dict[str, Any]:
        """Create manual payment invoice"""
        
        # Get appropriate wallet address
        address = self.wallet_addresses.get(currency.upper())
        if not address:
            # Default to USDT TRC20 if currency not supported
            address = self.wallet_addresses['USDT_TRC20']
            currency = 'USDT_TRC20'
        
        # Generate unique invoice ID
        invoice_id = f"manual_{uuid.uuid4().hex[:8]}"
        
        # Calculate expiry (24 hours from now)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        return {
            'invoice_id': invoice_id,
            'payment_url': None,  # No payment URL for manual payments
            'address': address,
            'amount': amount,
            'currency': currency.upper(),
            'status': 'pending',
            'expires_at': expires_at,
            'provider': 'manual',
            'instructions': {
                'ar': f'قم بإرسال {amount} {currency.upper()} إلى العنوان التالي',
                'en': f'Send {amount} {currency.upper()} to the following address'
            }
        }
    
    async def check_payment_status(self, invoice_id: str, provider: str = None) -> Dict[str, Any]:
        """Check payment status"""
        try:
            if provider == 'nowpayments' and self.nowpayments_api_key:
                return await self._check_nowpayments_status(invoice_id)
            
            elif provider == 'btcpay' and self.btcpay_api_key:
                return await self._check_btcpay_status(invoice_id)
            
            else:
                # Manual payment - would need blockchain verification
                return await self._check_manual_payment_status(invoice_id)
                
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    async def _check_nowpayments_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check NowPayments invoice status"""
        response = await self._make_nowpayments_request(f'/invoice/{invoice_id}')
        
        # Map NowPayments status to our status
        status_map = {
            'waiting': 'pending',
            'confirming': 'confirming',
            'confirmed': 'confirmed',
            'sending': 'confirmed',
            'partially_paid': 'partial',
            'finished': 'completed',
            'failed': 'failed',
            'refunded': 'refunded',
            'expired': 'expired'
        }
        
        nowpayments_status = response.get('payment_status', 'waiting')
        our_status = status_map.get(nowpayments_status, 'unknown')
        
        return {
            'status': our_status,
            'amount_paid': response.get('actually_paid'),
            'amount_expected': response.get('pay_amount'),
            'currency': response.get('pay_currency'),
            'transaction_id': response.get('payment_id'),
            'confirmations': response.get('network_fee'),
            'provider': 'nowpayments'
        }
    
    async def _check_btcpay_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check BTCPay Server invoice status"""
        response = await self._make_btcpay_request(f'/api/v1/invoices/{invoice_id}')
        
        # Map BTCPay status to our status
        status_map = {
            'New': 'pending',
            'Paid': 'confirming',
            'Confirmed': 'confirmed',
            'Complete': 'completed',
            'Expired': 'expired',
            'Invalid': 'failed'
        }
        
        btcpay_status = response.get('status', 'New')
        our_status = status_map.get(btcpay_status, 'unknown')
        
        return {
            'status': our_status,
            'amount_paid': response.get('price'),
            'amount_expected': response.get('price'),
            'currency': response.get('currency'),
            'transaction_id': response.get('id'),
            'provider': 'btcpay'
        }
    
    async def _check_manual_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check manual payment status (placeholder)"""
        # In a real implementation, this would check blockchain transactions
        # For now, return pending status
        return {
            'status': 'pending',
            'amount_paid': 0,
            'amount_expected': 0,
            'currency': 'USDT',
            'transaction_id': None,
            'provider': 'manual',
            'note': 'Manual verification required'
        }
    
    async def get_supported_currencies(self) -> List[Dict[str, Any]]:
        """Get list of supported payment currencies"""
        try:
            if self.nowpayments_api_key:
                response = await self._make_nowpayments_request('/currencies')
                return [
                    {
                        'currency': currency,
                        'name': currency,
                        'network': 'auto',
                        'min_amount': 0.001
                    }
                    for currency in response.get('currencies', [])
                ]
            else:
                # Return manual payment currencies
                return [
                    {
                        'currency': 'BTC',
                        'name': 'Bitcoin',
                        'network': 'BTC',
                        'min_amount': 0.0001
                    },
                    {
                        'currency': 'USDT',
                        'name': 'Tether (TRC20)',
                        'network': 'TRC20',
                        'min_amount': 1.0
                    },
                    {
                        'currency': 'USDT',
                        'name': 'Tether (ERC20)',
                        'network': 'ERC20',
                        'min_amount': 1.0
                    }
                ]
                
        except Exception as e:
            logger.error(f"Error fetching supported currencies: {e}")
            return []
    
    async def estimate_network_fee(self, currency: str, amount: float) -> Dict[str, Any]:
        """Estimate network fee for transaction"""
        try:
            if self.nowpayments_api_key:
                params = {
                    'amount': amount,
                    'currency_from': 'USD',
                    'currency_to': currency.upper()
                }
                response = await self._make_nowpayments_request('/estimate', 'GET')
                
                return {
                    'estimated_amount': response.get('estimated_amount'),
                    'currency': currency.upper(),
                    'network_fee': response.get('network_fee', 0),
                    'service_fee': response.get('service_fee', 0)
                }
            else:
                # Return estimated fees for manual payments
                fee_estimates = {
                    'BTC': amount * 0.001,  # 0.1% fee
                    'USDT_TRC20': 1.0,      # Fixed 1 USDT fee
                    'USDT_ERC20': 5.0       # Fixed 5 USDT fee
                }
                
                return {
                    'estimated_amount': amount,
                    'currency': currency.upper(),
                    'network_fee': fee_estimates.get(currency.upper(), 0),
                    'service_fee': 0
                }
                
        except Exception as e:
            logger.error(f"Error estimating network fee: {e}")
            return {
                'estimated_amount': amount,
                'currency': currency.upper(),
                'network_fee': 0,
                'service_fee': 0
            }
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

