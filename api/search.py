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
        """Search resources endpoint"""
        try:
            # Parse query parameters
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            params = parse_qs(query_string)
            
            # Extract parameters (parse_qs returns lists, get first item)
            q = params.get("q", [""])[0]
            
            try:
                page = int(params.get("page", [1])[0])
                per_page = int(params.get("per_page", [20])[0])
            except Exception:
                self.send_error(400, "Invalid pagination parameters")
                return
            
            offset = (page - 1) * per_page
            autor = params.get("autor", [""])[0].strip()
            anio = params.get("anio", [""])[0].strip()
            coleccion = params.get("coleccion", [""])[0].strip()
            tipo = params.get("tipo", [""])[0].strip()
            orden = params.get("orden", ["relevancia"])[0].strip()

            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    filters = []
                    query_params = []
                    
                    if autor:
                        filters.append("a.nombre_autor ILIKE '%' || %s || '%'")
                        query_params.append(autor)
                    if anio:
                        filters.append("r.año_publicacion = %s")
                        query_params.append(int(anio))
                    if coleccion:
                        filters.append("c.nombre = %s")
                        query_params.append(coleccion)
                    if tipo:
                        filters.append("r.tipo_documento = %s")
                        query_params.append(tipo)

                    where_clause = (" AND ".join(filters)) if filters else "TRUE"

                    total_sql = f"""
                        SELECT COUNT(DISTINCT r.id)
                        FROM buscar_recursos(%s) sr
                        JOIN recursos r ON r.id = sr.id
                        LEFT JOIN colecciones c ON c.id = r.id_coleccion
                        LEFT JOIN recurso_autor ra ON ra.recurso_id = r.id
                        LEFT JOIN autores a ON a.id = ra.autor_id
                        LEFT JOIN recurso_etiqueta re ON re.recurso_id = r.id
                        LEFT JOIN etiquetas e ON e.id = re.etiqueta_id
                        WHERE {where_clause}
                    """
                    cur.execute(total_sql, [q] + query_params)
                    total = cur.fetchone()[0]

                    if orden == "anio_asc":
                        order_sql = "r.año_publicacion ASC, sr.score DESC"
                    elif orden == "anio_desc":
                        order_sql = "r.año_publicacion DESC, sr.score DESC"
                    elif orden == "fecha_ingreso_desc":
                        order_sql = "r.fecha_ingreso DESC, sr.score DESC"
                    else:
                        order_sql = "sr.score DESC"

                    items_sql = f"""
                        SELECT sr.id, r.titulo, r.año_publicacion, sr.score
                        FROM buscar_recursos(%s) sr
                        JOIN recursos r ON r.id = sr.id
                        LEFT JOIN colecciones c ON c.id = r.id_coleccion
                        LEFT JOIN recurso_autor ra ON ra.recurso_id = r.id
                        LEFT JOIN autores a ON a.id = ra.autor_id
                        LEFT JOIN recurso_etiqueta re ON re.recurso_id = r.id
                        LEFT JOIN etiquetas e ON e.id = re.etiqueta_id
                        WHERE {where_clause}
                        GROUP BY sr.id, r.titulo, r.año_publicacion, sr.score
                        ORDER BY {order_sql}
                        LIMIT %s OFFSET %s
                    """
                    cur.execute(items_sql, [q] + query_params + [per_page, offset])
                    rows = cur.fetchall()

                items = [
                    {
                        "id": r[0], 
                        "titulo": r[1], 
                        "año_publicacion": r[2], 
                        "score": float(r[3]) if r[3] is not None else 0.0
                    }
                    for r in rows
                ]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"total": total, "items": items}
                self.wfile.write(json.dumps(response).encode())
                
            finally:
                conn.close()
                
        except KeyError as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": f"missing env: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
            
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