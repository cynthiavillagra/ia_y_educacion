from domain.material import Material
from typing import List, Optional

# -----------------------------------------------------------------------------
# PATRÓN DE DISEÑO: ADAPTER (Adaptador) - [DEPRECATED / LEGACY SUPPORT]
# -----------------------------------------------------------------------------
# Este archivo se mantiene por compatibilidad si algún test lo usa.
# En la versión v2, el repositorio devuelve Material directamente.
# -----------------------------------------------------------------------------

def to_material(row: dict, autores: list, etiquetas: list) -> Material:
    """
    Intenta adaptar datos viejos al nuevo esquema.
    Advertencia: Es una conversión simple ("best effort").
    """
    
    # Intentamos construir un Material v2 con lo que tenemos
    return Material(
        id=str(row.get("id", "")),
        titulo=row.get("titulo", "Sin título"),
        titulo_original=None,
        tipo_recurso=row.get("tipo_documento", "desconocido"), # Mapping approx
        descripcion_resumen=row.get("resumen"),
        autores="; ".join(autores) if autores else "",
        institucion_autora=None,
        institucion_fuente=row.get("coleccion", "Desconocida"),
        editorial_o_fuente=None,
        anio_publicacion=row.get("año_publicacion"),
        fecha_publicacion=None,
        pais_origen=None,
        idioma=None,
        doi=row.get("codigo_documento"), # Asumimos que codigo era un DOI a veces
        isbn_issn=None,
        numero_paginas=None,
        url_fuente_original=row.get("url_descarga", ""), # Asumimos link principal
        url_pdf_directo=None,
        archivo_local=row.get("estado_alojamiento") == "ALOJADO",
        url_archivo_local=row.get("url_descarga") if row.get("estado_alojamiento") == "ALOJADO" else None,
        tipo_acceso="abierto", # Default
        licencia=row.get("licencia_cc"),
        formato="PDF", # Default
        palabras_clave=", ".join(etiquetas) if etiquetas else "",
        areas_tematicas=None,
        nivel=None,
        tipo_publico=None,
        contexto_geografico=None,
        proporcionado_por="mixto",
        agregado_por="migration",
        fecha_incorporacion_repo=str(row.get("fecha_ingreso")),
        estado_revision="publicado",
        revisado_por=None,
        observaciones=None
    )
