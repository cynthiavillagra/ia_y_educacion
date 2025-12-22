from server.http_server import RequestHandler
from server.material_handler import handle_list_materials

# -----------------------------------------------------------------------------
# ARCHIVO PUENTE PARA VERCEL (Search)
# -----------------------------------------------------------------------------
# Debido a que la redirección por rewrites a veces falla o cachea rutas antiguas,
# creamos explícitamente este archivo para asegurar que /api/search exista físicamente.
# Importamos el mismo handler robusto del router principal.
# -----------------------------------------------------------------------------

# Vercel instanciará esta clase.
# RequestHandler ya tiene el router configurado globalmente en su definición de clase.
# Sin embargo, para estar 100% seguros de que la ruta /api/search se registra 
# si Vercel carga este archivo de forma aislada:

# Nos aseguramos de registrar la ruta si no existe, aunque sea redundante.
RequestHandler.router.add_route("GET", "/api/search", handle_list_materials)

# Exponemos el handler
handler = RequestHandler
