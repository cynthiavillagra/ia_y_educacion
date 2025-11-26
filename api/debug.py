from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        results = {
            "status": "running",
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "sys_path": sys.path,
            "env_check": "starting"
        }

        try:
            # 1. Check Imports
            try:
                import psycopg2
                results["psycopg2"] = "INSTALLED"
            except ImportError as e:
                results["psycopg2"] = f"MISSING: {e}"

            # 2. Check DB Connection using the new utils/db.py
            try:
                from utils.db import get_connection
                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    v = cur.fetchone()[0]
                    results["db_connection"] = f"SUCCESS: {v}"
                    
                    # 3. Test Search Function
                    try:
                        cur.execute("SELECT count(*) FROM buscar_recursos('test')")
                        count = cur.fetchone()[0]
                        results["search_function"] = f"SUCCESS: Found {count} results"
                    except Exception as e:
                        results["search_function"] = f"FAILED: {str(e)}"
                conn.close()
            except Exception as e:
                results["db_connection"] = f"FAILED: {str(e)}"

        except Exception as e:
            results["fatal_error"] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results, indent=2, default=str).encode())
