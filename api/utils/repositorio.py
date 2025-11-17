from typing import List, Optional, Tuple
from .db_connector import get_connection


def get_coleccion_id(nombre: str) -> Optional[str]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM colecciones WHERE nombre=%s", (nombre,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


def find_or_create_autor(nombre: str) -> str:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM autores WHERE nombre_autor=%s", (nombre,))
                row = cur.fetchone()
                if row:
                    return row[0]
                cur.execute("INSERT INTO autores (nombre_autor) VALUES (%s) RETURNING id", (nombre,))
                return cur.fetchone()[0]
    finally:
        conn.close()


def find_or_create_etiqueta(nombre: str) -> str:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM etiquetas WHERE nombre_etiqueta=%s", (nombre,))
                row = cur.fetchone()
                if row:
                    return row[0]
                cur.execute("INSERT INTO etiquetas (nombre_etiqueta) VALUES (%s) RETURNING id", (nombre,))
                return cur.fetchone()[0]
    finally:
        conn.close()


def insertar_recurso(
    titulo: str,
    resumen: Optional[str],
    codigo_documento: Optional[str],
    año_publicacion: int,
    estado_alojamiento: str,
    url_descarga: str,
    licencia_cc: str,
    tipo_documento: str,
    id_coleccion: str,
) -> str:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO recursos (titulo, resumen, codigo_documento, año_publicacion, estado_alojamiento,
                                          url_descarga, licencia_cc, tipo_documento, id_coleccion)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                    """,
                    (
                        titulo,
                        resumen,
                        codigo_documento,
                        año_publicacion,
                        estado_alojamiento,
                        url_descarga,
                        licencia_cc,
                        tipo_documento,
                        id_coleccion,
                    ),
                )
                return cur.fetchone()[0]
    finally:
        conn.close()


def vincular_autor(recurso_id: str, autor_id: str, orden: int) -> None:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO recurso_autor (recurso_id, autor_id, orden) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                    (recurso_id, autor_id, orden),
                )
    finally:
        conn.close()


def vincular_etiqueta(recurso_id: str, etiqueta_id: str) -> None:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO recurso_etiqueta (recurso_id, etiqueta_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (recurso_id, etiqueta_id),
                )
    finally:
        conn.close()
