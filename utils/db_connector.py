# -----------------------------------------------------------------------------
# [LEGACY] ARCHIVO OBSOLETO
# -----------------------------------------------------------------------------
# Este archivo pertenece a la arquitectura anterior.
# NO USAR en nuevo código.
#
# Reemplazo: utils/db.py
# -----------------------------------------------------------------------------

import os
import psycopg2
from psycopg2 import OperationalError


def get_connection():
    raw_host = os.getenv("SUPABASE_DB_HOST")
    host = (raw_host or "").strip().replace("https://", "").replace("http://", "")
    password = os.getenv("SUPABASE_DB_PASSWORD")
    if not host:
        raise KeyError("SUPABASE_DB_HOST")
    if not password:
        raise KeyError("SUPABASE_DB_PASSWORD")

    port = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    dbname = os.getenv("SUPABASE_DB_NAME", "postgres")
    sslmode = os.getenv("SUPABASE_DB_SSLMODE", "require")

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        sslmode=sslmode,
    )