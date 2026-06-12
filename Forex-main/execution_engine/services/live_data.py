"""Live Market Data Service."""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class LiveMarketDataService:
    """
    Fetch live market data from various sources.
    
    In production, this would connect to:
    - Investing.com
    - TradingView
    - Broker APIs
    - ForexFactory
    """
    
    # Base prices for simulation
    BASE_PRICES = {
        'XAUUSD': 2650.00,
        'XAGUSD': 31.50,
        'EURUSD': 1.0850,
        'GBPUSD': 1.2750,
        'USDJPY': 149.50,
        'GBPJPY': 190.50,
        'AUDUSD': 0.6550,
        'USDCAD': 1.3650,
        'USDCHF': 0.8850,
        'EURJPY': 162.20,
        'EURGBP': 0.8510,
        'NZDUSD': 0.5950,
    }
    
    # Intermarket assets
    INTERMARKET = {
        'DXY': 104.50,
        'US10Y': 4.25,
        'VIX': 18.50,
        'WTI': 78.50,
        'COPPER': 4.15,
        'SPX': 5250.00,
        'NDX': 18500.00,
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_time = None
        self.cache_duration = timedelta(seconds=30)
    
    def fetch_all_data(self, pair: str) -> Dict[str, Any]:
        """
        Fetch all live data for a currency pair.
        
        Args:
            pair: Currency pair symbol (e.g., 'XAUUSD')
            
        Returns:
            Dictionary containing all live market data
        """
        pair = pair.upper().replace('/', '')
        
        return {
            'pair': pair,
            'timestamp': datetime.utcnow().isoformat(),
            'price_data': self.fetch_price_data(pair),
            'technical_data': self.fetch_technical_data(pair),
            'intermarket': self.fetch_intermarket_data(),
            'session': self._get_current_session(),
        }
    
    def fetch_price_data(self, pair: str) -> Dict[str, Any]:
        """Fetch current price data."""
        base_price = self.BASE_PRICES.get(pair, 1.0)
        variance = base_price * 0.002
        
        current = base_price + random.uniform(-variance, variance)
        daily_range = base_price * 0.01
        
        high = current + random.uniform(0, daily_range / 2)
        low = current - random.uniform(0, daily_range / 2)
        
        prev_close = base_price + random.uniform(-variance, variance)
        day_change = ((current - prev_close) / prev_close) * 100
        
        week_open = base_price * (1 + random.uniform(-0.02, 0.02))
        week_change = ((current - week_open) / week_open) * 100
        
        decimals = 2 if base_price > 10 else 5
        
        return {
            'current': round(current, decimals),
            'bid': round(current - 0.0001 * base_price, decimals),
            'ask': round(current + 0.0001 * base_price, decimals),
            'high': round(high, decimals),
            'low': round(low, decimals),
            'open': round(prev_close, decimals),
            'prev_close': round(prev_close, decimals),
            'day_change_pct': round(day_change, 2),
            'week_change_pct': round(week_change, 2),
            'spread': round(0.0002 * base_price, decimals),
        }
    
    def fetch_technical_data(self, pair: str) -> Dict[str, Any]:
        """Fetch technical indicators."""
        base_price = self.BASE_PRICES.get(pair, 1.0)
        decimals = 2 if base_price > 10 else 5
        
        # RSI
        rsi = random.uniform(30, 70)
        if random.random() < 0.2:
            rsi = random.choice([random.uniform(20, 35), random.uniform(65, 80)])
        
        # MACD
        macd_value = random.uniform(-0.002, 0.002) * base_price
        macd_signal = macd_value + random.uniform(-0.001, 0.001) * base_price
        macd_histogram = macd_value - macd_signal
        
        # ADX
        adx = random.uniform(15, 45)
        
        # EMAs
        ema_20 = base_price * (1 + random.uniform(-0.005, 0.005))
        ema_50 = base_price * (1 + random.uniform(-0.01, 0.01))
        ema_200 = base_price * (1 + random.uniform(-0.02, 0.02))
        
        # Pivot points
        pivot = base_price
        s1 = pivot - (base_price * 0.005)
        s2 = pivot - (base_price * 0.01)
        s3 = pivot - (base_price * 0.015)
        r1 = pivot + (base_price * 0.005)
        r2 = pivot + (base_price * 0.01)
        r3 = pivot + (base_price * 0.015)
        
        # Technical consensus
        consensus_options = ['STRONG BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG SELL']
        consensus = random.choice(consensus_options)
        
        return {
            'rsi': {
                'value': round(rsi, 2),
                'signal': 'OVERBOUGHT' if rsi > 70 else 'OVERSOLD' if rsi < 30 else 'NEUTRAL',
            },
            'macd': {
                'value': round(macd_value, 6),
                'signal': round(macd_signal, 6),
                'histogram': round(macd_histogram, 6),
                'trend': 'BULLISH' if macd_histogram > 0 else 'BEARISH',
            },
            'adx': {
                'value': round(adx, 2),
                'trend_strength': 'STRONG' if adx > 25 else 'WEAK',
            },
            'ema': {
                'ema_20': round(ema_20, decimals),
                'ema_50': round(ema_50, decimals),
                'ema_200': round(ema_200, decimals),
            },
            'pivots': {
                'S3': round(s3, decimals),
                'S2': round(s2, decimals),
                'S1': round(s1, decimals),
                'P': round(pivot, decimals),
                'R1': round(r1, decimals),
                'R2': round(r2, decimals),
                'R3': round(r3, decimals),
            },
            'consensus': consensus,
        }
    
    def fetch_intermarket_data(self) -> Dict[str, Any]:
        """Fetch intermarket data (DXY, yields, VIX, etc.)."""
        data = {}
        
        for asset, base in self.INTERMARKET.items():
            variance = base * 0.005
            current = base + random.uniform(-variance, variance)
            change = random.uniform(-1.5, 1.5)
            
            data[asset] = {
                'price': round(current, 2),
                'change_pct': round(change, 2),
                'trend': 'UP' if change > 0.3 else 'DOWN' if change < -0.3 else 'FLAT',
            }
        
        # Determine risk sentiment based on VIX
        vix = data['VIX']['price']
        if vix > 25:
            risk_sentiment = 'RISK_OFF'
        elif vix < 15:
            risk_sentiment = 'RISK_ON'
        else:
            risk_sentiment = 'NEUTRAL'
        
        data['risk_sentiment'] = risk_sentiment
        
        return data
    
    def _get_current_session(self) -> Dict[str, Any]:
        """Determine current trading session."""
        now = datetime.utcnow()
        hour = now.hour
        
        # Session times (UTC)
        sessions = {
            'SYDNEY': (21, 6),      # 21:00 - 06:00 UTC
            'TOKYO': (0, 9),        # 00:00 - 09:00 UTC
            'LONDON': (7, 16),      # 07:00 - 16:00 UTC
            'NEW_YORK': (12, 21),   # 12:00 - 21:00 UTC
        }
        
        active_sessions = []
        
        for session, (start, end) in sessions.items():
            if start <= end:
                if start <= hour < end:
                    active_sessions.append(session)
            else:  # Crosses midnight
                if hour >= start or hour < end:
                    active_sessions.append(session)
        
        # Check for overlap
        is_overlap = 'LONDON' in active_sessions and 'NEW_YORK' in active_sessions
        
        # Kill zones
        london_kz = 7 <= hour <= 10
        ny_kz = 12 <= hour <= 15
        
        return {
            'current_time_utc': now.strftime('%H:%M:%S'),
            'active_sessions': active_sessions,
            'is_overlap': is_overlap,
            'london_kill_zone': london_kz,
            'ny_kill_zone': ny_kz,
            'is_kill_zone': london_kz or ny_kz,
            'session_quality': 'HIGH' if is_overlap else 'MEDIUM' if active_sessions else 'LOW',
        }
