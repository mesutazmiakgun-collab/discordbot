import discord
import os
import random
import asyncio
import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
# Load environment variables from .env file
load_dotenv()
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Optional guild ID to sync slash commands immediately in a test server
GUILD_ID = os.getenv('GUILD_ID')

# Prevent multiple bot instances using a lock file
LOCK_FILE = ".botlock"

def check_and_create_lock():
    """Check if another bot instance is running, prevent duplicates"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                old_pid = f.read().strip()
            print(f"⚠️  Bot lock file found (PID: {old_pid})")
            print("⚠️  Another bot instance may already be running!")
            print("⚠️  Deleting old lock file and starting fresh...")
            os.remove(LOCK_FILE)
        except Exception as e:
            print(f"Warning: Could not read lock file: {e}")
    
    # Create new lock file with current process ID
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        print(f"✅ Bot lock acquired (PID: {os.getpid()})")
    except Exception as e:
        print(f"Error creating lock file: {e}")

def cleanup_lock():
    """Remove lock file on exit"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print("✅ Bot lock cleaned up")
    except Exception as e:
        print(f"Warning: Could not remove lock file: {e}")

# Create bot with proper intents for slash commands
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True  # Required for reading message content
# Use a callable that returns an empty iterable to disable prefix commands
# (passing None causes discord.py to raise TypeError when processing messages)
bot = commands.Bot(command_prefix=lambda _bot, _msg: [], intents=intents, help_command=None)
bot_start_time = discord.utils.utcnow()

@bot.before_invoke
async def before_command(ctx):
    pass  # Silently track command execution

@bot.event
async def on_message(message: discord.Message):
    # Ignore all message content handling; this bot is slash-command only.
    return

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yaptık.')
    print(f'Loaded {len(bot.commands)} commands: {[cmd.name for cmd in bot.commands]}')
    print(f'GUILD_ID={GUILD_ID}')
    print(f'Guild count: {len(bot.guilds)}, guilds: {[guild.id for guild in bot.guilds]}')
    
    # Sync slash commands
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} guild slash command(s) for guild {GUILD_ID}")
        elif bot.guilds:
            synced = []
            for guild in bot.guilds:
                guild_synced = await bot.tree.sync(guild=guild)
                synced.extend(guild_synced)
                print(f"Synced {len(guild_synced)} slash command(s) for guild {guild.id}")
            print(f"Synced slash commands in {len(bot.guilds)} guild(s)")
        else:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} global slash command(s)")

        registered = [command.name for command in bot.tree.walk_commands()]
        print(f"Slash commands registered: {registered}")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")
death_messages = [
"{victim} was run over by an F-18 flown by {killer}.",
"{victim} was sniped by {killer} from 50ft away.",
"{victim} was quickscoped by {killer}.",
"{victim} was no-scoped by {killer}.",
"{victim} was flattened by a piano dropped by {killer}.",
"{victim} was launched into the sun by {killer}.",
"{victim} was erased from existence by {killer}.",
"{victim} was fed to a shark by {killer}.",
"{victim} was hunted down by {killer}'s attack helicopter.",
"{victim} forgot to pay taxes and was found by {killer}.",
"{victim} challenged {killer} to a duel and lost.",
"{victim} was drop-kicked into another dimension by {killer}.",
"{victim} was crushed by a giant rubber duck summoned by {killer}.",
"{victim} was vaporized by {killer}'s orbital laser.",
"{victim} was sent to the shadow realm by {killer}.",
"{victim} was deleted from the server by {killer}."
]

