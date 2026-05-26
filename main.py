import sys

print(sys.prefix)

import discord as disc
from discord.ext import commands
from discord import app_commands

import asyncio
import os
from datetime import datetime
import pytz

from survivor_token import TOKEN, OWNER_ID, TEST_SERVER_ID

import old_toolkit.send_error_embed as see

class SlashBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="@#",
            intents=disc.Intents.default(),
            activity=disc.CustomActivity(
                name = "I NEED HUMAN BLOOD"#, emoji = disc.PartialEmoji.from_str("🔪")
            ),
            status="online",
            owner_id = OWNER_ID
            )
        
    async def setup_hook(self) -> None:
        cog_count = 0
        for filename in os.listdir("./cogs"):
            try:
                if os.path.isfile(os.path.join("./cogs", filename)) \
                and filename.endswith('.py') \
                and filename != "COG_TEMPLATE.py":
                    await self.load_extension(f"cogs.{filename[:-len('.py')]}")
                    cog_count += 1
            except Exception as e:
                print(e)
                owner = await self.fetch_user(OWNER_ID)
                await owner.send(f"Couldn't load `{filename}` cog!")

        # copies it to my test server so it doesn't take forever to load
        # 1. Define the test guild object
        test_guild = disc.Object(id=TEST_SERVER_ID)
        
        # # ---- TEMP WIPING CODE ----
        # print("Wiping global command cache...")
        # self.tree.clear_commands(guild=None) # Clear local global memory
        # await self.tree.sync()               # Sync empty memory to Discord globally
        # # ---------------------------
        
        # 2. Copy the commands to the guild cache
        self.tree.copy_global_to(guild=test_guild)
        
        # 3. Sync specifically to that guild so changes appear INSTANTLY
        await self.tree.sync(guild=test_guild)
        print(f"Successfully loaded {cog_count} cog{'s' if cog_count != 1 else ''}.")

bot = SlashBot()

@bot.event
async def on_ready():
    now = datetime.now(pytz.timezone('America/Phoenix'))
    print(f"Logged in as {bot.user} at {now.strftime('%I:%M %p')}!")
    owner = await bot.fetch_user(OWNER_ID)
    await owner.send(f"Started bot at {now.strftime('%I:%M %p')}")
    
############################

@bot.group(name = "admin")
@commands.is_owner()
#@commands.dm_only()
async def admin(ctx: commands.Context):
    pass

@admin.command()
async def load(ctx: commands.Context, extension: str):
    try:
        # 1. Load the extension code into memory normally
        await bot.load_extension(f"cogs.{extension}")
    except Exception as e:
        # It's a good idea to log the real error to console so you can debug syntax errors
        print(f"Error loading {extension}: {e}")
        await see.error(ctx, f"`{extension}` cog does not exist or failed to parse.")
    else:
        # 2. Sync the command tree to push any app commands to Discord's servers
        try:
            await bot.tree.sync(guild=ctx.guild)            
            await ctx.send(f"Loaded and synced `{extension}` cog!", delete_after=10)
            print(f'Loaded & Synced "{extension}" cog!')
        except Exception as sync_error:
            print(f"Failed to sync command tree: {sync_error}")
            await ctx.send(f"Loaded `{extension}`, but failed to sync slash commands.", delete_after=10)

@admin.command()
async def unload(ctx: commands.Context, extension: str):
    try:
        # 1. Pull the extension out of the bot's runtime memory
        await bot.unload_extension(f"cogs.{extension}")
    except Exception as e:
        print(f"Error unloading {extension}: {e}")
        await see.error(ctx, f"`{extension}` cog does not exist or failed to unload.")
    else: 
        # 2. Sync to your test server to wipe the deleted slash commands from the UI
        await bot.tree.sync(guild=ctx.guild)
        
        await ctx.send(f"Unloaded and synced `{extension}` cog!", delete_after=10)
        print(f'Unloaded & Synced "{extension}" cog!')


@admin.command()
async def reload(ctx: commands.Context, extension: str):
    try:
        # 1. Hot-reload the extension with your updated Python code
        await bot.reload_extension(f"cogs.{extension}")
    except Exception as e:
        print(f"Error reloading {extension}: {e}")
        await see.error(ctx, f"`{extension}` cog failed to reload. Check console for syntax errors.")
    else:
        # 2. Sync to your test server so your code changes take effect INSTANTLY
        await bot.tree.sync(guild=ctx.guild)
        
        await ctx.send(f"Reloaded and synced `{extension}` cog!", delete_after=10)
        print(f'Reloaded & Synced "{extension}" cog!')


@admin.command()
async def sync(ctx: commands.Context):
    print("Synced bot tree.")
    test_guild = disc.Object(id=TEST_SERVER_ID)

    # 2. Copy the commands to the guild cache
    bot.tree.copy_global_to(guild=test_guild)
    
    # 3. Sync specifically to that guild so changes appear INSTANTLY
    await bot.tree.sync(guild=test_guild)
    # await bot.tree.sync()


bot.run(TOKEN)