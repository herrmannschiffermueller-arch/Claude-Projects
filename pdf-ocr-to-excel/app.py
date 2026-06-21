import base64
import io
import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from openpyxl import Workbook
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MISTRAL_API_URL = "https://api.mistral.ai/v1/ocr"
MISTRAL_MODEL = "mistral-ocr-latest"


def run_mistral_ocr(pdf_bytes: bytes, api_key: str) -> list[str]:
    """Sendet die PDF-Datei an die Mistral OCR API und gibt den erkannten Text je Seite zurück."""
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    payload = {
        "model": MISTRAL_MODEL,
        "document": {
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{encoded}",
        },
        "include_image_base64": False,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(MISTRAL_API_URL, json=payload, headers=headers, timeout=180)
    response.raise_for_status()
    data = response.json()
    pages = data.get("pages", [])
    return [page.get("markdown", "") for page in pages]


def markdown_table_to_rows(markdown: str) -> list[list[str]]:
    """Extrahiert Tabellenzeilen aus Markdown-Tabellen, falls vorhanden."""
    rows = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.fullmatch(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def build_excel(pages_text: list[str]) -> io.BytesIO:
    wb = Workbook()
    wb.remove(wb.active)

    for index, markdown in enumerate(pages_text, start=1):
        sheet = wb.create_sheet(title=f"Seite {index}")
        table_rows = markdown_table_to_rows(markdown)
        if table_rows:
            for row in table_rows:
                sheet.append(row)
        else:
            sheet.append(["Erkannter Text"])
            for line in markdown.splitlines():
                if line.strip():
                    sheet.append([line])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET"])
def index():
    has_key = bool(os.environ.get("MISTRAL_API_KEY"))
    return render_template("index.html", has_key=has_key)


@app.route("/convert", methods=["POST"])
def convert():
    api_key = request.form.get("api_key") or os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        flash("Bitte einen Mistral API-Key angeben.")
        return redirect(url_for("index"))

    uploaded_file = request.files.get("pdf_file")
    if not uploaded_file or uploaded_file.filename == "":
        flash("Bitte eine PDF-Datei auswählen.")
        return redirect(url_for("index"))

    filename = secure_filename(uploaded_file.filename)
    if not filename.lower().endswith(".pdf"):
        flash("Es werden nur PDF-Dateien unterstützt.")
        return redirect(url_for("index"))

    pdf_bytes = uploaded_file.read()

    try:
        pages_text = run_mistral_ocr(pdf_bytes, api_key)
    except requests.HTTPError as exc:
        flash(f"Fehler bei der Mistral OCR API: {exc.response.status_code} {exc.response.text}")
        return redirect(url_for("index"))
    except requests.RequestException as exc:
        flash(f"Verbindungsfehler zur Mistral OCR API: {exc}")
        return redirect(url_for("index"))

    if not pages_text:
        flash("Die OCR-Erkennung hat keinen Text geliefert.")
        return redirect(url_for("index"))

    excel_buffer = build_excel(pages_text)
    download_name = os.path.splitext(filename)[0] + ".xlsx"

    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
