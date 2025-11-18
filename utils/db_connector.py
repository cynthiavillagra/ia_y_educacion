import os
import psycopg2

def get_connection():
    """Return a psycopg2 connection to Supabase using connection pooling."""
    
    # Construir la connection string desde las variables básicas
    supabase_url = os.environ["SUPABASE_URL"]
    password = os.environ["SUPABASE_DB_PASSWORD"]
    
    # Extraer el project ref de la URL
    project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    # Host del pooler (ajusta la región si es necesaria)
    pooler_host = os.environ.get(
        "SUPABASE_POOLER_HOST", 
        "aws-0-us-east-1.pooler.supabase.com"
    )
    
    connection_string = (
        f"postgresql://postgres.{project_ref}:{password}@"
        f"{pooler_host}:6543/postgres?sslmode=require"
    )
    
    return psycopg2.connect(connection_string)