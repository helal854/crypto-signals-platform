"""
Blockchain service for payment verification
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for blockchain transaction verification"""
    
    def __init__(self, tron_api_key: str = None):
        self.tron_api_key = tron_api_key or "45837786-0cb2-4cb7-a5c4-323c21b5070d"
        self.session = None
        
        # API endpoints
        self.endpoints = {
            'btc': 'https://blockstream.info/api',
            'eth': 'https://api.etherscan.io/api',
            'tron': 'https://api.trongrid.io',
            'bsc': 'https://api.bscscan.com/api'
        }
        
        # Contract addresses for USDT
        self.usdt_contracts = {
            'eth': '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT ERC20
            'tron': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',      # USDT TRC20
            'bsc': '0x55d398326f99059fF775485246999027B3197955'    # USDT BEP20
        }
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Any:
        """Make HTTP request"""
        session = await self._get_session()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Blockchain API error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Blockchain API request failed: {e}")
            return None
    
    async def verify_btc_payment(self, address: str, amount: float, min_confirmations: int = 1) -> Dict[str, Any]:
        """Verify Bitcoin payment"""
        try:
            url = f"{self.endpoints['btc']}/address/{address}/txs"
            transactions = await self._make_request(url)
            
            if not transactions:
                return {'verified': False, 'error': 'Failed to fetch transactions'}
            
            for tx in transactions:
                # Check outputs for payments to our address
                for output in tx.get('vout', []):
                    if output.get('scriptpubkey_address') == address:
                        received_amount = output.get('value', 0) / 100000000  # Convert satoshis to BTC
                        confirmations = tx.get('status', {}).get('confirmed', False)
                        
                        if received_amount >= amount and confirmations:
                            return {
                                'verified': True,
                                'transaction_id': tx.get('txid'),
                                'amount': received_amount,
                                'confirmations': 1 if confirmations else 0,
                                'block_height': tx.get('status', {}).get('block_height')
                            }
            
            return {'verified': False, 'reason': 'Payment not found or insufficient amount'}
            
        except Exception as e:
            logger.error(f"Error verifying BTC payment: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def verify_eth_usdt_payment(self, address: str, amount: float, etherscan_api_key: str = None) -> Dict[str, Any]:
        """Verify USDT ERC20 payment"""
        try:
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': self.usdt_contracts['eth'],
                'address': address,
                'page': 1,
                'offset': 100,
                'sort': 'desc'
            }
            
            if etherscan_api_key:
                params['apikey'] = etherscan_api_key
            
            url = self.endpoints['eth']
            response = await self._make_request(url, params)
            
            if not response or response.get('status') != '1':
                return {'verified': False, 'error': 'Failed to fetch transactions'}
            
            transactions = response.get('result', [])
            
            for tx in transactions:
                if tx.get('to').lower() == address.lower():
                    received_amount = float(tx.get('value', 0)) / 1000000  # USDT has 6 decimals
                    confirmations = int(tx.get('confirmations', 0))
                    
                    if received_amount >= amount and confirmations >= 1:
                        return {
                            'verified': True,
                            'transaction_id': tx.get('hash'),
                            'amount': received_amount,
                            'confirmations': confirmations,
                            'block_number': tx.get('blockNumber')
                        }
            
            return {'verified': False, 'reason': 'Payment not found or insufficient amount'}
            
        except Exception as e:
            logger.error(f"Error verifying ETH USDT payment: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def verify_tron_usdt_payment(self, address: str, amount: float) -> Dict[str, Any]:
        """Verify USDT TRC20 payment"""
        try:
            headers = {'TRON-PRO-API-KEY': self.tron_api_key} if self.tron_api_key else {}
            
            # Get TRC20 transactions
            url = f"{self.endpoints['tron']}/v1/accounts/{address}/transactions/trc20"
            params = {
                'limit': 50,
                'contract_address': self.usdt_contracts['tron']
            }
            
            response = await self._make_request(url, params, headers)
            
            if not response or not response.get('success'):
                return {'verified': False, 'error': 'Failed to fetch transactions'}
            
            transactions = response.get('data', [])
            
            for tx in transactions:
                if tx.get('to') == address:
                    received_amount = float(tx.get('value', 0)) / 1000000  # USDT has 6 decimals
                    
                    # Check if transaction is confirmed
                    tx_info = await self._get_tron_transaction_info(tx.get('transaction_id'))
                    confirmed = tx_info.get('confirmed', False) if tx_info else False
                    
                    if received_amount >= amount and confirmed:
                        return {
                            'verified': True,
                            'transaction_id': tx.get('transaction_id'),
                            'amount': received_amount,
                            'confirmations': 1 if confirmed else 0,
                            'block_number': tx.get('block_number')
                        }
            
            return {'verified': False, 'reason': 'Payment not found or insufficient amount'}
            
        except Exception as e:
            logger.error(f"Error verifying TRON USDT payment: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def _get_tron_transaction_info(self, tx_id: str) -> Dict[str, Any]:
        """Get TRON transaction information"""
        try:
            headers = {'TRON-PRO-API-KEY': self.tron_api_key} if self.tron_api_key else {}
            url = f"{self.endpoints['tron']}/wallet/gettransactionbyid"
            
            data = {'value': tx_id}
            session = await self._get_session()
            
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'confirmed': 'blockNumber' in result,
                        'block_number': result.get('blockNumber'),
                        'energy_used': result.get('receipt', {}).get('energy_usage_total', 0)
                    }
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting TRON transaction info: {e}")
            return {}
    
    async def verify_bsc_usdt_payment(self, address: str, amount: float, bscscan_api_key: str = None) -> Dict[str, Any]:
        """Verify USDT BEP20 payment"""
        try:
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': self.usdt_contracts['bsc'],
                'address': address,
                'page': 1,
                'offset': 100,
                'sort': 'desc'
            }
            
            if bscscan_api_key:
                params['apikey'] = bscscan_api_key
            
            url = self.endpoints['bsc']
            response = await self._make_request(url, params)
            
            if not response or response.get('status') != '1':
                return {'verified': False, 'error': 'Failed to fetch transactions'}
            
            transactions = response.get('result', [])
            
            for tx in transactions:
                if tx.get('to').lower() == address.lower():
                    received_amount = float(tx.get('value', 0)) / 1000000000000000000  # 18 decimals for BEP20 USDT
                    confirmations = int(tx.get('confirmations', 0))
                    
                    if received_amount >= amount and confirmations >= 1:
                        return {
                            'verified': True,
                            'transaction_id': tx.get('hash'),
                            'amount': received_amount,
                            'confirmations': confirmations,
                            'block_number': tx.get('blockNumber')
                        }
            
            return {'verified': False, 'reason': 'Payment not found or insufficient amount'}
            
        except Exception as e:
            logger.error(f"Error verifying BSC USDT payment: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def verify_payment(self, currency: str, address: str, amount: float, network: str = None) -> Dict[str, Any]:
        """Verify payment based on currency and network"""
        try:
            currency = currency.upper()
            
            if currency == 'BTC':
                return await self.verify_btc_payment(address, amount)
            
            elif currency == 'USDT':
                if network == 'TRC20' or 'TRC20' in currency:
                    return await self.verify_tron_usdt_payment(address, amount)
                elif network == 'ERC20' or 'ERC20' in currency:
                    return await self.verify_eth_usdt_payment(address, amount)
                elif network == 'BEP20' or 'BEP20' in currency:
                    return await self.verify_bsc_usdt_payment(address, amount)
                else:
                    # Default to TRC20 for USDT
                    return await self.verify_tron_usdt_payment(address, amount)
            
            else:
                return {'verified': False, 'error': f'Unsupported currency: {currency}'}
                
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def get_address_balance(self, currency: str, address: str, network: str = None) -> Dict[str, Any]:
        """Get address balance"""
        try:
            currency = currency.upper()
            
            if currency == 'BTC':
                return await self._get_btc_balance(address)
            
            elif currency == 'USDT':
                if network == 'TRC20':
                    return await self._get_tron_usdt_balance(address)
                elif network == 'ERC20':
                    return await self._get_eth_usdt_balance(address)
                elif network == 'BEP20':
                    return await self._get_bsc_usdt_balance(address)
                else:
                    return await self._get_tron_usdt_balance(address)
            
            else:
                return {'balance': 0, 'error': f'Unsupported currency: {currency}'}
                
        except Exception as e:
            logger.error(f"Error getting address balance: {e}")
            return {'balance': 0, 'error': str(e)}
    
    async def _get_btc_balance(self, address: str) -> Dict[str, Any]:
        """Get Bitcoin address balance"""
        try:
            url = f"{self.endpoints['btc']}/address/{address}"
            response = await self._make_request(url)
            
            if response:
                balance = response.get('chain_stats', {}).get('funded_txo_sum', 0) / 100000000
                return {'balance': balance, 'currency': 'BTC'}
            else:
                return {'balance': 0, 'error': 'Failed to fetch balance'}
                
        except Exception as e:
            return {'balance': 0, 'error': str(e)}
    
    async def _get_tron_usdt_balance(self, address: str) -> Dict[str, Any]:
        """Get TRON USDT balance"""
        try:
            headers = {'TRON-PRO-API-KEY': self.tron_api_key} if self.tron_api_key else {}
            url = f"{self.endpoints['tron']}/v1/accounts/{address}/transactions/trc20"
            
            params = {
                'limit': 1,
                'contract_address': self.usdt_contracts['tron']
            }
            
            response = await self._make_request(url, params, headers)
            
            if response and response.get('success'):
                # This is a simplified balance check - in production, you'd calculate from all transactions
                return {'balance': 0, 'currency': 'USDT_TRC20', 'note': 'Balance calculation requires full transaction history'}
            else:
                return {'balance': 0, 'error': 'Failed to fetch balance'}
                
        except Exception as e:
            return {'balance': 0, 'error': str(e)}
    
    async def _get_eth_usdt_balance(self, address: str) -> Dict[str, Any]:
        """Get Ethereum USDT balance"""
        try:
            params = {
                'module': 'account',
                'action': 'tokenbalance',
                'contractaddress': self.usdt_contracts['eth'],
                'address': address,
                'tag': 'latest'
            }
            
            response = await self._make_request(self.endpoints['eth'], params)
            
            if response and response.get('status') == '1':
                balance = float(response.get('result', 0)) / 1000000  # USDT has 6 decimals
                return {'balance': balance, 'currency': 'USDT_ERC20'}
            else:
                return {'balance': 0, 'error': 'Failed to fetch balance'}
                
        except Exception as e:
            return {'balance': 0, 'error': str(e)}
    
    async def _get_bsc_usdt_balance(self, address: str) -> Dict[str, Any]:
        """Get BSC USDT balance"""
        try:
            params = {
                'module': 'account',
                'action': 'tokenbalance',
                'contractaddress': self.usdt_contracts['bsc'],
                'address': address,
                'tag': 'latest'
            }
            
            response = await self._make_request(self.endpoints['bsc'], params)
            
            if response and response.get('status') == '1':
                balance = float(response.get('result', 0)) / 1000000000000000000  # 18 decimals
                return {'balance': balance, 'currency': 'USDT_BEP20'}
            else:
                return {'balance': 0, 'error': 'Failed to fetch balance'}
                
        except Exception as e:
            return {'balance': 0, 'error': str(e)}
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

