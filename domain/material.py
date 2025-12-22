from dataclasses import dataclass
from typing import Optional

# -----------------------------------------------------------------------------
# CAPA: DOMAIN (Dominio)
# Metadatos v2 - Esquema definitivo y consistente.
# -----------------------------------------------------------------------------

@dataclass
class Material:
    # 1) Identificación
    id: str  # SAIA-EDU-001
    titulo: str
    titulo_original: Optional[str]
    tipo_recurso: str
    descripcion_resumen: Optional[str]

    # 2) Autoría y fuente
    autores: Optional[str]
    institucion_autora: Optional[str]
    institucion_fuente: str
    editorial_o_fuente: Optional[str]

    # 3) Publicación
    anio_publicacion: Optional[int]
    fecha_publicacion: Optional[str] # Date como string
    pais_origen: Optional[str]
    idioma: Optional[str]
    doi: Optional[str]
    isbn_issn: Optional[str]
    numero_paginas: Optional[int]

    # 4) Acceso y archivos
    url_fuente_original: str
    url_pdf_directo: Optional[str]
    archivo_local: bool
    url_archivo_local: Optional[str]
    tipo_acceso: Optional[str]
    licencia: Optional[str]
    formato: Optional[str]

    # 5) Clasificación
    palabras_clave: Optional[str]
    areas_tematicas: Optional[str]
    nivel: Optional[str]
    tipo_publico: Optional[str]
    contexto_geografico: Optional[str]

    # 6) Gobernanza
    proporcionado_por: Optional[str]
    agregado_por: str
    fecha_incorporacion_repo: Optional[str]
    estado_revision: Optional[str]
    revisado_por: Optional[str]
    observaciones: Optional[str]

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}
