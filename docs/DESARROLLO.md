# Guía de Desarrollo

Esta guía te ayudará a extender y mantener el proyecto siguiendo los patrones arquitectónicos establecidos.

## Primeros Pasos

### Requisitos Previos

- Python 3.11+
- PostgreSQL 15 (Supabase)
- Cuenta en Vercel (para deployment)
- Git

### Configuración Local

1. **Clonar el repositorio**:
```bash
git clone <repo-url>
cd ia_y_educacion
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:

Crear archivo `.env` en la raíz:
```bash
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_anonima
SUPABASE_SERVICE_KEY=tu_clave_servicio

# Database
SUPABASE_DB_HOST=db.tu-proyecto.supabase.co
SUPABASE_DB_PASSWORD=tu_password
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres
SUPABASE_DB_NAME=postgres
SUPABASE_DB_SSLMODE=require

# Storage
STORAGE_BUCKET=recursos-alojados
MAX_FILE_SIZE=10485760

# Server
PORT=8000
```

4. **Ejecutar servidor local**:
```bash
python app.py
```

El servidor estará disponible en `http://localhost:8000`

## Agregar una Nueva Funcionalidad

Sigue este flujo:Domain → Repository → Service → Handler → Router

### Ejemplo: Agregar "Favoritos"

#### 1. Definir el Modelo de Dominio

**Archivo**: `domain/favorito.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Favorito:
    """
    Modelo de dominio para favoritos de usuario.
    Sigue el patrón Domain Model: independiente de infraestructura.
    """
    id: int
    usuario_id: str
    material_id: int
    fecha_creacion: str
    
    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "material_id": self.material_id,
            "fecha_creacion": self.fecha_creacion
        }
```

#### 2. Crear el Repository

**Archivo**: `repositories/favorito_repository.py`

```python
from domain.favorito import Favorito
from utils.db import get_connection
from typing import List, Optional

class FavoritoRepository:
    """
    Patrón Repository: Abstrae el acceso a datos de favoritos.
    """
    
    def get_by_usuario(self, usuario_id: str) -> List[Favorito]:
        """Obtiene todos los favoritos de un usuario"""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, usuario_id, material_id, fecha_creacion
                    FROM favoritos
                    WHERE usuario_id = %s
                    ORDER BY fecha_creacion DESC
                """, (usuario_id,))
                rows = cur.fetchall()
                
                return [
                    Favorito(
                        id=r[0],
                        usuario_id=r[1],
                        material_id=r[2],
                        fecha_creacion=r[3].isoformat()
                    ) for r in rows
                ]
        finally:
            conn.close()
    
    def create(self, usuario_id: str, material_id: int) -> int:
        """Crea un nuevo favorito"""
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO favoritos (usuario_id, material_id)
                        VALUES (%s, %s)
                        RETURNING id
                    """, (usuario_id, material_id))
                    return cur.fetchone()[0]
        finally:
            conn.close()
    
    def delete(self, usuario_id: str, material_id: int) -> bool:
        """Elimina un favorito"""
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM favoritos
                        WHERE usuario_id = %s AND material_id = %s
                    """, (usuario_id, material_id))
                    return cur.rowcount > 0
        finally:
            conn.close()
```

#### 3. Crear el Service

**Archivo**: `services/favorito_service.py`

```python
from repositories.favorito_repository import FavoritoRepository
from typing import List

class FavoritoService:
    """
    Patrón Service Layer: Orquesta lógica de negocio de favoritos.
    """
    
    def __init__(self):
        self.repository = FavoritoRepository()
    
    def get_favoritos_usuario(self, usuario_id: str):
        """
        Obtiene favoritos del usuario.
        Aquí podríamos agregar lógica adicional (ej: verificar permisos).
        """
        return self.repository.get_by_usuario(usuario_id)
    
    def agregar_favorito(self, usuario_id: str, material_id: int):
        """
        Agrega un material a favoritos.
        Valida que el material existe antes de guardar.
        """
        # Validación de negocio
        if material_id <= 0:
            raise ValueError("ID de material inválido")
        
        return self.repository.create(usuario_id, material_id)
    
    def quitar_favorito(self, usuario_id: str, material_id: int):
        """Quita un material de favoritos"""
        return self.repository.delete(usuario_id, material_id)
```

#### 4. Crear el Handler

**Archivo**: `server/favorito_handler.py`

