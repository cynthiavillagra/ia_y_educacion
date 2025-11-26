# -----------------------------------------------------------------------------
# [LEGACY] ARCHIVO OBSOLETO
# -----------------------------------------------------------------------------
# Este archivo pertenece a la arquitectura anterior.
# NO USAR en nuevo código.
#
# Reemplazo: server/material_handler.py (handle_get_material)
# -----------------------------------------------------------------------------

from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connector import get_connection

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """GET /api/recurso_detalle?id=<id>
        Returns details of a specific resource
        """
        try:
            # Parse query parameters
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            params = parse_qs(query_string)
            
            recurso_id = params.get("id", [None])[0]
            
            if not recurso_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": "Missing id parameter"}
                self.wfile.write(json.dumps(response).encode())
                return

            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT r.id, r.titulo, r.resumen, r.año_publicacion, r.fecha_ingreso,
                               r.estado_alojamiento, r.url_descarga, r.licencia_cc,
                               r.tipo_documento, r.codigo_documento, c.nombre AS coleccion
                        FROM recursos r
                        JOIN colecciones c ON c.id = r.id_coleccion
                        WHERE r.id = %s
                        """,
                        (recurso_id,),
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        self.send_response(404)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {"error": "Resource not found"}
                        self.wfile.write(json.dumps(response).encode())
                        return

                    cur.execute(
                        """
                        SELECT a.nombre_autor
                        FROM recurso_autor ra
                        JOIN autores a ON a.id = ra.autor_id
                        WHERE ra.recurso_id = %s
                        ORDER BY ra.orden ASC
                        """,
                        (recurso_id,),
                    )
                    autores = [r[0] for r in cur.fetchall()]

                    cur.execute(
                        """
                        SELECT e.nombre_etiqueta
                        FROM recurso_etiqueta re
                        JOIN etiquetas e ON e.id = re.etiqueta_id
                        WHERE re.recurso_id = %s
                        ORDER BY e.nombre_etiqueta
                        """,
                        (recurso_id,),
                    )
                    etiquetas = [r[0] for r in cur.fetchall()]

                result = {
                    "id": row[0],
                    "titulo": row[1],
                    "resumen": row[2],
                    "año_publicacion": row[3],
                    "fecha_ingreso": row[4].isoformat() if row[4] else None,
                    "estado_alojamiento": row[5],
                    "url_descarga": row[6],
                    "licencia_cc": row[7],
                    "tipo_documento": row[8],
                    "codigo_documento": row[9],
                    "coleccion": row[10],
                    "autores": autores,
                    "etiquetas": etiquetas,
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(result).encode())
                
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