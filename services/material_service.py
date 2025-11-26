from typing import Dict, Any, Optional
from repositories.material_repository import MaterialRepository
from utils.validators import (
    validate_string_length, sanitize_text, validate_year, 
    validate_estado_alojamiento, validate_tipo_documento, 
    validate_url, validate_licencia, validate_doi, 
    validate_list_not_empty, ValidationError
)
from utils.normalize import normalize_tag

class MaterialService:
    def __init__(self):
        self.repository = MaterialRepository()

    def get_material(self, material_id: int):
        return self.repository.get_by_id(material_id)

    def search_materials(self, query: str, filters: Dict[str, Any], page: int = 1, per_page: int = 20, order: str = "relevancia"):
        return self.repository.search(query, filters, page, per_page, order)

    def upload_material(self, data: Dict[str, Any], file_bytes: Optional[bytes], filename: Optional[str]) -> int:
        # 1. Validate Data
        titulo = validate_string_length(sanitize_text(data.get("titulo", "")), "Título", 500)
        resumen = sanitize_text(data.get("resumen", ""))
        if resumen:
            resumen = validate_string_length(resumen, "Resumen", 5000, min_length=0)
        
        año = validate_year(int(data.get("año_publicacion")))
        estado = validate_estado_alojamiento(data.get("estado_alojamiento", "ORIGINAL").upper())
        tipo_doc = validate_tipo_documento(data.get("tipo_documento", ""))
        
        url_descarga = data.get("url_descarga")
        if estado == "ALOJADO":
            if not file_bytes:
                raise ValidationError("Archivo requerido para estado ALOJADO")
            # Upload file
            url_descarga = self.repository.upload_file(file_bytes, filename)
        else:
            if not url_descarga:
                raise ValidationError("URL de descarga requerida para estado ORIGINAL")
            url_descarga = validate_url(url_descarga)

        licencia = validate_licencia(data.get("licencia_cc", ""))
        coleccion = validate_string_length(sanitize_text(data.get("coleccion", "")), "Colección", 200)
        codigo_doc = validate_doi(data.get("codigo_documento"))
        
        autores = data.get("autores", [])
        validate_list_not_empty(autores, "Autores")
        
        etiquetas = data.get("etiquetas", [])
        # Normalize tags
        normalized_tags = []
        for tag in etiquetas:
            norm = normalize_tag(tag)
            if norm:
                normalized_tags.append(norm)

        # 2. Prepare Data for Repository
        clean_data = {
            "titulo": titulo,
            "resumen": resumen,
            "año_publicacion": año,
            "estado_alojamiento": estado,
            "tipo_documento": tipo_doc,
            "url_descarga": url_descarga,
            "licencia_cc": licencia,
            "coleccion": coleccion,
            "codigo_documento": codigo_doc,
            "autores": autores,
            "etiquetas": normalized_tags
        }

        # 3. Create in Repository
        return self.repository.create(clean_data)
