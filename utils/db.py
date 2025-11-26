import os
import psycopg2

# -----------------------------------------------------------------------------
# CAPA: UTILS / INFRASTRUCTURE (Infraestructura de Base de Datos)
# -----------------------------------------------------------------------------
# ¿Por qué?
# Conectarse a Postgres requiere leer muchas variables de entorno (host, user, pass, port).
# Repetir esto en cada repositorio sería un error grave (DRY - Don't Repeat Yourself).
#
# ¿Qué logramos?
# 1. Abstracción de Conexión: El repositorio solo pide `get_connection()` y recibe
#    un objeto conexión listo para usar.
# 2. Configuración Segura: Manejamos la lectura de variables de entorno en un solo lugar.
# -----------------------------------------------------------------------------

def get_connection():
    """
    Crea y retorna una nueva conexión a la base de datos PostgreSQL de Supabase.
    Usa la librería `psycopg2` que es el estándar de facto para Python + Postgres.
    """
    raw_host = os.getenv("SUPABASE_DB_HOST")
    # Limpieza básica del host por si viene con protocolo
    host = (raw_host or "").strip().replace("https://", "").replace("http://", "")
    password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if not host:
        raise KeyError("SUPABASE_DB_HOST no está definida")
    if not password:
        raise KeyError("SUPABASE_DB_PASSWORD no está definida")

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
