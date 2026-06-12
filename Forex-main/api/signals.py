from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import pytz
import random

def generate_weekly_signals():
    """Generate weekly trading signals for all pairs."""
    pairs = [
        {'symbol': 'XAUUSD', 'name': 'Gold', 'emoji': '🥇'},
        {'symbol': 'XAGUSD', 'name': 'Silver', 'emoji': '🥈'},
        {'symbol': 'EURUSD', 'name': 'Euro/Dollar', 'emoji': '🇪🇺'},
        {'symbol': 'GBPUSD', 'name': 'Pound/Dollar', 'emoji': '🇬🇧'},
        {'symbol': 'USDJPY', 'name': 'Dollar/Yen', 'emoji': '🇯🇵'},
        {'symbol': 'GBPJPY', 'name': 'Pound/Yen', 'emoji': '💷'},
        {'symbol': 'AUDUSD', 'name': 'Aussie/Dollar', 'emoji': '🇦🇺'},
        {'symbol': 'USDCAD', 'name': 'Dollar/Loonie', 'emoji': '🇨🇦'},
        {'symbol': 'USDCHF', 'name': 'Dollar/Franc', 'emoji': '🇨🇭'},
        {'symbol': 'NZDUSD', 'name': 'Kiwi/Dollar', 'emoji': '🇳🇿'}
    ]
    
    signals = []
    
    for pair in pairs:
        score = random.randint(8, 28)
        direction = random.choice(['BUY', 'SELL'])
        
        if score >= 22:
            confidence = 'HIGH'
            action = 'EXECUTE'
            color = 'green'
        elif score >= 14:
            confidence = 'MEDIUM'
            action = 'WAIT'
            color = 'yellow'
        else:
            confidence = 'LOW'
            action = 'SKIP'
            color = 'red'
        
        signals.append({
            'symbol': pair['symbol'],
            'name': pair['name'],
            'emoji': pair['emoji'],
            'direction': direction,
            'score': score,
            'max_score': 28,
            'confidence': confidence,
            'action': action,
            'color': color
        })
    
    # Sort by score descending
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    return signals

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        signals = generate_weekly_signals()
        
        response = {
            "success": True,
            "data": {
                "signals": signals,
                "top_3": signals[:3],
                "generated_at": datetime.now(pytz.UTC).isoformat(),
                "valid_until": "End of trading week"
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
