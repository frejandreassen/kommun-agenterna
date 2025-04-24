"""Verktyg för diarieföring och ärendenumrering för bygglovshantering."""

from datetime import datetime
import random
from google.adk.tools import FunctionTool

def generate_case_number():
    """
    Genererar ett unikt ärendenummer för bygglovsärenden i formatet:
    fbg-ÅÅÅÅMMDD-bglv-XXXXX
    
    där:
    - fbg: Kommunprefix (alltid samma)
    - ÅÅÅÅMMDD: Dagens datum
    - bglv: Flagga för bygglov
    - XXXXX: Slumpmässig siffersekvens (5 siffror)
    
    Returns:
        dict: Innehåller det genererade ärendenumret och tidsstämpeln
    """
    # Generera komponenterna
    prefix = "fbg"
    today = datetime.now().strftime("%Y%m%d")
    flag = "bglv"
    # Generera en 5-siffrig slumpmässig sekvens
    sequence = str(random.randint(10000, 99999))
    
    # Sätt ihop ärendenumret
    case_number = f"{prefix}-{today}-{flag}-{sequence}"
    
    return {
        "case_number": case_number,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

# Skapa FunctionTool från funktionen
generate_case_number_tool = FunctionTool(func=generate_case_number)