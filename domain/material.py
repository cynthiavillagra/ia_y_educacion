from dataclasses import dataclass
from typing import List, Optional

# -----------------------------------------------------------------------------
# CAPA: DOMAIN (Dominio)
# -----------------------------------------------------------------------------
# ¿Por qué?
# En aplicaciones simples, a veces pasamos diccionarios o JSONs crudos por todos lados.
# Eso es propenso a errores (typos en claves, no saber qué campos existen).
#
# ¿Qué logramos?
# 1. Definición Formal: Esta clase es el "contrato" de qué es un Material en nuestro sistema.
# 2. Type Hinting: El editor nos ayuda (autocompletado) porque sabe que `material.titulo` existe.
# 3. Independencia: Este objeto NO depende de la base de datos ni de la API. Es puro Python.
# -----------------------------------------------------------------------------

@dataclass
class Material:
    id: int
    titulo: str
    resumen: Optional[str]
    anio_publicacion: Optional[int]
    fecha_ingreso: Optional[str]
    estado_alojamiento: str
    url_descarga: Optional[str]
    licencia_cc: str
    tipo_documento: str
    codigo_documento: Optional[str]
    coleccion: str
    autores: List[str]
    etiquetas: List[str]

    def to_dict(self):
        """
        Helper para convertir el objeto a diccionario, útil para serializar a JSON
        en la respuesta HTTP.
        """
        return {
            "id": self.id,
            "titulo": self.titulo,
            "resumen": self.resumen,
            "año_publicacion": self.anio_publicacion,
            "fecha_ingreso": self.fecha_ingreso,
            "estado_alojamiento": self.estado_alojamiento,
            "url_descarga": self.url_descarga,
            "licencia_cc": self.licencia_cc,
            "tipo_documento": self.tipo_documento,
            "codigo_documento": self.codigo_documento,
            "coleccion": self.coleccion,
            "autores": self.autores,
            "etiquetas": self.etiquetas
        }
