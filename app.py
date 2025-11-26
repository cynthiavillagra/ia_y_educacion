from server.http_server import RequestHandler, run_server
from server.material_handler import handle_get_material, handle_list_materials, handle_upload_material, handle_options
from config.settings import PORT

# Register routes
RequestHandler.router.add_route("GET", "/api/material/get", handle_get_material)
RequestHandler.router.add_route("GET", "/api/material/list", handle_list_materials)
RequestHandler.router.add_route("POST", "/api/material/upload", handle_upload_material)
RequestHandler.router.add_route("OPTIONS", "/api/material/.*", handle_options)

# Legacy routes support (optional, for backward compatibility during migration)
RequestHandler.router.add_route("GET", "/api/recurso_detalle", handle_get_material)
RequestHandler.router.add_route("GET", "/api/search", handle_list_materials)
RequestHandler.router.add_route("POST", "/api/admin/ingestion", handle_upload_material)

if __name__ == "__main__":
    run_server(PORT)
