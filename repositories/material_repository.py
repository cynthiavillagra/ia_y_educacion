import json
from typing import List, Optional, Dict, Any
from utils.db import get_connection
from repositories.supabase_client import supabase_client
from domain.material import Material
from adapters.material_adapter import to_material

class MaterialRepository:
    def get_by_id(self, material_id: int) -> Optional[Material]:
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
                    (material_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None

                # Get authors
                cur.execute(
                    """
                    SELECT a.nombre_autor
                    FROM recurso_autor ra
                    JOIN autores a ON a.id = ra.autor_id
                    WHERE ra.recurso_id = %s
                    ORDER BY ra.orden ASC
                    """,
                    (material_id,),
                )
                autores = [r[0] for r in cur.fetchall()]

                # Get tags
                cur.execute(
                    """
                    SELECT e.nombre_etiqueta
                    FROM recurso_etiqueta re
                    JOIN etiquetas e ON e.id = re.etiqueta_id
                    WHERE re.recurso_id = %s
                    ORDER BY e.nombre_etiqueta
                    """,
                    (material_id,),
                )
                etiquetas = [r[0] for r in cur.fetchall()]

                # Map to domain
                data = {
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
                    "coleccion": row[10]
                }
                return to_material(data, autores, etiquetas)
        finally:
            conn.close()

    def search(self, query: str, filters: Dict[str, Any], page: int = 1, per_page: int = 20, order: str = "relevancia") -> Dict[str, Any]:
        offset = (page - 1) * per_page
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql_filters = []
                query_params = []
                
                autor = filters.get("autor")
                if autor:
                    sql_filters.append("(EXISTS (SELECT 1 FROM recurso_autor ra_f JOIN autores a_f ON ra_f.autor_id = a_f.id WHERE ra_f.recurso_id = r.id AND a_f.nombre_autor ILIKE %s) OR c.nombre ILIKE %s)")
                    query_params.append(f"%{autor}%")
                    query_params.append(f"%{autor}%")
                
                if filters.get("anio"):
                    sql_filters.append("r.año_publicacion = %s")
                    query_params.append(int(filters.get("anio")))
                
                if filters.get("coleccion"):
                    sql_filters.append("c.nombre = %s")
                    query_params.append(filters.get("coleccion"))
                
                if filters.get("tipo"):
                    sql_filters.append("r.tipo_documento = %s")
                    query_params.append(filters.get("tipo"))

                where_clause = (" AND ".join(sql_filters)) if sql_filters else "TRUE"

                # Count total
                total_sql = f"""
                    SELECT COUNT(DISTINCT r.id)
                    FROM buscar_recursos(%s) sr
                    JOIN recursos r ON r.id = sr.id
                    JOIN colecciones c ON c.id = r.id_coleccion
                    WHERE {where_clause}
                """
                # Note: The original query had LEFT JOINs for authors/tags in count, but COUNT(DISTINCT r.id) doesn't need them unless filtering by them.
                # The filter logic for authors is a subquery (EXISTS), so we don't need the LEFT JOINs for filtering.
                # However, to be safe and match original logic exactly:
                total_sql = f"""
                    SELECT COUNT(DISTINCT r.id)
                    FROM buscar_recursos(%s) sr
                    JOIN recursos r ON r.id = sr.id
                    LEFT JOIN colecciones c ON c.id = r.id_coleccion
                    WHERE {where_clause}
                """
                cur.execute(total_sql, [query] + query_params)
                total = cur.fetchone()[0]

                # Order
                if order == "anio_asc":
                    order_sql = "r.año_publicacion ASC, sr.score DESC"
                elif order == "anio_desc":
                    order_sql = "r.año_publicacion DESC, sr.score DESC"
                elif order == "fecha_ingreso_desc":
                    order_sql = "r.fecha_ingreso DESC, sr.score DESC"
                else:
                    order_sql = "sr.score DESC"

                # Fetch items
                items_sql = f"""
                    SELECT sr.id, r.titulo, r.año_publicacion, sr.score,
                           r.resumen, r.tipo_documento,
                           COALESCE(json_agg(DISTINCT a.nombre_autor) FILTER (WHERE a.id IS NOT NULL), '[]') as autores,
                           COALESCE(json_agg(DISTINCT e.nombre_etiqueta) FILTER (WHERE e.id IS NOT NULL), '[]') as etiquetas,
                           c.nombre as coleccion
                    FROM buscar_recursos(%s) sr
                    JOIN recursos r ON r.id = sr.id
                    LEFT JOIN colecciones c ON c.id = r.id_coleccion
                    LEFT JOIN recurso_autor ra ON ra.recurso_id = r.id
                    LEFT JOIN autores a ON a.id = ra.autor_id
                    LEFT JOIN recurso_etiqueta re ON re.recurso_id = r.id
                    LEFT JOIN etiquetas e ON e.id = re.etiqueta_id
                    WHERE {where_clause}
                    GROUP BY sr.id, r.titulo, r.año_publicacion, sr.score, r.resumen, r.tipo_documento, c.nombre
                    ORDER BY {order_sql}
                    LIMIT %s OFFSET %s
                """
                cur.execute(items_sql, [query] + query_params + [per_page, offset])
                rows = cur.fetchall()

                items = [
                    {
                        "id": r[0], 
                        "titulo": r[1], 
                        "año_publicacion": r[2], 
                        "score": float(r[3]) if r[3] is not None else 0.0,
                        "resumen": r[4],
                        "tipo_documento": r[5],
                        "autores": r[6],
                        "etiquetas": r[7],
                        "coleccion": r[8]
                    }
                    for r in rows
                ]
                return {"total": total, "items": items}
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Get collection ID
                    cur.execute("SELECT id FROM colecciones WHERE nombre=%s", (data["coleccion"],))
                    row = cur.fetchone()
                    if not row:
                        raise ValueError("Colección inexistente")
                    id_coleccion = row[0]

                    # Insert resource
                    cur.execute(
                        """
                        INSERT INTO recursos (titulo, resumen, codigo_documento, año_publicacion, estado_alojamiento,
                                              url_descarga, licencia_cc, tipo_documento, id_coleccion)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING id
                        """,
                        (
                            data["titulo"], data["resumen"], data["codigo_documento"], data["año_publicacion"],
                            data["estado_alojamiento"], data["url_descarga"], data["licencia_cc"],
                            data["tipo_documento"], id_coleccion,
                        ),
                    )
                    recurso_id = cur.fetchone()[0]

                    # Authors
                    orden = 1
                    for nombre in data["autores"]:
                        cur.execute("SELECT id FROM autores WHERE nombre_autor=%s", (nombre,))
                        a = cur.fetchone()
                        if not a:
                            cur.execute("INSERT INTO autores (nombre_autor) VALUES (%s) RETURNING id", (nombre,))
                            autor_id = cur.fetchone()[0]
                        else:
                            autor_id = a[0]
                        cur.execute(
                            "INSERT INTO recurso_autor (recurso_id, autor_id, orden) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                            (recurso_id, autor_id, orden),
                        )
                        orden += 1

                    # Tags
                    # Note: Tag normalization should happen in Service layer before calling Repository
                    for tag in data["etiquetas"]:
                        cur.execute("SELECT id FROM etiquetas WHERE nombre_etiqueta=%s", (tag,))
                        e = cur.fetchone()
                        if not e:
                            cur.execute("INSERT INTO etiquetas (nombre_etiqueta) VALUES (%s) RETURNING id", (tag,))
                            etiqueta_id = cur.fetchone()[0]
                        else:
                            etiqueta_id = e[0]
                        cur.execute(
                            "INSERT INTO recurso_etiqueta (recurso_id, etiqueta_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                            (recurso_id, etiqueta_id),
                        )
                    
                    return recurso_id
        finally:
            conn.close()

    def upload_file(self, file_bytes: bytes, filename: str) -> str:
        # Use Supabase Facade
        # Generate unique path
        import uuid
        path = f"uploads/{uuid.uuid4()}_{filename}"
        bucket = "recursos-alojados" # Should be in config
        
        # Upload
        supabase_client.upload_file(bucket, path, file_bytes)
        
        # Get public URL
        return supabase_client.get_public_url(bucket, path)

