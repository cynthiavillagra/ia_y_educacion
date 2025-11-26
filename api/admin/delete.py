class handler(BaseHTTPRequestHandler):
    
    def do_DELETE(self):
        """Handle resource deletion"""
        try:
            if not verify_token(self.headers):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": "Unauthorized"}
                self.wfile.write(json.dumps(response).encode())
                return

            # Get resource ID from query parameter
            path = self.path
            if '?' not in path:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": "ID de recurso requerido"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            query_string = path.split('?', 1)[1]
            params = {}
            for part in query_string.split('&'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    params[key] = value
            
            recurso_id = params.get('id')
            if not recurso_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": "ID de recurso requerido"}
                self.wfile.write(json.dumps(response).encode())
                return

            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        # Delete from junction tables first (due to foreign keys)
                        cur.execute("DELETE FROM recurso_autor WHERE recurso_id = %s", (recurso_id,))
                        cur.execute("DELETE FROM recurso_etiqueta WHERE recurso_id = %s", (recurso_id,))
                        
                        # Delete the resource itself
                        cur.execute("DELETE FROM recursos WHERE id = %s", (recurso_id,))
                        
                        if cur.rowcount == 0:
                            self.send_response(404)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            
                            response = {"error": "Recurso no encontrado"}
                            self.wfile.write(json.dumps(response).encode())
                            return
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"success": True}
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
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
