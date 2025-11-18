import os
import psycopg2


def get_connection():
    """Return a psycopg2 connection to Supabase Postgres using the connection pooler.

    Required env vars:
      - SUPABASE_URL            (e.g. https://xxxxxxxx.supabase.co)
      - SUPABASE_DB_PASSWORD    (database password for user postgres)
    Optional env vars:
      - SUPABASE_POOLER_HOST    (override pooler host; default aws-0-us-east-1.pooler.supabase.com)
    """

    supabase_url = os.getenv("SUPABASE_URL")
    password = os.getenv("SUPABASE_DB_PASSWORD")
    if not supabase_url:
        raise KeyError("SUPABASE_URL")
    if not password:
        raise KeyError("SUPABASE_DB_PASSWORD")

    # Extract project ref from the URL: https://<project-ref>.supabase.co
    project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]

    # Use Supabase connection pooler (recommended for serverless)
    host = os.getenv("SUPABASE_POOLER_HOST", "aws-0-us-east-1.pooler.supabase.com")
    user = f"postgres.{project_ref}"

    return psycopg2.connect(
        host=host,
        port=6543,
        dbname="postgres",
        user=user,
        password=password,
        sslmode="require",
    )