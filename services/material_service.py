from typing import Dict, Any, Optional
from repositories.material_repository import MaterialRepository
from utils.validators import (
    validate_string_length, sanitize_text, validate_year, 
    validate_estado_alojamiento, validate_tipo_documento, 
    validate_url, validate_licencia, validate_doi, 
    validate_list_not_empty, ValidationError
)
from utils.normalize import normalize_tag

# -----------------------------------------------------------------------------
# PATRÓN DE DISEÑO: SERVICE LAYER (Capa de Servicio)
# -----------------------------------------------------------------------------
# ¿Por qué?
# El repositorio solo sabe guardar y leer datos. El controlador (handler) solo sabe
# recibir peticiones HTTP.
# ¿Quién valida que el año sea correcto? ¿Quién decide si se sube un archivo o no?
# ¿Quién normaliza las etiquetas?
#
# ¿Qué logramos?
# 1. Lógica de Negocio Pura: Aquí viven las reglas de tu aplicación.
# 2. Reutilización: Si mañana creamos un comando de terminal (CLI) para cargar
#    materiales, usamos este mismo Servicio y todas las validaciones aplican igual.
# 3. Orquestación: El servicio coordina al Repositorio (guardar DB) y otras
#    acciones (como normalizar datos).
# -----------------------------------------------------------------------------

class MaterialService:
    def __init__(self):
        # Inyección de dependencias (manual): El servicio depende del repositorio
        self.repository = MaterialRepository()

    def get_material(self, material_id: int):
        """Solo delega, pero podría agregar lógica (ej. verificar permisos de lectura)."""
        return self.repository.get_by_id(material_id)

    def search_materials(self, query: str, filters: Dict[str, Any], page: int = 1, per_page: int = 20, order: str = "relevancia"):
        """Delega la búsqueda al repositorio."""
        return self.repository.search(query, filters, page, per_page, order)

    def upload_material(self, data: Dict[str, Any], file_bytes: Optional[bytes], filename: Optional[str]) -> int:
        """
        Orquesta la creación de un material:
        1. Valida todos los datos de entrada (Reglas de Negocio).
        2. Decide si hay que subir un archivo (Lógica Condicional).
        3. Normaliza datos (Limpieza).
        4. Llama al repositorio para persistir (Persistencia).
        """
        
        # --- PASO 1: VALIDACIÓN (Reglas de Negocio) ---
        titulo = validate_string_length(sanitize_text(data.get("titulo", "")), "Título", 500)
        resumen = sanitize_text(data.get("resumen", ""))
        if resumen:
            resumen = validate_string_length(resumen, "Resumen", 5000, min_length=0)
        
        año = validate_year(int(data.get("año_publicacion")))
        estado = validate_estado_alojamiento(data.get("estado_alojamiento", "ORIGINAL").upper())
        tipo_doc = validate_tipo_documento(data.get("tipo_documento", ""))
        
        # --- PASO 2: LÓGICA DE ARCHIVOS ---
        url_descarga = data.get("url_descarga")
        if estado == "ALOJADO":
            if not file_bytes:
                raise ValidationError("Archivo requerido para estado ALOJADO")
            # El servicio decide subir el archivo usando el repositorio
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
        
        # --- PASO 3: NORMALIZACIÓN ---
        etiquetas = data.get("etiquetas", [])
        normalized_tags = []
        for tag in etiquetas:
            norm = normalize_tag(tag)
            if norm:
                normalized_tags.append(norm)

        # --- PASO 4: PERSISTENCIA ---
        # Preparamos el diccionario limpio para el repositorio
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

        # Delegamos el guardado final
        return self.repository.create(clean_data)
