import os
import logging

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variable loader with validation
def load_env_var(var_name: int, required=True):
    value = os.getenv(var_name)
    if required and not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

# Load environment variables
mongo_uri = load_env_var('MONGODB_URI')
discord_token = load_env_var('DISCORD_TOKEN')
role_to_assign_id = int(load_env_var('ROLE_TO_ASSIGN_ID'))
welcome_channel_id = int(load_env_var('WELCOME_CHANNEL_ID'))
monitor_channel_id = int(load_env_var('MONITOR_CHANNEL_ID'))
leaderboard_channel_id = int(load_env_var('LEADERBOARD_CHANNEL_ID'))
kia_channel_id = int(load_env_var('KIA_CHANNEL_ID'))
channel_id = int(load_env_var('BOT_CHANNEL_ID'))
class_a_role_id = int(load_env_var('CLASS_A_ROLE_ID'))
guild_id = int(load_env_var('GUILD_ID'))
sos_network_id = int(load_env_var('SOS_NETWORK_ID'))
cadet_role_id = int(load_env_var('CADET_ROLE_ID'))
cadet_chat_id = int(load_env_var('CADET_CHAT_ID'))