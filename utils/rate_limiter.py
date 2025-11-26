from datetime import datetime, timedelta
from typing import Dict, Tuple

# -----------------------------------------------------------------------------
# CAPA: UTILS / SECURITY (Rate Limiting)
# -----------------------------------------------------------------------------
# ¿Por qué?
# Las APIs públicas son vulnerables a ataques de denegación de servicio (DoS)
# o abuso (scraping masivo).
#
# ¿Qué logramos?
# 1. Protección: Limitamos cuántas peticiones puede hacer una IP en un tiempo dado.
# 2. Estabilidad: Evitamos que un solo usuario sature el servidor.
#
# Nota: Esta implementación en memoria se resetea si el servidor reinicia (o en
# Serverless Functions). Para producción robusta se usa Redis.
# -----------------------------------------------------------------------------

# Almacén en memoria (Diccionario: IP -> Lista de timestamps)
_rate_limit_store: Dict[str, list] = {}

def check_rate_limit(ip: str, max_requests: int = 10, window_minutes: int = 1) -> Tuple[bool, int]:
    """
    Verifica si una IP ha excedido el límite de peticiones.
    Algoritmo: Ventana deslizante simple.
    
    Args:
        ip: IP del cliente.
        max_requests: Máximo de peticiones permitidas en la ventana.
        window_minutes: Tamaño de la ventana de tiempo en minutos.
        
    Returns:
        (is_allowed, remaining_requests)
    """
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # Get or create request history for this IP
    if ip not in _rate_limit_store:
        _rate_limit_store[ip] = []
    
    # Remove old requests outside the window (Limpieza)
    _rate_limit_store[ip] = [
        req_time for req_time in _rate_limit_store[ip]
        if req_time > window_start
    ]
    
    # Check if limit exceeded
    current_count = len(_rate_limit_store[ip])
    
    if current_count >= max_requests:
        return False, 0
    
    # Add this request
    _rate_limit_store[ip].append(now)
    
    remaining = max_requests - current_count - 1
    return True, remaining


def get_client_ip(headers) -> str:
    """
    Extrae la IP real del cliente desde los headers.
    Soporta proxies (X-Forwarded-For) comunes en Vercel/AWS.
    """
    # Try various headers
    ip = (
        headers.get('x-forwarded-for', '').split(',')[0].strip() or
        headers.get('x-real-ip', '') or
        headers.get('remote-addr', '') or
        'unknown'
    )
    
    return ip
