import json
import os
import shutil
from PyPDF2 import PdfReader, PdfWriter

ROOT = r"c:\Users\Cynthia\OneDrive\Escritorio\T.S. EN CIENCIA DE DATOS\saia ia y educacion recursos"
META_PATH = os.path.join(ROOT, "metadata.json")

def build_pdf_metadata(entry: dict) -> dict:
    title = entry.get("title", "") or ""
    author = entry.get("author", "") or ""
    year = entry.get("year", "") or ""
    publisher = entry.get("publisher", "") or ""
    keywords = [k for k in ["inteligencia artificial", "educación", str(year), publisher] if k]

    meta = {
        "/Title": title,
        "/Author": author,
        "/Subject": "IA y educación",
        "/Keywords": ", ".join(keywords)
    }
    # Custom fields (no todos los visores los muestran)
    if entry.get("original_url"):
        meta["/Source"] = entry["original_url"]
    if entry.get("url"):
        meta["/URL"] = entry["url"]
    return meta


def write_pdf_metadata(pdf_path: str, meta: dict) -> None:
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(meta)

    tmp_path = pdf_path + ".tmp"
    with open(tmp_path, "wb") as f:
        writer.write(f)
    # Reemplazo atómico best-effort
    backup_path = pdf_path + ".bak"
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
    except Exception:
        pass
    try:
        shutil.move(pdf_path, backup_path)
        shutil.move(tmp_path, pdf_path)
        os.remove(backup_path)
    except Exception:
        # Si algo falla, restaurar
        if os.path.exists(backup_path) and not os.path.exists(pdf_path):
            shutil.move(backup_path, pdf_path)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def main():
    with open(META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    ok, failed = 0, []
    for entry in data:
        rel = entry.get("file", "")
        if not rel:
            failed.append((rel, "sin campo 'file'"))
            continue
        pdf_path = os.path.join(ROOT, rel)
        if not os.path.exists(pdf_path):
            failed.append((rel, "archivo no encontrado"))
            continue
        try:
            meta = build_pdf_metadata(entry)
            write_pdf_metadata(pdf_path, meta)
            ok += 1
        except Exception as e:
            failed.append((rel, str(e)))

    print(f"Listo. PDFs actualizados: {ok}")
    if failed:
        print("Errores:")
        for rel, err in failed:
            print(f" - {rel}: {err}")


if __name__ == "__main__":
    main()
