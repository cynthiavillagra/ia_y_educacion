from utils.db_connector import get_connection


def handler(request):
    """GET /api/recurso/<id>
    Vercel no usa path params nativamente en Python, así que esperamos ?id=...
    """
    recurso_id = request.query.get("id")
    if not recurso_id:
        return {"error": "Missing id"}

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.id, r.titulo, r.resumen, r.año_publicacion, r.fecha_ingreso,
                       r.estado_alojamiento, r.url_descarga, r.licencia_cc,
                       r.tipo_documento, r.codigo_documento, c.nombre AS coleccion
                FROM recursos r
                JOIN colecciones c ON c.id = r.id_coleccion
                WHERE r.id = %s
                """,
                (recurso_id,),
            )
            row = cur.fetchone()
            if not row:
                return {"error": "Not found"}

            cur.execute(
                """
                SELECT a.nombre_autor
                FROM recurso_autor ra
                JOIN autores a ON a.id = ra.autor_id
                WHERE ra.recurso_id = %s
                ORDER BY ra.orden ASC
                """,
                (recurso_id,),
            )
            autores = [r[0] for r in cur.fetchall()]

            cur.execute(
                """
                SELECT e.nombre_etiqueta
                FROM recurso_etiqueta re
                JOIN etiquetas e ON e.id = re.etiqueta_id
                WHERE re.recurso_id = %s
                ORDER BY e.nombre_etiqueta
                """,
                (recurso_id,),
            )
            etiquetas = [r[0] for r in cur.fetchall()]

        result = {
            "id": row[0],
            "titulo": row[1],
            "resumen": row[2],
            "año_publicacion": row[3],
            "fecha_ingreso": row[4].isoformat() if row[4] else None,
            "estado_alojamiento": row[5],
            "url_descarga": row[6],
            "licencia_cc": row[7],
            "tipo_documento": row[8],
            "codigo_documento": row[9],
            "coleccion": row[10],
            "autores": autores,
            "etiquetas": etiquetas,
        }
        return result
    finally:
        conn.close()
