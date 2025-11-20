from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import uuid
import requests
import cgi
from io import BytesIO

# Add parent directory to path to import utils and auth
# We are in api/admin, so we need to go up two levels to reach root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.db_connector import get_connection
from api.auth import verify_token

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET", "recursos-alojados")
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default


def _upload_to_storage(file_bytes: bytes, filename: str) -> str:
    """Upload file to Supabase Storage and return public URL."""
    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
    path = f"uploads/{uuid.uuid4()}_{filename}"
    url = f"https://{project_ref}.supabase.co/storage/v1/object/{STORAGE_BUCKET}/{path}"
    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/octet-stream",
    }
    r = requests.post(url, headers=headers, data=file_bytes)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Storage upload failed: {r.status_code} {r.text}")

    # Public URL
    public_url = f"https://{project_ref}.supabase.co/storage/v1/object/public/{STORAGE_BUCKET}/{path}"
    return public_url


class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """Handle resource ingestion with file upload"""
        try:
            if not verify_token(self.headers):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": "Unauthorized"}
                self.wfile.write(json.dumps(response).encode())
                return

            # Parse multipart/form-data
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": "Content-Type must be multipart/form-data"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Parse form data
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse multipart data
            form_data = {}
            file_data = None
            filename = None
            
            # Simple multipart parser
            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
                'CONTENT_LENGTH': str(content_length)
            }
            
            fp = BytesIO(body)
            form = cgi.FieldStorage(fp=fp, environ=environ, keep_blank_values=True)
            
            # Extract form fields
            for key in form.keys():
                item = form[key]
                if item.filename:
                    # It's a file
                    file_data = item.file.read()
                    filename = item.filename
                else:
                    # It's a regular field
                    form_data[key] = item.value
            
            # Parse arrays that arrive stringified
            autores = form_data.get("autores", "[]")
            etiquetas = form_data.get("etiquetas", "[]")
            
            try:
                autores = json.loads(autores) if isinstance(autores, str) else autores
                etiquetas = json.loads(etiquetas) if isinstance(etiquetas, str) else etiquetas
            except Exception:
                autores = []
                etiquetas = []

            estado = form_data.get("estado_alojamiento", "ORIGINAL").upper()
            url_descarga = form_data.get("url_descarga")

            if estado == "ALOJADO":
                if not file_data:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"error": "archivo requerido para ALOJADO"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                if len(file_data) > MAX_FILE_SIZE:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"error": "archivo excede tamaño máximo"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                try:
                    url_descarga = _upload_to_storage(file_data, filename)
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"error": f"upload error: {e}"}
                    self.wfile.write(json.dumps(response).encode())
                    return
            else:
                if not url_descarga:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {"error": "url_descarga requerida para ORIGINAL"}
                    self.wfile.write(json.dumps(response).encode())
                    return

            recurso = {
                "titulo": form_data.get("titulo", "").strip(),
                "resumen": form_data.get("resumen", ""),
                "codigo_documento": form_data.get("codigo_documento") or None,
                "año_publicacion": int(form_data.get("año_publicacion")),
                "estado_alojamiento": estado,
                "url_descarga": url_descarga,
                "licencia_cc": form_data.get("licencia_cc", "").strip(),
                "coleccion": form_data.get("coleccion", "").strip(),
                "tipo_documento": form_data.get("tipo_documento", "").strip(),
                "autores": autores,
                "etiquetas": etiquetas,
            }

            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        # Colección -> id
                        cur.execute("SELECT id FROM colecciones WHERE nombre=%s", (recurso["coleccion"],))
                        row = cur.fetchone()
                        if not row:
                            self.send_response(400)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            
                            response = {"error": "coleccion inexistente"}
                            self.wfile.write(json.dumps(response).encode())
                            return
                        
                        id_coleccion = row[0]

                        # Insert recurso
                        cur.execute(
                            """
                            INSERT INTO recursos (titulo, resumen, codigo_documento, año_publicacion, estado_alojamiento,
                                                  url_descarga, licencia_cc, tipo_documento, id_coleccion)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            RETURNING id
                            """,
                            (
                                recurso["titulo"], recurso["resumen"], recurso["codigo_documento"], recurso["año_publicacion"],
                                recurso["estado_alojamiento"], recurso["url_descarga"], recurso["licencia_cc"],
                                recurso["tipo_documento"], id_coleccion,
                            ),
                        )
                        recurso_id = cur.fetchone()[0]

                        # Autores (crear si no existen)
                        orden = 1
                        for nombre in recurso["autores"]:
                            cur.execute("SELECT id FROM autores WHERE nombre_autor=%s", (nombre,))
                            a = cur.fetchone()
                            if not a:
                                cur.execute("INSERT INTO autores (nombre_autor) VALUES (%s) RETURNING id", (nombre,))
                                autor_id = cur.fetchone()[0]
                            else:
                                autor_id = a[0]
                            cur.execute(
                                "INSERT INTO recurso_autor (recurso_id, autor_id, orden) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                                (recurso_id, autor_id, orden),
                            )
                            orden += 1

                        # Etiquetas (crear si no existen)
                        for tag in recurso["etiquetas"]:
                            cur.execute("SELECT id FROM etiquetas WHERE nombre_etiqueta=%s", (tag,))
                            e = cur.fetchone()
                            if not e:
                                cur.execute("INSERT INTO etiquetas (nombre_etiqueta) VALUES (%s) RETURNING id", (tag,))
                                etiqueta_id = cur.fetchone()[0]
                            else:
                                etiqueta_id = e[0]
                            cur.execute(
                                "INSERT INTO recurso_etiqueta (recurso_id, etiqueta_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                                (recurso_id, etiqueta_id),
                            )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"id": str(recurso_id), "success": True}
                self.wfile.write(json.dumps(response).encode())
                
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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()