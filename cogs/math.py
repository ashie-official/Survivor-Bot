import discord as disc
from discord import app_commands as apps
from discord.ext import commands as cmds

from toolkit.command_info import CMD_INFO
from toolkit import iotools, handle_sessions, date_and_time as dnt

from datetime import datetime
import io
from scipy.stats import binom, nbinom
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

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
    async def online_time(
        self, intx: disc.Interaction,
        your_score: apps.Range[int, 1, None],
        highest_score: apps.Range[int, 1, None] | None = None
    ) -> None:
        TICK_RATE = 20
        now = dnt.now()
        
        embed = iotools.build_embed(
            intx,
            title = CMD_INFO['MATH']['online_time']['title'],
        )
        
        sessions = handle_sessions.load_sessions_data()['sessions']
        
        # setting default values if it goes weird
        last_time = datetime.fromisoformat(sessions[0]['datetime'])
        next_time = datetime.fromisoformat(sessions[-1]['datetime'])
        
        for session in sessions:
            session_time = datetime.fromisoformat(session['datetime'])
            
            if now < session_time: # the session is in the future
                next_time = datetime.fromisoformat(session['datetime'])
                break
            else:
                last_time = session_time
        
        days_elapsed = (now.date() - last_time.date()).days + 1
        
        embed.add_field(
            name = "Your Online Time",
            value = '\n'.join([
                f"**Time Played:** {dnt.convert_secs(your_score/TICK_RATE)}",
                f"**Average Time per Day: {round(your_score/TICK_RATE/days_elapsed/3600,1)} per day"
            ]),
            inline = False
        )
        
        if highest_score:
            lines = [
                f"**Time Played:** {dnt.convert_secs(highest_score/TICK_RATE)}",
                f"**Average Time per Day: {round(highest_score/TICK_RATE/days_elapsed/3600,1)} per day"
            ]
            
            if highest_score > your_score:
                lines.append("")
                lines.append(f"**Time Difference:** {dnt.convert_secs((highest_score - your_score)/TICK_RATE)}")
                lines.append(f"**Avg. Time/Day Diff.:** {round((highest_score - your_score)/TICK_RATE/days_elapsed/3600,1)} per day")

            embed.add_field(
                name = "Highest Online Time",
                value = '\n'.join(lines),
                inline = False
            )
        
        
        embed.add_field(
            name = "Overall Time",
            value = '\n'.join([
                f"**Last Session:** {dnt.timezone_str(last_time)}",
                f"**Time Elapsed:** {dnt.convert_secs((now - last_time).total_seconds())}",
                "",
                f"**Next Session:** {dnt.timezone_str(next_time)}",
                f"**Time Left: {dnt.convert_secs((next_time - now).total_seconds())}"
            ]),
            inline = False
        )
        
        await intx.response.send_message(embed=embed, ephemeral=True)

    
    
    
    def generate_attempt_plot(self,dist_obj, s: dict) -> io.BytesIO:
        """
        Plots the Negative Binomial distribution CDF.
        Trims off the initial flatline delay on high success targets.
        """
        # 🟢 New: Calculate the 0.1% completion floor instead of blindly starting at base successes
        plot_min = s['x_min'] + int(dist_obj.ppf(0.001))
        
        # Keep the bounds aligned with our metrics
        x_start = max(s['x_min'], plot_min)
        x_end = s['x_max'] # Already anchored nicely to p95 inside slash command

        x = np.arange(x_start, x_end + 1)
        cdf_y = dist_obj.cdf(x - s['x_min'])

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(7, 4))
        
        ax.set_xlim(x_start, x_end)
        ax.set_ylim(0, 1.05)
        canvas_left, canvas_right = ax.get_xlim()

        # Palette Map: Lime -> Orange -> Red
        ax.axvspan(canvas_left, s['p50'], facecolor='lime', alpha=0.1, edgecolor='none', label='0-50% (Lucky)')
        ax.axvspan(s['p50'], s['p75'], facecolor='orange', alpha=0.1, edgecolor='none', label='50-75% (Average)')
        ax.axvspan(s['p75'], canvas_right, facecolor='red', alpha=0.14, edgecolor='none', label='75-95% (Unlucky)')

        # Plots & Lines
        ax.plot(x, cdf_y, color='#5865F2', linewidth=2.5, label='Cumulative Probability')
        ax.axvline(s['mean'], color='#ff4757', linestyle='--', linewidth=1.5, label=f"Mean ({s['mean']:.1f})")
        ax.axvline(s['mode'], color='#1e90ff', linestyle=':', linewidth=2, label=f"Mode ({s['mode']})")

        # Styling
        ax.set_xlabel(s['x_label'], fontsize=10)
        ax.set_ylabel('Probability (Cumulative)', fontsize=10)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.grid(True, axis='y', linestyle=':', alpha=0.4)
        ax.legend(loc='upper left', bbox_to_anchor=(0.01, 0.99), fontsize=8)
        
        plt.tight_layout()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=120)
        img_buffer.seek(0)
        plt.close(fig)
        return img_buffer
    
    @apps.command(
        name=CMD_INFO['MATH']['attempt_stats']['name'],
        description=CMD_INFO['MATH']['attempt_stats']['desc'],
    )
    @apps.describe(
        rate = CMD_INFO['MATH']['attempt_stats']['args']['rate'],
        successes = CMD_INFO['MATH']['attempt_stats']['args']['successes']
    )
    async def attempt_stats(
        self, intx: disc.Interaction, 
        rate: apps.Range[float, 0.0001, 1.0], 
        successes: apps.Range[int, 1, None] = 1
    ):
        await intx.response.defer(ephemeral=True)

        frozen_dist = nbinom(n=successes, p=rate)
        mean = round(successes / rate, 2)
        mode = 1 if successes == 1 else successes + int(np.floor((successes - 1) * (1 - rate) / rate)) 
        
        p50 = successes + int(frozen_dist.ppf(0.50))
        p75 = successes + int(frozen_dist.ppf(0.75))
        p95 = successes + int(frozen_dist.ppf(0.95))

        stats_data = {
            "title": f"Attempts needed for {successes} successes ({round(100*rate, 2)}% success rate)" if successes != 1 else f"Attempts needed for success ({round(100*rate, 2)}% success rate)",
            "x_label": "Total Attempts Required",
            "mean": mean, "mode": mode, "p50": p50, "p75": p75, "p95": p95,
            "x_min": successes, "x_max": p95
        }

        # Format Text Embed Fields
        embed = iotools.build_embed(intx, title=stats_data["title"])
        embed.add_field(name="Expected Averages", value=f"**Average (Mean)**: `{mean}` attempts\n**Most Likely (Mode)**: `{mode}` attempts", inline=False)
        embed.add_field(
            name="Percentiles",
            value='\n'.join([
                f"**50th Percentile (Median):** 50% of players done in `{p50}` attempts",
                f"**75th Percentile:** 75% of players done in `{p75}` attempts",
                f"**95th Percentile:** 95% of players done in `{p95}` attempts (Safe Bet)"
            ]),
            inline=False
        )
        
        # Render and dispatch securely
        embed.set_image(url="attachment://cdf_graph.png")
        with self.generate_attempt_plot(frozen_dist, stats_data) as buf:
            await intx.followup.send(embed=embed, file=disc.File(fp=buf, filename="cdf_graph.png"))
    
    
    
    def generate_success_plot(self,dist_obj, s: dict) -> io.BytesIO:
        """
        Plots the Binomial distribution CDF. 
        Trims extreme left and right outliers to keep the curve perfectly centered.
        """
        # 🟢 New: Dynamically find where the data actually matters (0.1% to 99.9%)
        plot_min = int(dist_obj.ppf(0.001))
        plot_max = int(dist_obj.ppf(0.999))
        
        # Ensure our statistical landmarks are visible even with tight clipping
        x_start = min(plot_min, s['p95'])
        x_end = max(plot_max, s['p50'])

        x = np.arange(x_start, x_end + 1)
        cdf_y = dist_obj.cdf(x)

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(7, 4))
        
        ax.set_xlim(x_start, x_end)
        ax.set_ylim(0, 1.05)
        canvas_left, canvas_right = ax.get_xlim()

        # Palette Map: Red -> Orange -> Yellow -> Lime
        ax.axvspan(canvas_left, s['p95'], facecolor='red', alpha=0.14, edgecolor='none', label='0-5% (Floor Guarantee)')
        ax.axvspan(s['p95'], s['p75'], facecolor='orange', alpha=0.1, edgecolor='none', label='5-25% (Low Yield)')
        ax.axvspan(s['p75'], s['p50'], facecolor='yellow', alpha=0.1, edgecolor='none', label='25-50% (Below Average)')
        ax.axvspan(s['p50'], canvas_right, facecolor='lime', alpha=0.1, edgecolor='none', label='>50% (Above Average)')

        # Plots & Lines
        ax.plot(x, cdf_y, color='#5865F2', linewidth=2.5, label='Cumulative Probability')
        ax.axvline(s['mean'], color='#ff4757', linestyle='--', linewidth=1.5, label=f"Mean ({s['mean']:.1f})")
        ax.axvline(s['mode'], color='#1e90ff', linestyle=':', linewidth=2, label=f"Mode ({s['mode']})")

        # Styling
        ax.set_xlabel(s['x_label'], fontsize=10)
        ax.set_ylabel('Probability (Cumulative)', fontsize=10)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.grid(True, axis='y', linestyle=':', alpha=0.4)
        ax.legend(loc='upper left', bbox_to_anchor=(0.01, 0.99), fontsize=8)
        
        plt.tight_layout()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=120)
        img_buffer.seek(0)
        plt.close(fig)
        return img_buffer
    
    @apps.command(
        name=CMD_INFO['MATH']['success_stats']['name'],
        description=CMD_INFO['MATH']['success_stats']['desc'],
    )
    @apps.describe(
        rate = CMD_INFO['MATH']['success_stats']['args']['rate'],
        attempts = CMD_INFO['MATH']['success_stats']['args']['attempts']
    )
    async def success_stats(
        self, intx: disc.Interaction,
        rate: apps.Range[float, 0.0001, 1.0], 
        attempts: apps.Range[int, 2, None]
    ):
        await intx.response.defer(ephemeral=True)

        frozen_dist = binom(n=attempts, p=rate)
        mean = round(attempts * rate, 2)
        mode = int(np.floor((attempts + 1) * rate))
        
        p50 = int(frozen_dist.ppf(0.50))
        p75 = int(frozen_dist.ppf(0.25))  # Bottom 25% boundary line
        p95 = int(frozen_dist.ppf(0.05))  # Bottom 5% absolute floor line

        stats_data = {
            "title": f"Expected yield for {attempts} attempts ({round(100*rate, 2)}% success rate)",
            "x_label": "Total Successes Yielded",
            "mean": mean, "mode": mode, "p50": p50, "p75": p75, "p95": p95,
            "x_min": 0, "x_max": int(frozen_dist.ppf(0.99))
        }

        # Format Text Embed Fields
        embed = iotools.build_embed(intx, title=stats_data["title"])
        embed.add_field(name="Expected Averages", value=f"**Average (Mean)**: `{mean}` successes\n**Most Likely (Mode)**: `{mode}` successes", inline=False)
        embed.add_field(
            name="Percentiles",
            value='\n'.join([
                f"**5th Percentile:** 95% chance to get at least `{p95}` successes (Safe Bet)",
                f"**25th Percentile:** 75% chance to get at least `{p75}` successes",
                f"**50th Percentile (Median):** 50% chance to get at least `{p50}` successes",
            ]),
            inline=False
        )

        # Render and dispatch securely
        embed.set_image(url="attachment://cdf_graph.png")
        with self.generate_success_plot(frozen_dist, stats_data) as buf:
            await intx.followup.send(embed=embed, file=disc.File(fp=buf, filename="cdf_graph.png"))
        
    
async def setup(bot):
    await bot.add_cog(MATH(bot))