import discord as disc
from discord import app_commands as apps
from discord.ext import commands as cmds

from toolkit.command_info import CMD_INFO
from toolkit import iotools

class MY_COG(
    cmds.GroupCog, 
    group_name=CMD_INFO['COG_NAME']['GROUP_INFORMATION']['name'], 
    group_description=CMD_INFO['COG_NAME']['GROUP_INFORMATION']['desc']
):
    def __init__(self, bot: cmds.Bot):
        self.bot = bot
    
    @apps.command(
        name=CMD_INFO['COG_NAME']['COMMAND']['name'],
        description=CMD_INFO['COG_NAME']['COMMAND']['desc'],
    )
    @apps.describe(
        arg = CMD_INFO['COG_NAME']['COMMAND']['args']['arg']
    )
    async def cmd(self, intx: disc.Interaction, arg) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['COG_NAME']['COMMAND']['title'],
            body = CMD_INFO['COG_NAME']['COMMAND']['body']
        )
        await intx.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MY_COG(bot))