@bot.tree.command(name="help", description="Show bot commands and usage")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Help", description="Use slash commands in this server. Type `/` to open the command menu with autocomplete.", color=discord.Color.green())
    embed.add_field(name="🤖 Bot Commands", value="/hello - Say hello!\n/bye - Say goodbye!\n/howareyou - Ask how the bot is doing\n/ineedhelp - Get help information\n/wherecanigethelp - Learn where to get help\n/whoareyou - Learn about the bot\n/whatcanyoudo - See bot capabilities\n/tsbtrailer - Get TSB trailer link", inline=False)
    embed.add_field(name="ℹ️ Info Commands", value="/ping - Check bot latency\n/serverinfo - Get server information\n/userinfo [user] - Get user information\n/avatar [user] - Get user avatar\n/botinfo - Show bot information\n/membercount - Show member count\n/servericon - Show server icon\n/serverstats - Show detailed server stats\n/invite - Get bot invite link\n/help - Show this help menu", inline=False)
    embed.add_field(name="🎲 Fun Commands", value="/roll [sides] - Roll a dice (default 6)\n/coinflip - Flip a coin\n/rps <choice> - Play rock-paper-scissors\n/8ball <question> - Ask the magic 8-ball\n/choose <opt1> | <opt2> | ... - Let bot choose\n/quote - Get a random quote\n/joke - Hear a random joke\n/inspire - Get inspiration\n/fact - Get a random fact\n/reverse <text> - Reverse text\n/poll <question> - Create a yes/no poll\n/hug <user> - Give someone a hug\n/slap <user> - Playfully slap someone\n/kiss <user> - Kiss someone\n/punch <user> - Punch someone playfully\n/dance [user] - Dance with someone\n/color - Show a random color\n/commands - List all available commands", inline=False)
    embed.add_field(name="🛡️ Moderation Commands", value="/clear [amount] - Clear messages\n/kick <user> [reason] - Kick a user\n/ban <user> [reason] - Ban a user\n/unban <name> - Unban a user\n/mute <user> [minutes] - Timeout user\n/unmute <user> - Remove timeout\n/warn <user> [reason] - Warn a user\n/slowmode <seconds> - Set channel slowmode\n/lockdown - Lock channel\n/unlock - Unlock channel\n/announce <message> - Make announcement", inline=False)
    embed.add_field(name="⚙️ Utility Commands", value="/say <message> - Make bot repeat message\n/embed <title> <description> - Create embed\n/timer <minutes> - Set a timer\n/remind <minutes> <message> - Set reminder\n/countdown <seconds> - Start countdown\n/roles [user] - Show user roles\n/serverroles - List server roles\n/suggest <suggestion> - Submit suggestion\n/feedback <feedback> - Give feedback\n/serverrules - Show server rules\n/serverbanner - Show server banner\n/roleinfo <role> - Get role details", inline=False)
    embed.set_footer(text="More commands are coming soon!")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='kill', description='Generate a random death message')
async def kill_slash(interaction: discord.Interaction, member: discord.Member):

    death_message = random.choice(death_messages).format(
        victim=member.display_name,
        killer=interaction.user.display_name
    )

    embed = discord.Embed(
        title="💀 Death Message",
        description=death_message,
        color=discord.Color.dark_red()
    )

    await interaction.response.send_message(embed=embed)

# Slash command versions for popup/autocomplete support
@bot.tree.command(name='hello', description='Say hello')
async def hello_slash(interaction: discord.Interaction):
    await interaction.response.send_message('hello!')

@bot.tree.command(name='bye', description='Say goodbye')
async def bye_slash(interaction: discord.Interaction):
    await interaction.response.send_message('bye!')

@bot.tree.command(name='howareyou', description='Ask how the bot is doing')
async def how_are_you_slash(interaction: discord.Interaction):
    await interaction.response.send_message("I'm doing well, thank you!")

@bot.tree.command(name='ineedhelp', description='Get help information')
async def i_need_help_slash(interaction: discord.Interaction):
    await interaction.response.send_message("I'm here to help!")

@bot.tree.command(name='wherecanigethelp', description='Learn where to get help')
async def where_can_i_get_help_slash(interaction: discord.Interaction):
    await interaction.response.send_message('You can get help by asking questions to people in the server!')

@bot.tree.command(name='whoareyou', description='Learn about the bot')
async def who_are_you_slash(interaction: discord.Interaction):
    await interaction.response.send_message("I'm a bot designed to help you!")

@bot.tree.command(name='whatcanyoudo', description='See bot capabilities')
async def what_can_you_do_slash(interaction: discord.Interaction):
    await interaction.response.send_message('I can respond to certain commands and help you with information!')

@bot.tree.command(name='tsbtrailer', description='Get TSB trailer link')
async def tsb_trailer_slash(interaction: discord.Interaction):
    await interaction.response.send_message('https://www.youtube.com/watch?v=ZAMDGF-Wcy4')

@bot.tree.command(name='ping', description='Check bot latency')
async def ping_slash(interaction: discord.Interaction):
    latency = round(bot.latency * 1000) if bot.latency else 0
    await interaction.response.send_message(f'🏓 Pong! Latency: {latency}ms')

@bot.tree.command(name='serverinfo', description='Get server information')
async def server_info_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return

    embed = discord.Embed(title=f'{guild.name} Server Info', color=discord.Color.blue())
    embed.add_field(name='👥 Members', value=guild.member_count, inline=True)
    embed.add_field(name='📅 Created', value=guild.created_at.strftime('%Y-%m-%d'), inline=True)
    if guild.owner:
        embed.add_field(name='👑 Owner', value=guild.owner.mention, inline=True)
    else:
        embed.add_field(name='👑 Owner', value='Unknown', inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='userinfo', description='Get user information')
