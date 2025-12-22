# Registro de Cambios y Puntos de Control (Checkpoints)

## 2025-12-21: Migración a Metadatos v2 (Refactorización Mayor)

### 🎯 Objetivo
Implementar el set de metadatos "v2" definitivo y consistente, priorizando portabilidad, búsqueda unificada y simplificación del esquema de base de datos.

### 🛠 Cambios Realizados

#### Base de Datos
- **Refactorización Completa**: Se eliminaron las tablas relacionales (`autores`, `colecciones`, `etiquetas`, `recurso_autor`, `recurso_etiqueta`).
- **Tabla Única (`recursos`)**: Se consolidó todo en una tabla ancha (wide table) con columnas descriptivas según la especificación v2.
- **Nuevas Columnas**: `titulo_original`, `institucion_fuente`, `tipo_recurso` (enum), `archivo_local` (bool), `estado_revision`, etc.
- **Full-Text Search Actualizado**: La columna generada `vector_busqueda` ahora indexa título, resumen, palabras clave y autores en un solo vector.

#### Backend (Python)
- **Dominio (`domain/material.py`)**: Dataclass actualizada para reflejar 1:1 las columnas de la nueva tabla.
- **Repositorio (`repositories/material_repository.py`)**: 
    - Se eliminaron todos los `JOINs` complejos.
    - Consultas `SELECT` directas y rápidas.
    - Soporte para filtros dinámicos sobre las nuevas columnas (`institucion_fuente`, `tipo_recurso`, etc.).
    - Implementación de `create` y `update` adaptada a la tabla simple.
- **Servicio (`services/material_service.py`)**: Lógica de validación actualizada para los nuevos tipos de datos y reglas de negocio v2.
- **Handler (`server/material_handler.py`)**: Endpoints actualizados para mapear correctamente los parámetros de búsqueda y formularios de carga/edición.

#### Documentación
- **Sincronización v2**: Se actualizaron `ARQUITECTURA.md`, `PATRONES_DE_DISEÑO.md`, `docs/DATABASE.md` y `docs/DESARROLLO.md` para eliminar referencias a las tablas relacionales antiguas y reflejar el diseño de "Tabla Única".

#### Deprecación
- Archivos en `api/` (como `recurso_detalle.py`, `autores.py`, `admin/update.py`) marcados como **OBSOLETOS**. Deben usarse los endpoints en `server/material_handler.py`.

### ⚠️ Impacto
- **Breaking Change**: La estructura de la base de datos es incompatible con versiones anteriores.
- **Migración de Datos**: Se requiere recarga de datos (borrón y cuenta nueva recomendado).
- **Frontend**: Requiere ajustes menores en los nombres de campos esperados en el JSON si se usaban los antiguos (aunque se mantuvo cierta compatibilidad en el Adapter).
