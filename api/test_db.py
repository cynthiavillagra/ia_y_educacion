from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connector import get_connection

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Test database connection"""
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "ok": True, 
                "db_response": result[0] if result else None,
                "message": "Database connection successful"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "ok": False, 
                "error": str(e)
            }
            
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()