```python
from urllib.parse import parse_qs
from services.favorito_service import FavoritoService
from utils.response import Response
from utils.auth import verify_token, get_user_id_from_token

favorito_service = FavoritoService()

def handle_list_favoritos(handler, params):
    """
    Patrón Controller: Maneja GET /api/favorito/list
    """
    # 1. Autenticación
    token = handler.headers.get('Authorization')
    if not verify_token(handler.headers):
        Response.error(handler, "Unauthorized", 401)
        return
    
    # 2. Extraer usuario del token
    usuario_id = get_user_id_from_token(token)
    
    try:
        # 3. Llamar al servicio
        favoritos = favorito_service.get_favoritos_usuario(usuario_id)
        
        # 4. Formatear respuesta
        Response.json(handler, {"favoritos": [f.to_dict() for f in favoritos]})
    except Exception as e:
        Response.error(handler, str(e))

def handle_add_favorito(handler, params):
    """Maneja POST /api/favorito/add"""
    if not verify_token(handler.headers):
        Response.error(handler, "Unauthorized", 401)
        return
    
    # Parser POST body
    content_length = int(handler.headers.get('Content-Length', 0))
    body = handler.rfile.read(content_length).decode('utf-8')
    data = json.loads(body)
    
    material_id = data.get("material_id")
    usuario_id = get_user_id_from_token(handler.headers.get('Authorization'))
    
    try:
        favorito_id = favorito_service.agregar_favorito(usuario_id, material_id)
        Response.json(handler, {"id": favorito_id, "success": True})
    except ValueError as e:
        Response.error(handler, str(e), 400)
    except Exception as e:
        Response.error(handler, str(e))
```

#### 5. Registrar Rutas

**Archivo**: `app.py`

```python
from server.favorito_handler import handle_list_favoritos, handle_add_favorito

# Agregar al final, después de las rutas existentes
RequestHandler.router.add_route("GET", "/api/favorito/list", handle_list_favoritos)
RequestHandler.router.add_route("POST", "/api/favorito/add", handle_add_favorito)
RequestHandler.router.add_route("DELETE", "/api/favorito/remove", handle_remove_favorito)
```

#### 6. Crear Migración de Base de Datos

**Archivo**: `migrations/2025-11-25-favoritos.sql`

```sql
-- Migration: Agregar tabla de favoritos
-- Autor: [Tu Nombre]
-- Fecha: 2025-11-25

BEGIN;

CREATE TABLE public.favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id VARCHAR NOT NULL,
    material_id UUID NOT NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Evitar duplicados
    UNIQUE(usuario_id, material_id),
    
    -- FK a recursos
    CONSTRAINT favoritos_material_fkey 
        FOREIGN KEY (material_id) 
        REFERENCES public.recursos(id) 
        ON DELETE CASCADE
);

-- Índice para búsquedas por usuario
CREATE INDEX idx_favoritos_usuario ON favoritos(usuario_id);

-- RLS: Solo el usuario puede ver sus propios favoritos
ALTER TABLE public.favoritos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios ven sus favoritos" ON public.favoritos
    FOR SELECT
    USING (auth.uid()::text = usuario_id);

CREATE POLICY "Usuarios crean sus favoritos" ON public.favoritos
    FOR INSERT
    WITH CHECK (auth.uid()::text = usuario_id);

CREATE POLICY "Usuarios eliminan sus favoritos" ON public.favoritos
    FOR DELETE
    USING (auth.uid()::text = usuario_id);

COMMIT;
```

## Mejores Prácticas

### Código

1. **Siempre usa Type Hints**:
```python
# ✅ CORRECTO
def get_material(self, material_id: int) -> Optional[Material]:
    ...

# ❌ INCORRECTO
def get_material(self, material_id):
    ...
```

2. **Validación en Service Layer**:
```python
# ✅ CORRECTO: Validación en Service
class MaterialService:
    def upload_material(self, data, ...):
        titulo = validate_string_length(data["titulo"], ...)
        ...

# ❌ INCORRECTO: Validación en Handler
def handle_upload(handler, params):
    if len(data["titulo"]) > 500:
        ...
```

3. **Queries Parametrizadas Siempre**:
```python
# ✅ CORRECTO
cur.execute("SELECT * FROM recursos WHERE id=%s", (material_id,))

# ❌ INCORRECTO
cur.execute(f"SELECT * FROM recursos WHERE id={material_id}")
```

4. **Usa Context Managers**:
```python
# ✅ CORRECTO
conn = get_connection()
try:
    with conn:
        with conn.cursor() as cur:
            ...
finally:
    conn.close()

# ❌ INCORRECTO
conn = get_connection()
cur = conn.cursor()
cur.execute(...)
conn.commit()
conn.close()
```

