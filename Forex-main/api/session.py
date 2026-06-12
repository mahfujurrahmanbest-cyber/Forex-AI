from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import pytz

def get_trading_sessions():
    """Get current trading session status."""
    now = datetime.now(pytz.UTC)
    hour = now.hour
    
    sessions = {
        'sydney': {'start': 21, 'end': 6, 'active': False},
        'tokyo': {'start': 0, 'end': 9, 'active': False},
        'london': {'start': 7, 'end': 16, 'active': False},
        'new_york': {'start': 12, 'end': 21, 'active': False}
    }
    
    active_sessions = []
    
    # Sydney (21:00 - 06:00 UTC)
    if hour >= 21 or hour < 6:
        sessions['sydney']['active'] = True
        active_sessions.append('SYDNEY')
    
    # Tokyo (00:00 - 09:00 UTC)
    if 0 <= hour < 9:
        sessions['tokyo']['active'] = True
        active_sessions.append('TOKYO')
    
    # London (07:00 - 16:00 UTC)
    if 7 <= hour < 16:
        sessions['london']['active'] = True
        active_sessions.append('LONDON')
    
    # New York (12:00 - 21:00 UTC)
    if 12 <= hour < 21:
        sessions['new_york']['active'] = True
        active_sessions.append('NEW_YORK')
    
    # Kill zones
    kill_zones = {
        'london_kz': 7 <= hour < 10,
        'ny_kz': 12 <= hour < 15,
        'overlap_kz': 12 <= hour < 16,
        'asian_kz': 0 <= hour < 3
    }
    
    is_overlap = sessions['london']['active'] and sessions['new_york']['active']
    
    return {
        'current_time': now.strftime('%H:%M:%S UTC'),
        'sessions': sessions,
        'active_sessions': active_sessions,
        'is_overlap': is_overlap,
        'kill_zone': kill_zones,
        'best_time_to_trade': is_overlap or kill_zones['london_kz'] or kill_zones['ny_kz']
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "success": True,
            "data": get_trading_sessions()
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
