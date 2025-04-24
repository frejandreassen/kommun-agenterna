# handlaggare/bygglov/tools.py

import os
from typing import Dict, Any

# --- Configuration ---
DB_FILE = "arende_db.txt"  # Simple text file acting as DB
CORRECT_PASSWORD = "pa55w0rd" # The secret password

def append_to_db(note: str, password: str) -> Dict[str, Any]:
    """
    Appends a note to the secure text file database if the correct password is provided.

    Args:
        note (str): The text note to append to the database.
        password (str): The password required for write access.

    Returns:
        Dict[str, Any]: A dictionary indicating the status ('success' or 'error')
                       and a corresponding message.
    """
    print(f"--- Tool: append_to_db called (Password Provided: {'Yes' if password else 'No'}) ---")
    if password == CORRECT_PASSWORD:
        try:
            # Ensure directory exists if needed (optional, depends on where DB_FILE is)
            # os.makedirs(os.path.dirname(DB_FILE), exist_ok=True) 
            
            with open(DB_FILE, "a", encoding="utf-8") as f:
                f.write(note + "\n")
            print(f"--- Tool: Successfully appended note to {DB_FILE} ---")
            return {"status": "success", "message": "Note added successfully."}
        except IOError as e:
            print(f"--- Tool Error (append_to_db): {e} ---")
            return {"status": "error", "error_message": f"Failed to write to database file: {e}"}
    else:
        print(f"--- Tool Error (append_to_db): Incorrect password provided. ---")
        return {"status": "error", "error_message": "Incorrect password provided."}

def read_from_db(password: str) -> Dict[str, Any]:
    """
    Reads the entire content of the secure text file database if the correct password is provided.

    Args:
        password (str): The password required for read access.

    Returns:
        Dict[str, Any]: A dictionary indicating the status ('success' or 'error').
                       On success, includes 'content' with the file data.
                       On error, includes 'error_message'.
    """
    print(f"--- Tool: read_from_db called (Password Provided: {'Yes' if password else 'No'}) ---")
    if password == CORRECT_PASSWORD:
        try:
            if not os.path.exists(DB_FILE):
                 print(f"--- Tool: Database file {DB_FILE} not found. Returning empty. ---")
                 return {"status": "success", "content": "No notes found yet."}
                 
            with open(DB_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"--- Tool: Successfully read content from {DB_FILE} ---")
            return {"status": "success", "content": content}
        except FileNotFoundError:
            print(f"--- Tool: Database file {DB_FILE} not found. Returning empty. ---")
            return {"status": "success", "content": "No notes found yet."}
        except IOError as e:
            print(f"--- Tool Error (read_from_db): {e} ---")
            return {"status": "error", "error_message": f"Failed to read from database file: {e}"}
    else:
        print(f"--- Tool Error (read_from_db): Incorrect password provided. ---")
        return {"status": "error", "error_message": "Incorrect password provided."}