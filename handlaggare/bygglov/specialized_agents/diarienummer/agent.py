"""Specialistagent för diarieföring av bygglovsärenden."""
from google.adk.agents import Agent

# Importera verktyg från lokala tools.py
from .tools import generate_case_number_tool

# Definiera modellen för denna specialist
DIARIENUMMER_AGENT_MODELL = "gemini-2.5-flash-preview-04-17"

# State-nycklar
STATE_DIARIE_INFO = "bygglov:diarie_info"
STATE_CASE_DETAILS = "bygglov:case_details"

diarienummer_agent = Agent(
    name="DiarienummerAgent",
    model=DIARIENUMMER_AGENT_MODELL,
    description="Genererar unika diarienummer för bygglovsärenden och sparar dem i session state.",
    instruction=f"""Du är en specialistagent för diarieföring av bygglovsärenden.

    **Ditt arbetsflöde:**

    1. **Hämta Case Details:** Hämta ärendedetaljer från state '{STATE_CASE_DETAILS}' för att förstå ärendet.
    
    2. **Generera Diarienummer:** Använd verktyget `generate_case_number_tool` för att skapa ett unikt diarienummer.
    
    3. **Spara Diarieföring:** Ta resultatet från verktyget och kombinera med ärendedetaljer för att skapa 
       en komplett diarieföringsinformation. Spara detta i state '{STATE_DIARIE_INFO}'.
    
    4. **Returnera Bekräftelse:** Returnera en bekräftelse som innehåller det genererade diarienumret och 
       annan relevant information för diarieföringen.
    
    Använd alltid verktyget `generate_case_number_tool` för att skapa diarienummer, generera aldrig egna nummer manuellt.
    """,
    tools=[generate_case_number_tool]  # Använder verktyget från tools.py
)

# Exportera instansen för Bygglov Team Lead att importera
root_agent = diarienummer_agent  # Använd ett konsekvent namn för export