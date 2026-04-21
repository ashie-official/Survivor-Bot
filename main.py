import discord as disc
from discord.ext import commands
from discord import app_commands

import asyncio
import os
from datetime import datetime
import pytz

from survivor_token import TOKEN, OWNER_ID

import toolkit.send_error_embed as see


intents = disc.Intents.all()
prefix = "@#"

bot = commands.Bot(
    command_prefix=prefix,
    intents=intents,
    activity=disc.CustomActivity(
        name = "I NEED HUMAN BLOOD"#, emoji = disc.PartialEmoji.from_str("🔪")
    ),
    status="online",
    owner_id = OWNER_ID
)

@bot.event
async def on_ready():
    now = datetime.now(pytz.timezone('America/Phoenix'))
    print(f"Logged in as {bot.user} at {now.strftime('%I:%M %p')}!")
    
    owner = await bot.fetch_user(OWNER_ID)
    await owner.send(f"Started bot at {now.strftime('%I:%M %p')}")
    
    cog_count = 0
    for filename in os.listdir("./cogs"):
        try:
            if os.path.isfile(os.path.join("./cogs", filename)) \
            and filename.endswith('.py') \
            and filename != "COG_TEMPLATE.py":
                await bot.load_extension(f"cogs.{filename[:-3]}")
                cog_count += 1
        except:
            await owner.send(f"Couldn't load {filename} cog!")
    print(f"Successfully loaded {cog_count} cog{'s' if cog_count != 1 else ''}.")

# @bot.event
# async def on_command_error(ctx: commands.Context, error):
#     if isinstance(error, commands.CommandNotFound):
#         print("Tried to run nonexistent command")
#         await see.error(
#             ctx, 
#             "That command doesn't exist!"
#         )
#     elif isinstance(error, commands.MissingRequiredArgument):
#         print("Tried to run command with missing argument")
#         await see.error(
#             ctx, 
#             f"Missing required arguments! See `{prefix}help` for more details."
#         )
#     elif isinstance(error, commands.BadArgument):
#         print("Tried to run command with invalid argument")
#         await see.error(
#             ctx, 
#             f"Invalid argument! See `{prefix}help` for more details"
#         )


@bot.group(name = "admin")
@commands.is_owner()
@commands.dm_only()
async def admin(ctx: commands.Context):
    pass

@admin.command()
async def load(ctx: commands.Context, extension: str):
    try:
        await bot.load_extension(f"cogs.{extension}")
    except:
        await see.error(ctx,f"`{extension}` cog does not exist.")
    else:
        await ctx.send(f"Loaded `{extension}` cog!", delete_after=10)
        print(f'Loaded "{extension}" cog!')

@admin.command()
async def unload(ctx: commands.Context, extension: str):
    try:
        await bot.unload_extension(f"cogs.{extension}")
    except:
        await see.error(ctx,f"`{extension}` cog does not exist.")
    else: 
        await ctx.send(f"Unloaded `{extension}` cog!", delete_after=10)
        print(f'Unloaded "{extension}" cog!')

@admin.command()
async def reload(ctx: commands.Context, extension: str):
    try:
        await bot.reload_extension(f"cogs.{extension}")
    except:
        await see.error(ctx,f"`{extension}` cog does not exist.")
    else:
        await ctx.send(f"Reloaded `{extension}` cog!", delete_after=10)
        print(f'Reloaded "{extension}" cog!')

@admin.command()
async def sync(ctx: commands.Context):
    print("Synced bot tree.")
    await bot.tree.sync()


bot.run(TOKEN)