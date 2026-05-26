import discord as disc
from discord import app_commands as apps
from discord.ext import commands as cmds

from toolkit.command_info import CMD_INFO
from toolkit import iotools, handle_sessions, date_and_time as dnt

from datetime import datetime

class MATH(
    cmds.GroupCog, 
    group_name=CMD_INFO['MATH']['GROUP_INFORMATION']['name'], 
    group_description=CMD_INFO['MATH']['GROUP_INFORMATION']['desc']
):
    def __init__(self, bot: cmds.Bot):
        self.bot = bot
    
    @apps.command(
        name=CMD_INFO['MATH']['online_time']['name'],
        description=CMD_INFO['MATH']['online_time']['desc'],
    )
    @apps.describe(
        your_score = CMD_INFO['MATH']['online_time']['args']['your_score'],
        highest_score = CMD_INFO['MATH']['online_time']['args']['highest_score']
    )
    async def online_time(self, intx: disc.Interaction, your_score: int, highest_score: int | None = None) -> None:
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['MATH']['online_time']['title'],
            body = CMD_INFO['MATH']['online_time']['body']
        )
        
        TICK_RATE = 20
        player_time = your_score/TICK_RATE # kept in seconds for time purposes
        
        sessions = handle_sessions.load_sessions_data()['sessions']
        
        now = dnt.now()
        latest_session = sessions[0]
        latest_session_time = datetime.fromisoformat(sessions[0]['datetime'])
        
        for session in sessions:
            session_time = datetime.fromisoformat(latest_session['datetime'])
            
            if now < session_time:
                break
            else:
                latest_session = session
                latest_session_time = session_time
        
        time_elapsed = latest_session_time - now
        days_elapsed = latest_session_time.day - now.day + 1
        
        player_time_average = dnt.convert_secs(player_time/days_elapsed)
        
        
        
        
        if highest_score:
            highest_time = highest_score/TICK_RATE
            pass
        
        
        
        
        
        await intx.response.send_message(embed=embed, ephemeral=True)
        

async def setup(bot):
    await bot.add_cog(MATH(bot))