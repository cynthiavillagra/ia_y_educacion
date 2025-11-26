from urllib.parse import parse_qs
import json
import cgi
from io import BytesIO
from services.material_service import MaterialService
from utils.response import Response

material_service = MaterialService()

def handle_get_material(handler, params):
    query_string = handler.path.split('?', 1)[1] if '?' in handler.path else ''
    qs = parse_qs(query_string)
    material_id = qs.get("id", [None])[0]
    
    if not material_id:
        Response.error(handler, "Missing id parameter", 400)
        return

    try:
        material = material_service.get_material(int(material_id))
        if material:
            Response.json(handler, material.to_dict())
        else:
            Response.error(handler, "Material not found", 404)
    except Exception as e:
        Response.error(handler, str(e))

def handle_list_materials(handler, params):
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
    from utils.auth import verify_token
    if not verify_token(handler.headers):
        Response.error(handler, "Unauthorized", 401)
        return
    
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

    # Parse JSON fields
    try:
        if "autores" in data:
            data["autores"] = json.loads(data["autores"]) if isinstance(data["autores"], str) else data["autores"]
        if "etiquetas" in data:
            data["etiquetas"] = json.loads(data["etiquetas"]) if isinstance(data["etiquetas"], str) else data["etiquetas"]
    except Exception:
        pass

    try:
        recurso_id = material_service.upload_material(data, file_bytes, filename)
        Response.json(handler, {"id": str(recurso_id), "success": True})
    except Exception as e:
        Response.error(handler, str(e), 400)

def handle_options(handler, params):
    Response.json(handler, {}, 200)
