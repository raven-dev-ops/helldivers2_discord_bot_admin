import discord
from discord.ext import commands
from config import discord_token
import logging
import os
from database import create_indexes
import traceback

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)

async def load_cogs():
    """
    Load the bot's cogs in the correct order.
    """
    cogs = [
        'cogs.departure_cog',
        'cogs.members_cog',
        'cogs.promotion_cog',
        'cogs.arrival_cog',
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"Successfully loaded cog: {cog}")
        except Exception as e:
            logging.error(f"Failed to load cog {cog}: {e}")
            logging.error(traceback.format_exc())

@bot.event
async def setup_hook():
    """
    Hook to load all cogs during bot startup.
    """
    logging.info("Running setup_hook to load cogs...")
    # Ensure MongoDB indexes are created
    await create_indexes()

    await load_cogs()
    logging.info("Cogs loaded.")

@bot.event
async def on_ready():
    """
    Triggered when the bot is ready.
    """
    try:
        logging.info(f'{bot.user} has logged in and is ready.')
        if os.getenv('SYNC_COMMANDS') == 'true':
            synced = await bot.tree.sync()
            logging.info(f"Slash commands synced ({len(synced)} commands).")
    except Exception as e:
        logging.error(f"An error occurred during on_ready: {e}")

def validate_env_variables():
    """
    Validate that all required environment variables are set.
    """
    required_env_vars = [
        'DISCORD_TOKEN', 'MONGODB_URI',
        'ROLE_TO_ASSIGN_ID', 'WELCOME_CHANNEL_ID',
        'MONITOR_CHANNEL_ID', 'LEADERBOARD_CHANNEL_ID',
        'KIA_CHANNEL_ID', 'BOT_CHANNEL_ID',
        'CLASS_A_ROLE_ID', 'GUILD_ID', 'SOS_NETWORK_ID', 'CADET_CHAT_ID', 'CADET_ROLE_ID'
    ]
    for var in required_env_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"{var} environment variable is not set.")

if __name__ == "__main__":
    validate_env_variables()
    discord_token = os.getenv('DISCORD_TOKEN')
    try:
        bot.run(discord_token)
    except Exception as e:
        logging.error(f"An error occurred while running the bot: {e}")
