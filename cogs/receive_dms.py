import discord as disc
from discord import app_commands as apps
from discord.ext import commands as cmds

from toolkit.command_info import CMD_INFO
from toolkit import iotools
from toolkit import handle_users


class RECEIVE_DMS(
    cmds.GroupCog, 
    group_name=CMD_INFO['RECEIVE_DMS']['GROUP_INFORMATION']['name'], 
    group_description=CMD_INFO['RECEIVE_DMS']['GROUP_INFORMATION']['desc']
):
    def __init__(self, bot: cmds.Bot):
        self.bot = bot
    
    @apps.command(
        name=CMD_INFO['RECEIVE_DMS']['announcements']['name'],
        description=CMD_INFO['RECEIVE_DMS']['announcements']['desc'],
    )
    @apps.choices(opt=[
        apps.Choice(name="in 🟢", value=1),
        apps.Choice(name="out 🔴", value=0)
    ])
    async def announcements(self, intx: disc.Interaction, opt: apps.Choice[int]) -> None:
        is_opting_in = bool(opt.value)
        
        user_profile = await handle_users.load_user_profile(intx)
        user_profile['receive_announcements'] = is_opting_in
        handle_users.save_user_profile(intx, user_profile)
        
        if is_opting_in:
            title = "Enabled Announcements!"
            body = "You will now receive announcements from the Minecraft Survivor CBS Team."
            colour = disc.Colour.green()
        else:
            title = "Disabled Announcements!"
            body = "You will no longer receive announcements from the Minecraft Survivor CBS Team."
            colour = disc.Colour.brand_red()
            
        embed = iotools.build_embed(intx, title = title, body = body, colour = colour)
        await intx.response.send_message(embed=embed, ephemeral=True)
    
    reminder = apps.Group(
        name=       CMD_INFO['RECEIVE_DMS']['reminder']['GROUP_INFORMATION']['name'], 
        description=CMD_INFO['RECEIVE_DMS']['reminder']['GROUP_INFORMATION']['desc']
    )
    
    @reminder.command(
        name=       CMD_INFO['RECEIVE_DMS']['reminder']['add']['name'],
        description=CMD_INFO['RECEIVE_DMS']['reminder']['add']['desc'],
    )
    @apps.describe(
        hours =     CMD_INFO['RECEIVE_DMS']['reminder']['add']['args']['hours'],
        minutes =   CMD_INFO['RECEIVE_DMS']['reminder']['add']['args']['minutes'],
        name =      CMD_INFO['RECEIVE_DMS']['reminder']['add']['args']['name'],
        week =      CMD_INFO['RECEIVE_DMS']['reminder']['add']['args']['week']
    )
    async def reminder_add(
        self, 
        intx: disc.Interaction, 
        hours: apps.Range[int, 0, 23] = 0, 
        minutes: apps.Range[int, 0, 59] = 0, 
        name: str = "",
        week: apps.Range[int, 1, 15] | None = None
    ):
        minutes_before = 60*hours + minutes
        week = week if week else 0
        is_repeating = not bool(week) # if week is 0, it's repeating
        reminder = {
            "name": name.strip(),
            "minutes_before": minutes_before,
            "week": week,
            "is_repeating": is_repeating
        }
        
        user_profile = await handle_users.load_user_profile(intx)
        user_reminders = user_profile['session_reminders']
        already_exists = any(minutes_before == r['minutes_before'] and week == r['week'] for r in user_reminders)
        
        
        # 1. divmod dynamically splits your total minutes into (hours, remaining_minutes) in one line
        hours_before, mins_remaining = divmod(minutes_before, 60)

        # 2. Build your time descriptive segments dynamically
        time_segments = []
        if hours_before > 0:
            time_segments.append(f"{hours_before} hour{'s' if hours_before > 1 else ''}")
        if mins_remaining > 0:
            time_segments.append(f"{mins_remaining} minute{'s' if mins_remaining > 1 else ''}")

        # Join them together with a comma if both exist (e.g., "1 hour, 30 minutes")
        time_string = ", ".join(time_segments) if time_segments else "0 minutes"
        
        if already_exists:
            # 3. Determine your clean text targets based on the status flags
            reminder_type = "repeating " if is_repeating else ""
            event_target = "the session" if is_repeating else f"week {week}"

            # 4. Assemble the final body text in one single, beautifully readable f-string
            body = f"There is a {reminder_type}reminder for {time_string} before {event_target}."
            
            title = "A reminder like that already exists!"            
            colour = disc.Colour.brand_red()
        else:
            user_profile['session_reminders'].append(reminder)
            handle_users.save_user_profile(intx, user_profile)
            title = f"Created reminder{': '+name if name else ''}."
            body = \
                f"**Week:** {"Repeating" if is_repeating else week}\n" + \
                f"**Time before:** {time_string}"
            colour = disc.Colour.green()
            
        embed = iotools.build_embed(intx, title = title, body = body, colour = colour)
        await intx.response.send_message(embed=embed, ephemeral=True)
    
    
    def _prep_reminder_list_(self, reminders: list[dict])-> str:
        sorted_reminders = sorted(
            reminders,
            key=lambda r: (
                r['week'], 
                -r['minutes_before']                      
            )
        )
        
        embed_body_lines = []

        for index, r in enumerate(sorted_reminders, start=1):
            # Format the time layout cleanly
            hours, mins = divmod(r['minutes_before'], 60)
            if r['minutes_before'] == 0:
                time_str = "0m"
            else:
                time_str = " ".join([f"{hours}h" if hours else "", f"{mins}m" if mins else ""]).strip()

            # Determine indicators
            type_icon = "🔁" if r['is_repeating'] else "🗓️"
            target = "All Sessions" if r['is_repeating'] else f"Week {r['week']}"
            
            # DYNAMIC NAME CHECK: If name is empty, label it by its list index position
            if r['name'] and r['name'].strip():
                display_name = f"{r['name'].strip()}"
            else:
                display_name = f"Reminder #{index}"
                
            # Assemble your clean bullet point line
            embed_body_lines.append(
                f"{type_icon} **{index}. {display_name}:** `{time_str}` before {target}"
            )

        final_body = "\n".join(embed_body_lines)
        return final_body
    
    @reminder.command(
        name=       CMD_INFO['RECEIVE_DMS']['reminder']['list']['name'],
        description=CMD_INFO['RECEIVE_DMS']['reminder']['list']['desc'],
    )
    async def reminder_list(self, intx: disc.Interaction):
        user_profile = await handle_users.load_user_profile(intx)
        user_reminders = user_profile['session_reminders']
        
        if not user_reminders:
            # user has no reminders!
            body = "You have no reminders set yet!\nUse `/receive_dms session_reminder set` to set a reminder."
            colour = disc.Colour.brand_red()
        else:
            body = self._prep_reminder_list_(user_reminders)
            colour = disc.Colour.green()
            
        embed = iotools.build_embed(
            intx,
            title = "Session Reminder List", 
            body = body,
            colour = colour
        )
        await intx.response.send_message(embed=embed, ephemeral=True)
    
    
    @reminder.command(
        name=CMD_INFO['RECEIVE_DMS']['reminder']['remove']['name'],
        description=CMD_INFO['RECEIVE_DMS']['reminder']['remove']['desc'],
    )
    async def reminder_remove(self, intx: disc.Interaction):
        user_profile = await handle_users.load_user_profile(intx)
        user_reminders = user_profile.get('session_reminders', [])
        
        if not user_reminders:
            embed = iotools.build_embed(
                intx=intx, 
                title="Remove Reminder", 
                body="You don't have any reminders set up yet! Nothing to remove.", 
                colour=disc.Colour.brand_red()
            )
            return await intx.response.send_message(embed=embed, ephemeral=True)

        # PERFECT REUSE: Feeds data seamlessly straight to your helper method!
        list_body = self._prep_reminder_list_(user_reminders)
        
        embed = iotools.build_embed(
            intx=intx, 
            title="Select Reminder to Remove", 
            body=list_body, 
            colour=disc.Colour.orange()
        )
        
        dropdown_shelf = ReminderDropdownView(self.bot, user_reminders)
        
        await intx.response.send_message(
            embed=embed, 
            view=dropdown_shelf, 
            ephemeral=True
        )
    
    
