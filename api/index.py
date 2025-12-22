from flask import Flask, request, jsonify
from server.material_handler import material_service
import traceback

app = Flask(__name__)

# -----------------------------------------------------------------------------
# FLASK APP: Nueva Arquitectura V2 (Robusta y Standard)
# -----------------------------------------------------------------------------

@app.route('/api/search', methods=['GET'])
def search_materials():
    """Endpoint unificado de búsqueda"""
    try:
        q = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        order = request.args.get('orden', 'relevancia')
        
        # Filtros
        filters = {
            "autor": request.args.get('autor', '').strip(),
            "anio": request.args.get('anio', '').strip(),
            "fuente": request.args.get('fuente', '').strip(),
            "tipo": request.args.get('tipo', '').strip(),
            "tema": request.args.get('tema', '').strip(),
        }

        result = material_service.search_materials(q, filters, page, per_page, order)
        return jsonify(result)
    except Exception as e:
        print(traceback.format_exc()) # Log server side
        return jsonify({"error": str(e)}), 500

@app.route('/api/recurso_detalle', methods=['GET'])
def get_material():
    """Obtener detalle de recurso por ID"""
    try:
        mid = request.args.get('id')
        if not mid:
            return jsonify({"error": "Missing id"}), 400
            
        material = material_service.get_material(mid)
        if material:
            return jsonify(material.to_dict())
        else:
            return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/ingestion', methods=['POST'])
def ingestion():
    """Subida de nuevos recursos (Admin)"""
    # TODO: Validar Token Auth aquí si es necesario, o usar wrapper
    try:
        data = request.form.to_dict()
        file = request.files.get('archivo')
        
        file_bytes = None
        filename = None
        if file:
            file_bytes = file.read()
            filename = file.filename
            
        recurso_id = material_service.upload_material(data, file_bytes, filename)
        return jsonify({"id": recurso_id, "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint de compatibilidad para evitar 404s
@app.route('/api/material/list', methods=['GET'])
def compat_list():
    return search_materials()

# Para Vercel (exponemos 'app' como variable global)
# No necesitamos if __name__ == '__main__' porque Vercel importa 'app'