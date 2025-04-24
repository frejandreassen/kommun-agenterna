# handlaggare/bygglov/specialized_agents/preview_artifact/tools.py
"""Verktyg för att generera HTML-artefakt/kvitto."""
import datetime
import json
import os
import html # Importera för att escapa data vid behov
from typing import Dict, Any
from google.adk.tools import ToolContext
from google.genai import types

# STATE-konstanter (Antag att dessa är korrekta och matchar vad som sätts tidigare i flödet)
STATE_CASE_DETAILS = "bygglov_case_details"
STATE_DIARIE_INFO = "bygglov_diarie_info"
STATE_ACTION_RESULTS = "bygglov_action_results"
STATE_REPORT_ARTIFACT_NAME = "bygglov_html_receipt_filename"

# --- MER KOMPLETT HTML-MALL ---
# Ersätt alla <!-- ... --> med faktiska placeholders
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bygglovskvitto - {DECISION_NUMBER}</title>
    <style>
        body {{ font-family: sans-serif; margin: 2em; line-height: 1.5; }}
        h1, h2 {{ color: #2c3e50; border-bottom: 1px solid #bdc3c7; padding-bottom: 0.3em; margin-top: 1.5em; }}
        h1 {{ font-size: 1.8em; }}
        h2 {{ font-size: 1.4em; }}
        .section {{ margin-bottom: 1.5em; background-color: #fdfefe; padding: 1em; border: 1px solid #ecf0f1; border-radius: 5px;}}
        .label {{ font-weight: bold; min-width: 160px; display: inline-block; color: #34495e; }}
        .value {{ display: inline; color: #555; }}
        .info-pair {{ margin-bottom: 0.5em; }}
        pre {{ background-color: #ecf0f1; padding: 1em; border: 1px solid #bdc3c7; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; font-size: 0.9em; color: #333;}}
        .footer {{ margin-top: 2em; border-top: 1px solid #ccc; padding-top: 1em; font-size: 0.8em; color: #7f8c8d; }}
    </style>
</head>
<body>
    <h1>Bygglovskvitto / Ärendesammanfattning</h1>

    <div class="section">
        <h2>Grundinformation</h2>
        <div class="info-pair"><span class="label">Diarienummer:</span> <span class="value">{DIARIE_NUMMER}</span></div>
        <div class="info-pair"><span class="label">Datum för Kvitto:</span> <span class="value">{DATUM}</span></div>
        <div class="info-pair"><span class="label">Ärendetyp:</span> <span class="value">{ÄRENDETYP}</span></div>
        <div class="info-pair"><span class="label">Sökande/Mottagare:</span> <span class="value">{MOTTAGARE_NAMN}</span></div>
        <div class="info-pair"><span class="label">Fastighet:</span> <span class="value">{FASTIGHET}</span></div>
        <div class="info-pair"><span class="label">Handläggare (Agent):</span> <span class="value">{HANDLÄGGARE}</span></div>
        <div class="info-pair"><span class="label">Ursprungligt Ärendenr:</span> <span class="value">{CASE_NUMBER}</span></div>
        <div class="info-pair"><span class="label">Beslutsnr (om tillämpligt):</span> <span class="value">{DECISION_NUMBER}</span></div>
    </div>

    <div class="section">
        <h2>Ärendebeskrivning</h2>
        <p>{BESKRIVNING}</p>
    </div>

    <div class="section">
        <h2>Genomförda Kontroller & Resultat</h2>
        <p>Följande automatiska kontroller har utförts under handläggningen:</p>
        <pre>{KONTROLLRESULTAT_JSON}</pre>
    </div>

    <div class="section">
        <h2>Status och Nästa Steg</h2>
        <p>{PROCESS_FRAMÅT}</p>
    </div>

    <div class="footer">
        <p>Detta är ett automatiskt genererat kvitto från Kommunens Digitala Assistent.</p>
        <p>Genererat: {DATUM_TID_NU}</p>
    </div>
</body>
</html>
"""

def generate_html_receipt_tool(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Genererar ett HTML-kvitto för bygglov baserat på data i session state
    och sparar som artefakt. Använder bygglovsspecifika state-nycklar.

    Args:
        tool_context: ADK Tool Context.

    Returns:
        Dictionary med status och info om artefakten.
    """
    print("--- Tool: generate_html_receipt_tool (Bygglov) anropad ---")
    # *** FELSÖKNING: Logga state direkt ***
    print(f"DEBUG: State vid start av generate_html_receipt_tool: {json.dumps(tool_context.state, indent=2, default=str)}")

    try:
        # Hämta data med get och standardvärden
        case_details = tool_context.state.get(STATE_CASE_DETAILS, {})
        diarie_info = tool_context.state.get(STATE_DIARIE_INFO, {})
        action_results = tool_context.state.get(STATE_ACTION_RESULTS, {})

        # *** FELSÖKNING: Logga hämtad data ***
        print(f"DEBUG: Hämtade case_details: {case_details}")
        print(f"DEBUG: Hämtade diarie_info: {diarie_info}")
        print(f"DEBUG: Hämtade action_results: {action_results}")

        # Säkerställ att vi har nödvändig info för filnamn etc.
        diarie_nummer = diarie_info.get('nummer', f"EjDiariefört_{datetime.datetime.now().strftime('%H%M%S')}")
        decision_nummer = case_details.get('decision_number', diarie_nummer) # Använd diarienummer om beslutsnr saknas

        # Förbered data för mallen - använd .get för alla! Escapa text som kan innehålla HTML/JS.
        template_data = {
            "DECISION_NUMBER": html.escape(decision_nummer),
            "DIARIE_NUMMER": html.escape(diarie_nummer),
            "DATUM": html.escape(diarie_info.get('datum', datetime.date.today().isoformat())),
            "ÄRENDETYP": html.escape(case_details.get('ärendetyp', 'Okänd ärendetyp')),
            "MOTTAGARE_NAMN": html.escape(case_details.get('sökande_namn', 'Okänd')),
            "FASTIGHET": html.escape(case_details.get('fastighet', 'Okänd')),
            "HANDLÄGGARE": html.escape(case_details.get('handläggare', 'Okänd')),
            "CASE_NUMBER": html.escape(case_details.get('case_number', 'Okänt')), # Lade till denna
            "BESKRIVNING": html.escape(case_details.get('ärende_beskrivning', 'Ingen beskrivning angiven.')),
            "KONTROLLRESULTAT_JSON": html.escape(json.dumps(action_results, indent=2, ensure_ascii=False)),
            "PROCESS_FRAMÅT": html.escape("Bygglovsärendet är nu diariefört. Detta kvitto sammanfattar utförda kontroller."),
            "DATUM_TID_NU": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Lade till för footer
        }

        # *** FELSÖKNING: Logga data som ska formateras ***
        print(f"DEBUG: Förberedd template_data: {template_data}")

        # Fyll i mallen - fånga ev. KeyError här om en placeholder saknas i template_data
        try:
            filled_html = HTML_TEMPLATE.format(**template_data)
        except KeyError as fmt_e:
            print(f"FEL: KeyError vid HTML-formatering. Saknad nyckel: {fmt_e}. Kontrollera HTML_TEMPLATE och template_data.")
            return {"status": "error", "error_message": f"Internt fel: Kunde inte formatera HTML-mallen, saknad data för '{fmt_e}'."}

        # Skapa och spara artefakten
        html_bytes = filled_html.encode('utf-8')
        mime_type = "text/html"
        filename = f"Bygglovskvitto_{diarie_nummer}.html" # Använd garanterat unikt nummer

        # *** FELSÖKNING: Logga innan save_artifact ***
        print(f"DEBUG: Försöker spara artefakt: Filnamn='{filename}', Mime='{mime_type}', Storlek={len(html_bytes)} bytes")

        # Spara som artefakt via ToolContext
        version = tool_context.save_artifact(filename=filename, artifact=types.Part.from_data(data=html_bytes, mime_type=mime_type))
        print(f"INFO: Sparade HTML-kvitto artefakt '{filename}' version {version}")

        # Spara artefaktnamnet i state så att nästa agent kan referera till det
        tool_context.state[STATE_REPORT_ARTIFACT_NAME] = filename
        print(f"INFO: Uppdaterade state '{STATE_REPORT_ARTIFACT_NAME}' med värdet '{filename}'")

        return {
            "status": "success",
            "message": "HTML-kvitto för bygglov genererat och sparat.",
            "artifact_filename": filename,
            "artifact_version": version
        }
    # Mer specifik felhantering
    except KeyError as e:
         # Detta fångar troligen fel vid hämtning från state om .get inte används,
         # eller om man försöker komma åt en nyckel som inte finns i den returnerade dicten.
         print(f"FEL (KeyError) i generate_html_receipt_tool: Nyckel saknas - troligen i state-datan. Fel: {e}")
         return {"status": "error", "error_message": f"Kunde inte generera kvitto (bygglov), nödvändig information saknas (KeyError): {e}"}
    except ValueError as e:
         # Detta fångar troligen felet från save_artifact om ArtifactService saknas/är felkonfigurerad
         print(f"FEL (ValueError) vid sparning av artefakt i generate_html_receipt_tool: {e}")
         return {"status": "error", "error_message": f"Kunde inte spara kvitto-artefakt (bygglov - ValueError): {e}. Kontrollera ArtifactService-konfigurationen."}
    except Exception as e:
        # Fånga alla andra oväntade fel
        import traceback
        print(f"FATALT FEL (Exception) i generate_html_receipt_tool: {type(e).__name__} - {e}")
        print(traceback.format_exc()) # Skriv ut hela stack trace för djupare analys
        return {"status": "error", "error_message": f"Ett oväntat internt fel inträffade vid generering av bygglovskvitto ({type(e).__name__})."}

__all__ = ["generate_html_receipt_tool"]