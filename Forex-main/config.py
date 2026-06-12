"""Application configuration settings."""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///forex_signals.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Data refresh interval (minutes)
    DATA_REFRESH_INTERVAL = 15
    
    # Supported currency pairs
    CURRENCY_PAIRS = [
        'XAU/USD',  # Gold
        'XAG/USD',  # Silver
        'EUR/USD',
        'GBP/USD',
        'USD/JPY',
        'GBP/JPY',
        'AUD/USD',
        'USD/CAD',
        'USD/CHF',
        'EUR/JPY',
        'EUR/GBP',
        'NZD/USD',
    ]
    
    # COT data mapping (CFTC codes)
    COT_CODES = {
        'XAU/USD': '088691',
        'XAG/USD': '084691',
        'EUR/USD': '099741',
        'GBP/USD': '096742',
        'USD/JPY': '097741',
        'AUD/USD': '232741',
        'USD/CAD': '090741',
        'USD/CHF': '092741',
        'NZD/USD': '112741',
        'USD_INDEX': '098662',
    }
    
    # Signal scoring weights
    SCORING_WEIGHTS = {
        'cot_bearish': 2,
        'rsi_extreme': 2,
        'macd_bearish': 1,
        'below_50_ema': 1,
        'below_200_ema': 1,
        'technical_sell': 1,
        'near_resistance': 1,
        'weekly_downtrend': 1,
    }
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 8
    MEDIUM_CONFIDENCE_THRESHOLD = 5


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Use Redis for caching in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
