from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from server.router import Router
import json
import os

class RequestHandler(BaseHTTPRequestHandler):
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
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Static file serving (basic)
        if path.startswith("/static/") or path == "/" or path.endswith(".html"):
            self.serve_static(path)
            return

        handler, params = self.router.match(method, path)
        if handler:
            try:
                handler(self, params)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def serve_static(self, path):
        if path == "/":
            path = "/static/index.html"
        elif not path.startswith("/static/"):
            path = f"/static{path}"
        
        # Security check
        if ".." in path:
            self.send_error(403, "Forbidden")
            return

        # Remove leading / for file system path
        file_path = path[1:] 
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            # Guess mime type
            if file_path.endswith(".html"):
                self.send_header("Content-type", "text/html")
            elif file_path.endswith(".css"):
                self.send_header("Content-type", "text/css")
            elif file_path.endswith(".js"):
                self.send_header("Content-type", "application/javascript")
            elif file_path.endswith(".png"):
                self.send_header("Content-type", "image/png")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()