async def user_info_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    if isinstance(member, discord.User) and interaction.guild is not None:
        member = interaction.guild.get_member(member.id) or member

    embed = discord.Embed(title=f'{member.name}#{member.discriminator}', color=getattr(member, 'color', discord.Color.blue()) if getattr(member, 'color', None) != discord.Color.default() else discord.Color.blue())
    embed.add_field(name='🆔 ID', value=member.id, inline=True)
    embed.add_field(name='📅 Account Created', value=member.created_at.strftime('%Y-%m-%d'), inline=True)
    if isinstance(member, discord.Member):
        embed.add_field(name='📅 Joined', value=member.joined_at.strftime('%Y-%m-%d') if member.joined_at else 'Unknown', inline=True)
        embed.add_field(name='🎭 Roles', value=len(member.roles) - 1, inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    else:
        embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='avatar', description='Get user avatar')
async def avatar_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=getattr(member, 'color', discord.Color.blue()) if getattr(member, 'color', None) != discord.Color.default() else discord.Color.blue())
    embed.set_image(url=member.avatar.url if member.avatar else member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='botinfo', description='Show bot information')
async def bot_info_slash(interaction: discord.Interaction):
    total_commands = len(bot.commands)
    await interaction.response.send_message(f'🤖 I am {bot.user.name}, and I currently support {total_commands} commands. Use `/help` to see them all!')

@bot.tree.command(name='membercount', description='Show member count')
async def member_count_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return
    await interaction.response.send_message(f'👥 This server has {guild.member_count} members.')

