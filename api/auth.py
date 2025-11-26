# -----------------------------------------------------------------------------
# ARCHIVO LEGACY (OBSOLETO)
# -----------------------------------------------------------------------------
# ESTE ARCHIVO YA NO SE USA EN LA NUEVA ARQUITECTURA.
#
# Reemplazo:
# La lógica de verificación de tokens se ha movido a:
# -> `utils/auth.py`
#
# Razón:
# Centralizar la seguridad en un módulo de utilidades reutilizable, en lugar
# de tener scripts sueltos en la carpeta api/.
# -----------------------------------------------------------------------------

import os
import jwt  # Requiere: pip install PyJWT

# Obtenemos el secreto desde las variables de entorno (Anexo B de tu PDF)
JWT_SECRET = os.environ.get("JWT_SECRET", "")

def verify_token(headers):
    """
    Verifica que el Authorization header contenga un JWT válido firmado por Supabase.
    Retorna True si es válido, False en caso contrario.
    """
    auth = headers.get("authorization") or headers.get("Authorization")
    
    # 1. Validación básica de formato
    if not auth or not auth.lower().startswith("bearer "):
        print("Error Auth: Header faltante o formato incorrecto")
        return False
    
    token = auth.split(" ", 1)[1].strip()
    
    if not JWT_SECRET:
        print("Error Auth: JWT_SECRET no configurado en entorno")
        return False

    try:
        # 2. Decodificar y verificar firma
        # Supabase usa algoritmo HS256 y el JWT_SECRET para firmar
        decoded = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated", # Verifica que sea un usuario logueado
            options={"verify_exp": True} # Verifica que no haya expirado
        )
        
        # Opcional: Si quisieras saber QUIÉN es el usuario, está en decoded['sub']
        # print(f"Usuario autenticado: {decoded.get('sub')}")
        
        return True

    except jwt.ExpiredSignatureError:
        print("Error Auth: El token ha expirado")
        return False
    except jwt.InvalidTokenError as e:
        print(f"Error Auth: Token inválido - {str(e)}")
        return False
    except Exception as e:
        print(f"Error Auth: {str(e)}")
        return False
