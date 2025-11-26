import os
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "")

def verify_token(headers):
    """
    Verifies that the Authorization header contains a valid JWT signed by Supabase.
    Returns True if valid, False otherwise.
    """
    auth = headers.get("authorization") or headers.get("Authorization")
    
    if not auth or not auth.lower().startswith("bearer "):
        return False
    
    token = auth.split(" ", 1)[1].strip()
    
    if not JWT_SECRET:
        # Log warning: JWT_SECRET not configured
        return False

    try:
        jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True}
        )
        return True

    except Exception:
        return False
