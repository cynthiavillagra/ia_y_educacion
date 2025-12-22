import json
from typing import List, Optional, Dict, Any
from utils.db import get_connection
from repositories.supabase_client import supabase_client
from domain.material import Material
from adapters.material_adapter import to_material

# -----------------------------------------------------------------------------
# REPOSITORIO v2: Adaptado a esquema plano (Metadatos v2)
# -----------------------------------------------------------------------------

class MaterialRepository:
    def get_by_id(self, material_id: str) -> Optional[Material]:
        """
        Busca un recurso por su ID visible (SAIA-EDU-xxx).
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        id, titulo, titulo_original, tipo_recurso, descripcion_resumen,
                        autores, institucion_autora, institucion_fuente, editorial_o_fuente,
                        anio_publicacion, fecha_publicacion, pais_origen, idioma, doi, isbn_issn, numero_paginas,
                        url_fuente_original, url_pdf_directo, archivo_local, url_archivo_local, tipo_acceso, licencia, formato,
                        palabras_clave, areas_tematicas, nivel, tipo_publico, contexto_geografico,
                        proporcionado_por, agregado_por, fecha_incorporacion_repo, estado_revision, revisado_por, observaciones
                    FROM recursos
                    WHERE id = %s
                    """,
                    (material_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                
                # Mapeo directo a objeto Material (asumiendo orden correcto)
                # Al ser una tabla plana, el mapeo es 1:1.
                # Validar tipos (fechas a str si hace falta)
                return Material(
                    id=row[0], titulo=row[1], titulo_original=row[2], tipo_recurso=row[3], descripcion_resumen=row[4],
                    autores=row[5], institucion_autora=row[6], institucion_fuente=row[7], editorial_o_fuente=row[8],
                    anio_publicacion=row[9], fecha_publicacion=str(row[10]) if row[10] else None, 
                    pais_origen=row[11], idioma=row[12], doi=row[13], isbn_issn=row[14], numero_paginas=row[15],
                    url_fuente_original=row[16], url_pdf_directo=row[17], archivo_local=row[18], url_archivo_local=row[19],
                    tipo_acceso=row[20], licencia=row[21], formato=row[22],
                    palabras_clave=row[23], areas_tematicas=row[24], nivel=row[25], tipo_publico=row[26], contexto_geografico=row[27],
                    proporcionado_por=row[28], agregado_por=row[29], fecha_incorporacion_repo=str(row[30]) if row[30] else None,
                    estado_revision=row[31], revisado_por=row[32], observaciones=row[33]
                )
        finally:
            conn.close()

    def search(self, query: str, filters: Dict[str, Any], page: int = 1, per_page: int = 20, order: str = "relevancia") -> Dict[str, Any]:
        offset = (page - 1) * per_page
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql_filters = []
                query_params = []
                
                # Filtros dinámicos (v2)
                if filters.get("autor"):
                    sql_filters.append("autores ILIKE %s")
                    query_params.append(f"%{filters.get('autor')}%")
                
                if filters.get("anio"):
                    sql_filters.append("anio_publicacion = %s")
                    query_params.append(int(filters.get("anio")))
                
                if filters.get("fuente"):
                    sql_filters.append("institucion_fuente ILIKE %s")
                    query_params.append(f"%{filters.get('fuente')}%")
                
                if filters.get("tipo"):
                    sql_filters.append("tipo_recurso = %s")
                    query_params.append(filters.get("tipo"))

                if filters.get("tema"):
                    sql_filters.append("(palabras_clave ILIKE %s OR areas_tematicas ILIKE %s)")
                    val = f"%{filters.get('tema')}%"
                    query_params.append(val)
                    query_params.append(val)

                where_clause = (" AND ".join(sql_filters)) if sql_filters else "TRUE"

                # 1. Total (Paginación)
                # Usamos la función buscar_recursos que ya encapsula FTS si hay query, o nada si no la hay.
                # PERO buscar_recursos devuelve (id, titulo...)
                # Si hay texto de búsqueda, unimos con el resultado de la función.
                # Si NO hay texto, filtramos directo la tabla.
                
                if query and query.strip():
                    base_from = "buscar_recursos(%s) sr JOIN recursos r ON r.id = sr.id"
                    base_params = [query]
                else:
                    base_from = "recursos r"
                    base_params = []
                
                # Total Count
                count_sql = f"SELECT COUNT(*) FROM {base_from} WHERE {where_clause}"
                cur.execute(count_sql, base_params + query_params)
                total = cur.fetchone()[0]

                # 2. Orden
                if order == "anio_asc":
                    order_sql = "r.anio_publicacion ASC"
                elif order == "anio_desc":
                    order_sql = "r.año_publicacion DESC" # Ojo con el nombre de col si cambia en DB
                elif order == "recientes":
                    order_sql = "r.fecha_incorporacion_repo DESC"
                else:
                    # Si hay búsqueda FTS, score DESC. Si no, recientes.
                    order_sql = "sr.score DESC" if query and query.strip() else "r.fecha_incorporacion_repo DESC"

                # 3. Items
                if query and query.strip():
                     select_cols = "sr.id, r.titulo, r.anio_publicacion, sr.score, r.descripcion_resumen, r.tipo_recurso, r.autores, r.palabras_clave, r.institucion_fuente"
                else:
                     select_cols = "r.id, r.titulo, r.anio_publicacion, 0.0 as score, r.descripcion_resumen, r.tipo_recurso, r.autores, r.palabras_clave, r.institucion_fuente"

                items_sql = f"""
                    SELECT {select_cols}
                    FROM {base_from}
                    WHERE {where_clause}
                    ORDER BY {order_sql}
                    LIMIT %s OFFSET %s
                """
                
                full_params = base_params + query_params + [per_page, offset]
                cur.execute(items_sql, full_params)
                rows = cur.fetchall()

                items = [
                    {
                        "id": r[0], 
                        "titulo": r[1], 
                        "anio_publicacion": r[2], 
                        "score": float(r[3]),
                        "resumen": r[4],
                        "tipo_recurso": r[5],
                        "autores": r[6], # Ya viene como string plano
                        "etiquetas": r[7], # Ya viene como string plano
                        "institucion": r[8]
                    }
                    for r in rows
                ]
                return {"total": total, "items": items}
        finally:
            conn.close()

    def create(self, data: Material) -> str:
        """
        Inserta un nuevo recurso (simple INSERT).
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO recursos (
                        id, titulo, titulo_original, tipo_recurso, descripcion_resumen,
                        autores, institucion_autora, institucion_fuente, editorial_o_fuente,
                        anio_publicacion, fecha_publicacion, pais_origen, idioma, doi, isbn_issn, numero_paginas,
                        url_fuente_original, url_pdf_directo, archivo_local, url_archivo_local, tipo_acceso, licencia, formato,
                        palabras_clave, areas_tematicas, nivel, tipo_publico, contexto_geografico,
                        proporcionado_por, agregado_por, estado_revision, revisado_por, observaciones
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    RETURNING id
                    """,
                    (
                        data.id, data.titulo, data.titulo_original, data.tipo_recurso, data.descripcion_resumen,
                        data.autores, data.institucion_autora, data.institucion_fuente, data.editorial_o_fuente,
                        data.anio_publicacion, data.fecha_publicacion, data.pais_origen, data.idioma, data.doi, data.isbn_issn, data.numero_paginas,
                        data.url_fuente_original, data.url_pdf_directo, data.archivo_local, data.url_archivo_local, data.tipo_acceso, data.licencia, data.formato,
                        data.palabras_clave, data.areas_tematicas, data.nivel, data.tipo_publico, data.contexto_geografico,
                        data.proporcionado_por, data.agregado_por, data.estado_revision, data.revisado_por, data.observaciones
                    )
                )
                conn.commit()
                return cur.fetchone()[0]
        finally:
            conn.close()

    
    def update(self, data: Material) -> bool:
        """
        Actualiza un recurso existente.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE recursos SET
                        titulo = %s, titulo_original = %s, tipo_recurso = %s, descripcion_resumen = %s,
                        autores = %s, institucion_autora = %s, institucion_fuente = %s, editorial_o_fuente = %s,
                        anio_publicacion = %s, fecha_publicacion = %s, pais_origen = %s, idioma = %s, doi = %s, isbn_issn = %s, numero_paginas = %s,
                        url_fuente_original = %s, url_pdf_directo = %s, archivo_local = %s, url_archivo_local = %s, tipo_acceso = %s, licencia = %s, formato = %s,
                        palabras_clave = %s, areas_tematicas = %s, nivel = %s, tipo_publico = %s, contexto_geografico = %s,
                        proporcionado_por = %s, estado_revision = %s, revisado_por = %s, observaciones = %s
                    WHERE id = %s
                    """,
                    (
                        data.titulo, data.titulo_original, data.tipo_recurso, data.descripcion_resumen,
                        data.autores, data.institucion_autora, data.institucion_fuente, data.editorial_o_fuente,
                        data.anio_publicacion, data.fecha_publicacion, data.pais_origen, data.idioma, data.doi, data.isbn_issn, data.numero_paginas,
                        data.url_fuente_original, data.url_pdf_directo, data.archivo_local, data.url_archivo_local, data.tipo_acceso, data.licencia, data.formato,
                        data.palabras_clave, data.areas_tematicas, data.nivel, data.tipo_publico, data.contexto_geografico,
                        data.proporcionado_por, data.estado_revision, data.revisado_por, data.observaciones,
                        data.id
                    )
                )
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()

    def upload_file(self, file_bytes: bytes, filename: str) -> str:
        import uuid
        path = f"uploads/{uuid.uuid4()}_{filename}"
        bucket = "recursos-alojados" 
        supabase_client.upload_file(bucket, path, file_bytes)
        return supabase_client.get_public_url(bucket, path)
