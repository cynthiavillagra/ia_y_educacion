from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY

class SupabaseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            cls._instance.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

    def get_client(self) -> Client:
        return self.client

    def upload_file(self, bucket: str, path: str, file_data: bytes, content_type: str = "application/pdf"):
        return self.client.storage.from_(bucket).upload(
            path=path,
            file=file_data,
            file_options={"content-type": content_type, "upsert": "false"}
        )

    def get_public_url(self, bucket: str, path: str):
        return self.client.storage.from_(bucket).get_public_url(path)

    # Helper for DB operations if needed, though repositories might use client directly
    def table(self, table_name: str):
        return self.client.table(table_name)

# Global instance
supabase_client = SupabaseClient()
