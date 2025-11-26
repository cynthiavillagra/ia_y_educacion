"""
# -----------------------------------------------------------------------------
# UTILITY: Validators
# -----------------------------------------------------------------------------
# Propósito:
# Centralizar la lógica de validación de entradas de usuario.
#
# Diseño:
# - Funciones puras que lanzan `ValidationError` si la validación falla.
# - Utilizado por la capa de Servicio (`services/material_service.py`) antes
#   de procesar cualquier lógica de negocio.
#
# Seguridad:
# - Validación de tipos, rangos, formatos (Regex) y listas permitidas (Allow-lists).
# - Sanitización básica de texto.
# -----------------------------------------------------------------------------

Input validation utilities for security
Validates all user inputs before processing
"""
import re
from datetime import datetime
from typing import Optional, List


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_year(year: int) -> int:
    """Validate year is within acceptable range"""
    current_year = datetime.now().year
    if not isinstance(year, int):
        raise ValidationError("El año debe ser un número entero")
    if year < 1900 or year > current_year + 1:
        raise ValidationError(f"El año debe estar entre 1900 y {current_year + 1}")
    return year


def validate_url(url: str) -> str:
    """Validate URL format and allowed protocols"""
    if not url or not isinstance(url, str):
        raise ValidationError("La URL no puede estar vacía")
    
    url = url.strip()
    
    # Check for allowed protocols
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("La URL debe comenzar con http:// o https://")
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        raise ValidationError("Formato de URL inválido")
    
    return url


def validate_tipo_documento(tipo: str) -> str:
    """Validate document type is one of allowed values"""
    allowed_types = ['ARTICULO', 'TESIS', 'LIBRO', 'INFORME', 'OTRO']
    
    if not tipo or not isinstance(tipo, str):
        raise ValidationError("El tipo de documento es requerido")
    
    tipo = tipo.upper().strip()
    
    if tipo not in allowed_types:
        raise ValidationError(f"Tipo de documento inválido. Valores permitidos: {', '.join(allowed_types)}")
    
    return tipo


def validate_estado_alojamiento(estado: str) -> str:
    """Validate hosting state"""
    allowed_states = ['ALOJADO', 'ORIGINAL']
    
    if not estado or not isinstance(estado, str):
        raise ValidationError("El estado de alojamiento es requerido")
    
    estado = estado.upper().strip()
    
    if estado not in allowed_states:
        raise ValidationError(f"Estado de alojamiento inválido. Valores permitidos: {', '.join(allowed_states)}")
    
    return estado


def validate_string_length(value: str, field_name: str, max_length: int, min_length: int = 1) -> str:
    """Validate string length"""
    if not value or not isinstance(value, str):
        raise ValidationError(f"{field_name} no puede estar vacío")
    
    value = value.strip()
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} debe tener al menos {min_length} caracteres")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} no puede exceder {max_length} caracteres")
    
    return value


def validate_doi(doi: Optional[str]) -> Optional[str]:
    """Validate DOI format (optional field)"""
    if not doi:
        return None
    
    doi = doi.strip()
    
    # DOI pattern: 10.xxxx/xxxxx
    doi_pattern = re.compile(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', re.IGNORECASE)
    
    if not doi_pattern.match(doi):
        # Not a DOI, might be ISBN or other code - allow it
        return doi
    
    return doi


def validate_licencia(licencia: str) -> str:
    """Validate Creative Commons license"""
    allowed_licenses = [
        'CC BY 4.0',
        'CC BY-SA 4.0',
        'CC BY-ND 4.0',
        'CC BY-NC 4.0',
        'CC BY-NC-SA 4.0',
        'CC BY-NC-ND 4.0',
        'CC0 1.0'
    ]
    
    if not licencia or not isinstance(licencia, str):
        raise ValidationError("La licencia es requerida")
    
    licencia = licencia.strip()
    
    if licencia not in allowed_licenses:
        raise ValidationError(f"Licencia inválida. Valores permitidos: {', '.join(allowed_licenses)}")
    
    return licencia


def validate_list_not_empty(items: List, field_name: str) -> List:
    """Validate that a list is not empty"""
    if not items or not isinstance(items, list) or len(items) == 0:
        raise ValidationError(f"{field_name} debe contener al menos un elemento")
    
    return items


def sanitize_text(text: str) -> str:
    """Basic text sanitization - remove potentially dangerous characters"""
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit to reasonable length to prevent DoS
    if len(text) > 50000:
        text = text[:50000]
    
    return text.strip()
