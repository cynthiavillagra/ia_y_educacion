from urllib.parse import parse_qs
import json
import cgi
from io import BytesIO
from services.material_service import MaterialService
from utils.response import Response

# -----------------------------------------------------------------------------
# PATRÓN DE DISEÑO: CONTROLLER / HANDLER (Controlador)
# -----------------------------------------------------------------------------
# ¿Por qué?
# El Servicio (`MaterialService`) no debe saber nada de HTTP (headers, JSON, query params).
# El Repositorio menos.
# Necesitamos una capa que "hable HTTP" y traduzca eso a llamadas al Servicio.
#
# ¿Qué logramos?
# 1. Separación de Protocolo: Si mañana queremos usar WebSockets o gRPC, el Servicio
#    no cambia. Solo creamos un nuevo Handler.
# 2. Manejo de Errores HTTP: Aquí decidimos si un error es 400 (Bad Request),
#    404 (Not Found) o 500 (Server Error).
# 3. Parsing: Aquí extraemos los datos del request (body, query params).
# -----------------------------------------------------------------------------

# Instanciamos el servicio una sola vez (Singleton implícito)
material_service = MaterialService()

def handle_get_material(handler, params):
    """
    Maneja GET /api/material/get?id=...
    """
    # 1. Extraer parámetros HTTP
    query_string = handler.path.split('?', 1)[1] if '?' in handler.path else ''
    qs = parse_qs(query_string)
    material_id = qs.get("id", [None])[0]
    
    if not material_id:
        Response.error(handler, "Missing id parameter", 400)
        return

    try:
        # 2. Llamar al Servicio (Lógica de Negocio)
        material = material_service.get_material(int(material_id))
        
        # 3. Formatear Respuesta HTTP
        if material:
            Response.json(handler, material.to_dict())
        else:
            Response.error(handler, "Material not found", 404)
    except Exception as e:
        Response.error(handler, str(e))

def handle_list_materials(handler, params):
    """
    Maneja GET /api/material/list?q=...
    """
    query_string = handler.path.split('?', 1)[1] if '?' in handler.path else ''
    qs = parse_qs(query_string)
    
    q = qs.get("q", [""])[0]
    page = int(qs.get("page", [1])[0])
    per_page = int(qs.get("per_page", [20])[0])
    
    filters = {
        "autor": qs.get("autor", [""])[0].strip(),
        "anio": qs.get("anio", [""])[0].strip(),
        "coleccion": qs.get("coleccion", [""])[0].strip(),
        "tipo": qs.get("tipo", [""])[0].strip(),
    }
    order = qs.get("orden", ["relevancia"])[0].strip()

    try:
        result = material_service.search_materials(q, filters, page, per_page, order)
        Response.json(handler, result)
    except Exception as e:
        Response.error(handler, str(e))

def handle_upload_material(handler, params):
    """
    Maneja POST /api/material/upload
    Recibe Multipart Form Data (Archivos + JSON).
    """
    # 1. Verificar Autenticación (Middleware manual)
    from utils.auth import verify_token
    if not verify_token(handler.headers):
        Response.error(handler, "Unauthorized", 401)
        return
    
    # 2. Parsear Multipart (Complejo en HTTP puro, por eso usamos cgi)
    content_type = handler.headers.get('Content-Type', '')
    if 'multipart/form-data' not in content_type:
        Response.error(handler, "Content-Type must be multipart/form-data", 400)
        return

    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length)
    
    environ = {
        'REQUEST_METHOD': 'POST',
        'CONTENT_TYPE': content_type,
        'CONTENT_LENGTH': str(content_length)
    }
    
    fp = BytesIO(body)
    form = cgi.FieldStorage(fp=fp, environ=environ, keep_blank_values=True)
    
    data = {}
    file_bytes = None
    filename = None

    for key in form.keys():
        item = form[key]
        if item.filename:
            file_bytes = item.file.read()
            filename = item.filename
        else:
            data[key] = item.value

    # Parsear campos JSON que vienen como string en el form-data
    try:
        if "autores" in data:
            data["autores"] = json.loads(data["autores"]) if isinstance(data["autores"], str) else data["autores"]
        if "etiquetas" in data:
            data["etiquetas"] = json.loads(data["etiquetas"]) if isinstance(data["etiquetas"], str) else data["etiquetas"]
    except Exception:
        pass

    try:
        # 3. Llamar al Servicio
        recurso_id = material_service.upload_material(data, file_bytes, filename)
        Response.json(handler, {"id": str(recurso_id), "success": True})
    except Exception as e:
        Response.error(handler, str(e), 400)

def handle_options(handler, params):
    """Manejo de CORS Preflight"""
    Response.json(handler, {}, 200)
