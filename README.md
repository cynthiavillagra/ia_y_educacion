# Repositorio Digital: IA y Educación

Plataforma de acceso abierto para documentación sobre Inteligencia Artificial, Educación, Ética y Uso Responsable con licencias Creative Commons.

## 🎯 Descripción

Este proyecto implementa un **repositorio digital de código abierto** que permite:

- 🔍 **Búsqueda avanzada** con full-text search en español
- 📑 **Gestión de recursos** educativos (artículos, tesis, libros, informes)
- 🏷️ **Clasificación** por autores, colecciones y etiquetas
- 📊 **Filtros dinámicos** por año, tipo de documento y más
- ⚡ **Rendimiento optimizado** con índices y paginación
- 🔐 **Seguridad robusta** con Row Level Security (RLS)

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura de Monolito Modular en Capas** con **7 patrones de diseño**:

```
┌─────────────────────────────────────────┐
│  Presentation Layer (HTTP Handlers)    │  ← Controllers
├─────────────────────────────────────────┤
│  Application Layer (Services)          │  ← Business Logic
├─────────────────────────────────────────┤
│  Domain Layer (Models)                  │  ← Pure Business Objects
├─────────────────────────────────────────┤
│  Infrastructure Layer (Repositories)    │  ← Data Access
├─────────────────────────────────────────┤
│  Adapters (External Services)          │  ← Integration
└─────────────────────────────────────────┘
```

### Patrones Implementados

1. **Repository Pattern** - Abstracción de acceso a datos
2. **Service Layer Pattern** - Lógica de negocio centralizada
3. **Adapter Pattern** - Traducción entre DB y dominio
4. **Facade Pattern** - Simplificación de Supabase Client
5. **Router Pattern** - Enrutamiento de peticiones
6. **Controller/Handler Pattern** - Capa de presentación HTTP
7. **Domain Model Pattern** - Objetos de negocio puros

📖 **[Ver documentación completa de arquitectura →](ARQUITECTURA.md)**  
📚 **[Guía educativa de patrones →](PATRONES_DE_DISEÑO.md)**

## 🚀 Tecnologías

- **Backend**: Python 3.11+ (Serverless en Vercel)
- **Base de Datos**: PostgreSQL 15 (Supabase)
- **Autenticación**: Supabase Auth (JWT)
- **Storage**: Supabase Storage
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Deployment**: Vercel

## 📁 Estructura del Proyecto

```
ia_y_educacion/
├── domain/              # Modelos de negocio puros
│   └── material.py
├── services/            # Lógica de aplicación
│   └── material_service.py
├── repositories/        # Acceso a datos
│   ├── material_repository.py
│   └── supabase_client.py
├── adapters/            # Traducción de datos
│   └── material_adapter.py
├── server/              # Capa HTTP
│   ├── http_server.py
│   ├── router.py
│   └── material_handler.py
├── utils/               # Utilidades transversales
│   ├── validators.py
│   ├── normalize.py
│   ├── auth.py
│   ├── db.py
│   ├── rate_limiter.py
│   └── response.py
├── config/              # Configuración
│   └── settings.py
├── static/              # Frontend
├── docs/                # Documentación técnica
│   ├── DATABASE.md
│   └── DESARROLLO.md
├── ARQUITECTURA.md
├── PATRONES_DE_DISEÑO.md
└── app.py              # Punto de entrada
```

## 🔧 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd ia_y_educacion
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env`:

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

### 4. Configurar Base de Datos

Ejecutar migraciones en Supabase SQL Editor:

```bash
# 1. Esquema principal
psql < bbdd_definitiva.sql

# 2. RLS policies
psql < migration_rls.sql

# 3. Datos iniciales (opcional)
psql < carga_datos.sql
```

### 5. Ejecutar servidor local

```bash
python app.py
```

El servidor estará disponible en `http://localhost:8000`

## 🔍 API Endpoints

### Públicos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/material/get?id={id}` | GET | Obtener detalle de un material |
| `/api/material/list?q={query}&page={n}` | GET | Buscar y listar materiales |

