from utils.db_connector import get_connection

# Vercel Python Serverless Function entrypoint
# The platform calls 'handler(request)'. We treat 'request' as an object
# providing .query (dict-like) and we return a JSON-serializable dict.

def handler(request):
    q = request.query.get("q", "")
    page = int(request.query.get("page", 1))
    per_page = int(request.query.get("per_page", 20))
    offset = (page - 1) * per_page
    autor = (request.query.get("autor") or "").strip()
    anio = (request.query.get("anio") or "").strip()
    coleccion = (request.query.get("coleccion") or "").strip()
    tipo = (request.query.get("tipo") or "").strip()
    orden = (request.query.get("orden") or "relevancia").strip()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Build dynamic filters shared by total and items
            filters = []
            params = []
            # autor filter via join autores
            if autor:
                filters.append("a.nombre_autor ILIKE '%' || %s || '%'")
                params.append(autor)
            # anio filter
            if anio:
                filters.append("r.año_publicacion = %s")
                params.append(int(anio))
            # coleccion filter
            if coleccion:
                filters.append("c.nombre = %s")
                params.append(coleccion)
            # tipo filter
            if tipo:
                filters.append("r.tipo_documento = %s")
                params.append(tipo)

            where_clause = (" AND ".join(filters)) if filters else "TRUE"

            # total with buscar_recursos + joins (distinct ids)
            total_sql = f"""
                SELECT COUNT(DISTINCT r.id)
                FROM buscar_recursos(%s) sr
                JOIN recursos r ON r.id = sr.id
                LEFT JOIN colecciones c ON c.id = r.id_coleccion
                LEFT JOIN recurso_autor ra ON ra.recurso_id = r.id
                LEFT JOIN autores a ON a.id = ra.autor_id
                LEFT JOIN recurso_etiqueta re ON re.recurso_id = r.id
                LEFT JOIN etiquetas e ON e.id = re.etiqueta_id
                WHERE {where_clause}
            """
            cur.execute(total_sql, [q] + params)
            total = cur.fetchone()[0]

            # order by mapping
            if orden == "anio_asc":
                order_sql = "r.año_publicacion ASC, sr.score DESC"
            elif orden == "anio_desc":
                order_sql = "r.año_publicacion DESC, sr.score DESC"
            elif orden == "fecha_ingreso_desc":
                order_sql = "r.fecha_ingreso DESC, sr.score DESC"
            else:  # relevancia
                order_sql = "sr.score DESC"

            items_sql = f"""
                SELECT sr.id, r.titulo, r.año_publicacion, sr.score
                FROM buscar_recursos(%s) sr
                JOIN recursos r ON r.id = sr.id
                LEFT JOIN colecciones c ON c.id = r.id_coleccion
                LEFT JOIN recurso_autor ra ON ra.recurso_id = r.id
                LEFT JOIN autores a ON a.id = ra.autor_id
                LEFT JOIN recurso_etiqueta re ON re.recurso_id = r.id
                LEFT JOIN etiquetas e ON e.id = re.etiqueta_id
                WHERE {where_clause}
                GROUP BY sr.id, r.titulo, r.año_publicacion, sr.score
                ORDER BY {order_sql}
                LIMIT %s OFFSET %s
            """
            cur.execute(items_sql, [q] + params + [per_page, offset])
            rows = cur.fetchall()

        items = [
            {"id": r[0], "titulo": r[1], "año_publicacion": r[2], "score": float(r[3]) if r[3] is not None else 0.0}
            for r in rows
        ]
        return {"total": total, "items": items}
    finally:
        conn.close()
