# IA y Educación – Biblioteca de recursos

Repositorio local con documentos (PDF) y metadatos estructurados sobre IA y educación.

## Estructura
- `pdfs/` – Todos los PDF normalizados (ASCII, guiones bajos)
- `metadata.json` – Metadatos externos por documento
- `normalize_and_merge.ps1` – Script usado para normalizar nombres y mantener consistencia

## Convenciones de nombres (PDF)
- Sin tildes ni caracteres especiales
- Espacios → `_`
- Ejemplo: `IA en la escuela - Guía para un uso crítico.pdf` → `IA_en_la_escuela_-_Guia_para_un_uso_critico.pdf`

## Esquema de `metadata.json`
Cada entrada es un objeto con los campos mínimos:
```json
{
  "file": "pdfs/<nombre_normalizado>.pdf",
  "title": "<título del documento>",
  "author": "<autores>",
  "year": <año>,
  "publisher": "<editorial/organismo>",
  "url": "<doi o enlace estable>",
  "original_url": "<página fuente oficial>"
}
```
Campos opcionales útiles:
- `license` – Licencia de uso (p. ej., CC BY-SA 4.0)
- `description` – Breve resumen del contenido
- `book` – Si es un capítulo dentro de un libro/informe

## Validación rápida
Usá este script para verificar que todos los archivos existen y que los campos obligatorios están completos.

```python
# validate_metadata.py
import json, os

ROOT = r"c:\\Users\\Cynthia\\OneDrive\\Escritorio\\T.S. EN CIENCIA DE DATOS\\saia ia y educacion recursos"
REQUIRED = ["title", "author", "year", "publisher", "url", "original_url"]

with open(os.path.join(ROOT, "metadata.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

missing_files = []
incomplete = []

for e in data:
    fpath = os.path.join(ROOT, e.get("file", ""))
    if not os.path.exists(fpath):
        missing_files.append(e.get("file", "(sin file)"))
    fields = [k for k in REQUIRED if not e.get(k)]
    if fields:
        incomplete.append((e.get("file", "(sin file)"), fields))

print("OK archivos" if not missing_files else "Archivos faltantes:")
for m in missing_files: print(" -", m)
print("OK metadatos completos" if not incomplete else "Entradas con campos vacíos:")
for f, fs in incomplete: print(" -", f, "→", ", ".join(fs))
```

## Flujo sugerido de trabajo
- Agregar nuevos PDF a `pdfs/` con nombres ya normalizados
- Añadir su entrada a `metadata.json`
- Ejecutar validación
- (Opcional) Propagar metadatos internos al PDF con PyPDF2

## Licencias
- Respetar la licencia indicada por cada documento en sus metadatos.

---
Cualquier aporte o corrección de metadatos es bienvenida.
