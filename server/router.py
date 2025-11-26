import re

# -----------------------------------------------------------------------------
# PATRÓN DE DISEÑO: ROUTER (Enrutador)
# -----------------------------------------------------------------------------
# ¿Por qué?
# Un servidor HTTP recibe peticiones crudas (GET /api/material/get?id=1).
# Necesitamos un mecanismo que diga: "Ah, esta URL corresponde a la función X".
#
# ¿Qué logramos?
# 1. Centralización: Todas las rutas están definidas en un solo lugar (o se registran
#    en un solo objeto).
# 2. Flexibilidad: Podemos usar expresiones regulares (Regex) para capturar parámetros
#    en la URL si quisiéramos (ej: /material/123).
# 3. Desacople: El servidor HTTP no sabe qué lógica ejecuta, solo le pasa la pelota
#    al Router, y el Router al Handler.
# -----------------------------------------------------------------------------

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, method, path_pattern, handler):
        """
        Registra una nueva ruta.
        :param method: GET, POST, PUT, DELETE, etc.
        :param path_pattern: Regex o string exacto de la ruta.
        :param handler: Función que procesará la petición.
        """
        self.routes.append({
            "method": method,
            "pattern": re.compile(f"^{path_pattern}$"),
            "handler": handler
        })

    def match(self, method, path):
        """
        Busca si existe una ruta registrada para el método y path dados.
        Retorna el handler y los parámetros capturados (si los hay).
        """
        for route in self.routes:
            if route["method"] == method or route["method"] == "*":
                match = route["pattern"].match(path)
                if match:
                    return route["handler"], match.groupdict()
        return None, None
