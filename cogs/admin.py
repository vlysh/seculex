import discord
from discord.ext import commands
import logging
from footer import FOOTER_TEXT  # Import the footer text from footer.py

logger = logging.getLogger('discord')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Define initial owner IDs
        self.owner_ids = {1273840535466938422, 364141719597613056}
        # Set to store dynamically allowed user IDs
        self.allowed_ids = set()
        # Maintenance mode flag
        self.maintenance_mode = False
        logger.info("Admin cog initialized with owner IDs and maintenance mode setup")

        # Add global check for prefix commands
        self.bot.add_check(self.maintenance_check_prefix)

    def is_allowed(self, user_id: int) -> bool:
        """Check if a user is an owner or in the allowed list"""
        return user_id in self.owner_ids or user_id in self.allowed_ids

    async def maintenance_check_prefix(self, ctx: commands.Context) -> bool:
        """Global check for prefix commands to enforce maintenance mode"""
        if ctx.command.name in ["pvt", "pvtallow", "pvtremove"]:
            return True  # Allow admin commands to run for permission checks
        if self.maintenance_mode and not self.is_allowed(ctx.author.id):
            embed = discord.Embed(
                title="🚧 Bot in Maintenance Mode",
                description="The bot is currently under maintenance. Only owners and allowed users can use it. Please try again later.",
                color=discord.Color.orange()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)
            return False
        return True

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        """Global error handler for slash commands to enforce maintenance mode"""
        if isinstance(error, app_commands.CheckFailure) or (self.maintenance_mode and not self.is_allowed(interaction.user.id)):
            embed = discord.Embed(
                title="🚧 Bot in Maintenance Mode",
                description="The bot is currently under maintenance. Only owners and allowed users can use it. Please try again later.",
                color=discord.Color.orange()
            )
            embed.set_footer(text=FOOTER_TEXT)
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    # Handle !pvt command to toggle maintenance mode
    @commands.command(name="pvt")
    async def pvt(self, ctx):
        if not self.is_allowed(ctx.author.id):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only bot owners and allowed users can toggle maintenance mode!",
                color=discord.Color.red()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)
            return

        self.maintenance_mode = not self.maintenance_mode
        status = "enabled" if self.maintenance_mode else "disabled"
        description = (
            "The bot is now in maintenance mode. Only owners and allowed users can interact."
            if self.maintenance_mode
            else "The bot is now available for all users."
        )
        embed = discord.Embed(
            title=f"🔧 Maintenance Mode {status.capitalize()}",
            description=description,
            color=discord.Color.blue() if self.maintenance_mode else discord.Color.green()
        )
        embed.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=embed)
        logger.info(f"Maintenance mode {status} by {ctx.author} (ID: {ctx.author.id})")

    # Handle !pvtallow command to add allowed user
    @commands.command(name="pvtallow")
    async def pvtallow(self, ctx, user_id: int):
        if not await self.bot.is_owner(ctx.author):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only bot owners can add allowed users!",
                color=discord.Color.red()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)
            return

        self.allowed_ids.add(user_id)
        embed = discord.Embed(
            title="✅ User Allowed",
            description=f"User with ID {user_id} has been added to the allowed list.",
            color=discord.Color.green()
        )
        embed.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=embed)
        logger.info(f"User {user_id} added to allowed list by {ctx.author} (ID: {ctx.author.id})")

    # Handle !pvtremove command to remove allowed user
    @commands.command(name="pvtremove")
    async def pvtremove(self, ctx, user_id: int):
        if not await self.bot.is_owner(ctx.author):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only bot owners can remove allowed users!",
                color=discord.Color.red()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)
            return

        if user_id in self.allowed_ids:
            self.allowed_ids.remove(user_id)
            embed = discord.Embed(
                title="✅ User Removed",
                description=f"User with ID {user_id} has been removed from the allowed list.",
                color=discord.Color.green()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)
            logger.info(f"User {user_id} removed from allowed list by {ctx.author} (ID: {ctx.author.id})")
        else:
            embed = discord.Embed(
                title="❌ User Not Found",
                description=f"User with ID {user_id} is not in the allowed list.",
                color=discord.Color.red()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)

    async def cog_command_error(self, ctx, error):
        """Handle errors for commands in this cog"""
        if isinstance(error, commands.CheckFailure):
            pass  # Already handled by maintenance_check_prefix
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Argument",
                description="Please provide a user ID. Usage: !pvtallow <user_id> or !pvtremove <user_id>",
                color=discord.Color.red()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)
        else:
            logger.error(f"Error in Admin cog command: {error}")
            embed = discord.Embed(
                title="⚠️ Unexpected Error",
                description=f"An error occurred: {str(error)}",
                color=discord.Color.red()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))