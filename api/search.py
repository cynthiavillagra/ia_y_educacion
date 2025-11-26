from http.server import BaseHTTPRequestHandler
from server.material_handler import handle_list_materials

# -----------------------------------------------------------------------------
# ARCHIVO LEGACY (PROXY)
# -----------------------------------------------------------------------------
# Este archivo existe por compatibilidad con Vercel (File-System Routing).
# Redirige la ejecución al nuevo handler en `server/material_handler.py`.
# -----------------------------------------------------------------------------

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Delegamos la ejecución al nuevo handler centralizado
        handle_list_materials(self, None)

    def do_OPTIONS(self):
        # Manejo básico de CORS para preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()