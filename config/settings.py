import os
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# CAPA: CONFIGURATION (Configuración)
# -----------------------------------------------------------------------------
# ¿Por qué?
# No queremos "hardcodear" (escribir fijo en el código) claves secretas ni URLs.
# Usamos variables de entorno (.env) para que:
# 1. Sea seguro: No subimos las claves a GitHub.
# 2. Sea flexible: En local usamos una DB, en producción otra, solo cambiando el .env.
#
# ¿Qué logramos?
# Centralizamos la lectura de configuración. Si mañana cambiamos cómo se lee
# una variable, solo tocamos este archivo.
# -----------------------------------------------------------------------------

# Carga las variables del archivo .env al entorno de Python
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 8000))
