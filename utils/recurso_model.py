# -----------------------------------------------------------------------------
# ARCHIVO LEGACY (OBSOLETO)
# -----------------------------------------------------------------------------
# ESTE ARCHIVO YA NO SE USA EN LA NUEVA ARQUITECTURA.
#
# Reemplazo:
# El modelo de dominio se encuentra en:
# -> `domain/material.py`
#
# Razón:
# Uso de Dataclasses modernas y separación de lógica de validación (Service) vs Modelo (Domain).
# -----------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RecursoDigital:
    titulo: str
    resumen: Optional[str]
    codigo_documento: Optional[str]
    año_publicacion: int
    estado_alojamiento: str  # 'ALOJADO' | 'ORIGINAL'
    url_descarga: str
    licencia_cc: str
    coleccion: str
    tipo_documento: str  # 'ARTICULO'|'TESIS'|'LIBRO'|'INFORME'|'OTRO'
    autores: List[str] = field(default_factory=list)
    etiquetas: List[str] = field(default_factory=list)

    def validar_datos(self) -> None:
        assert self.titulo and len(self.titulo) <= 500, "titulo inválido"
        assert 1900 <= int(self.año_publicacion) <= 2100, "año_publicacion inválido"
        assert self.estado_alojamiento in ("ALOJADO", "ORIGINAL"), "estado inválido"
        assert self.url_descarga and self.licencia_cc and self.coleccion and self.tipo_documento, "campos requeridos"

    def es_alojado(self) -> bool:
        return self.estado_alojamiento == "ALOJADO"

    def obtener_url_acceso(self) -> str:
        return self.url_descarga
