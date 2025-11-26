from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY

# -----------------------------------------------------------------------------
# PATRÓN DE DISEÑO: FACADE (Fachada)
# -----------------------------------------------------------------------------
# ¿Por qué?
# Supabase tiene una librería compleja con muchos métodos. Si usamos `create_client`
# directamente en todos lados, acoplamos nuestro código a esa librería específica.
#
# ¿Qué logramos?
# 1. Simplificar: Proveemos métodos simples (`upload_file`, `get_public_url`) que
#    hacen exactamente lo que necesitamos, ocultando la complejidad de configuración.
# 2. Desacoplar: Si mañana cambiamos Supabase por AWS S3 o Firebase, solo cambiamos
#    este archivo. El resto del sistema ni se entera.
# 3. Singleton: Aseguramos que solo haya UNA instancia del cliente conectada.
# -----------------------------------------------------------------------------

class SupabaseClient:
    _instance = None

    def __new__(cls):
        # Implementación del patrón Singleton para reutilizar la conexión
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            # Inicializamos el cliente real de Supabase aquí
            cls._instance.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

    def get_client(self) -> Client:
        """Retorna el cliente crudo por si necesitamos acceso total."""
        return self.client

    def upload_file(self, bucket: str, path: str, file_data: bytes, content_type: str = "application/pdf"):
        """
        Método simplificado para subir archivos.
        Oculta los detalles de headers y opciones de la librería de Supabase.
        """
        return self.client.storage.from_(bucket).upload(
            path=path,
            file=file_data,
            file_options={"content-type": content_type, "upsert": "false"}
        )

    def get_public_url(self, bucket: str, path: str):
        """Obtiene la URL pública sin exponer la lógica interna del SDK."""
        return self.client.storage.from_(bucket).get_public_url(path)

    def table(self, table_name: str):
        """Acceso directo a tablas, útil para el Repositorio."""
        return self.client.table(table_name)

# Instancia global lista para usar (Singleton)
supabase_client = SupabaseClient()
