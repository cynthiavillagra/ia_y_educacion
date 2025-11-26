"""
# -----------------------------------------------------------------------------
# UTILITY: Rate Limiter
# -----------------------------------------------------------------------------
# Propósito:
# Implementar un limitador de tasa simple en memoria para proteger los endpoints
# de abusos básicos o ataques de denegación de servicio (DoS).
#
# Patrón:
# Token Bucket (simplificado) / Ventana deslizante.
#
# Nota:
# Al ser "in-memory", el estado se pierde si el servidor se reinicia (o en Serverless
# cuando la instancia se recicla). Para producción distribuida, se usaría Redis.
# -----------------------------------------------------------------------------

Simple rate limiting for serverless functions
Uses in-memory storage (resets per cold start, but provides basic protection)
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple

# In-memory store (resets on cold start)
_rate_limit_store: Dict[str, list] = {}

def check_rate_limit(ip: str, max_requests: int = 10, window_minutes: int = 1) -> Tuple[bool, int]:
    """
    Check if IP has exceeded rate limit
    
    Args:
        ip: Client IP address
        max_requests: Maximum requests allowed in window
        window_minutes: Time window in minutes
        
    Returns:
        Tuple of (is_allowed, remaining_requests)
    """
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # Get or create request history for this IP
    if ip not in _rate_limit_store:
        _rate_limit_store[ip] = []
    
    # Remove old requests outside the window
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
    Extract client IP from headers
    Vercel provides this in x-forwarded-for or x-real-ip
    """
    # Try various headers
    ip = (
        headers.get('x-forwarded-for', '').split(',')[0].strip() or
        headers.get('x-real-ip', '') or
        headers.get('remote-addr', '') or
        'unknown'
    )
    
    return ip
