import json

class Response:
    @staticmethod
    def json(handler, data, status=200):
        handler.send_response(status)
        handler.send_header('Content-type', 'application/json')
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode())

    @staticmethod
    def error(handler, message, status=500):
        Response.json(handler, {"error": message}, status)