@bot.tree.command(name='servericon', description='Show server icon')
async def server_icon_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return
    if guild.icon:
        embed = discord.Embed(title=f'{guild.name} Icon', color=discord.Color.blue())
        embed.set_image(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message('❌ This server does not have an icon.')

@bot.tree.command(name='serverstats', description='Show detailed server stats')
async def server_stats_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return
    online = sum(1 for member in guild.members if member.status != discord.Status.offline)
    text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
    voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
    roles_count = len(guild.roles)
    premium_count = guild.premium_subscription_count or 0
    embed = discord.Embed(title=f'{guild.name} Server Stats', color=discord.Color.blurple())
    embed.add_field(name='👥 Members', value=guild.member_count, inline=True)
    embed.add_field(name='🟢 Online', value=online, inline=True)
    embed.add_field(name='🏷️ Roles', value=roles_count, inline=True)
    embed.add_field(name='💬 Text Channels', value=text_channels, inline=True)
    embed.add_field(name='🔊 Voice Channels', value=voice_channels, inline=True)
    embed.add_field(name='🚀 Boosts', value=f'{premium_count} (Level {guild.premium_tier})', inline=True)
    embed.add_field(name='😄 Emojis', value=len(guild.emojis), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='invite', description='Get bot invite link')
async def invite_slash(interaction: discord.Interaction):
    invite_url = os.getenv('BOT_INVITE')
    if invite_url:
        await interaction.response.send_message(f'🔗 Invite me with this link: {invite_url}')
    else:
        await interaction.response.send_message("🔗 I don't have an invite link configured yet. Ask the bot owner to set BOT_INVITE in the .env file.")

@bot.tree.command(name='quote', description='Get a random quote')
async def quote_slash(interaction: discord.Interaction):
    quotes = [
        'Believe you can and you\'re halfway there.',
        'The only limit to our realization of tomorrow is our doubts of today.',
        'You miss 100% of the shots you don\'t take.',
        'Success is not final, failure is not fatal: it is the courage to continue that counts.',
        'Never let success get to your head. Never let failure get to your heart.',
        'The best way to predict the future is to create it.',
    ]
    await interaction.response.send_message(f'💬 {random.choice(quotes)}')

@bot.tree.command(name='joke', description='Hear a random joke')
async def joke_slash(interaction: discord.Interaction):
    jokes = [
        'Why did the scarecrow win an award? Because he was outstanding in his field!',
        'Why don\'t scientists trust atoms? Because they make up everything!',
        'What do you call fake spaghetti? An impasta!',
        'Why did the math book look sad? Because it had too many problems.',
        'I told my computer I needed a break, and it said \'No problem, I’ll go to sleep.',
    ]
    await interaction.response.send_message(f'😂 {random.choice(jokes)}')

@bot.tree.command(name='inspire', description='Get inspiration')
async def inspire_slash(interaction: discord.Interaction):
    inspirations = [
        'Every day is a second chance.',
        'Small steps every day add up to big results.',
        'You are capable of amazing things.',
        'The harder you work for something, the greater you\'ll feel when you achieve it.',
        'Don\'t wait for opportunity. Create it.',
    ]
    await interaction.response.send_message(f'✨ {random.choice(inspirations)}')

@bot.tree.command(name='fact', description='Get a random fact')
async def fact_slash(interaction: discord.Interaction):
    facts = [
        'Honey never spoils. Archaeologists have eaten 3,000-year-old honey and found it perfectly edible.',
        'Octopuses have three hearts and blue blood.',
        'A group of flamingos is called a flamboyance.',
        'Bananas are berries, but strawberries are not.',
        'A day on Venus is longer than a year on Venus.',
    ]
    await interaction.response.send_message(f'🔍 Fact: {random.choice(facts)}')

@bot.tree.command(name='reverse', description='Reverse text')
async def reverse_slash(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f'🔁 {text[::-1]}')

@bot.tree.command(name='poll', description='Create a yes/no poll')
async def poll_slash(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title='📊 Poll', description=question, color=discord.Color.purple())
    embed.set_footer(text=f'Poll created by {interaction.user}')
    message = await interaction.response.send_message(embed=embed)
    # No reaction support after response object, use followup if needed

@bot.tree.command(name='roll', description='Roll a dice')
async def roll_slash(interaction: discord.Interaction, sides: int = 6):
    if sides < 2 or sides > 100:
        await interaction.response.send_message('❌ Please choose a number between 2 and 100 for dice sides!')
        return
    result = random.randint(1, sides)
    await interaction.response.send_message(f'🎲 You rolled a {result} (1-{sides})')

@bot.tree.command(name='coinflip', description='Flip a coin')
async def coin_flip_slash(interaction: discord.Interaction):
    result = random.choice(['Heads', 'Tails'])
    await interaction.response.send_message(f'🪙 Coin flip result: **{result}**!')

@bot.tree.command(name='rps', description='Play rock-paper-scissors')
async def rock_paper_scissors_slash(interaction: discord.Interaction, choice: str):
    choices = ['rock', 'paper', 'scissors']
    choice = choice.lower()
    if choice not in choices:
        await interaction.response.send_message('❌ Please choose rock, paper, or scissors!')
        return
    bot_choice = random.choice(choices)
    if choice == bot_choice:
        result = f"🤝 It's a tie! We both chose {choice}"
    elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
        result = f'🎉 You win! {choice} beats {bot_choice}'
    else:
        result = f'😢 You lose! {bot_choice} beats {choice}'
    await interaction.response.send_message(result)

@bot.tree.command(name='8ball', description='Ask the magic 8-ball')
async def eight_ball_slash(interaction: discord.Interaction, question: str):
    responses = [
        'It is certain.',
        'Without a doubt.',
        'Most likely.',
        'Ask again later.',
        'Better not tell you now.',
        'My sources say no.',
        'Very doubtful.',
        'Signs point to yes.',
    ]
    await interaction.response.send_message(f'🎱 {random.choice(responses)}')

@bot.tree.command(name='choose', description='Let bot choose from options')
async def choose_slash(interaction: discord.Interaction, options: str):
    choices = [part.strip() for part in options.replace(',', '|').split('|') if part.strip()]
    if len(choices) < 2:
        await interaction.response.send_message('❌ Provide at least two options separated by `|` or `,`.')
        return
    await interaction.response.send_message(f'🎯 I choose: **{random.choice(choices)}**')

@bot.tree.command(name='say', description='Make bot repeat a message')
async def say_slash(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name='embed', description='Create an embed with color and fields')
async def create_embed_slash(interaction: discord.Interaction, title: str, description: str, color: str = 'blue'):
    if len(title) > 256:
        await interaction.response.send_message('❌ Title is too long! Maximum 256 characters.')
        return
    if len(description) > 4096:
        await interaction.response.send_message('❌ Description is too long! Maximum 4096 characters.')
        return
    
    # Parse color
    color_map = {
        'red': discord.Color.red(),
        'blue': discord.Color.blue(),
        'green': discord.Color.green(),
        'yellow': discord.Color.gold(),
        'purple': discord.Color.purple(),
        'pink': discord.Color.magenta(),
        'cyan': discord.Color.cyan(),
        'orange': discord.Color.orange(),
        'white': discord.Color.lighter_gray(),
    }
    embed_color = color_map.get(color.lower(), discord.Color.blue())
    
    embed = discord.Embed(title=title, description=description, color=embed_color)
    embed.set_footer(text=f'Created by {interaction.user}', icon_url=interaction.user.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='uptime', description='Show bot uptime')
async def uptime_slash(interaction: discord.Interaction):
    uptime_duration = discord.utils.utcnow() - bot_start_time
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    await interaction.response.send_message(f'⏱️ Uptime: {hours}h {minutes}m {seconds}s')

@bot.tree.command(name='timer', description='Set a timer in minutes')
async def timer_slash(interaction: discord.Interaction, minutes: int):
    if minutes < 1 or minutes > 1440:
        await interaction.response.send_message('❌ Please provide a timer value between 1 and 1440 minutes.')
        return
    await interaction.response.send_message(f'⏳ Timer started for {minutes} minutes! I will remind you when time is up.')
    async def timer_task():
        await asyncio.sleep(minutes * 60)
        await interaction.followup.send(f'⏰ Time is up, {interaction.user.mention}! Your {minutes}-minute timer has ended.')
    bot.loop.create_task(timer_task())

@bot.tree.command(name='remind', description='Set a reminder')
async def remind_slash(interaction: discord.Interaction, minutes: int, reminder: str):
    if minutes < 1 or minutes > 1440:
        await interaction.response.send_message('❌ Please provide a reminder time between 1 and 1440 minutes.')
        return
    await interaction.response.send_message(f'⏰ Reminder set for {minutes} minutes from now, {interaction.user.mention}!')
    async def reminder_task():
        await asyncio.sleep(minutes * 60)
        await interaction.followup.send(f'🔔 {interaction.user.mention}, reminder: {reminder}')
    bot.loop.create_task(reminder_task())

@bot.tree.command(name='countdown', description='Start a countdown in seconds')
async def countdown_slash(interaction: discord.Interaction, seconds: int):
    if seconds < 1 or seconds > 300:
        await interaction.response.send_message('❌ Please use a countdown between 1 and 300 seconds.')
        return
    message = await interaction.response.send_message(f'⏳ Countdown: {seconds} seconds remaining...')

    # edit response with follow-up message
    while seconds > 0:
        await asyncio.sleep(1)
        seconds -= 1
        try:
            await interaction.edit_original_response(content=f'⏳ Countdown: {seconds} seconds remaining...')
        except Exception:
            pass
    await interaction.followup.send(f'✅ Countdown complete, {interaction.user.mention}!')

@bot.tree.command(name='serverrules', description='Show server rules')
async def server_rules_slash(interaction: discord.Interaction):
    rules = (
        '1. Be kind and respectful.\n'
        '2. No spam or self-promotion.\n'
        '3. Keep channels on topic.\n'
        '4. Follow Discord Terms of Service.\n'
        '5. Have fun and help each other!'
    )
    await interaction.response.send_message(f'📜 Server Rules:\n{rules}')

@bot.tree.command(name='roles', description='Show user roles')
async def roles_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    role_names = [role.name for role in member.roles if role.name != '@everyone'] if isinstance(member, discord.Member) else []
    if not role_names:
        await interaction.response.send_message(f'ℹ️ {member.display_name} has no roles besides @everyone.')
        return
    await interaction.response.send_message(f'🛡️ Roles for {member.display_name}: {", ".join(role_names)}')

@bot.tree.command(name='serverroles', description='List server roles')
async def server_roles_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return
    roles = [role.name for role in guild.roles if role.name != '@everyone']
    await interaction.response.send_message(f'🏷️ Server Roles ({len(roles)}): {", ".join(roles)}')

@bot.tree.command(name='suggest', description='Submit a suggestion')
async def suggest_slash(interaction: discord.Interaction, suggestion: str):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return
    suggestion_channel = discord.utils.get(guild.text_channels, name='suggestions')
    embed = discord.Embed(title='💡 New Suggestion', description=suggestion, color=discord.Color.green())
    embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
    embed.add_field(name='Server', value=guild.name, inline=True)
    embed.add_field(name='Channel', value=interaction.channel.mention, inline=True)
    if suggestion_channel:
        await suggestion_channel.send(embed=embed)
        await interaction.response.send_message(f'✅ Suggestion sent to {suggestion_channel.mention}.')
    else:
        await interaction.response.send_message('✅ Suggestion noted! Create a `#suggestions` channel to send suggestions there automatically.')

@bot.tree.command(name='feedback', description='Give feedback')
async def feedback_slash(interaction: discord.Interaction, feedback_text: str):
    if not feedback_text.strip():
        await interaction.response.send_message('❌ Please provide feedback.')
        return
    await interaction.response.send_message(f'✅ Thanks for your feedback, {interaction.user.mention}!')

@bot.tree.command(name='announce', description='Make an announcement')
@app_commands.checks.has_permissions(manage_guild=True)
async def announce_slash(interaction: discord.Interaction, announcement: str):
    embed = discord.Embed(title='📢 Server Announcement', description=announcement, color=discord.Color.gold())
    embed.set_footer(text=f'Announced by {interaction.user}')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='clear', description='Clear messages')
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_slash(interaction: discord.Interaction, amount: int = 5):
    if amount < 1 or amount > 100:
        await interaction.response.send_message('❌ Please specify a number between 1 and 100!')
        return
    deleted = await interaction.channel.purge(limit=amount + 1)
    await interaction.response.send_message(f'🗑️ Successfully deleted {len(deleted) - 1} messages!', delete_after=5)

