import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import logging
from datetime import datetime

# Configure logging for this file
logger = logging.getLogger(__name__)

class VerifyButton(View):
    def __init__(self, role_id):
        super().__init__(timeout=None)  # Make the button persistent
        self.role_id = role_id

    async def verify_callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Verification role not found! Please contact an admin.", ephemeral=True)
            logger.error(f"Verification role {self.role_id} not found in guild {interaction.guild.id}")
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("✅ You are already verified!", ephemeral=True)
            return

        # Defer the response to allow time for role assignment
        await interaction.response.defer(ephemeral=True)

        try:
            await interaction.user.add_roles(role)
            logger.info(f"User {interaction.user.id} verified with role {role.id} in guild {interaction.guild.id}")
            await interaction.followup.send("✅ You have been verified!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to assign roles!", ephemeral=True)
            logger.error(f"Bot lacks permission to assign role {role.id} in guild {interaction.guild.id}")
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            logger.error(f"HTTP error during verification for user {interaction.user.id}: {str(e)}")
        except Exception as e:
            await interaction.followup.send(f"❌ An unexpected error occurred: {str(e)}", ephemeral=True)
            logger.error(f"Unexpected verification error for user {interaction.user.id}: {str(e)}")

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        logger.error(f"Error in VerifyButton: {str(error)}")
        await interaction.followup.send("⚠️ An error occurred during verification. Please try again or contact an admin.", ephemeral=True)

    def add_items(self):
        verify_button = Button(
            label="Verify",
            style=discord.ButtonStyle.green,
            custom_id="verify_button",
            emoji="✅"
        )
        verify_button.callback = self.verify_callback
        self.add_item(verify_button)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="verify_setup",
        description="Setup the verification system"
    )
    @app_commands.describe(
        role="The role to give upon verification",
        channel="The channel for verification",
        custom_message="Optional custom message for the verification embed"
    )
    @app_commands.checks.has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)  # For prefix command permission check
    async def verify_setup(
        self,
        ctx: commands.Context,
        role: discord.Role,
        channel: discord.TextChannel,
        custom_message: str = None  # Optional parameter for custom message
    ):
        """Setup the verification system with a button"""

        # Check if bot has permission to send messages
        if not channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send("❌ I don't have permission to send messages in that channel!", ephemeral=True)
            logger.error(f"Bot lacks send_messages permission in channel {channel.id} in guild {ctx.guild.id}")
            return

        # Set default message if none provided, otherwise use the custom message
        default_message = (
            "<a:verify:1352219812700491776> Click the 'Verify' button below to get verified.\n"
            "<:security:1352220027205451841> Your safety is our priority!"
        )
        embed_description = custom_message if custom_message else default_message

        # Create embed with dynamic server name and updated color
        embed = discord.Embed(
            title=f"Welcome to {ctx.guild.name}",
            description=embed_description,
            color=0xa46ffb,  # Updated color to #a46ffb
            timestamp=datetime.utcnow()
        )

        # Set footer with try-except for importing FOOTER_TEXT
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        # Create view with verify button
        view = VerifyButton(role.id)
        view.add_items()  # Explicitly add the button to ensure it's initialized

        # Send verification message
        try:
            await channel.send(embed=embed, view=view)
            # Use ctx.send with ephemeral=True for slash commands, otherwise normal send
            if ctx.interaction:
                await ctx.send(f"✅ Verification system set up in {channel.mention}!", ephemeral=True)
            else:
                await ctx.send(f"✅ Verification system set up in {channel.mention}!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages in that channel!", ephemeral=True)
            logger.error(f"Bot lacks permission to send in channel {channel.id} in guild {ctx.guild.id}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            logger.error(f"Verification setup error in guild {ctx.guild.id}: {str(e)}")

async def setup(bot):
    await bot.add_cog(Verification(bot))