# handlaggare/bygglov/agent.py
"""
Team Lead / Koordinator för Bygglovsärenden.
Använder specialiserade agenter som verktyg.
"""
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

# --- State-nycklar (Definiera här temporärt, flytta till central fil senare) ---
# Nycklar specifika för bygglovsprocessen kan prefixas med t.ex. 'bygglov:'
STATE_INITIAL_QUERY = "initial_user_query" # Generell
STATE_CASE_DETAILS = "bygglov:case_details" # Bygglovsspecifik
STATE_ACTION_RESULTS = "bygglov:action_results" # Bygglovsspecifik
STATE_DIARIE_INFO = "bygglov:diarie_info" # Bygglovsspecifik
STATE_REPORT_ARTIFACT_NAME = "bygglov:html_receipt_filename" # Bygglovsspecifik
STATE_FINAL_OUTPUT_FOR_USER = "bygglov:final_output" # Bygglovsspecifik
# ---------------------------------------------------------------------------

# Importera den specialiserade agenten för förhandsgranskning/kvitto
try:
    # Relativ import till underkatalogen 'specialized_agents' och dess 'preview_artefact'-paket
    from .specialized_agents.preview_artifact.agent import root_agent as preview_artifact_agent_instance
    specialists_imported = True
    print("DEBUG: Successfully imported PreviewArtefactAgent.")
except ImportError as e:
    print(f"VARNING: Kunde inte importera PreviewArtefactAgent från .specialized_agents.preview_artefact.agent. Fel: {e}")
    preview_artifact_agent_instance = Agent(name="DummyPreview", model="gemini-2.0-flash", description="Dummy Preview Artefact Agent")
    specialists_imported = False

# Importera den nya specialiserade agenten för diarieföring
try:
    # Relativ import till underkatalogen 'specialized_agents' och dess 'diarienummer'-paket
    from .specialized_agents.diarienummer.agent import root_agent as diarienummer_agent_instance
    print("DEBUG: Successfully imported DiarienummerAgent.")
except ImportError as e:
    print(f"VARNING: Kunde inte importera DiarienummerAgent från .specialized_agents.diarienummer.agent. Fel: {e}")
    diarienummer_agent_instance = Agent(name="DummyDiarienummer", model="gemini-2.0-flash", description="Dummy Diarienummer Agent")

# Importera andra specialist-agenter som denna Team Lead behöver
# Exempel:
# try:
#     from ...support_agents.arkiv_agent.agent import root_agent as arkiv_specialist_instance # Gå upp två nivåer till roten, sedan ner
#     # Importera fler...
# except ImportError:
#     arkiv_specialist_instance = Agent(name="DummyArkiv", ...)
#     # ...

# Importera ev. FunctionTools som denna agent använder direkt
# from .tools import some_bygglov_specific_function_tool

# Definiera modell för DENNA agent explicit
BYGGLOV_LEAD_MODELL = 'gemini-2.5-flash-preview-04-17' # Eller annan lämplig modell

# --- Bygglov Team Lead Agent Definition ---

bygglov_agent_lead = Agent(
    name="BygglovTeamAgent", # Tydligare namn som reflekterar rollen
    model=BYGGLOV_LEAD_MODELL,
    description="Koordinerar hanteringen av bygglovsärenden genom att anropa specialiserade agenter och verktyg.",

    instruction=f"""Du är teamledare för bygglov. Du har tagit emot ett ärende från Huvudhandläggaren (Dispatcher). Den initiala frågan finns troligen i state '{STATE_INITIAL_QUERY}'.

    **Ditt arbetsflöde för att hantera ett komplett bygglovsärende:**
    1.  **Extrahera Detaljer:** Om inte redan gjort, analysera den initiala frågan och samla ärendedetaljer. Spara dessa i state '{STATE_CASE_DETAILS}'.
    2.  **Planera Kontroller:** Bestäm vilka kontroller som behövs (t.ex. detaljplan, arkivsökning, grannhörande, tekniska krav).
    3.  **Anropa Specialister (som Verktyg):** Använd dina `AgentTool`-verktyg för att utföra kontrollerna. Samla resultaten, antingen från verktygens returvärden eller genom att instruera dem att spara i state (helst i en gemensam dictionary under '{STATE_ACTION_RESULTS}'). Exempel på verktyg du kan ha:
        *   `ArkivSpecialistAgent`: För att söka tidigare ärenden.
        *   `HandboksSpecialistAgent`: För att kolla regler/detaljplan.
        *   `RegisterSpecialistAgent`: För Lantmäteriet etc.
    4.  **Sammanställ & Beslutsunderlag:** När nödvändiga kontroller är gjorda, sammanställ resultaten (från state '{STATE_ACTION_RESULTS}') och förbered eventuellt ett beslutsunderlag.
    5.  **Arkivering/Avslut:** När ärendet är redo att avslutas:
        *   Anropa först `DiarienummerAgent` för diarieföring, som genererar ett unikt diarienummer och sparar info i state '{STATE_DIARIE_INFO}'.
        *   Anropa sedan **`PreviewArtefactAgent`** för att generera HTML-kvittot. Den läser nödvändig info från state och sparar artefaktens namn i '{STATE_REPORT_ARTIFACT_NAME}'.
    6.  **Slutkommunikation:** Anropa en specialist/verktyg (t.ex. `MedborgarKommunikationsAgent`) för att formulera ett meddelande till användaren. Inkludera viktig information som diarienummer (från '{STATE_DIARIE_INFO}') och namnet på HTML-kvittot (från '{STATE_REPORT_ARTIFACT_NAME}'). Spara detta slutmeddelande i state '{STATE_FINAL_OUTPUT_FOR_USER}'.
    7.  Returnera detta slutmeddelande.

    Var metodisk och se till att anropa verktygen i logisk ordning. Använd state för att hålla reda på information mellan stegen.
    """,

    # Lista AgentTools för de specialister DENNA agent behöver
    tools=[
        # Lägg till AgentTool för ALLA specialister som denna lead behöver
        AgentTool(agent=preview_artifact_agent_instance), # PreviewArtefactAgent
        AgentTool(agent=diarienummer_agent_instance), # Lägg till den nya DiarienummerAgent
        # AgentTool(agent=arkiv_specialist_instance),
        # AgentTool(agent=register_specialist_instance),
        # AgentTool(agent=handboks_specialist_instance),
        # AgentTool(agent=medborgar_kommunikations_agent_instance),
        # Lägg även till ev FunctionTools som denna lead använder direkt
        # some_bygglov_specific_function_tool
    ] if specialists_imported else [], # Säkerhetskoll

    # Spara Team Leadens slutgiltiga sammanfattning/meddelande
    output_key=STATE_FINAL_OUTPUT_FOR_USER
)

# Exportera denna Team Lead så att Dispatchern kan importera den
# Behåll namnet root_agent om det är vad dispatchern förväntar sig
root_agent = bygglov_agent_lead

# För testning (valfritt)
if __name__ == "__main__":
     if specialists_imported:
        print(f"Bygglov Team Lead Agent '{root_agent.name}' skapad med modell '{root_agent.model}'.")
        print(f"Verktyg (AgentTools): {[tool.agent.name for tool in root_agent.tools if isinstance(tool, AgentTool)]}")
     else:
        print("Kunde inte skapa fungerande Bygglov Team Lead på grund av importfls" \
        "el.")