import discord as disc
from discord.ext import commands as cmds
from datetime import datetime, timezone
import asyncio

import toolkit.reactions as reactions
import toolkit.tonkotsu_users as tk_users

BOT_PREFIX = "@#"
DATETIME_FORMAT_STR = "%Y-%m-%d %H:%M"



def get_full_cmd_str(ctx: cmds.Context) -> str:
    return BOT_PREFIX+ctx.command.qualified_name
    
def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)

def get_current_datetime_str(format: str = DATETIME_FORMAT_STR) -> str:
    return datetime.now(timezone.utc).strftime(format = format)

def build_embed(
    extension: str,
    ctx: cmds.Context, 
    user: disc.User = None,
    title: str = None, 
    delete_time: int = None, 
    description: str = None, 
    url = None, 
    colour: disc.Colour = None
) -> disc.Embed:
    '''
    # Assumes user is registered.
    '''
    if not user:
        user = ctx.author
    if not colour:
        try:
            user_color = tk_users.get_user_settings(extension, user=user)["hex_code"]
            if user_color != "default":
                colour = disc.Colour.from_str(user_color)
        except:
            pass
        if not colour and user.colour != disc.Colour.default(): 
            colour = user.colour

    embed = disc.Embed(
        title = title,
        description = description,
        url = url,
        timestamp = get_current_datetime(),
        colour = colour
    )

    embed.set_author(name = f"{user.display_name}", icon_url = user.display_avatar)
    delete_str = ""
    if delete_time:
        delete_str = "\nThis message will be deleted after"+\
        (f" {delete_time // 60} minutes" if (delete_time // 60) > 0 else '')+\
        (f" {delete_time % 60} seconds" if (delete_time % 60) > 0 else '')
    embed.set_footer(text = f"{ctx.author.display_name} used {get_full_cmd_str(ctx)}{delete_str}")

    return embed

async def delete_message(message: disc.Message, user_author: disc.User, delay: int, allow_pins = True) -> None:
    await message.add_reaction("❌")
    if delay == 0: return None
    
    await message.add_reaction("📌")
    await asyncio.sleep(delay)
    
    has_pin = await reactions.exists_reaction_from_user(message, "📌", user_author)
    if allow_pins and has_pin: 
        print("kept a pinned message")
        return None
    try: await message.delete()
    except: pass