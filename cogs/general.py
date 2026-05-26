import discord as disc
from discord import app_commands as apps
from discord.ext import commands as cmds

from toolkit.command_info import CMD_INFO
from toolkit import iotools

class GENERAL(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #--------------------------------------------------------
    # group = apps.Group(
    #     name=CMD_INFO['COG_NAME']['group']['name'], 
    #     description=CMD_INFO['COG_NAME']['group']['desc']
    # )
    #--------------------------------------------------------

    @apps.command(
        name=CMD_INFO['GENERAL']['about']['name'],
        description=CMD_INFO['GENERAL']['about']['desc'],
    )
    async def about(self, intx: disc.Interaction) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['GENERAL']['about']['title'],
            body = CMD_INFO['GENERAL']['about']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)

    
    @apps.command(
        name=CMD_INFO['GENERAL']['help']['name'],
        description=CMD_INFO['GENERAL']['help']['desc'],
    )
    async def help(self, intx: disc.Interaction) -> None:
        pass

async def setup(bot):
    await bot.add_cog(GENERAL(bot))