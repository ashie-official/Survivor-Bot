import discord as disc
from discord import app_commands as apps
from discord.ext import commands as cmds

from toolkit.command_info import CMD_INFO
from toolkit import iotools

class SURVIVOR_HELP(
    cmds.GroupCog, 
    group_name=CMD_INFO['SURVIVOR_HELP']['GROUP_INFORMATION']['name'], 
    group_description=CMD_INFO['SURVIVOR_HELP']['GROUP_INFORMATION']['desc']
):
    def __init__(self, bot: cmds.Bot):
        self.bot = bot
    
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['about']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['about']['desc'],
    )
    async def about(self, intx: disc.Interaction) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['SURVIVOR_HELP']['about']['title'],
            body = CMD_INFO['SURVIVOR_HELP']['about']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)
    
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['rules']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['rules']['desc'],
    )
    async def rules(self, intx: disc.Interaction) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['SURVIVOR_HELP']['rules']['title'],
            body = CMD_INFO['SURVIVOR_HELP']['rules']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)
    
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['banned_mods']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['banned_mods']['desc'],
    )
    async def banned_mods(self, intx: disc.Interaction) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['SURVIVOR_HELP']['banned_mods']['title'],
            body = CMD_INFO['SURVIVOR_HELP']['banned_mods']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)
        
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['server_info']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['server_info']['desc'],
    )
    async def server_info(self, intx: disc.Interaction) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['SURVIVOR_HELP']['server_info']['title'],
            body = CMD_INFO['SURVIVOR_HELP']['server_info']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)
        
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['FAQ']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['FAQ']['desc'],
    )
    async def faq(self, intx: disc.Interaction) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['SURVIVOR_HELP']['FAQ']['title'],
            body = CMD_INFO['SURVIVOR_HELP']['FAQ']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)
    
    
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['show_random_tip']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['show_random_tip']['desc'],
    )
    async def show_random_tip(self, intx: disc.Interaction) -> None:
        # TODO
        embed = iotools.build_embed(
            intx,
            title = "",     # CMD_INFO['SURVIVOR_HELP']['show_random_tip']['title'],
            body = ""       # CMD_INFO['SURVIVOR_HELP']['show_random_tip']['body']
        )
        await intx.response.send_message(embed=embed,ephemeral=True)
    
    
    @apps.command(
        name=CMD_INFO['SURVIVOR_HELP']['user_submit_tip']['name'],
        description=CMD_INFO['SURVIVOR_HELP']['user_submit_tip']['desc'],
    )
    @apps.describe(content = CMD_INFO['SURVIVOR_HELP']['user_submit_tip']['args']['content'])
    async def user_submit_tip(self, intx: disc.Interaction, content: str) -> None:
        # TODO
        embed = iotools.build_embed(
            intx,
            title = "",     # CMD_INFO['SURVIVOR_HELP']['user_submit_tip']['title'],
            body = ""       # CMD_INFO['SURVIVOR_HELP']['user_submit_tip']['body']
        )
        await intx.response.send_message(embed=embed,ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(SURVIVOR_HELP(bot))