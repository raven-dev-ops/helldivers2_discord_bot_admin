# cogs/members_cog.py

import discord
from discord.ext import commands
import logging
from database import get_mongo_client # Ensure this import is correct
from utils import log_to_monitor_channel # Ensure this import is correct
import asyncio # Import asyncio for potential delays

# Define the role ID you want to assign
TARGET_ROLE_ID = 1370202044425830541

class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Consider adding a check for the mongo_db client here as well if needed
        if not hasattr(self.bot, 'mongo_db') or self.bot.mongo_db is None:
            logging.warning("MongoDB client not found in bot object during MembersCog init. Database functions may fail.")


    @commands.Cog.listener()
    async def on_ready(self):
        """Assigns a specific role to all eligible members (excluding bots) across all guilds on startup."""
        logging.info("MembersCog is ready. Starting role assignment process...")

        target_role_id_int = TARGET_ROLE_ID # Use the defined constant

        for guild in self.bot.guilds:
            logging.info(f"Processing guild: '{guild.name}' ({guild.id}) for role assignment.")

            role = guild.get_role(target_role_id_int)

            if role is None:
                logging.warning(f"Role with ID {target_role_id_int} not found in guild '{guild.name}' ({guild.id}). Skipping role assignment for this guild.")
                continue # Skip to the next guild

            # Check if the bot has permissions to manage roles in this guild
            if not guild.me.guild_permissions.manage_roles:
                logging.error(f"Bot lacks 'Manage Roles' permission in guild '{guild.name}' ({guild.id}). Cannot assign roles in this guild. Skipping.")
                continue # Skip to the next guild

            # Check if the bot's role is higher than the target role in this guild
            if role >= guild.me.top_role:
                 logging.error(f"Bot's top role '{guild.me.top_role.name}' is not higher than or equal to the target role '{role.name}' ({role.id}) in guild '{guild.name}' ({guild.id}). Cannot assign this role in this guild. Skipping.")
                 continue # Skip to the next guild


            logging.info(f"Attempting to assign role '{role.name}' ({role.id}) to eligible members in guild '{guild.name}' ({guild.id}).")
            assigned_count = 0
            skipped_count = 0
            failed_count = 0

            # Filter out bots and members who already have the role
            members_to_assign = [m for m in guild.members if not m.bot and role not in m.roles]

            total_members_to_assign = len(members_to_assign)
            if total_members_to_assign == 0:
                logging.info(f"All eligible members in guild '{guild.name}' ({guild.id}) already have the role '{role.name}'.")
                continue # Move to the next guild

            logging.info(f"Found {total_members_to_assign} eligible members to assign role in guild '{guild.name}' ({guild.id}).")


            for i, member in enumerate(members_to_assign):
                # No need for interaction followup messages in on_ready

                try:
                    # Double check if the member still doesn't have the role (could have been added manually)
                    if role not in member.roles:
                         await member.add_roles(role, reason="Automatic role assignment on bot startup.")
                         assigned_count += 1
                         logging.debug(f"Assigned role '{role.name}' to {member.display_name} ({member.id}) in guild {guild.id}.")
                    else:
                        skipped_count += 1 # Count members who got the role since the list was made

                except discord.Forbidden:
                    logging.error(f"Bot lacks permissions to assign role '{role.name}' to {member.display_name} ({member.id}) in guild {guild.id}. Check role hierarchy.")
                    failed_count += 1
                except Exception as e:
                    logging.error(f"Failed to assign role '{role.name}' to {member.display_name} ({member.id}) in guild {guild.id}: {e}")
                    failed_count += 1

                # Add a delay to mitigate Discord API rate limits for add_roles
                await asyncio.sleep(0.5) # Adjust delay as needed based on server size and rate limits


            logging.info(f"Role assignment process finished for guild '{guild.name}' ({guild.id}):")
            logging.info(f"  Successfully assigned: {assigned_count}")
            # Calculate total skipped more accurately: total members - bots - already had role initially - successfully assigned - failed
            initial_eligible_members = len([m for m in guild.members if not m.bot and role not in m.roles]) # Re-calculate initially eligible
            total_members = len(guild.members)
            total_bots = len([m for m in guild.members if m.bot])
            initial_had_role = len([m for m in guild.members if role in m.roles])
            # Skipped = (Total Members - Total Bots - Initial Had Role) - Assigned - Failed
            # Or simpler: Initially eligible - Assigned - Failed
            skipped_during_loop = initial_eligible_members - assigned_count - failed_count
            logging.info(f"  Skipped (already had role or was a bot): {total_members - total_bots - assigned_count - failed_count}") # Simpler approx
            logging.info(f"  Failed to assign: {failed_count}")

        logging.info("Completed role assignment process for all guilds.")


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Updates the Alliance collection if a member changes their server nickname."""
        # Ensure bot can connect to DB for this operation
        if not hasattr(self.bot, 'mongo_db') or self.bot.mongo_db is None:
             logging.warning("MongoDB client not available for on_member_update.")
             return

        try:
            # Only proceed if the display name (server nickname) actually changed
            if before.display_name != after.display_name:
                db = self.bot.mongo_db['GPTHellbot'] # Use the bot's existing connection
                alliance_collection = db['Alliance']

                # Update the 'server_nickname' in the Alliance collection
                new_server_nickname = after.display_name.strip()
                result = await alliance_collection.update_one(
                    {
                        "discord_id": str(after.id),
                        "discord_server_id": str(after.guild.id)
                    },
                    {
                        "$set": {
                            "server_nickname": new_server_nickname
                        }
                    }
                )
                if result.matched_count > 0:
                    logging.info(f"Updated server_nickname for Discord ID {after.id} in guild {after.guild.id} to '{new_server_nickname}'.")
                else:
                    logging.warning(f"No Alliance entry found for Discord ID {after.id} in guild {after.guild.id} during nickname update.")
        except Exception as e:
            logging.error(f"Error updating nickname for {after.display_name} ({after.id}) in guild {after.guild.id}: {e}")
            # Use self.bot for log_to_monitor_channel as it's a cog method
            await log_to_monitor_channel(self.bot, f"Error updating nickname for {after.display_name}: {e}", logging.ERROR)


async def setup(bot):
     # Ensure the bot has the mongo_db client before adding the cog if on_member_update relies on it
     # This check might be redundant if handled in main bot setup, but good practice if this cog
     # could be loaded independently.
    if not hasattr(bot, 'mongo_db') or bot.mongo_db is None:
        logging.warning("MongoDB client not found in bot object during MembersCog setup. Database functions in this cog may fail.")
        # Decide if the cog should load anyway or not. Loading allows the cog to function,
        # but the on_member_update database logic will warn/fail.
        pass # Allow cog to load, log a warning

    await bot.add_cog(MembersCog(bot))