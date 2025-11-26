# -----------------------------------------------------------------------------
# UTILITY: Normalization
# -----------------------------------------------------------------------------
# Propósito:
# Proporcionar funciones para normalizar texto, útil para búsquedas y
# consistencia de datos (tags, autores, etc.).
#
# Funcionalidad:
# - Eliminación de acentos (NFD).
# - Conversión a minúsculas.
# - Limpieza de espacios.
# -----------------------------------------------------------------------------

import unicodedata


def normalize_tag(text: str) -> str:
    """
    Normalize a tag by:
    1. Converting to lowercase
    2. Removing accents/diacritics
    3. Stripping whitespace
    
    Examples:
        "Educación" -> "educacion"
        "Ética" -> "etica"
        "IA" -> "ia"
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove accents: NFD decomposition + filter out combining characters
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Strip whitespace
    text = text.strip()
    
    return text
