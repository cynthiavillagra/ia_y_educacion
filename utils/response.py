import json

# -----------------------------------------------------------------------------
# CAPA: UTILS / HTTP (Ayudantes HTTP)
# -----------------------------------------------------------------------------
# ¿Por qué?
# En `BaseHTTPRequestHandler`, enviar una respuesta JSON requiere 4 o 5 líneas de código:
# poner status, poner headers, terminar headers, codificar JSON a bytes, escribir.
#
# ¿Qué logramos?
# 1. Código Limpio: En los handlers, en vez de 5 líneas, usamos 1: `Response.json(...)`.
# 2. Consistencia: Aseguramos que todas nuestras respuestas tengan los headers correctos
#    (ej: Content-Type: application/json, CORS).
# -----------------------------------------------------------------------------

class Response:
    @staticmethod
    def json(handler, data, status=200):
        """
        Envía una respuesta JSON estándar.
        :param handler: La instancia de BaseHTTPRequestHandler.
        :param data: Diccionario o lista para serializar a JSON.
        :param status: Código de estado HTTP (200, 400, 500, etc.).
        """
        handler.send_response(status)
        handler.send_header('Content-type', 'application/json')
        # CORS: Permitir acceso desde cualquier origen (útil para desarrollo/frontend separado)
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode())

    @staticmethod
    def error(handler, message, status=500):
        """
        Atajo para enviar un error JSON con formato {"error": "mensaje"}.
        """
        Response.json(handler, {"error": message}, status)
