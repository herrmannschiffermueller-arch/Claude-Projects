# Meeting Notes → PDF

Bereitet rohe Meeting-Notizen mit einer **lokalen KI (Ollama)** auf und exportiert
sie als formatiertes PDF-Protokoll.

Alles läuft lokal auf deinem Rechner – die Notizen verlassen ihn nie.

## Voraussetzungen

1. [Ollama](https://ollama.com) installieren und ein Modell laden:
   ```bash
   ollama pull llama3.1
   ollama serve
   ```
2. Python-Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
   `weasyprint` benötigt unter Linux zusätzlich Systembibliotheken (Pango, Cairo):
   ```bash
   sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2
   ```

## Verwendung

```bash
python meeting_notes_to_pdf.py examples/beispiel_notizen.txt -o protokoll.pdf
```

Optionen:

- `--model llama3.1` – anderes lokales Modell verwenden
- `--ollama-url http://localhost:11434/api/generate` – falls Ollama auf einem anderen Port/Host läuft
- `--json-out daten.json` – die strukturierten Daten zusätzlich als JSON speichern

## Wie es funktioniert

1. Rohe Notizen (.txt) werden eingelesen.
2. Ein lokales LLM (über Ollama) extrahiert Titel, Datum, Teilnehmer, Zusammenfassung,
   Themen, Entscheidungen, Action Items und nächste Schritte als strukturiertes JSON.
3. Die Daten werden in die HTML/CSS-Vorlage `templates/meeting.html` eingesetzt.
4. WeasyPrint rendert daraus ein professionelles PDF.

## Vorlage anpassen

Die PDF-Optik liegt komplett in `templates/meeting.html` (CSS im `<style>`-Block) –
Farben, Logo, Schriftart etc. können dort frei angepasst werden, ohne den Python-Code
zu ändern.
