from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from server.router import Router
import json
import os

# -----------------------------------------------------------------------------
# COMPONENTE: HTTP SERVER (Servidor Web)
# -----------------------------------------------------------------------------
# ¿Por qué?
# Necesitamos escuchar en un puerto (8000) y recibir bytes de la red.
# Python trae `http.server` en su librería estándar, lo que nos permite
# levantar un servidor SIN instalar frameworks pesados como Flask o Django.
#
# ¿Qué hace?
# 1. Escucha peticiones (GET, POST, etc.).
# 2. Sirve archivos estáticos (HTML, CSS, JS) de la carpeta `static`.
# 3. Delega las peticiones de API al `Router`.
# -----------------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    # Router compartido por todas las instancias del handler
    router = Router()

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_PUT(self):
        self.handle_request("PUT")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def do_OPTIONS(self):
        self.handle_request("OPTIONS")

    def handle_request(self, method):
        """
        Punto central de entrada para cualquier request.
        Decide si servir un archivo estático o llamar a la API.
        """
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Lógica simple para servir archivos estáticos (Frontend)
        if path.startswith("/static/") or path == "/" or path.endswith(".html"):
            self.serve_static(path)
            return

        # Si no es estático, buscamos en el Router (API)
        handler, params = self.router.match(method, path)
        if handler:
            try:
                handler(self, params)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def serve_static(self, path):
        """
        Sirve archivos del disco duro.
        Equivalente a lo que haría Nginx o Apache.
        """
        if path == "/":
            path = "/static/index.html"
        elif not path.startswith("/static/"):
            path = f"/static{path}"
        
        # Seguridad básica: evitar salir del directorio (Directory Traversal)
        if ".." in path:
            self.send_error(403, "Forbidden")
            return

        # Quitamos el slash inicial para tener path relativo
        file_path = path[1:] 
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            # Adivinamos el Content-Type (MIME type)
            if file_path.endswith(".html"):
                self.send_header("Content-type", "text/html")
            elif file_path.endswith(".css"):
                self.send_header("Content-type", "text/css")
            elif file_path.endswith(".js"):
                self.send_header("Content-type", "application/javascript")
            elif file_path.endswith(".png"):
                self.send_header("Content-type", "image/png")
            self.end_headers()
            
            # Enviamos el archivo en binario
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()
