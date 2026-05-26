import discord as disc
from discord.ext import commands as cmds
from datetime import datetime, timezone
import asyncio

BOT_PREFIX = "/"
DATETIME_FORMAT_STR = "%Y-%m-%d %H:%M"

def get_full_cmd_str(intx: disc.Interaction) -> str:
    if not intx.command: return ""
    return BOT_PREFIX+intx.command.qualified_name
    
def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)

def get_current_datetime_str(format: str = DATETIME_FORMAT_STR) -> str:
    return datetime.now(timezone.utc).strftime(format = format)

def build_embed(
    intx: disc.Interaction, 
    user: disc.User = None,     # type: ignore
    title: str = None,          # type: ignore
    body: str = None,           # type: ignore
    url = None, 
    colour: disc.Colour = None, # type: ignore
    ignore_footer = False,
) -> disc.Embed:
    '''
    # Assumes user is registered.
    '''
    if not user:
        user = intx.user

    embed = disc.Embed(
        title = title,
        description = body,
        url = url,
        timestamp = get_current_datetime(),
        colour = colour
    )

    # embed.set_author(name = f"{user.display_name}", icon_url = user.display_avatar)
    if not ignore_footer:
        embed.set_footer(text = f"{user.display_name} used {get_full_cmd_str(intx)}")

    return embed