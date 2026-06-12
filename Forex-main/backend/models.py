"""Database models for forex signal application."""
from datetime import datetime
from backend import db


class CurrencyPair(db.Model):
    """Currency pair model."""
    __tablename__ = 'currency_pairs'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(20), default='forex')  # forex, metal
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = db.relationship('PriceData', backref='pair', lazy='dynamic')
    signals = db.relationship('Signal', backref='pair', lazy='dynamic')
    cot_data = db.relationship('COTData', backref='pair', lazy='dynamic')
    
    def __repr__(self):
        return f'<CurrencyPair {self.symbol}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'category': self.category,
            'is_active': self.is_active,
        }


class PriceData(db.Model):
    """Price data model."""
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    pair_id = db.Column(db.Integer, db.ForeignKey('currency_pairs.id'), nullable=False)
    
    # Price data
    bid = db.Column(db.Float)
    ask = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    open_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    
    # Technical indicators
    rsi_14 = db.Column(db.Float)
    macd_value = db.Column(db.Float)
    macd_signal = db.Column(db.Float)
    macd_histogram = db.Column(db.Float)
    ema_50 = db.Column(db.Float)
    ema_200 = db.Column(db.Float)
    
    # Pivot points
    pivot = db.Column(db.Float)
    support_1 = db.Column(db.Float)
    support_2 = db.Column(db.Float)
    resistance_1 = db.Column(db.Float)
    resistance_2 = db.Column(db.Float)
    
    # Moving average consensus
    ma_consensus = db.Column(db.String(20))  # BUY, SELL, NEUTRAL
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    timeframe = db.Column(db.String(10), default='D1')  # M1, M5, H1, H4, D1, W1
    
    def __repr__(self):
        return f'<PriceData {self.pair_id} @ {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pair_id': self.pair_id,
            'bid': self.bid,
            'ask': self.ask,
            'high': self.high,
            'low': self.low,
            'rsi_14': self.rsi_14,
            'macd_value': self.macd_value,
            'macd_signal': self.macd_signal,
            'ema_50': self.ema_50,
            'ema_200': self.ema_200,
            'pivot': self.pivot,
            'support_1': self.support_1,
            'support_2': self.support_2,
            'resistance_1': self.resistance_1,
            'resistance_2': self.resistance_2,
            'ma_consensus': self.ma_consensus,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class COTData(db.Model):
    """Commitment of Traders data model."""
    __tablename__ = 'cot_data'
    
    id = db.Column(db.Integer, primary_key=True)
    pair_id = db.Column(db.Integer, db.ForeignKey('currency_pairs.id'), nullable=False)
    
    # Non-commercial positions
    nc_long = db.Column(db.Integer)
    nc_short = db.Column(db.Integer)
    nc_net = db.Column(db.Integer)  # Long - Short
    
    # Commercial positions
    comm_long = db.Column(db.Integer)
    comm_short = db.Column(db.Integer)
    comm_net = db.Column(db.Integer)
    
    # Changes
    nc_net_change = db.Column(db.Integer)  # Weekly change
    
    # Derived
    cot_bias = db.Column(db.String(10))  # BULLISH, BEARISH, NEUTRAL
    
    # Report date
    report_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<COTData {self.pair_id} @ {self.report_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pair_id': self.pair_id,
            'nc_long': self.nc_long,
            'nc_short': self.nc_short,
            'nc_net': self.nc_net,
            'comm_long': self.comm_long,
            'comm_short': self.comm_short,
            'comm_net': self.comm_net,
            'nc_net_change': self.nc_net_change,
            'cot_bias': self.cot_bias,
            'report_date': self.report_date.isoformat() if self.report_date else None,
        }


class Signal(db.Model):
    """Trading signal model."""
    __tablename__ = 'signals'
    
    id = db.Column(db.Integer, primary_key=True)
    pair_id = db.Column(db.Integer, db.ForeignKey('currency_pairs.id'), nullable=False)
    
    # Signal details
    direction = db.Column(db.String(10), nullable=False)  # BUY, SELL
    score = db.Column(db.Integer, default=0)  # 0-10
    confidence = db.Column(db.String(10))  # HIGH, MEDIUM, LOW
    
    # Trade levels
    entry_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    take_profit_1 = db.Column(db.Float)
    take_profit_2 = db.Column(db.Float)
    
    # Risk metrics
    risk_reward_ratio = db.Column(db.Float)
    risk_percent = db.Column(db.Float, default=1.0)
    
    # Timeframe and duration
    timeframe = db.Column(db.String(10), default='H4')
    estimated_duration = db.Column(db.String(20))  # e.g., "3-5 days"
    
    # Scoring breakdown
    score_breakdown = db.Column(db.JSON)  # Detailed scoring
    
    # Analysis
    analysis = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, closed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Signal {self.pair_id} {self.direction} Score:{self.score}>'
    
    def to_dict(self):
        pair = CurrencyPair.query.get(self.pair_id)
        return {
            'id': self.id,
            'pair_id': self.pair_id,
            'symbol': pair.symbol if pair else None,
            'direction': self.direction,
            'score': self.score,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit_1': self.take_profit_1,
            'take_profit_2': self.take_profit_2,
            'risk_reward_ratio': self.risk_reward_ratio,
            'risk_percent': self.risk_percent,
            'timeframe': self.timeframe,
            'estimated_duration': self.estimated_duration,
            'score_breakdown': self.score_breakdown,
            'analysis': self.analysis,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Report(db.Model):
    """Generated report model."""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), default='weekly')  # daily, weekly
    
    # Report period
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    
    # File info
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    
    # Metadata
    signals_count = db.Column(db.Integer)
    top_signals = db.Column(db.JSON)  # Summary of top signals
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'report_type': self.report_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'signals_count': self.signals_count,
            'top_signals': self.top_signals,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
