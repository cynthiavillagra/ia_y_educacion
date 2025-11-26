import sys
import os
import json
from utils.response import Response

def handle_debug(handler, params):
    """
    Handler de diagnóstico para verificar el estado del servidor Vercel.
    """
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
        # Security: Don't show password
        if val and var != "SUPABASE_DB_PASSWORD":
            results["env_vars_check"][f"{var}_val"] = val

    # 2. Check Imports
    try:
        import psycopg2
        results["imports"]["psycopg2"] = "OK"
    except ImportError as e:
        results["imports"]["psycopg2"] = f"FAILED: {str(e)}"

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

    Response.json(handler, results)