@bot.tree.command(name='slowmode', description='Set channel slowmode')
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode_slash(interaction: discord.Interaction, seconds: int):
    if seconds < 0 or seconds > 21600:
        await interaction.response.send_message('❌ Slowmode must be between 0 and 21600 seconds.')
        return
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f'✅ Slowmode set to {seconds} seconds for this channel.')

@bot.tree.command(name='lockdown', description='Lock channel for @everyone')
@app_commands.checks.has_permissions(manage_roles=True)
async def lockdown_slash(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message('🔒 Channel locked down for @everyone.')

@bot.tree.command(name='unlock', description='Unlock channel for @everyone')
@app_commands.checks.has_permissions(manage_roles=True)
async def unlock_slash(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = None
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message('🔓 Channel unlocked for @everyone.')

@bot.tree.command(name='warn', description='Warn a user')
@app_commands.checks.has_permissions(kick_members=True)
async def warn_slash(interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
    embed = discord.Embed(title='⚠️ Warning Issued', description=reason, color=discord.Color.orange())
    embed.add_field(name='Member', value=member.mention, inline=True)
    embed.add_field(name='Warned by', value=interaction.user.mention, inline=True)
    embed.set_footer(text=f'User ID: {member.id}')
    try:
        await member.send(f'You have been warned in {interaction.guild.name}: {reason}')
    except Exception:
        pass
    mod_log_channel = discord.utils.get(interaction.guild.text_channels, name='mod-log')
    if mod_log_channel:
        await mod_log_channel.send(embed=embed)
    await interaction.response.send_message(f'✅ {member.mention} has been warned.')

@bot.tree.command(name='kick', description='Kick a user')
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
    if member == interaction.user:
        await interaction.response.send_message("❌ You can't kick yourself!")
        return
    if interaction.user.top_role <= member.top_role:
        await interaction.response.send_message("❌ You can't kick someone with a higher or equal role!")
        return
    if interaction.guild.me.top_role <= member.top_role:
        await interaction.response.send_message("❌ I can't kick someone with a higher or equal role than me!")
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f'👢 {member.mention} has been kicked. Reason: {reason}')

@bot.tree.command(name='ban', description='Ban a user')
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
    if member == interaction.user:
        await interaction.response.send_message("❌ You can't ban yourself!")
        return

    if interaction.user.top_role <= member.top_role:
        await interaction.response.send_message("❌ You can't ban someone with a higher or equal role!")
        return

    if interaction.guild.me.top_role <= member.top_role:
        await interaction.response.send_message("❌ I can't ban someone with a higher or equal role than me!")
        return



    death_message = random.choice(death_messages).format(
        victim=member.display_name,
        killer=interaction.user.display_name
    )

    await member.ban(reason=reason)

    embed = discord.Embed(
        title="💀 Ban Hammer Activated",
        description=death_message,
        color=discord.Color.red()
    )

    embed.add_field(name="Reason", value=reason, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='unban', description='Unban a user')
@app_commands.checks.has_permissions(ban_members=True)
async def unban_slash(interaction: discord.Interaction, member_name: str):
    banned_users = await interaction.guild.bans()
    member_name = member_name.lower()
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name + '#' + user.discriminator).lower() == member_name or user.name.lower() == member_name:
            await interaction.guild.unban(user)
            await interaction.response.send_message(f'✅ {user.name}#{user.discriminator} has been unbanned!')
            return
    await interaction.response.send_message('❌ User not found in ban list!')

@bot.tree.command(name='mute', description='Timeout a user')
@app_commands.checks.has_permissions(moderate_members=True)
async def mute_slash(interaction: discord.Interaction, member: discord.Member, minutes: int = 5):
    if minutes < 1 or minutes > 1440:
        await interaction.response.send_message('❌ Please specify minutes between 1 and 1440 (24 hours)!')
        return
    if interaction.guild.me.top_role <= member.top_role:
        await interaction.response.send_message("❌ I can't mute someone with a higher or equal role than me!")
        return
    duration = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=f'Timed out by {interaction.user}')
    await interaction.response.send_message(f'🤐 {member.mention} has been muted for {minutes} minutes!')

