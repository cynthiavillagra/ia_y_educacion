from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Endpoint de prueba para verificar que la API funciona"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "API IA y Educación funcionando correctamente",
            "status": "ok",
            "version": "1.0",
            "endpoints": [
                "/api/test_db - Test conexión a base de datos",
                "/api/search - Búsqueda de recursos",
                "/api/recurso_detalle - Detalle de un recurso",
                "/api/ingestion - Ingesta de nuevos recursos (POST)"
            ]
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Maneja CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()