from discord import app_commands as apps

import json
import os
from datetime import date as dt_date, time as dt_time, datetime as dt_datetime

_TOOLKIT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_TOOLKIT_DIR)
_SESSIONS_FILE_PATH = os.path.join(_ROOT_DIR, "data", "sessions.json")

def parse_date(value: str) -> dt_date:
    """Converts a user input string 'MM/DD' into a native python date object.
    Raises ValueError if improperly formatted."""
    parsed_dt = dt_datetime.strptime(f"2026/{value}", "%Y/%m/%d")
    return parsed_dt.date()

def parse_time(value: str) -> dt_time:
    """Converts a user input string 'HH:MM' (24-hour style) into a native python time object.
    Raises ValueError if improperly formatted."""
    parsed_dt = dt_datetime.strptime(value, "%H:%M")
    return parsed_dt.time()

def load_sessions_data() -> dict:
    """Loads the entire configuration dictionary from sessions.json."""
    
    with open(_SESSIONS_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sessions_data(data: dict) -> None:
    """Saves the completely updated structural configuration down to disk securely."""
    with open(_SESSIONS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_session_choices() -> list:
    """Reads active sessions out to dropdown choices with clean formatting."""
    data = load_sessions_data()
    choices = []
    from discord import app_commands as apps
    
    for index, s in enumerate(data.get("sessions", [])):
        # Parse the stored ISO string into a usable datetime object
        # Handles cases with or without timezone offsets safely
        try:
            dt_obj = dt_datetime.fromisoformat(s["datetime"])
        except ValueError:
            continue
            
        # Format Example: "Fri 8/21, 8:00 PM"
        # %a = Abbreviated weekday (Fri)
        # %m/%d = Month/Day without leading zero padding depends on OS, 
        # so we strip or use standard formatting
        weekday = dt_obj.strftime("%a")
        date_str = f"{dt_obj.month}/{dt_obj.day}"
        time_str = dt_obj.strftime("%I:%M %p").lstrip("0") # 8:00 PM instead of 08:00 PM
        
        # Build the exact user-facing label you requested
        label = f"{weekday} {date_str}, {time_str} ({s['duration']} min)"
        
        # We still store the index string as the inner VALUE so your code
        # knows exactly which list position to update when submitted.
        choices.append(apps.Choice(name=label, value=str(index)))
        
    return choices[:25] # Discord limits dropdowns to 25 items max