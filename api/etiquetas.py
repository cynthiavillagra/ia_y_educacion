# -----------------------------------------------------------------------------
# ARCHIVO LEGACY (OBSOLETO)
# -----------------------------------------------------------------------------
# ESTE ARCHIVO YA NO SE USA EN LA NUEVA ARQUITECTURA.
#
# Reemplazo:
# La lógica de etiquetas se maneja implícitamente al crear/editar materiales en:
# -> `repositories/material_repository.py`
# -> `services/material_service.py`
#
# Razón:
# Centralizar la lógica de dominio.
# -----------------------------------------------------------------------------

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connector import get_connection

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """GET /api/etiquetas
        Returns all unique tags from the database
        """
        try:
            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        # Get all unique tags ordered alphabetically
                        cur.execute("""
                            SELECT DISTINCT nombre_etiqueta 
                            FROM etiquetas 
                            ORDER BY nombre_etiqueta ASC
                        """)
                        rows = cur.fetchall()
                        tags = [row[0] for row in rows]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(tags).encode())
                
            finally:
                conn.close()
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
