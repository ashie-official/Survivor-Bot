import discord as disc
from discord.ext import commands as cmds
from datetime import datetime, timezone

import toolkit.iotools as iotools

async def error(ctx: cmds.Context, error_msg: str):
    BOT_PREFIX = "@#"
    DELETE_AFTER = 30
    embed = disc.Embed(
        title = ":warning: ERROR! :warning:",
        description = error_msg,
        colour = disc.Colour.brand_red(),
        timestamp = datetime.now(timezone.utc)
    )
    embed.set_author(name = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
    try: 
        embed.set_footer(text = BOT_PREFIX+ctx.command.qualified_name +\
                        " • This error message and your command will be deleted after 30 seconds.")
    except: 
        embed.set_footer(text = "This error message and your command will be deleted after 30 seconds.")
    
    await ctx.message.delete(delay = DELETE_AFTER)
    sent_message = await ctx.send(embed = embed, reference = ctx.message.reference, mention_author=True)
    await iotools.delete_message(sent_message, ctx.author, delay = DELETE_AFTER, allow_pins=False)
    return None

async def cmd_group(ctx: cmds.Context, arg: str = None):
    if not arg:
        await error(ctx, "Enter a subcommand.")
    else:
        await error(ctx, "That subcommand doesn't exist!")