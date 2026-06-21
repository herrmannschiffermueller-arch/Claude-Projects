# PDF OCR zu Excel (Mistral OCR)

Eine kleine Flask-Webanwendung, die im Browser läuft: PDF-Datei hochladen,
Text per [Mistral OCR API](https://docs.mistral.ai/capabilities/document_ai/document_ocr/)
erkennen lassen und das Ergebnis als Excel-Datei (`.xlsx`) herunterladen.

## Funktionsweise

- Jede Seite der PDF wird einzeln per Mistral OCR verarbeitet.
- Enthält eine Seite eine Markdown-Tabelle, wird diese als echte Tabelle in
  ein eigenes Excel-Blatt übertragen.
- Andernfalls wird der erkannte Fließtext zeilenweise in das Excel-Blatt
  geschrieben.
- Jede PDF-Seite ergibt ein eigenes Excel-Blatt ("Seite 1", "Seite 2", ...).

## Installation

```bash
cd pdf-ocr-to-excel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Konfiguration

Mistral API-Key besorgen unter https://console.mistral.ai/.

Entweder als Umgebungsvariable hinterlegen (Datei `.env` aus `.env.example`
kopieren und Key eintragen) oder bei jedem Aufruf direkt im Browser-Formular
eingeben.

```bash
cp .env.example .env
# .env bearbeiten und MISTRAL_API_KEY setzen
```

## Start

```bash
python app.py
```

Anschließend im Browser öffnen: http://localhost:5000

## Nutzung

1. PDF-Datei im Formular auswählen.
2. Falls kein Key in `.env` hinterlegt ist, den Mistral API-Key eingeben.
3. Auf "In Excel umwandeln" klicken.
4. Die erzeugte `.xlsx`-Datei wird automatisch heruntergeladen.
