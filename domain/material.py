from dataclasses import dataclass
from typing import List, Optional

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
