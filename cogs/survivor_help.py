import discord as disc
from discord.ext import commands as cmds


import toolkit.send_error_embed as see

class SURVIVOR_HELP(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cmds.group(name = "MY_COG", invoke_without_command = True)
    async def my_cog(self, ctx: cmds.Context, arg: str = None):
        await see.cmd_group(ctx, arg)
    
    @my_cog.command()
    async def subfunction(self, ctx: cmds.Context):
        await ctx.send(
            "default message"
        )

async def setup(bot):
    await bot.add_cog(SURVIVOR_HELP(bot))