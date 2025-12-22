from urllib.parse import parse_qs, unquote
import json
import cgi
from io import BytesIO
from services.material_service import MaterialService
from utils.response import Response

# -----------------------------------------------------------------------------
# HANDLER V2: Interface HTTP para Metadatos v2
# -----------------------------------------------------------------------------

material_service = MaterialService()

def handle_get_material(handler, params):
    """GET /api/material/get?id=..."""
    query_string = handler.path.split('?', 1)[1] if '?' in handler.path else ''
    qs = parse_qs(query_string)
    material_id = qs.get("id", [None])[0]
    
    if not material_id:
        Response.error(handler, "Missing id parameter", 400)
        return

    try:
        # ID es string ahora
        material = material_service.get_material(material_id)
        if material:
            Response.json(handler, material.to_dict())
        else:
            Response.error(handler, "Material not found", 404)
    except Exception as e:
        Response.error(handler, str(e))

def handle_list_materials(handler, params):
    """GET /api/material/list?q=..."""
    query_string = handler.path.split('?', 1)[1] if '?' in handler.path else ''
    qs = parse_qs(query_string)
    
    q = unquote(qs.get("q", [""])[0])
    page = int(qs.get("page", [1])[0])
    per_page = int(qs.get("per_page", [20])[0])
    
    # Mapeo de filtros query param -> servicio
    # Soportamos legacy 'coleccion' mapeando a 'fuente'
    filters = {
        "autor": unquote(qs.get("autor", [""])[0]).strip(),
        "anio": qs.get("anio", [""])[0].strip(),
        "fuente": unquote(qs.get("fuente", [qs.get("coleccion", [""])[0]])[0]).strip(),
        "tipo": unquote(qs.get("tipo", [""])[0]).strip(),
        "tema": unquote(qs.get("tema", [""])[0]).strip(),
    }
    order = qs.get("orden", ["relevancia"])[0].strip()

    try:
        result = material_service.search_materials(q, filters, page, per_page, order)
        Response.json(handler, result)
    except Exception as e:
        Response.error(handler, str(e))

def _parse_multipart(handler):
    content_type = handler.headers.get('Content-Type', '')
    if 'multipart/form-data' not in content_type:
        raise ValueError("Content-Type must be multipart/form-data")

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
            # Decode bytes to utf-8 string
            value = item.value
            if isinstance(value, bytes):
                value = value.decode('utf-8') 
            data[key] = value
            
    return data, file_bytes, filename

def handle_upload_material(handler, params):
    """POST /api/material/upload"""
    # TODO: Auth check
    try:
        data, file_bytes, filename = _parse_multipart(handler)
        recurso_id = material_service.upload_material(data, file_bytes, filename)
        Response.json(handler, {"id": recurso_id, "success": True})
    except Exception as e:
        Response.error(handler, str(e), 400)

def handle_update_material(handler, params):
    """POST /api/material/update"""
    try:
        data, file_bytes, filename = _parse_multipart(handler)
        
        mid = data.get("id")
        if not mid:
            raise ValueError("ID requerido para update")
            
        success = material_service.update_material(mid, data, file_bytes, filename)
        Response.json(handler, {"success": success, "id": mid})
    except Exception as e:
        Response.error(handler, str(e), 400)

def handle_options(handler, params):
    Response.json(handler, {}, 200)
