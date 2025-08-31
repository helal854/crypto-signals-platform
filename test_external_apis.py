"""
Test external API integrations
"""

import asyncio
import sys
import os

# Add the backend src directory to Python path
sys.path.append('/home/ubuntu/crypto-signals-platform/backend/crypto_signals_api/src')

from services.binance_service import BinanceService
from services.coingecko_service import CoinGeckoService
from services.fear_greed_service import FearGreedService
from services.trading_economics_service import TradingEconomicsService
from services.payment_service import PaymentService
from services.blockchain_service import BlockchainService

async def test_binance_service():
    """Test Binance API service"""
    print("🔸 Testing Binance Service...")
    
    try:
        async with BinanceService() as binance:
            # Test price fetching
            btc_price = await binance.get_symbol_price('BTCUSDT')
            print(f"   ✅ BTC Price: ${btc_price.get('price', 'N/A')}")
            
            # Test support/resistance calculation
            sr_data = await binance.calculate_support_resistance('BTCUSDT')
            print(f"   ✅ Support/Resistance calculated for BTC")
            
            # Test top symbols
            top_symbols = await binance.get_top_symbols(5)
            print(f"   ✅ Top 5 symbols fetched: {len(top_symbols)} symbols")
            
            # Test futures leaderboard (mock)
            leaderboard = await binance.get_futures_leaderboard()
            print(f"   ✅ Futures leaderboard: {len(leaderboard)} traders")
            
    except Exception as e:
        print(f"   ❌ Binance Service Error: {e}")

async def test_coingecko_service():
    """Test CoinGecko API service"""
    print("🔸 Testing CoinGecko Service...")
    
    try:
        async with CoinGeckoService() as coingecko:
            # Test price fetching
            prices = await coingecko.get_coin_price(['bitcoin', 'ethereum'])
            print(f"   ✅ Crypto prices fetched: {len(prices)} coins")
            
            # Test top cryptocurrencies
            top_cryptos = await coingecko.get_top_cryptocurrencies(10)
            print(f"   ✅ Top cryptocurrencies: {len(top_cryptos)} coins")
            
            # Test market data
            market_data = await coingecko.get_market_data()
            print(f"   ✅ Global market data fetched")
            
            # Test formatted prices
            formatted = await coingecko.format_crypto_prices()
            print(f"   ✅ Formatted prices: {len(formatted)} coins")
            
    except Exception as e:
        print(f"   ❌ CoinGecko Service Error: {e}")

async def test_fear_greed_service():
    """Test Fear & Greed Index service"""
    print("🔸 Testing Fear & Greed Service...")
    
    try:
        async with FearGreedService() as fg:
            # Test current index
            current = await fg.get_current_index()
            print(f"   ✅ Current F&G Index: {current.get('value', 'N/A')} ({current.get('value_classification', 'N/A')})")
            
            # Test historical data
            historical = await fg.get_historical_index(7)
            print(f"   ✅ Historical data: {len(historical)} days")
            
            # Test trend analysis
            trend = await fg.get_index_trend()
            print(f"   ✅ Trend analysis: {trend.get('trend', 'N/A')}")
            
            # Test formatted index
            formatted = await fg.get_formatted_index()
            print(f"   ✅ Formatted index with Arabic classification")
            
    except Exception as e:
        print(f"   ❌ Fear & Greed Service Error: {e}")

async def test_trading_economics_service():
    """Test TradingEconomics service"""
    print("🔸 Testing TradingEconomics Service...")
    
    try:
        async with TradingEconomicsService() as te:
            # Test economic calendar
            calendar = await te.get_economic_calendar(7)
            print(f"   ✅ Economic calendar: {len(calendar)} events")
            
            # Test formatted calendar
            formatted = await te.get_formatted_calendar(7)
            print(f"   ✅ Formatted calendar: {len(formatted)} events")
            
            # Test country indicators
            indicators = await te.get_country_indicators('united-states')
            print(f"   ✅ US indicators: {len(indicators)} indicators")
            
    except Exception as e:
        print(f"   ❌ TradingEconomics Service Error: {e}")

async def test_payment_service():
    """Test Payment service"""
    print("🔸 Testing Payment Service...")
    
    try:
        async with PaymentService() as payment:
            # Test supported currencies
            currencies = await payment.get_supported_currencies()
            print(f"   ✅ Supported currencies: {len(currencies)} currencies")
            
            # Test invoice creation (manual)
            invoice = await payment.create_payment_invoice(
                amount=50.0,
                currency='USDT',
                order_id='test_order_123',
                description='Test subscription'
            )
            print(f"   ✅ Invoice created: {invoice.get('invoice_id', 'N/A')}")
            
            # Test fee estimation
            fee = await payment.estimate_network_fee('USDT', 50.0)
            print(f"   ✅ Network fee estimated: {fee.get('network_fee', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ Payment Service Error: {e}")

async def test_blockchain_service():
    """Test Blockchain service"""
    print("🔸 Testing Blockchain Service...")
    
    try:
        async with BlockchainService() as blockchain:
            # Test BTC balance (example address)
            btc_balance = await blockchain.get_address_balance(
                'BTC', 
                '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'  # Genesis block address
            )
            print(f"   ✅ BTC balance check completed")
            
            # Test USDT TRC20 balance
            usdt_balance = await blockchain.get_address_balance(
                'USDT', 
                'TJkLFH53mJUzaTMxLtYqa28jzL9CppJotV',
                'TRC20'
            )
            print(f"   ✅ USDT TRC20 balance check completed")
            
    except Exception as e:
        print(f"   ❌ Blockchain Service Error: {e}")

async def main():
    """Run all tests"""
    print("🧪 Starting External API Integration Tests...\n")
    
    await test_binance_service()
    print()
    
    await test_coingecko_service()
    print()
    
    await test_fear_greed_service()
    print()
    
    await test_trading_economics_service()
    print()
    
    await test_payment_service()
    print()
    
    await test_blockchain_service()
    print()
    
    print("✅ All API integration tests completed!")

if __name__ == "__main__":
    asyncio.run(main())

