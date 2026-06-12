"""Data fetching service for market data."""
import random
from datetime import datetime, date
from flask import current_app

from backend import db
from backend.models import CurrencyPair, PriceData, COTData


class DataFetcher:
    """
    Fetch market data from external sources.
    
    Note: In production, this would connect to real data APIs.
    For demonstration, we generate realistic sample data.
    """
    
    # Base prices for each pair (approximate market values)
    BASE_PRICES = {
        'XAU/USD': 2650.00,
        'XAG/USD': 31.50,
        'EUR/USD': 1.0850,
        'GBP/USD': 1.2750,
        'USD/JPY': 149.50,
        'GBP/JPY': 190.50,
        'AUD/USD': 0.6550,
        'USD/CAD': 1.3650,
        'USD/CHF': 0.8850,
        'EUR/JPY': 162.20,
        'EUR/GBP': 0.8510,
        'NZD/USD': 0.5950,
    }
    
    def __init__(self):
        self.pairs = {}
    
    def _get_pair(self, symbol):
        """Get or cache currency pair."""
        if symbol not in self.pairs:
            self.pairs[symbol] = CurrencyPair.query.filter_by(symbol=symbol).first()
        return self.pairs[symbol]
    
    def _generate_price_data(self, symbol):
        """
        Generate realistic price data for a symbol.
        
        In production, this would fetch from:
        - Investing.com API
        - TradingView
        - Broker APIs (OANDA, etc.)
        """
        base_price = self.BASE_PRICES.get(symbol, 1.0)
        
        # Add some randomness to simulate market movement
        variance = base_price * 0.002  # 0.2% variance
        current_price = base_price + random.uniform(-variance, variance)
        
        # Calculate daily range
        daily_range = base_price * 0.008  # 0.8% daily range
        high = current_price + random.uniform(0, daily_range / 2)
        low = current_price - random.uniform(0, daily_range / 2)
        
        # Technical indicators
        rsi = random.uniform(30, 70)  # RSI between 30-70 normally
        if random.random() < 0.2:  # 20% chance of extreme RSI
            rsi = random.choice([random.uniform(20, 35), random.uniform(65, 80)])
        
        # MACD
        macd_value = random.uniform(-0.002, 0.002) * base_price
        macd_signal = macd_value + random.uniform(-0.001, 0.001) * base_price
        macd_histogram = macd_value - macd_signal
        
        # EMAs
        ema_50 = base_price * (1 + random.uniform(-0.01, 0.01))
        ema_200 = base_price * (1 + random.uniform(-0.02, 0.02))
        
        # Pivot points
        pivot = (high + low + current_price) / 3
        support_1 = 2 * pivot - high
        support_2 = pivot - (high - low)
        resistance_1 = 2 * pivot - low
        resistance_2 = pivot + (high - low)
        
        # MA consensus
        consensus_options = ['STRONG BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG SELL']
        ma_consensus = random.choice(consensus_options)
        
        return {
            'bid': round(current_price, 5 if base_price < 10 else 2),
            'ask': round(current_price * 1.0001, 5 if base_price < 10 else 2),
            'high': round(high, 5 if base_price < 10 else 2),
            'low': round(low, 5 if base_price < 10 else 2),
            'open_price': round(base_price, 5 if base_price < 10 else 2),
            'close_price': round(current_price, 5 if base_price < 10 else 2),
            'rsi_14': round(rsi, 2),
            'macd_value': round(macd_value, 6),
            'macd_signal': round(macd_signal, 6),
            'macd_histogram': round(macd_histogram, 6),
            'ema_50': round(ema_50, 5 if base_price < 10 else 2),
            'ema_200': round(ema_200, 5 if base_price < 10 else 2),
            'pivot': round(pivot, 5 if base_price < 10 else 2),
            'support_1': round(support_1, 5 if base_price < 10 else 2),
            'support_2': round(support_2, 5 if base_price < 10 else 2),
            'resistance_1': round(resistance_1, 5 if base_price < 10 else 2),
            'resistance_2': round(resistance_2, 5 if base_price < 10 else 2),
            'ma_consensus': ma_consensus,
        }
    
    def _generate_cot_data(self, symbol):
        """
        Generate realistic COT data for a symbol.
        
        In production, this would fetch from:
        - Tradingster.com
        - CFTC website
        - Quandl
        """
        # Generate realistic contract numbers
        base_contracts = random.randint(50000, 300000)
        
        nc_long = base_contracts + random.randint(-20000, 20000)
        nc_short = base_contracts + random.randint(-20000, 20000)
        nc_net = nc_long - nc_short
        
        comm_long = base_contracts + random.randint(-30000, 30000)
        comm_short = base_contracts + random.randint(-30000, 30000)
        comm_net = comm_long - comm_short
        
        nc_net_change = random.randint(-15000, 15000)
        
        # Determine bias
        if nc_net > 10000:
            cot_bias = 'BULLISH'
        elif nc_net < -10000:
            cot_bias = 'BEARISH'
        else:
            cot_bias = 'NEUTRAL'
        
        return {
            'nc_long': nc_long,
            'nc_short': nc_short,
            'nc_net': nc_net,
            'comm_long': comm_long,
            'comm_short': comm_short,
            'comm_net': comm_net,
            'nc_net_change': nc_net_change,
            'cot_bias': cot_bias,
            'report_date': date.today(),
        }
    
    def fetch_price_data(self, symbol):
        """Fetch and store price data for a symbol."""
        pair = self._get_pair(symbol)
        if not pair:
            return None
        
        data = self._generate_price_data(symbol)
        
        price_data = PriceData(
            pair_id=pair.id,
            timestamp=datetime.utcnow(),
            timeframe='D1',
            **data
        )
        
        db.session.add(price_data)
        return price_data
    
    def fetch_cot_data(self, symbol):
        """Fetch and store COT data for a symbol."""
        pair = self._get_pair(symbol)
        if not pair:
            return None
        
        data = self._generate_cot_data(symbol)
        
        cot_data = COTData(
            pair_id=pair.id,
            **data
        )
        
        db.session.add(cot_data)
        return cot_data
    
    def fetch_all_data(self):
        """Fetch data for all active currency pairs."""
        pairs = CurrencyPair.query.filter_by(is_active=True).all()
        
        for pair in pairs:
            self.fetch_price_data(pair.symbol)
            self.fetch_cot_data(pair.symbol)
        
        db.session.commit()
        return len(pairs)
