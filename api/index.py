"""
API Flask para Vercel - Versión Autocontenida
Este archivo contiene TODO lo necesario para funcionar sin dependencias internas.
"""
from flask import Flask, request, jsonify
import os
import psycopg2
import traceback

app = Flask(__name__)

# -----------------------------------------------------------------------------
# DATABASE CONNECTION (Inline)
# -----------------------------------------------------------------------------
def get_connection():
    """Crea conexión a PostgreSQL usando variables de entorno de Supabase."""
    raw_host = os.getenv("SUPABASE_DB_HOST", "")
    host = raw_host.strip().replace("https://", "").replace("http://", "")
    password = os.getenv("SUPABASE_DB_PASSWORD", "")
    
    if not host or not password:
        raise ValueError("SUPABASE_DB_HOST y SUPABASE_DB_PASSWORD son requeridas")
    
    port = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    dbname = os.getenv("SUPABASE_DB_NAME", "postgres")
    sslmode = os.getenv("SUPABASE_DB_SSLMODE", "require")
    
    return psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password, sslmode=sslmode
    )

# -----------------------------------------------------------------------------
# SEARCH ENDPOINT
# -----------------------------------------------------------------------------
@app.route('/api/search', methods=['GET'])
@app.route('/api/material/list', methods=['GET'])
def search_materials():
    """Búsqueda de recursos con filtros y paginación."""
    try:
        q = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        order = request.args.get('orden', 'relevancia')
        
        autor = request.args.get('autor', '').strip()
        anio = request.args.get('anio', '').strip()
        fuente = request.args.get('fuente', '').strip()
        tipo = request.args.get('tipo', '').strip()
        
        offset = (page - 1) * per_page
        
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Construir filtros dinámicos
                filters = []
                params = []
                
                if autor:
                    filters.append("autores ILIKE %s")
                    params.append(f"%{autor}%")
                if anio:
                    filters.append("anio_publicacion = %s")
                    params.append(int(anio))
                if fuente:
                    filters.append("institucion_fuente ILIKE %s")
                    params.append(f"%{fuente}%")
                if tipo:
                    filters.append("tipo_recurso = %s")
                    params.append(tipo)
                
                where_clause = " AND ".join(filters) if filters else "TRUE"
                
                # Búsqueda con o sin query de texto
                if q:
                    # Full-text search usando la función de la DB
                    base_sql = """
                        FROM buscar_recursos(%s) sr 
                        JOIN recursos r ON r.id = sr.id
                        WHERE {where}
                    """.format(where=where_clause)
                    base_params = [q] + params
                    
                    # Order
                    if order == "anio_asc":
                        order_sql = "r.anio_publicacion ASC NULLS LAST"
                    elif order == "anio_desc":
                        order_sql = "r.anio_publicacion DESC NULLS LAST"
                    elif order == "recientes":
                        order_sql = "r.fecha_incorporacion_repo DESC NULLS LAST"
                    else:
                        order_sql = "sr.score DESC"
                    
                    select_cols = """
                        sr.id, r.titulo, r.anio_publicacion, sr.score,
                        r.descripcion_resumen, r.tipo_recurso, r.autores,
                        r.palabras_clave, r.institucion_fuente
                    """
                else:
                    # Sin query, listado directo
                    base_sql = "FROM recursos r WHERE {where}".format(where=where_clause)
                    base_params = params
                    
                    if order == "anio_asc":
                        order_sql = "r.anio_publicacion ASC NULLS LAST"
                    elif order == "anio_desc":
                        order_sql = "r.anio_publicacion DESC NULLS LAST"
                    else:
                        order_sql = "r.fecha_incorporacion_repo DESC NULLS LAST"
                    
                    select_cols = """
                        r.id, r.titulo, r.anio_publicacion, 0.0 as score,
                        r.descripcion_resumen, r.tipo_recurso, r.autores,
                        r.palabras_clave, r.institucion_fuente
                    """
                
                # Total
                count_sql = f"SELECT COUNT(*) {base_sql}"
                cur.execute(count_sql, base_params)
                total = cur.fetchone()[0]
                
                # Items
                items_sql = f"""
                    SELECT {select_cols}
                    {base_sql}
                    ORDER BY {order_sql}
                    LIMIT %s OFFSET %s
                """
                cur.execute(items_sql, base_params + [per_page, offset])
                rows = cur.fetchall()
                
                items = [{
                    "id": r[0],
                    "titulo": r[1],
                    "anio_publicacion": r[2],
                    "score": float(r[3]) if r[3] else 0.0,
                    "descripcion_resumen": r[4],
                    "tipo_recurso": r[5],
                    "autores": r[6],
                    "etiquetas": r[7],
                    "institucion_fuente": r[8]
                } for r in rows]
                
        finally:
            conn.close()
        
        return jsonify({"total": total, "items": items})
        
    except Exception as e:
        print(f"ERROR in search: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# DETAIL ENDPOINT
# -----------------------------------------------------------------------------
@app.route('/api/recurso_detalle', methods=['GET'])
@app.route('/api/material/get', methods=['GET'])
def get_material():
    """Obtener detalle completo de un recurso."""
    try:
        mid = request.args.get('id')
        if not mid:
            return jsonify({"error": "Parámetro 'id' requerido"}), 400
        
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, titulo, titulo_original, tipo_recurso, descripcion_resumen,
                        autores, institucion_autora, institucion_fuente, editorial_o_fuente,
                        anio_publicacion, fecha_publicacion, pais_origen, idioma, doi, isbn_issn,
                        url_fuente_original, url_pdf_directo, archivo_local, url_archivo_local,
                        tipo_acceso, licencia, formato, palabras_clave, areas_tematicas,
                        proporcionado_por, agregado_por, fecha_incorporacion_repo, estado_revision
                    FROM recursos
                    WHERE id = %s
                """, (mid,))
                row = cur.fetchone()
                
                if not row:
                    return jsonify({"error": "Recurso no encontrado"}), 404
                
                result = {
                    "id": row[0],
                    "titulo": row[1],
                    "titulo_original": row[2],
                    "tipo_recurso": row[3],
                    "descripcion_resumen": row[4],
                    "autores": row[5],
                    "institucion_autora": row[6],
                    "institucion_fuente": row[7],
                    "editorial_o_fuente": row[8],
                    "anio_publicacion": row[9],
                    "fecha_publicacion": str(row[10]) if row[10] else None,
                    "pais_origen": row[11],
                    "idioma": row[12],
                    "doi": row[13],
                    "isbn_issn": row[14],
                    "url_fuente_original": row[15],
                    "url_pdf_directo": row[16],
                    "archivo_local": row[17],
                    "url_archivo_local": row[18],
                    "tipo_acceso": row[19],
                    "licencia": row[20],
                    "formato": row[21],
                    "palabras_clave": row[22],
                    "areas_tematicas": row[23],
                    "proporcionado_por": row[24],
                    "agregado_por": row[25],
                    "fecha_incorporacion_repo": str(row[26]) if row[26] else None,
                    "estado_revision": row[27]
                }
        finally:
            conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR in get_material: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# CONFIG ENDPOINT (para frontend Supabase Auth)
# -----------------------------------------------------------------------------
@app.route('/api/config', methods=['GET'])
def get_config():
    """Devuelve configuración pública para el frontend."""
    return jsonify({
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", "")
    })

# -----------------------------------------------------------------------------
# HEALTH CHECK
# -----------------------------------------------------------------------------
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# -----------------------------------------------------------------------------
# ADMIN: CREATE (Ingestion)
# -----------------------------------------------------------------------------
@app.route('/api/admin/ingestion', methods=['POST'])
def create_resource():
    """Crear nuevo recurso."""
    try:
        # TODO: Verificar token JWT aquí si es necesario
        # auth_header = request.headers.get('Authorization')
        
        # Obtener datos del formulario
        data = request.form.to_dict() if request.form else request.get_json() or {}
        
        # Generar ID único
        import uuid
        from datetime import date
        resource_id = f"SAIA-{uuid.uuid4().hex[:8].upper()}"
        
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO recursos (
                        id, titulo, titulo_original, tipo_recurso, descripcion_resumen,
                        autores, institucion_autora, institucion_fuente,
                        anio_publicacion, pais_origen, idioma, doi, isbn_issn,
                        url_fuente_original, archivo_local, tipo_acceso, licencia, formato,
                        palabras_clave, fecha_incorporacion_repo
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s
                    )
                    RETURNING id
                """, (
                    resource_id,
                    data.get('titulo'),
                    data.get('titulo_original'),
                    data.get('tipo_recurso', 'paper_academico'),
                    data.get('descripcion_resumen'),
                    data.get('autores'),
                    data.get('institucion_autora'),
                    data.get('institucion_fuente'),
                    int(data.get('anio_publicacion')) if data.get('anio_publicacion') else None,
                    data.get('pais_origen'),
                    data.get('idioma'),
                    data.get('doi'),
                    data.get('isbn_issn'),
                    data.get('url_fuente_original'),
                    data.get('archivo_local', 'false') == 'true',
                    data.get('tipo_acceso', 'abierto'),
                    data.get('licencia'),
                    data.get('formato'),
                    data.get('palabras_clave'),
                    date.today()
                ))
                conn.commit()
                new_id = cur.fetchone()[0]
        finally:
            conn.close()
        
        return jsonify({"id": new_id, "success": True})
        
    except Exception as e:
        print(f"ERROR in create_resource: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# ADMIN: UPDATE
# -----------------------------------------------------------------------------
@app.route('/api/admin/update', methods=['PUT', 'POST'])
def update_resource():
    """Actualizar recurso existente."""
    try:
        data = request.get_json() or {}
        resource_id = data.get('id')
        
        if not resource_id:
            return jsonify({"error": "ID requerido"}), 400
        
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE recursos SET
                        titulo = %s,
                        titulo_original = %s,
                        tipo_recurso = %s,
                        descripcion_resumen = %s,
                        autores = %s,
                        institucion_autora = %s,
                        institucion_fuente = %s,
                        anio_publicacion = %s,
                        pais_origen = %s,
                        idioma = %s,
                        doi = %s,
                        isbn_issn = %s,
                        url_fuente_original = %s,
                        tipo_acceso = %s,
                        licencia = %s,
                        formato = %s,
                        palabras_clave = %s
                    WHERE id = %s
                """, (
                    data.get('titulo'),
                    data.get('titulo_original'),
                    data.get('tipo_recurso'),
                    data.get('descripcion_resumen'),
                    data.get('autores'),
                    data.get('institucion_autora'),
                    data.get('institucion_fuente'),
                    int(data.get('anio_publicacion')) if data.get('anio_publicacion') else None,
                    data.get('pais_origen'),
                    data.get('idioma'),
                    data.get('doi'),
                    data.get('isbn_issn'),
                    data.get('url_fuente_original'),
                    data.get('tipo_acceso'),
                    data.get('licencia'),
                    data.get('formato'),
                    data.get('palabras_clave'),
                    resource_id
                ))
                conn.commit()
                updated = cur.rowcount > 0
        finally:
            conn.close()
        
        if updated:
            return jsonify({"success": True, "id": resource_id})
        else:
            return jsonify({"error": "Recurso no encontrado"}), 404
        
    except Exception as e:
        print(f"ERROR in update_resource: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# ADMIN: DELETE
# -----------------------------------------------------------------------------
@app.route('/api/admin/delete', methods=['DELETE'])
def delete_resource():
    """Eliminar recurso."""
    try:
        resource_id = request.args.get('id')
        
        if not resource_id:
            return jsonify({"error": "ID requerido"}), 400
        
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recursos WHERE id = %s", (resource_id,))
                conn.commit()
                deleted = cur.rowcount > 0
        finally:
            conn.close()
        
        if deleted:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Recurso no encontrado"}), 404
        
    except Exception as e:
        print(f"ERROR in delete_resource: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# Para Vercel: exportamos 'app'