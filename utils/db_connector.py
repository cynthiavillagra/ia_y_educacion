import os
import psycopg2

def get_connection():
    """Return a psycopg2 connection to Supabase Postgres.
    
    Required environment variables:
      - SUPABASE_URL: Your project URL (e.g., https://xxxxx.supabase.co)
      - SUPABASE_DB_PASSWORD: Your database password
    """
    
    # Obtener la URL de Supabase
    supabase_url = os.environ.get("SUPABASE_URL", "")
    password = os.environ.get("SUPABASE_DB_PASSWORD", "")
    
    if not supabase_url or not password:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_DB_PASSWORD environment variables")
    
    # Extraer el project reference de la URL
    # De: https://bruvzimzklfjwckpyhrj.supabase.co
    # A: bruvzimzklfjwckpyhrj
    project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
    
    # Usar connection pooling (port 6543) para serverless
    host = f"aws-0-us-east-1.pooler.supabase.com"
    user = f"postgres.{project_ref}"
    
    return psycopg2.connect(
        host=host,
        port=6543,
        dbname="postgres",
        user=user,
        password=password,
        sslmode="require"
    )