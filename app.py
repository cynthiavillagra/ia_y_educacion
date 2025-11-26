from server.http_server import RequestHandler, run_server
from server.material_handler import handle_get_material, handle_list_materials, handle_upload_material, handle_options
from server.debug_handler import handle_debug
from config.settings import PORT

# -----------------------------------------------------------------------------
# PUNTO DE ENTRADA (Entry Point)
# -----------------------------------------------------------------------------
# Este archivo es el "pegamento" que une todo.
# 1. Importa el Servidor y el Router.
# 2. Importa los Handlers (Controladores).
# 3. Define las rutas (mapea URL -> Handler).
# 4. Inicia el servidor.
# -----------------------------------------------------------------------------

# Registro de Rutas (Wiring)
# Aquí definimos qué función se ejecuta para cada URL.
# Es como el índice de un libro.

# Rutas de la API (Nuevas)
RequestHandler.router.add_route("GET", "/api/material/get", handle_get_material)
RequestHandler.router.add_route("GET", "/api/material/list", handle_list_materials)
RequestHandler.router.add_route("POST", "/api/material/upload", handle_upload_material)
RequestHandler.router.add_route("POST", "/api/material/upload", handle_upload_material)
RequestHandler.router.add_route("OPTIONS", "/api/material/.*", handle_options)
RequestHandler.router.add_route("GET", "/api/debug", handle_debug)

# Rutas Legacy (Compatibilidad con el frontend anterior)
# Esto permite que el frontend viejo siga funcionando sin cambios mientras migramos.
RequestHandler.router.add_route("GET", "/api/recurso_detalle", handle_get_material)
RequestHandler.router.add_route("GET", "/api/search", handle_list_materials)
RequestHandler.router.add_route("POST", "/api/admin/ingestion", handle_upload_material)

if __name__ == "__main__":
    # Solo se ejecuta si corremos `python app.py` directamente.
    # En Vercel, este bloque se ignora y se usa `api/index.py`.
    run_server(PORT)
