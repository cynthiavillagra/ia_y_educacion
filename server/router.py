import re

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, method, path_pattern, handler):
        self.routes.append({
            "method": method,
            "pattern": re.compile(f"^{path_pattern}$"),
            "handler": handler
        })

    def match(self, method, path):
        for route in self.routes:
            if route["method"] == method or route["method"] == "*":
                match = route["pattern"].match(path)
                if match:
                    return route["handler"], match.groupdict()
        return None, None
