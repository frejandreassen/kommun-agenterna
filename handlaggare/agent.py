# handlaggare/agent.py
"""
Definierar HuvudHandlaggareAgent som agerar dispatcher
och routar till specialistagenter för Alkohol eller Bygglov.
Modell konfigureras direkt här.
"""
from google.adk.agents import Agent # Använder LlmAgent alias

# Definiera önskad modell för DENNA dispatcher-agent explicit
# Välj en kapabel modell för routing-logik
DISPATCHER_MODELL = 'gemini-2.5-flash-preview-04-17' # Eller 'gemini-2.5-pro-...'

# Importera de faktiska specialistagent-INSTANSERNA från deras moduler
# Dessa instanser förväntas nu ha sin 'model' satt i sina egna agent.py-filer.

from .alkohol.agent import root_agent as alkohol_agent_instance
from .bygglov.agent import root_agent as bygglov_agent_instance



# --- HuvudHandlaggareAgent (Dispatcher) Definition ---


huvud_handlaggare_agent = Agent(
    name="HuvudHandlaggareAgent",
    # Sätt modellen explicit här
    model=DISPATCHER_MODELL,
    description="Tar emot användarförfrågningar och dirigerar dem till rätt specialist för antingen alkoholärenden eller bygglovsärenden.",

    # Lista sub-agenterna som den kan delegera till
    sub_agents=[
        alkohol_agent_instance,
        bygglov_agent_instance,
    ],

    # Instruktionen fokuserar på routing via transfer_to_agent
    instruction=f"""Du är Huvudhandläggaren (router). Ditt enda ansvar är att förstå om användarens fråga gäller **alkoholrelaterade ärenden** eller **bygglovsrelaterade ärenden** och sedan omedelbart **överföra kontrollen** till rätt specialist.

    Dina specialister är:
    *   `{alkohol_agent_instance.name}`: {alkohol_agent_instance.description}
    *   `{bygglov_agent_instance.name}`: {bygglov_agent_instance.description}

    **Arbetsflöde:**
    1. Analysera användarens fråga.
    2. Om frågan handlar om alkohol/serveringstillstånd, anropa **omedelbart** `transfer_to_agent(agent_name='{alkohol_agent_instance.name}')`.
    3. Om frågan handlar om bygglov/byggnader/planer, anropa **omedelbart** `transfer_to_agent(agent_name='{bygglov_agent_instance.name}')`.
    4. Vid oklarhet, ställ en förtydligande fråga (alkohol eller bygglov?).
    5. **Svara inte själv på sakfrågan.** Din uppgift är bara att routa.
    """,
    tools=[], # Ren dispatcher har inga egna verktyg
)
# Exportera denna dispatcher som root_agent för handläggare-modulen
root_agent = huvud_handlaggare_agent



# För testning (valfritt)
if __name__ == "__main__":

    print(f"Dispatcher Agent '{root_agent.name}' skapad med modell '{root_agent.model}'.")
    print(f"Kan delegera till: {[sub.name for sub in root_agent.sub_agents]}")
