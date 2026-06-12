from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import pytz

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "name": "ForexRank-AI",
            "version": "1.0.0",
            "status": "online",
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "endpoints": {
                "analyze": "/api/analyze",
                "session": "/api/session",
                "signals": "/api/signals"
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