# ==========================================
# 1. THE CONFIRMATION EMBED PANEL
# ==========================================
class DeleteConfirmationView(disc.ui.View):
    def __init__(self, bot: cmds.Bot, target_index: int, label: str, details: str):
        super().__init__(timeout=60)
        self.bot = bot
        self.target_index = target_index
        self.label = label
        self.details = details

    @disc.ui.button(label="Yes, Delete It", style=disc.ButtonStyle.danger, emoji="🗑️")
    async def confirm(self, intx: disc.Interaction, button: disc.ui.Button):
        await intx.response.defer(ephemeral=True)
        
        user_profile = await handle_users.load_user_profile(intx)
        reminders = user_profile.get('session_reminders', [])
        
        # Verify the list array bounds haven't shifted mid-session
        if self.target_index < 0 or self.target_index >= len(reminders):
            error_embed = iotools.build_embed(
                intx=intx,
                title="Action Failed",
                body="⚠️ This reminder no longer exists on your profile layout.",
                colour=disc.Colour.brand_red(),
                ignore_footer=True
            )
            return await intx.edit_original_response(embed=error_embed, view=None)
            
        reminders.pop(self.target_index)
        handle_users.save_user_profile(intx, user_profile)
        
        # Standardized syntax check successful
        success_embed = iotools.build_embed(
            intx=intx,
            title="Reminder Successfully Removed",
            body=f"❌ Deleted **{self.label}**\n*{self.details}*",
            colour=disc.Colour.green(),
            ignore_footer=True
        )
        
        await intx.edit_original_response(embed=success_embed, view=None)

    @disc.ui.button(label="Cancel", style=disc.ButtonStyle.secondary)
    async def cancel(self, intx: disc.Interaction, button: disc.ui.Button):
        cancel_embed = iotools.build_embed(
            intx=intx,
            title="Canceled",
            body="❌ No changes were made to your profile data configuration.",
            colour=disc.Colour.yellow(),
            ignore_footer=True
        )
        await intx.response.edit_message(embed=cancel_embed, view=None)

