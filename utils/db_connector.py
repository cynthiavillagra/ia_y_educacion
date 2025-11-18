import os
import psycopg2

def get_connection():
    """Return a psycopg2 connection to Supabase using connection pooling."""
    
    # Si tienes la connection string completa (RECOMENDADO)
    if "SUPABASE_CONNECTION_STRING" in os.environ:
        return psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    
    # Fallback: construir desde partes
    connection_string = (
        f"postgresql://postgres.{os.environ['SUPABASE_PROJECT_REF']}:"
        f"{os.environ['SUPABASE_DB_PASSWORD']}@"
        f"{os.environ['SUPABASE_POOLER_HOST']}:6543/postgres?sslmode=require"
    )
    return psycopg2.connect(connection_string)