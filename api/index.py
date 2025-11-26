# En su lugar, Vercel busca una variable `handler` que sea una clase HTTP.
# Cuando llega una petición, Vercel instancia esa clase y maneja UN solo request.
#
# ¿Qué logramos?
# Adaptamos nuestro "Monolito Modular" para que funcione en la nube sin cambios
# drásticos. Reutilizamos toda la lógica de `server/` pero expuesta de la forma
# que Vercel espera.
# -----------------------------------------------------------------------------

# Registro de Rutas (igual que en app.py)
RequestHandler.router.add_route("GET", "/api/material/get", handle_get_material)
RequestHandler.router.add_route("GET", "/api/material/list", handle_list_materials)
RequestHandler.router.add_route("POST", "/api/material/upload", handle_upload_material)
RequestHandler.router.add_route("POST", "/api/material/upload", handle_upload_material)
RequestHandler.router.add_route("OPTIONS", "/api/material/.*", handle_options)
RequestHandler.router.add_route("GET", "/api/debug", handle_debug)

# Rutas Legacy
RequestHandler.router.add_route("GET", "/api/recurso_detalle", handle_get_material)
RequestHandler.router.add_route("GET", "/api/search", handle_list_materials)
RequestHandler.router.add_route("POST", "/api/admin/ingestion", handle_upload_material)

# Vercel busca esta variable 'handler'.
# Debe ser una clase que herede de BaseHTTPRequestHandler.
handler = RequestHandler