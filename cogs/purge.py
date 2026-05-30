import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional
import logging

# Configure logging for this file
logger = logging.getLogger("discord.cogs.purge")

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='purge',
        description='Delete a specified number of messages'
    )
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        """Delete a specified number of messages"""
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel

        try:
            # Delete messages
            deleted = await channel.purge(limit=amount)
            embed = discord.Embed(
                title="Messages Purged ✅",
                description=f"Deleted {len(deleted)} messages.",
                color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Purged {len(deleted)} messages in {channel.name} by {interaction.user.name}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
            logger.warning(f"Permission denied purging messages in {channel.name} by {interaction.user.name}")
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            logger.error(f"Error in purge command: {str(e)}")

    @app_commands.command(
        name='purge_after',
        description='Delete messages after a specific message ID'
    )
    @app_commands.describe(message_id="ID of the message to purge after")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge_after(self, interaction: discord.Interaction, message_id: str):
        """Delete messages after a specific message ID"""
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel

        try:
            message = await channel.fetch_message(int(message_id))
            deleted = await channel.purge(after=message)
            embed = discord.Embed(
                title="Messages Purged ✅",
                description=f"Deleted {len(deleted)} messages after the specified message.",
                color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Purged {len(deleted)} messages after message ID {message_id} in {channel.name} by {interaction.user.name}")
        except discord.NotFound:
            await interaction.followup.send("❌ Message not found!", ephemeral=True)
            logger.warning(f"Message ID {message_id} not found in {channel.name} by {interaction.user.name}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
            logger.warning(f"Permission denied purging messages in {channel.name} by {interaction.user.name}")
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID!", ephemeral=True)
            logger.warning(f"Invalid message ID {message_id} in {channel.name} by {interaction.user.name}")

    @app_commands.command(
        name='purge_user',
        description='Delete messages from a specific user'
    )
    @app_commands.describe(
        user="The user whose messages to delete",
        amount="Number of messages to check (optional)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge_user(self, interaction: discord.Interaction, user: discord.Member, amount: Optional[int] = None):
        """Delete messages from a specific user"""
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel

        try:
            def check(msg):
                return msg.author == user

            deleted = await channel.purge(limit=amount, check=check)
            embed = discord.Embed(
                title="Messages Purged ✅",
                description=f"Deleted {len(deleted)} messages from {user.mention}.",
                color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Purged {len(deleted)} messages from {user.name} in {channel.name} by {interaction.user.name}")
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
            logger.warning(f"Permission denied purging messages from {user.name} in {channel.name} by {interaction.user.name}")
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            logger.error(f"Error in purge_user command: {str(e)}")

async def setup(bot):
    await bot.add_cog(Purge(bot))