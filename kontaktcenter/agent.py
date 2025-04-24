from google.adk.agents import Agent # Använder LlmAgent alias



from handlaggare.alkohol.agent import alkohol_agent
from handlaggare.bygglov.agent import bygglov_agent


kontaktcenter_agent = Agent(
    name="KontaktcenterAgent",
    # Sätt modellen explicit här
    model='gemini-2.0-flash',
    description="Tar emot användarförfrågningar och dirigerar dem till rätt specialist för antingen alkoholärenden eller bygglovsärenden.",

    # Lista sub-agenterna som den kan delegera till
    sub_agents=[
        alkohol_agent,
        bygglov_agent,
    ],

    # Instruktionen fokuserar på routing
    instruction=f"""Du jobbar som medborgarservice på kontaktcenter på falkenbergs kommun. 
    
    Du kan vara behjälplig och svara på frågor, eller sammankoppla medborgaren till rätt handläggare.
    """,
    tools=[], # Ren dispatcher har inga egna verktyg
)

root_agent = kontaktcenter_agent