# ==========================================
# 2. THE EMBED-DRIVEN DROPDOWN CONTAINER
# ==========================================
class ReminderDropdownView(disc.ui.View):
    def __init__(self, bot: cmds.Bot, reminders: list[dict]):
        super().__init__(timeout=180)
        self.bot = bot
        
        # ⚠️ WE REPLICATE YOUR UNIQUE SORT CRITERIA HERE ⚠️
        # This keeps option numbering identical to the layout generated by _prep_reminder_list_
        sorted_reminders = sorted(
            reminders,
            key=lambda r: (r['week'] if r['week'] is not None else 0, -r['minutes_before'])
        )
        
        options = []
        for index, r in enumerate(sorted_reminders, start=1):
            hours, mins = divmod(r['minutes_before'], 60)
            if r['minutes_before'] == 0:
                time_str = "0m"
            else:
                time_str = " ".join([f"{hours}h" if hours else "", f"{mins}m" if mins else ""]).strip()
            target = "All Sessions" if r['is_repeating'] else f"Wk {r['week']}"
            
            if r['name'] and r['name'].strip():
                display_name = r['name'].strip()
            else:
                display_name = f"Reminder #{index}"
            
            options.append(
                disc.SelectOption(
                    label=f"{index}. {display_name}",
                    description=f"{time_str} before {target}",
                    value=str(index - 1) # Shifted back to 0-based index targeting for code sorting arrays
                )
            )

        self.select_menu = disc.ui.Select(
            placeholder="Select a reminder to delete...",
            options=options,
            min_values=1,
            max_values=1
        )
        
        self.select_menu.callback = self.on_dropdown_select
        self.add_item(self.select_menu)

    async def on_dropdown_select(self, intx: disc.Interaction):
        chosen_index = int(self.select_menu.values[0])
        chosen_option = next(opt for opt in self.select_menu.options if opt.value == str(chosen_index))
        
        confirm_body = (
            f"Are you absolutely sure you want to permanently delete this reminder?\n\n"
            f"**Target:** {chosen_option.label}\n"
            f"**Configuration:** *{chosen_option.description}*"
        )
        
        confirm_embed = iotools.build_embed(
            intx=intx,
            title="⚠️ Confirm Reminder Deletion",
            body=confirm_body,
            colour=disc.Colour.orange(),
            ignore_footer=True
        )
        
        confirm_screen = DeleteConfirmationView(
            bot=self.bot, 
            target_index=chosen_index, 
            label=chosen_option.label, 
            details=chosen_option.description
        )
        
        await intx.response.send_message(
            embed=confirm_embed,
            view=confirm_screen,
            ephemeral=True
        )

    
async def setup(bot):
    await bot.add_cog(RECEIVE_DMS(bot))