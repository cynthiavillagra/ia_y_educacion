import os

SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

def verify_token(headers):
    """
    Verify the Authorization header against the Supabase Service Key.
    Returns True if valid, False otherwise.
    """
    auth = headers.get("authorization") or headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return False
    token = auth.split(" ", 1)[1].strip()
    return token == SERVICE_KEY
