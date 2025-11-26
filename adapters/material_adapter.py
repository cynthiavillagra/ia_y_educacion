from domain.material import Material

def to_material(row: dict, autores: list, etiquetas: list) -> Material:
    """
    Adapts raw data from Supabase/DB to a Material domain object.
    Assumes 'row' contains keys matching the DB columns or the query aliases.
    """
    return Material(
        id=row.get("id"),
        titulo=row.get("titulo"),
        resumen=row.get("resumen"),
        anio_publicacion=row.get("año_publicacion"),
        fecha_ingreso=row.get("fecha_ingreso"), # Should be formatted string or handled in service
        estado_alojamiento=row.get("estado_alojamiento"),
        url_descarga=row.get("url_descarga"),
        licencia_cc=row.get("licencia_cc"),
        tipo_documento=row.get("tipo_documento"),
        codigo_documento=row.get("codigo_documento"),
        coleccion=row.get("coleccion"), # This might come from a join alias
        autores=autores,
        etiquetas=etiquetas
    )
