import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @app_commands.command(
        name="nuke",
        description="Nuke (recreate) the current channel"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def nuke(self, interaction: discord.Interaction):
        """Nuke the current channel (admin only)"""
        # Check cooldown
        if interaction.channel_id in self.cooldowns:
            await interaction.response.send_message("This channel was recently nuked. Please wait.", ephemeral=True)
            return

        await interaction.response.defer()

        # Store channel properties
        channel = interaction.channel
        channel_position = channel.position
        channel_category = channel.category
        channel_name = channel.name

        # Create new channel
        try:
            new_channel = await channel.clone()
            await new_channel.edit(position=channel_position)

            # Delete old channel
            await channel.delete()

            # Send confirmation message
            embed = discord.Embed(
                title="Channel Nuked! 💥",
                description=f"Channel was nuked by {interaction.user.mention}",
                color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
            )
            # Add the footer logic
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            await new_channel.send(embed=embed)

            # Set cooldown
            self.cooldowns[new_channel.id] = True

            # Remove cooldown after 5 minutes
            await asyncio.sleep(300)
            if new_channel.id in self.cooldowns:
                del self.cooldowns[new_channel.id]
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to nuke this channel!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Nuke(bot))