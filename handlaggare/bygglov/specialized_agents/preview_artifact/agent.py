# handlaggare/bygglov/specialized_agents/preview_artefact/agent.py
"""Specialistagent för att generera HTML-kvitton för bygglov."""
from google.adk.agents import Agent
# Importera konfig/verktyg relativt till specialistens plats
# Justera antal punkter beroende på exakt var config finns


from .tools import generate_html_receipt_tool


# Definiera modellen för denna specialist
PREVIEW_AGENT_MODELL = "gemini-2.5-flash-preview-04-17" #"("PreviewArtefactAgent") # Lägg till namn i config

preview_artifact_agent = Agent(
    name="PreviewArtifactAgent",
    model=PREVIEW_AGENT_MODELL,
    description="Genererar ett HTML-kvitto/sammanfattning för ett slutfört bygglovsärende och sparar det som en artefakt.",
    instruction=f"""Din uppgift är att generera ett HTML-kvitto för ett bygglovsärende som precis har diarieförts.
    All nödvändig information (ärendedetaljer, diarienummer, resultat från kontroller) finns redan i session state.
    Använd verktyget `generate_html_receipt_tool` för att skapa och spara HTML-filen som en artefakt.
    Verktyget kommer att läsa från state och spara artefaktens namn i state.
    Returnera en bekräftelse på att kvittot har skapats och namnet på artefaktfilen.""",
    tools=[generate_html_receipt_tool] # Använder sitt lokala verktyg
)

# Exportera instansen för Bygglov Team Lead att importera
root_agent = preview_artifact_agent # Använd ett konsekvent namn för export