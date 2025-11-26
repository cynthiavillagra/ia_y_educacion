from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import pkg_resources

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        results = {
            "status": "running",
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "sys_path": sys.path,
            "env_vars_check": {},
            "db_connection": "pending",
            "search_function": "pending",
            "imports": {}
        }

        # 1. Check Environment Variables
        env_vars = [
            "SUPABASE_DB_HOST", "SUPABASE_DB_USER", "SUPABASE_DB_NAME", 
            "SUPABASE_DB_PORT", "SUPABASE_DB_PASSWORD", "SUPABASE_DB_SSLMODE"
        ]
        for var in env_vars:
            val = os.getenv(var)
            results["env_vars_check"][var] = "OK" if val else "MISSING"
            if val and var != "SUPABASE_DB_PASSWORD":
                results["env_vars_check"][f"{var}_val"] = val

        # 2. Check Imports
        try:
            import psycopg2
            results["imports"]["psycopg2"] = "OK"
        except ImportError as e:
            results["imports"]["psycopg2"] = f"FAILED: {str(e)}"

        try:
            from server.material_handler import handle_list_materials
            results["imports"]["server.material_handler"] = "OK"
        except ImportError as e:
            results["imports"]["server.material_handler"] = f"FAILED: {str(e)}"

        # 3. Test DB Connection
        try:
            from utils.db import get_connection
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                v = cur.fetchone()[0]
                results["db_connection"] = f"SUCCESS: {v}"
                
                # 4. Test Search Function
                try:
                    cur.execute("SELECT count(*) FROM buscar_recursos('test')")
                    count = cur.fetchone()[0]
                    results["search_function"] = f"SUCCESS: Found {count} results (test)"
                except Exception as e:
                    results["search_function"] = f"FAILED: {str(e)}"
            conn.close()
        except Exception as e:
            results["db_connection"] = f"FAILED: {str(e)}"

        # Send Response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results, indent=2, default=str).encode())
