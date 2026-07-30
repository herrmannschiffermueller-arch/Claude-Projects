# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a loose collection of small, independent projects/tools, each living in its own
top-level directory. There is no shared build system, package manifest, or CI across
projects — treat each subdirectory as self-contained and consult its own README.md first.

Current projects:

- `meeting-notes-pdf/` — Python CLI that turns raw meeting notes into a formatted PDF
  protocol using a local LLM via Ollama.

## meeting-notes-pdf

### Setup & commands

```bash
cd meeting-notes-pdf
pip install -r requirements.txt
```

`weasyprint` (PDF rendering) needs system libraries on Linux:
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2
```

Requires a local Ollama instance with a model pulled:
```bash
ollama pull llama3.1
ollama serve
```

Run it:
```bash
python meeting_notes_to_pdf.py examples/beispiel_notizen.txt -o protokoll.pdf
```

Useful flags: `--model <name>` (default `llama3.1`), `--ollama-url <url>` (default
`http://localhost:11434/api/generate`), `--json-out <path>` (also dump the structured
data as JSON).

There is no test suite in this repo currently.

### Architecture

Single-script pipeline in `meeting_notes_to_pdf.py`:

1. Raw `.txt` notes are read from disk.
2. `call_ollama()` sends them to a local Ollama model with a fixed German system
   prompt (`SYSTEM_PROMPT`) that forces a strict JSON schema back (title, date,
   location, attendees, summary, topics, decisions, action_items, next_steps).
   `parse_json_response()` strips markdown code fences and extracts the JSON object
   defensively, since LLM output isn't always clean.
3. `render_pdf()` feeds that JSON into the Jinja2 template `templates/meeting.html`.
4. WeasyPrint renders the resulting HTML/CSS string to a PDF file.

All visual styling (colors, fonts, layout, the `@page` rules for headers/footers/page
numbers) lives entirely in `templates/meeting.html`'s `<style>` block — change the
look there, not in the Python code. The Python side only ever deals with structured
data; it has no knowledge of PDF layout.

Everything runs locally: notes are never sent anywhere except the local Ollama
endpoint. Keep new features consistent with that (no calls to external/cloud LLM
APIs).
