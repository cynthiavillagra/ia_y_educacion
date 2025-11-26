import os
import jwt

# -----------------------------------------------------------------------------
# CAPA: UTILS / SECURITY (Utilidades de Seguridad)
# -----------------------------------------------------------------------------
# ¿Por qué?
# La lógica de verificar un token JWT es técnica y repetitiva. No queremos ensuciar
# los Handlers con detalles de criptografía o librerías de terceros.
#
# ¿Qué logramos?
# 1. Reutilización: Podemos proteger cualquier endpoint llamando a `verify_token`.
# 2. Seguridad Centralizada: Si cambiamos el algoritmo de firma o la clave secreta,
#    solo tocamos este archivo.
# -----------------------------------------------------------------------------

JWT_SECRET = os.environ.get("JWT_SECRET", "")

def verify_token(headers):
    """
    Verifica que el Authorization header contenga un JWT válido firmado por Supabase.
    
    Flujo:
    1. Busca el header 'Authorization'.
    2. Extrae el token (quita el prefijo 'Bearer ').
    3. Usa la librería PyJWT para verificar la firma usando el JWT_SECRET de Supabase.
    
    Returns:
        True si el token es válido y no ha expirado.
        False si hay cualquier error.
    """
    auth = headers.get("authorization") or headers.get("Authorization")
    
    if not auth or not auth.lower().startswith("bearer "):
        return False
    
    token = auth.split(" ", 1)[1].strip()
    
    if not JWT_SECRET:
        # Log warning: JWT_SECRET not configured
        # En producción esto debería ser un error crítico
        return False

    try:
        # Decodificamos el token. Si la firma no coincide con JWT_SECRET,
        # o si el token expiró, esto lanzará una excepción.
        jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated", # Supabase usa este audience por defecto
            options={"verify_exp": True}
        )
        return True

    except Exception:
        # Cualquier error (token malformado, expirado, firma inválida) retorna False
        return False