@bot.tree.command(name='unmute', description='Remove timeout from a user')
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute_slash(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None, reason=f'Timeout removed by {interaction.user}')
    await interaction.response.send_message(f'🔊 {member.mention} has been unmuted!')

@bot.tree.command(name='serverbanner', description='Show server banner')
async def server_banner_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message('❌ This command can only be used in a server.')
        return
    if guild.banner:
        embed = discord.Embed(title=f'{guild.name} Banner', color=discord.Color.blue())
        embed.set_image(url=guild.banner.url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message('❌ This server does not have a banner.')

@bot.tree.command(name='roleinfo', description='Show role information')
async def role_info_slash(interaction: discord.Interaction, role: discord.Role):
    embed = discord.Embed(title=f'Role: {role.name}', color=role.color or discord.Color.blue())
    embed.add_field(name='ID', value=role.id, inline=True)
    embed.add_field(name='Color', value=str(role.color), inline=True)
    embed.add_field(name='Hoist', value='Yes' if role.hoist else 'No', inline=True)
    embed.add_field(name='Mentionable', value='Yes' if role.mentionable else 'No', inline=True)
    embed.add_field(name='Position', value=role.position, inline=True)
    embed.add_field(name='Members', value=len(role.members), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='hug', description='Give someone a hug')
async def hug_slash(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f'🤗 {interaction.user.mention} gives {member.mention} a warm hug!')

@bot.tree.command(name='slap', description='Playfully slap someone')
async def slap_slash(interaction: discord.Interaction, member: discord.Member):
    messages = [
        f'😅 {interaction.user.mention} playfully slaps {member.mention}!',
        f'🤨 {interaction.user.mention} smacks {member.mention} across the face!',
        f'💢 {interaction.user.mention} slaps {member.mention} with a fish!',
        f'👋 {interaction.user.mention} gives {member.mention} a mighty slap!',
    ]
    await interaction.response.send_message(random.choice(messages))

@bot.tree.command(name='kiss', description='Kiss someone')
async def kiss_slash(interaction: discord.Interaction, member: discord.Member):
    messages = [
        f'😘 {interaction.user.mention} kisses {member.mention}!',
        f'💋 {interaction.user.mention} gives {member.mention} a kiss!',
        f'😚 Smooch! {interaction.user.mention} → {member.mention}',
    ]
    await interaction.response.send_message(random.choice(messages))

@bot.tree.command(name='punch', description='Punch someone playfully')
async def punch_slash(interaction: discord.Interaction, member: discord.Member):
    messages = [
        f'👊 {interaction.user.mention} punches {member.mention}!',
        f'💥 {interaction.user.mention} throws a punch at {member.mention}!',
        f'🥊 {interaction.user.mention} lands a hit on {member.mention}!',
    ]
    await interaction.response.send_message(random.choice(messages))

@bot.tree.command(name='dance', description='Dance with someone')
async def dance_slash(interaction: discord.Interaction, member: discord.Member = None):
    if member:
        messages = [
            f'💃 {interaction.user.mention} dances with {member.mention}!',
            f'🕺 {interaction.user.mention} and {member.mention} are dancing!',
        ]
        await interaction.response.send_message(random.choice(messages))
    else:
        messages = [
            f'💃 {interaction.user.mention} is dancing!',
            f'🕺 {interaction.user.mention} busts a move!',
        ]
        await interaction.response.send_message(random.choice(messages))

@bot.tree.command(name='commands', description='Show all available slash commands')
async def list_commands_slash(interaction: discord.Interaction):
    commands = [cmd.name for cmd in interaction.client.tree.walk_commands()]
    cmd_text = ', '.join(sorted(commands))
    embed = discord.Embed(title='📋 Available Commands', description=f'Total: {len(commands)}', color=discord.Color.blurple())
    # Split into chunks for readability
    chunk_size = 10
    for i in range(0, len(commands), chunk_size):
        chunk = commands[i:i+chunk_size]
        embed.add_field(name=f'Commands {i+1}-{min(i+chunk_size, len(commands))}', value=', '.join(sorted(chunk)), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='color', description='Show a random color')
async def color_slash(interaction: discord.Interaction):
    value = random.randint(0, 0xFFFFFF)
    color = discord.Color(value)
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    embed = discord.Embed(title='🎨 Random Color', color=color)
    embed.add_field(name='Hex', value=f'#{value:06X}', inline=True)
    embed.add_field(name='RGB', value=f'({r}, {g}, {b})', inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='rate', description='Rate something or someone')
async def rate_slash(interaction: discord.Interaction, target: str):
    rating = random.randint(1, 10)
    response = f'📊 I rate {target}: **{rating}/10**'
    if rating <= 3:
        response += ' 💔'
    elif rating <= 6:
        response += ' 😐'
    elif rating <= 8:
        response += ' 😊'
    else:
        response += ' 😍'
    await interaction.response.send_message(response)

@bot.tree.command(name='poke', description='Poke someone')
async def poke_slash(interaction: discord.Interaction, member: discord.Member):
    messages = [
        f'👉 {interaction.user.mention} pokes {member.mention}!',
        f'💬 {interaction.user.mention} pokes {member.mention} with a stick!',
        f'✨ {interaction.user.mention} curiously pokes {member.mention}!',
    ]
    await interaction.response.send_message(random.choice(messages))

@bot.tree.command(name='trivia', description='Get a fun trivia fact')
async def trivia_slash(interaction: discord.Interaction):
    trivia_facts = [
        'Honey lasts forever! Archaeologists found 3,000-year-old honey that was still edible.',
        'A group of flamingos is called a \"flamboyance\".',
        'Bananas are berries, but strawberries are not technically berries.',
        'Octopuses have three hearts and blue blood.',
        'A day on Venus is longer than a year on Venus.',
        'Butterflies taste with their feet.',
        'Penguins can jump up to 6 meters high.',
        'Sharks have been on Earth longer than dinosaurs.',
        'A cockroach can live for a week without its head.',
        'Cleopatra lived closer to the invention of pizza than to the building of the Great Pyramid.',
    ]
    await interaction.response.send_message(f'🧠 {random.choice(trivia_facts)}')

@bot.tree.command(name='ship', description='Ship two people together')
async def ship_slash(interaction: discord.Interaction, person1: str, person2: str):
    percentage = random.randint(1, 100)
    bars = '█' * (percentage // 10) + '░' * (10 - percentage // 10)
    response = f'💕 **{person1}** + **{person2}** = **{percentage}%** compat\n{bars}'
    await interaction.response.send_message(response)

@bot.event
async def on_command_error(ctx, error):
    # Prevent duplicate error messages
    if hasattr(ctx, '_error_handled'):
        return
    ctx._error_handled = True

    print(f"Error handler triggered for command '{ctx.command.name if ctx.command else 'unknown'}': {type(error).__name__}")

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required arguments! Use `.help` to see command usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid arguments! Use `.help` to see command usage.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found! Make sure you're mentioning a valid user.")
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("❌ User not found! Make sure you're providing a valid username.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `.help` to see available commands.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"❌ Command is on cooldown! Try again in {round(error.retry_after)} seconds.")
    elif isinstance(error, commands.MaxConcurrencyReached):
        await ctx.send("❌ This command is being used too many times right now. Please wait.")
    else:
        # Log the error for debugging but don't show full error to users
        print(f"Unhandled error in command {ctx.command}: {error}")
        await ctx.send("❌ An unexpected error occurred! Please try again later.")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"[Slash Command Error] {interaction.command.name if interaction.command else 'unknown'}: {type(error).__name__} - {error}")
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use that command.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message("❌ This command is on cooldown. Try again later.", ephemeral=True)
    elif isinstance(error, app_commands.MissingRequiredArgument):
        await interaction.response.send_message("❌ Missing required argument for this command.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Command failed. Please try again later.", ephemeral=True)

# Only run the bot when this script is executed directly
if __name__ == "__main__":
    check_and_create_lock()
    
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if token:
        try:
            keep_alive()
            bot.run(token)
        except RuntimeError as e:
            if "already running" in str(e).lower():
                print("Bot is already running!")
            else:
                print(f"Failed to start bot: {e}")
        finally:
            cleanup_lock()
    else:
        print("Error: DISCORD_TOKEN not found in .env file")
        cleanup_lock()
else:
    print("Bot module imported but not running automatically.")
    print("To run the bot, execute this script directly: python bot.py")
