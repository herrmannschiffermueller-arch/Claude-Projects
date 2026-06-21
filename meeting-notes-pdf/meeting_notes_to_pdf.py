#!/usr/bin/env python3
"""Strukturiert rohe Meeting-Notizen mit einer lokalen KI (Ollama) und
erzeugt daraus ein formatiertes PDF.

Voraussetzung: Ollama läuft lokal (https://ollama.com), z.B.:
    ollama pull llama3.1
    ollama serve

Verwendung:
    python meeting_notes_to_pdf.py notizen.txt -o protokoll.pdf
    python meeting_notes_to_pdf.py notizen.txt -o protokoll.pdf --model llama3.1
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.1"
TEMPLATE_DIR = Path(__file__).parent / "templates"

SYSTEM_PROMPT = """Du bist ein Assistent, der rohe, unstrukturierte Meeting-Notizen \
in ein klares Protokoll umwandelt. Antworte AUSSCHLIESSLICH mit validem JSON \
(keine Markdown-Codeblöcke, kein Fließtext davor/danach) nach exakt diesem Schema:

{
  "title": "Kurzer, prägnanter Meeting-Titel",
  "date": "Datum falls erkennbar, sonst leerer String",
  "location": "Ort/Tool falls erkennbar, sonst leerer String",
  "attendees": ["Name1", "Name2"],
  "summary": "2-4 Sätze Zusammenfassung des Meetings",
  "topics": ["Thema 1", "Thema 2"],
  "decisions": ["Entscheidung 1", "Entscheidung 2"],
  "action_items": [
    {"task": "Aufgabe", "owner": "Person oder leer", "due": "Datum oder leer"}
  ],
  "next_steps": ["Nächster Schritt 1"]
}

Schreibe auf Deutsch, sei prägnant, erfinde keine Fakten die nicht in den Notizen \
stehen. Wenn eine Kategorie nichts enthält, gib ein leeres Array bzw. leeren String zurück."""


def call_ollama(raw_notes: str, model: str, url: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nMeeting-Notizen:\n\"\"\"\n{raw_notes}\n\"\"\""
    try:
        resp = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False, "format": "json"},
            timeout=300,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.exit(
            "Fehler: Konnte keine Verbindung zu Ollama herstellen.\n"
            f"Läuft Ollama lokal unter {url}? Starte es mit: ollama serve\n"
            f"Und stelle sicher, dass das Modell vorhanden ist: ollama pull {model}"
        )
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Fehler von Ollama: {e}\nAntwort: {resp.text[:500]}")

    raw_response = resp.json().get("response", "")
    return parse_json_response(raw_response)


def parse_json_response(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        sys.exit(f"Konnte KI-Antwort nicht als JSON parsen: {e}\nRohausgabe:\n{text[:1000]}")


def render_pdf(data: dict, output_path: Path) -> None:
    from weasyprint import HTML

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("meeting.html")
    html_content = template.render(
        title=data.get("title") or "Meeting-Protokoll",
        date=data.get("date") or "",
        location=data.get("location") or "",
        attendees=data.get("attendees") or [],
        summary=data.get("summary") or "",
        topics=data.get("topics") or [],
        decisions=data.get("decisions") or [],
        action_items=data.get("action_items") or [],
        next_steps=data.get("next_steps") or [],
    )
    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(str(output_path))


def main():
    parser = argparse.ArgumentParser(description="Meeting-Notizen mit lokaler KI aufbereiten und als PDF exportieren.")
    parser.add_argument("input", help="Pfad zur Textdatei mit rohen Meeting-Notizen")
    parser.add_argument("-o", "--output", default="protokoll.pdf", help="Pfad der Ausgabe-PDF")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama-Modellname (Standard: {DEFAULT_MODEL})")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="Ollama API-Endpunkt")
    parser.add_argument("--json-out", help="Optional: strukturierte Daten zusätzlich als JSON speichern")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"Eingabedatei nicht gefunden: {input_path}")

    raw_notes = input_path.read_text(encoding="utf-8")
    if not raw_notes.strip():
        sys.exit("Eingabedatei ist leer.")

    print(f"Sende Notizen an lokales Modell '{args.model}' ...")
    data = call_ollama(raw_notes, args.model, args.ollama_url)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Strukturierte Daten gespeichert: {args.json_out}")

    output_path = Path(args.output)
    print("Erzeuge PDF ...")
    render_pdf(data, output_path)
    print(f"Fertig: {output_path}")


if __name__ == "__main__":
    main()
