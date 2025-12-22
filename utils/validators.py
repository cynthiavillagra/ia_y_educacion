import re
from datetime import datetime
from typing import Optional, Any

# -----------------------------------------------------------------------------
# CAPA: UTILS / VALIDATION (Validación)
# Actualizado para Metadatos v2
# -----------------------------------------------------------------------------

class ValidationError(Exception):
    pass

def validate_year(year: Any) -> Optional[int]:
    """Valida que el año sea razonable."""
    if year is None or str(year).strip() == "":
        return None
    try:
        y = int(year)
    except ValueError:
        raise ValidationError("El año debe ser un número entero")
        
    current_year = datetime.now().year
    if y < 1900 or y > current_year + 5: # Permitimos un poco de margen futuro
        raise ValidationError(f"El año invalido: {y}")
    return y

def validate_url(url: str, required: bool = True) -> Optional[str]:
    """Valida formato de URL."""
    if not url:
        if required:
            raise ValidationError("URL requerida")
        return None
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("La URL debe comenzar con http:// o https://")
    return url

def validate_tipo_recurso(tipo: str) -> str:
    """Valida tipo de recurso contra la lista controlada v2."""
    validos = [
        'paper_academico', 'libro', 'capitulo_libro', 'informe', 'guia', 
        'normativa', 'diseno_curricular', 'articulo_web', 'web_institucional', 
        'material_docente', 'boletin', 'dataset', 'presentacion'
    ]
    if tipo not in validos:
        raise ValidationError(f"Tipo de recurso inválido: {tipo}")
    return tipo

def validate_required_text(value: str, field_name: str) -> str:
    """Valida texto obligatorio no vacío."""
    if not value or not str(value).strip():
        raise ValidationError(f"{field_name} es obligatorio")
    return str(value).strip()

def sanitize_text(text: Any) -> Optional[str]:
    """Limpia texto básico."""
    if text is None:
        return None
    s = str(text).strip()
    return s if s else None
