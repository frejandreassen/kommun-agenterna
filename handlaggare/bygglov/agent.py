# handlaggare/bygglov/agent.py
"""
Bygglovshandläggaragent
Använder specialiserade agenter som verktyg.
"""
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool



from .specialized_agents.preview_artifact.agent import root_agent as preview_artifact_agent_instance
from .specialized_agents.diarienummer.agent import root_agent as diarienummer_agent_instance



# --- Bygglov Team Lead Agent Definition ---
bygglov_agent = Agent(
    name="Bygglovshandlaggare", 
    model='gemini-2.5-flash-preview-04-17',
    description="Koordinerar hanteringen av bygglovsärenden genom att anropa specialiserade agenter och verktyg.",

    instruction=f"""Du är bygglovshandläggare och hjälper medborgare.
    """,

    # Lista AgentTools för de specialister DENNA agent behöver
    tools=[
        # Lägg till AgentTool för ALLA specialister som denna lead behöver
        AgentTool(agent=preview_artifact_agent_instance), # PreviewArtefactAgent
        AgentTool(agent=diarienummer_agent_instance), # Lägg till den nya DiarienummerAgent
    ]
)

# Exportera denna Team Lead så att Dispatchern kan importera den
# Behåll namnet root_agent om det är vad dispatchern förväntar sig
root_agent = bygglov_agent