import discord as disc
from discord.ext import commands as cmds
import json
import os

_TOOLKIT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_TOOLKIT_DIR)
_DATA_DIR = os.path.join(_ROOT_DIR, "data")
_USERS_FOLDER_PATH = os.path.join(_DATA_DIR, "users")
_TEMPLATE_FILE_PATH = os.path.join(_USERS_FOLDER_PATH, "template.json")
#os.makedirs(_USERS_FOLDER_PATH, exist_ok=True)


# --- Example Core Functions inside your toolkit file ---

def get_user_filepath(user_id: int) -> str:
    """Helper to cleanly build an absolute path for any user ID."""
    return os.path.join(_USERS_FOLDER_PATH, f"{user_id}.json")

def is_user_registered(user_id) -> bool:
    return os.path.exists(get_user_filepath(user_id))

async def register_new_user(intx: disc.Interaction):
    """
    Registers a new user by copying the template file and 
    populating it with their user ID, username and global name.
    
    Returns True if successful, or False if unsuccessful,
    typically as a result of Discord user lookup.
    """
    with open(_TEMPLATE_FILE_PATH, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
    
    bot = intx.client
    user_id = intx.user.id
    
    user = bot.get_user(user_id)
    if not user:
        try:
            user = await bot.fetch_user(user_id)
        except disc.NotFound:
            print(f"❌ Could not register user: ID {user_id} does not exist on Discord.")
            return False
        except disc.HTTPException:
            print(f"❌ Could not register user: Discord API error while looking up user ID {user_id}.")
            return False
    
    # Save this layout immediately as the user's permanent file
    profile_data["id"] = user.id
    profile_data["username"] = user.name
    profile_data["global_name"] = user.global_name or user.name
    save_user_profile(intx, profile_data)
    return True

async def load_user_profile(intx: disc.Interaction) -> dict:
    """
    Loads a user's JSON profile. If the profile doesn't exist, it reads the 
    master template.json file to generate and save a new profile instantly.
    """
    user_id = intx.user.id
    filepath = get_user_filepath(user_id)
    
    # 1. If the profile file does NOT exist yet, initialize it
    if not is_user_registered(user_id): await register_new_user(intx)

    # 2. Now that it we're sure it exists, open it
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_profile(intx: disc.Interaction, data: dict) -> None:
    """Saves profile data down to the user's specific file securely."""
    filepath = get_user_filepath(intx.user.id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
