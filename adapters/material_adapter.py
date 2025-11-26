from domain.material import Material

# -----------------------------------------------------------------------------
# PATRÓN DE DISEÑO: ADAPTER (Adaptador)
# -----------------------------------------------------------------------------
# ¿Por qué?
# La base de datos (Supabase/Postgres) nos devuelve datos "crudos" (diccionarios,
# tuplas, nombres de columnas con guiones bajos, etc.).
# Nuestra aplicación quiere trabajar con objetos limpios y bien definidos (Clase Material).
#
# ¿Qué logramos?
# 1. Traducción: Convertimos el "idioma" de la base de datos al "idioma" del dominio.
# 2. Protección: Si cambiamos el nombre de una columna en la DB, solo tocamos este
#    archivo. El resto de la app sigue usando `material.titulo` sin enterarse.
# -----------------------------------------------------------------------------

def to_material(row: dict, autores: list, etiquetas: list) -> Material:
    """
    Convierte (adapta) los datos crudos de la base de datos a una instancia de Material.
    
    Args:
        row: Diccionario con los datos de la tabla 'recursos'.
        autores: Lista de nombres de autores.
        etiquetas: Lista de nombres de etiquetas.
    
    Returns:
        Una instancia limpia de la clase Material.
    """
    return Material(
        id=row.get("id"),
        titulo=row.get("titulo"),
        resumen=row.get("resumen"),
        anio_publicacion=row.get("año_publicacion"),
        # Normalizamos la fecha a string ISO o None si viene vacía
        fecha_ingreso=row.get("fecha_ingreso"), 
        estado_alojamiento=row.get("estado_alojamiento"),
        url_descarga=row.get("url_descarga"),
        licencia_cc=row.get("licencia_cc"),
        tipo_documento=row.get("tipo_documento"),
        codigo_documento=row.get("codigo_documento"),
        coleccion=row.get("coleccion"), # Puede venir de un JOIN
        autores=autores,
        etiquetas=etiquetas
    )
