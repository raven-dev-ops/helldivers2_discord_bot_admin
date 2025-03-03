# utils.py

import logging
from config import monitor_channel_id

async def log_to_monitor_channel(bot, message: str, level=logging.INFO):
    """Logs a message to the monitor channel and structured logs."""
    try:
        monitor_channel = bot.get_channel(monitor_channel_id)
        if monitor_channel:
            await monitor_channel.send(message)
        logging.log(level, message)
    except Exception as e:
        logging.error(f"Failed to log to monitor channel: {e}")
