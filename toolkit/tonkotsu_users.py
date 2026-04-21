import discord as disc
import json
import os

def get_profiles_dir() -> str:
    return os.path.abspath(os.path.join(os.getcwd(), "profiles"))

def get_user_dir(user: disc.User, folder: str = None) -> str:
    if folder: 
        return os.path.join(get_profiles_dir(), str(user.id), folder)
    return os.path.join(get_profiles_dir(), str(user.id))

def get_user_settings(extension: str, *, user: disc.User = None, user_id_str: str = None) -> dict:
    '''
    # Assumes user is registered.
    '''
    if not user and not user_id_str:
        raise TypeError("Either user or user_id must be populated")
    elif user_id_str:
        return json.load(open(os.path.join(get_profiles_dir(), user_id_str, "settings", f"{extension}.json")))
    elif user:
        return json.load(open(os.path.join(get_user_dir(user), "settings", f"{extension}.json")))
    
def is_user_registered(user: disc.User, extension: str = None) -> bool:
    user_dir = get_user_dir(user, extension)
    # user folder exists
    return os.path.isdir(user_dir)

def register_new_user(user: disc.User, extension: str = None) -> None:
    user_dir = get_user_dir(user)
    
    if not os.path.isdir(os.path.join(user_dir, "settings")):
        os.makedirs(os.path.join(user_dir, "settings"))
    
    if extension: os.makedirs(os.path.join(user_dir, extension))