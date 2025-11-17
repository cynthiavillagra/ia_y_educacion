import os
import psycopg2

def get_connection():
    """Return a psycopg2 connection to Supabase Postgres using env vars.

    Required env:
      - SUPABASE_URL (e.g. https://xyzcompany.supabase.co)
      - SUPABASE_DB_PASSWORD (database password)
    """
    supabase_url = os.environ["SUPABASE_URL"]
    host = supabase_url.replace("https://", "").replace(".supabase.co", "") + ".supabase.co"
    return psycopg2.connect(
        host=host,
        dbname="postgres",
        user="postgres",
        password=os.environ["SUPABASE_DB_PASSWORD"],
        port=5432,
        sslmode="require",
    )