### Testing

1. **Tests Unitarios para Servicios**:
```python
# test_material_service.py
import pytest
from services.material_service import MaterialService

def test_upload_material_validates_year():
    service = MaterialService()
    
    data = {"año_publicacion": 3000}  # Año inválido
    
    with pytest.raises(ValidationError):
        service.upload_material(data, None, None)
```

2. **Tests de Integración para Repositories**:
```python
# test_material_repository.py
def test_get_by_id_returns_material():
    repo = MaterialRepository()
    
    # Asume que existe material con ID 1
    material = repo.get_by_id(1)
    
    assert material is not None
    assert material.titulo is not None
```

### Git

1. **Commits Descriptivos**:
```bash
# ✅ CORRECTO
git commit -m "feat: agregar funcionalidad de favoritos

- Crear domain/favorito.py
- Implementar FavoritoRepository
- Agregar endpoints REST"

# ❌ INCORRECTO
git commit -m "cambios"
```

2. **Branches Descriptivas**:
```bash
git checkout -b feature/favoritos
git checkout -b fix/validation-error
git checkout -b refactor/service-layer
```

## Debugging

### Logs

Usa el módulo `utils/logger.py`:

```python
from utils.logger import logger

def upload_material(self, data, ...):
    logger.info(f"Subiendo material: {data.get('titulo')}")
    
    try:
        ...
    except Exception as e:
        logger.error(f"Error subiendo material: {e}")
        raise
```

### Analizar Queries Lentas

```sql
-- Ejecutar en PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM buscar_recursos('inteligencia artificial');
```

### Vercel Logs

```bash
vercel logs
vercel logs --follow  # En tiempo real
```

## Deployment

### Desarrollo Local

```bash
python app.py
# http://localhost:8000
```

### Vercel (Producción)

```bash
# Instalar Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy a producción
vercel --prod
```

### Variables de Entorno en Vercel

```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_DB_PASSWORD
...
```

## Resolución de Problemas Comunes

### Error: "Connection Refused"

**Problema**: No se puede conectar a la base de datos

**Solución**:
1. Verificar que `SUPABASE_DB_HOST` no tenga `https://`
2. Verificar que `SUPABASE_DB_PASSWORD` sea correcto
3. Probar con `psql` directamente

### Error: "Token Expired"

**Problema**: Token JWT expirado

**Solución**:
1. Re-autenticarse en el frontend
2. Implementar refresh token (feature futura)

### Error: "Policy Violation"

**Problema**: RLS bloqueando operación

**Solución**:
1. Verificar que el usuario esté autenticado
2. Revisar políticas RLS en la base de datos

## Recursos Adicionales

- [ARQUITECTURA.md](../ARQUITECTURA.md) - Arquitectura completa
- [PATRONES_DE_DISEÑO.md](../PATRONES_DE_DISEÑO.md) - Guía de patrones
- [DATABASE.md](DATABASE.md) - Esquema y optimizaciones
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Vercel Docs](https://vercel.com/docs)

## Convenciones de Código

### Naming

- **Clases**: `PascalCase` (ej: `MaterialService`)
- **Funciones**: `snake_case` (ej: `get_material`)
- **Constantes**: `UPPER_SNAKE_CASE` (ej: `MAX_FILE_SIZE`)
- **Privadas**: `_prefijo` (ej: `_helper_function`)

### Estructura de Archivos

```
nueva_feature/
├── domain/
│   └── nueva_entidad.py        # Modelo de dominio
├── repositories/
│   └── nueva_repository.py     # Acceso a datos
├── services/
│   └── nueva_service.py        # Lógica de negocio
├── server/
│   └── nueva_handler.py        # Controlador HTTP
└── migrations/
    └── YYYY-MM-DD-nueva.sql    # Cambios de DB
```

## Checklist: Agregar Nueva Entidad

- [ ] Crear modelo en `domain/`
- [ ] Crear repository en `repositories/`
- [ ] Crear service en `services/`
- [ ] Crear handler en `server/`
- [ ] Registrar rutas en `app.py`
- [ ] Crear migración SQL
- [ ] Agregar tests
- [ ] Documentar en README
- [ ] Crear PR con descripción clara

## Contacto y Soporte

Para preguntas sobre la arquitectura o decisiones de diseño, revisar:
- Comentarios en el código (todos los archivos tienen `# -----------------------------------------------------------------------------`)
- Documentación de patrones
- Issues en GitHub
