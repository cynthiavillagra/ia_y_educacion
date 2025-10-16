import json, os

ROOT = r"c:\Users\Cynthia\OneDrive\Escritorio\T.S. EN CIENCIA DE DATOS\saia ia y educacion recursos"
REQUIRED = ["title", "author", "year", "publisher", "url", "original_url"]

with open(os.path.join(ROOT, "metadata.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

missing_files = []
incomplete = []

for e in data:
    f_rel = e.get("file", "")
    f_abs = os.path.join(ROOT, f_rel)
    if not f_rel or not os.path.exists(f_abs):
        missing_files.append(f_rel or "(sin file)")
    fields = [k for k in REQUIRED if not e.get(k)]
    if fields:
        incomplete.append((f_rel or "(sin file)", fields))

print("Validación de metadata.json:")
print("- OK archivos" if not missing_files else "- Archivos faltantes:")
for m in missing_files:
    print("  -", m)
print("- OK metadatos completos" if not incomplete else "- Entradas con campos vacíos:")
for f, fs in incomplete:
    print("  -", f, "→", ", ".join(fs))
