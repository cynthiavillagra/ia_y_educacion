import json
from datetime import datetime
import os

# -----------------------------------------------------------------------------
# CAPA: UTILS / LOGGING (Auditoría)
# -----------------------------------------------------------------------------
# ¿Por qué?
# En sistemas críticos, necesitamos saber "quién hizo qué y cuándo".
# Los logs de consola (print) se pierden. Necesitamos persistencia.
#
# ¿Qué logramos?
# 1. Trazabilidad: Si alguien borra un recurso, sabemos quién fue.
# 2. Debugging: Si algo falla, tenemos un historial de acciones previas.
# -----------------------------------------------------------------------------

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'admin_actions.log')

def log_admin_action(action: str, user_id: str, resource_id: str = None, details: dict = None):
    """
    Registra una acción administrativa en un archivo de log (JSON Lines).
    
    Args:
        action: Acción realizada (CREATE, UPDATE, DELETE).
        user_id: ID del usuario que realizó la acción.
        resource_id: ID del recurso afectado (si aplica).
        details: Diccionario con detalles adicionales.
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'user_id': user_id,
        'resource_id': resource_id,
        'details': details or {}
    }
    
    try:
        # Append to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        # Don't fail the request if logging fails
        print(f'Warning: Failed to log admin action: {e}')


def get_user_id_from_token(headers) -> str:
    """
    Extrae el ID de usuario del token (Placeholder).
    En producción, esto decodificaría el JWT para sacar el 'sub'.
    """
    # TODO: Decode JWT to get actual user ID
    auth_header = headers.get('Authorization', '')
    if auth_header:
        # For now, just return 'admin'
        # In production, decode JWT and extract user_id
        return 'admin'
    return 'unknown'
