import os
import json
import uuid
import requests
from utils.db_connector import get_connection

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET", "recursos-alojados")
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default


def _auth_ok(request):
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return False
    token = auth.split(" ", 1)[1].strip()
    return token == SERVICE_KEY


def _upload_to_storage(file_bytes: bytes, filename: str) -> str:
    """Upload file to Supabase Storage and return public URL."""
    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
    path = f"uploads/{uuid.uuid4()}_{filename}"
    url = f"https://{project_ref}.supabase.co/storage/v1/object/{STORAGE_BUCKET}/{path}"
    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/octet-stream",
    }
    r = requests.post(url, headers=headers, data=file_bytes)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Storage upload failed: {r.status_code} {r.text}")

    # Public URL
    public_url = f"https://{project_ref}.supabase.co/storage/v1/object/public/{STORAGE_BUCKET}/{path}"
    return public_url


def handler(request):
    if request.method != "POST":
        return {"error": "Method not allowed"}

    if not _auth_ok(request):
        return {"error": "Unauthorized"}

    # Expect multipart/form-data
    form = request.form or {}
    files = request.files or {}

    # Parse arrays that arrive stringified
    autores = form.get("autores", "[]")
    etiquetas = form.get("etiquetas", "[]")
    try:
        autores = json.loads(autores) if isinstance(autores, str) else autores
        etiquetas = json.loads(etiquetas) if isinstance(etiquetas, str) else etiquetas
    except Exception:
        autores = []
        etiquetas = []

    estado = form.get("estado_alojamiento", "ORIGINAL").upper()

    url_descarga = form.get("url_descarga")
    archivo = files.get("archivo")

    if estado == "ALOJADO":
        if not archivo:
            return {"error": "archivo requerido para ALOJADO"}
        archivo_bytes = archivo.read()
        if len(archivo_bytes) > MAX_FILE_SIZE:
            return {"error": "archivo excede tamaño máximo"}
        try:
            url_descarga = _upload_to_storage(archivo_bytes, archivo.filename)
        except Exception as e:
            return {"error": f"upload error: {e}"}
    else:
        if not url_descarga:
            return {"error": "url_descarga requerida para ORIGINAL"}

    recurso = {
      "titulo": form.get("titulo", "").strip(),
      "resumen": form.get("resumen", ""),
      "codigo_documento": form.get("codigo_documento") or None,
      "año_publicacion": int(form.get("año_publicacion")),
      "estado_alojamiento": estado,
      "url_descarga": url_descarga,
      "licencia_cc": form.get("licencia_cc", "").strip(),
      "coleccion": form.get("coleccion", "").strip(),
      "tipo_documento": form.get("tipo_documento", "").strip(),
      "autores": autores,
      "etiquetas": etiquetas,
    }

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Colección -> id
                cur.execute("SELECT id FROM colecciones WHERE nombre=%s", (recurso["coleccion"],))
                row = cur.fetchone()
                if not row:
                    return {"error": "coleccion inexistente"}
                id_coleccion = row[0]

                # Insert recurso
                cur.execute(
                    """
                    INSERT INTO recursos (titulo, resumen, codigo_documento, año_publicacion, estado_alojamiento,
                                          url_descarga, licencia_cc, tipo_documento, id_coleccion)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                    """,
                    (
                        recurso["titulo"], recurso["resumen"], recurso["codigo_documento"], recurso["año_publicacion"],
                        recurso["estado_alojamiento"], recurso["url_descarga"], recurso["licencia_cc"],
                        recurso["tipo_documento"], id_coleccion,
                    ),
                )
                recurso_id = cur.fetchone()[0]

                # Autores (crear si no existen)
                orden = 1
                for nombre in recurso["autores"]:
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

                # Etiquetas (crear si no existen)
                for tag in recurso["etiquetas"]:
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
        return {"id": str(recurso_id)}
    finally:
        conn.close()
