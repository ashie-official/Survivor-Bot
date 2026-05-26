import discord as disc
from discord.ext import commands as cmds

async def get_payload_info(bot: cmds.Bot, payload: disc.RawReactionActionEvent):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    #if bot_only and message.author.id != bot.user.id: raise Exception("Reacted to non-bot message.")

    if isinstance(channel, disc.channel.DMChannel): 
        reaction_author = bot.get_user(payload.user_id)
    else:
        reaction_author = payload.member
    return (channel, message, reaction_author)

async def do_we_gaf(bot: cmds.Bot, payload: disc.RawReactionActionEvent, bot_only = True):
    channel, message, reaction_author = await get_payload_info(bot, payload)
    
    # Ignore reactions on non-bot messages
    if bot_only and message.author.id != bot.user.id: return False
    
    # Ignore reactions from bot
    if reaction_author.id == bot.user.id: return False
    
    # If the user has the right to destroy the output, i.e. they own the output's contents or were the invoker
    for embed in message.embeds:
        did_user_cause_output = embed.footer.text.startswith(reaction_author.display_name)
        does_user_own_content = embed.author.name == reaction_author.display_name
        
        if did_user_cause_output or does_user_own_content:
            return True
    return False

async def exists_reaction_from_user(message: disc.Message, emoji_name: str, user: disc.User):
    # i hate the way i wrote this. TODO: rewrite this so it's prettier. i hate it
    try:
        message = await message.fetch() # get the most up-to-date version of the reaction
    except:
        # Being unable to fetch message implies that it's been deleted
        return False
    if not message.reactions: 
        return False

    check_me = None
    for reaction in message.reactions:
        if isinstance(reaction.emoji, str):
            if reaction.emoji == emoji_name:
                check_me = reaction
                break
        elif reaction.emoji.name == emoji_name:
            check_me = reaction
            break
    else:
        return False
    
    async for reaction_user in check_me.users():
        if user.id == reaction_user.id: return True
    return False

async def confirm_action(bot: cmds.Bot, ctx: cmds.Context, embed: disc.Embed):
    message = await ctx.send(embed=embed)
    await message.add_reaction('✅')
    await message.add_reaction('🚫')
    
    def check(payload: disc.RawReactionActionEvent):
        #print(payload.emoji.format('utc-8'))
        return  (payload.message_id == message.id)\
            and (payload.user_id == ctx.author.id)\
            and (payload.emoji.name in ['✅', '🚫'])
        
    try:
        payload = await bot.wait_for('raw_reaction_add', timeout=30.0, check=check)
        await message.delete()
        if payload.emoji.name == '✅': return True
        elif payload.emoji.name == '🚫': return False
    except:
        await message.delete()
        return False