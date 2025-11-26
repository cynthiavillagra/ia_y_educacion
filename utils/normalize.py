import unicodedata

# -----------------------------------------------------------------------------
# CAPA: UTILS / NORMALIZATION (Normalización)
# -----------------------------------------------------------------------------
# ¿Por qué?
# Los usuarios escriben "Ética", "etica", "ETICA", " Ética ".
# Para la búsqueda y el ordenamiento, necesitamos un formato canónico.
#
# ¿Qué logramos?
# 1. Consistencia: Guardamos siempre en minúsculas y sin acentos (para tags).
# 2. Búsqueda Efectiva: Al buscar "etica" encontramos "Ética".
# -----------------------------------------------------------------------------

def normalize_tag(text: str) -> str:
    """
    Normaliza una etiqueta (tag) para almacenamiento consistente.
    
    Pasos:
    1. Convertir a minúsculas.
    2. Eliminar acentos/diacríticos (NFD decomposition).
    3. Eliminar espacios extra.
    
    Ejemplos:
        "Educación" -> "educacion"
        "Ética" -> "etica"
        "IA" -> "ia"
    """
    if not text:
        return ""
    
    # 1. Convertir a minúsculas
    text = text.lower()
    
    # 2. Eliminar acentos: Descomponemos caracteres (á -> a + ´) y filtramos los combinables
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # 3. Eliminar espacios al inicio y final
    text = text.strip()
    
    return text
