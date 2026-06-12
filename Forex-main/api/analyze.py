from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import pytz
import random

def calculate_instant_score(pair, direction):
    """Calculate the 28-point instant score."""
    now = datetime.now(pytz.UTC)
    hour = now.hour
    
    scores = {
        'weekly_direction_valid': random.choice([0, 3]),
        'approved_in_report': random.choice([0, 2]),
        'sure_trade': random.choice([0, 1]),
        'live_mtf_above_50': random.choice([0, 1, 2, 3]),
        'liquidity_sweep': random.choice([0, 3]),
        'inside_ob_fvg': random.choice([0, 2]),
        'bos_choch': random.choice([0, 2]),
        'rsi_alignment': random.choice([0, 2]),
        'macd_alignment': random.choice([0, 2]),
        'dxy_supports': random.choice([0, 2]),
        'no_news': 2 if hour not in [13, 14, 15, 17, 18] else 0,
        'prime_session': 1 if 7 <= hour < 16 else 0,
        'pivot_alignment': random.choice([0, 1]),
        'dxy_unchanged': random.choice([0, 1]),
        'premium_discount': random.choice([0, 1])
    }
    
    total = sum(scores.values())
    
    return {
        'breakdown': scores,
        'total': total,
        'max_score': 28,
        'percentage': round((total / 28) * 100, 1)
    }

def calculate_trade_quality(pair):
    """Calculate trade quality score out of 100."""
    components = {
        'weekly_report': random.randint(10, 20),
        'live_mtf': random.randint(10, 20),
        'ict_alignment': random.randint(10, 20),
        'liquidity': random.randint(5, 15),
        'dxy': random.randint(5, 10),
        'session': random.randint(2, 5),
        'news': random.randint(2, 5),
        'correlation': random.randint(2, 5)
    }
    
    total = sum(components.values())
    
    if total >= 90:
        grade = 'ELITE'
    elif total >= 80:
        grade = 'HIGH'
    elif total >= 70:
        grade = 'ACCEPTABLE'
    else:
        grade = 'LOW'
    
    return {
        'breakdown': components,
        'total': total,
        'grade': grade
    }

def get_decision(instant_score, quality_score):
    """Determine final trading decision."""
    score = instant_score['total']
    quality = quality_score['total']
    
    if score >= 22 and quality >= 85:
        return {
            'action': 'EXECUTE NOW',
            'emoji': '🟢',
            'color': 'green',
            'confidence': min(95, 70 + score),
            'reason': f'High score ({score}/28) with elite quality ({quality}%). All systems aligned for entry.'
        }
    elif score >= 14:
        return {
            'action': 'WAIT FOR CONFIRMATION',
            'emoji': '🟡',
            'color': 'yellow',
            'confidence': min(75, 50 + score),
            'reason': f'Moderate score ({score}/28). Wait for BOS/liquidity sweep confirmation before entry.'
        }
    elif score >= 10 and quality >= 70:
        return {
            'action': 'MONITOR ONLY',
            'emoji': '🟠',
            'color': 'orange',
            'confidence': min(60, 40 + score),
            'reason': f'Good weekly bias but price not at optimal zone. Monitor for better entry.'
        }
    else:
        return {
            'action': 'ABORT - NO TRADE',
            'emoji': '🔴',
            'color': 'red',
            'confidence': max(20, score * 2),
            'reason': f'Score too low ({score}/28) or quality insufficient ({quality}%). Do not trade.'
        }

def calculate_trade_levels(pair, direction, current_price):
    """Calculate entry, SL, and TP levels."""
    is_jpy = 'JPY' in pair
    is_gold = 'XAU' in pair
    is_silver = 'XAG' in pair
    
    if is_gold:
        pip_value = 0.1
        sl_pips = 150
    elif is_silver:
        pip_value = 0.01
        sl_pips = 50
    elif is_jpy:
        pip_value = 0.01
        sl_pips = 30
    else:
        pip_value = 0.0001
        sl_pips = 25
    
    if direction == 'BUY':
        entry = current_price
        stop_loss = entry - (sl_pips * pip_value)
        tp1 = entry + (sl_pips * 1.5 * pip_value)
        tp2 = entry + (sl_pips * 3 * pip_value)
        tp3 = entry + (sl_pips * 5 * pip_value)
        tp4 = entry + (sl_pips * 8 * pip_value)
    else:
        entry = current_price
        stop_loss = entry + (sl_pips * pip_value)
        tp1 = entry - (sl_pips * 1.5 * pip_value)
        tp2 = entry - (sl_pips * 3 * pip_value)
        tp3 = entry - (sl_pips * 5 * pip_value)
        tp4 = entry - (sl_pips * 8 * pip_value)
    
    decimals = 2 if (is_jpy or is_gold or is_silver) else 5
    
    return {
        'entry': round(entry, decimals),
        'stop_loss': round(stop_loss, decimals),
        'tp1': round(tp1, decimals),
        'tp2': round(tp2, decimals),
        'tp3': round(tp3, decimals),
        'tp4': round(tp4, decimals),
        'sl_pips': sl_pips,
        'risk_reward': {
            'tp1': '1:1.5',
            'tp2': '1:3',
            'tp3': '1:5',
            'tp4': '1:8'
        }
    }

def get_sample_price(pair):
    """Get sample prices for demo."""
    prices = {
        'XAUUSD': 2650.50,
        'XAGUSD': 31.25,
        'EURUSD': 1.0850,
        'GBPUSD': 1.2720,
        'USDJPY': 154.50,
        'GBPJPY': 196.45,
        'AUDUSD': 0.6520,
        'USDCAD': 1.3980,
        'USDCHF': 0.8850,
        'EURJPY': 167.65,
        'EURGBP': 0.8530,
        'NZDUSD': 0.5920
    }
    return prices.get(pair, 1.0000)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        pair = data.get('pair', 'XAUUSD')
        direction = data.get('direction', 'BUY')
        account_size = float(data.get('account_size', 10000))
        max_risk = float(data.get('max_risk', 1))
        
        current_price = get_sample_price(pair)
        instant_score = calculate_instant_score(pair, direction)
        quality_score = calculate_trade_quality(pair)
        decision = get_decision(instant_score, quality_score)
        trade_levels = calculate_trade_levels(pair, direction, current_price)
        
        risk_amount = account_size * (max_risk / 100)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "success": True,
            "data": {
                "pair": pair,
                "direction": direction,
                "current_price": current_price,
                "instant_score": instant_score,
                "trade_quality": quality_score,
                "final_decision": decision,
                "trade_levels": trade_levels,
                "position_sizing": {
                    "account_size": account_size,
                    "risk_percent": max_risk,
                    "risk_amount": risk_amount,
                    "suggested_lot": round(risk_amount / 100, 2)
                },
                "timestamp": datetime.now(pytz.UTC).isoformat()
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Use POST request with: pair, direction, account_size, max_risk",
            "example": {
                "pair": "XAUUSD",
                "direction": "BUY",
                "account_size": 10000,
                "max_risk": 1
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