### Administrativos (Requieren autenticación)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/material/upload` | POST | Subir nuevo material |
| `/api/material/update` | PUT | Actualizar material existente |
| `/api/material/delete` | DELETE | Eliminar material |

### Ejemplo: Buscar materiales

```bash
curl "http://localhost:8000/api/material/list?q=inteligencia+artificial&page=1&per_page=20"
```

```json
{
  "total": 45,
  "items": [
    {
      "id": "SAIA-EDU-001",
      "titulo": "Introducción a la IA en Educación",
      "anio_publicacion": 2023,
      "score": 0.95,
      "autores": "García, M.; López, J.",
      "etiquetas": "inteligencia artificial, educación",
      "institucion_fuente": "IA y Educación"
    }
  ]
}
```

## 🗄️ Base de Datos

El esquema incluye:

- **Full-Text Search** en español con `tsvector` y `ts_rank`
- **Row Level Security (RLS)** para control de acceso granular
- **Índices optimizados** para consultas rápidas
- **Metadatos v2**: Tabla única plana (wide table) para máxima portabilidad
- **Función almacenada** `buscar_recursos()` para búsqueda compleja

📖 **[Ver documentación completa de BD →](docs/DATABASE.md)**

## 👨‍💻 Desarrollo

### Agregar Nueva Funcionalidad

Sigue el flujo: **Domain → Repository → Service → Handler → Router**

1. **Crear modelo de dominio** en `domain/`
2. **Crear repository** en `repositories/`
3. **Crear service** en `services/`
4. **Crear handler** en `server/`
5. **Registrar ruta** en `app.py`

📖 **[Ver guía completa de desarrollo →](docs/DESARROLLO.md)**

### Patrones a Seguir

✅ **Hacer**:
- Validar en Service Layer
- Usar queries parametrizadas
- Type hints en todas las funciones
- Documentar patrones en comentarios

❌ **Evitar**:
- SQL en handlers
- Lógica de negocio en repositories
- Hardcodear valores
- Mezclar responsabilidades

## 🧪 Testing

```bash
# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Coverage
pytest --cov=. tests/
```

## 🚀 Deployment

### Vercel

```bash
# Instalar Vercel CLI
npm install -g vercel

# Deploy a staging
vercel

# Deploy a producción
vercel --prod
```

### Variables de Entorno en Vercel

```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_DB_PASSWORD
# ... resto de variables
```

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [ARQUITECTURA.md](ARQUITECTURA.md) | Arquitectura en capas completa con diagramas |
| [PATRONES_DE_DISEÑO.md](PATRONES_DE_DISEÑO.md) | Guía educativa de los 7 patrones |
| [docs/DATABASE.md](docs/DATABASE.md) | Esquema de BD, índices y RLS |
| [docs/DESARROLLO.md](docs/DESARROLLO.md) | Guía para desarrolladores |

## 🔐 Seguridad

- ✅ **Queries parametrizadas** para prevenir SQL Injection
- ✅ **Row Level Security (RLS)** en Supabase
- ✅ **JWT tokens** para autenticación
- ✅ **Validación de entrada** en todas las capas
- ✅ **Sanitización de texto** para prevenir XSS
- ✅ **Rate limiting** para prevenir abuso

## 📄 Licencia

Este proyecto y su código fuente están bajo licencia [MIT](LICENSE).

Los documentos del repositorio están bajo licencias Creative Commons según lo especificado en cada recurso.

## 👥 Contribución

Las contribuciones son bienvenidas.Por favor:

1. Fork el repositorio
2. Crea una branch para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Sigue los patrones arquitectónicos establecidos
4. Agrega tests
5. Documenta tu código con comentarios educativos
6. Envía un Pull Request

## 📞 Contacto

Para preguntas sobre la arquitectura o decisiones de diseño:
- Revisar comentarios en el código (todos los archivos tienen documentación detallada)
- Consultar la documentación de patrones
- Abrir un issue en GitHub

---

**Documentación completa**: [https://deepwiki.com/cynthiavillagra/ia_y_educacion/](https://deepwiki.com/cynthiavillagra/ia_y_educacion/)
