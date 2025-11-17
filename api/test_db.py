from utils.db_connector import get_connection

def handler(request):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
        return {"ok": True, "db_response": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}
