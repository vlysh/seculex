import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_reminders = set()

    @app_commands.command()
    @app_commands.describe(
        user="The user to remind",
        message="The reminder message (write a message or leave blank for default message: 'You have been requested to come to the server as soon as possible.')"
    )
    async def remind(self, interaction: discord.Interaction, user: discord.Member, message: str = ""):
        """Send a reminder to a user"""
        reminder_id = f"{interaction.user.id}-{user.id}-{interaction.id}"
        if reminder_id in self.pending_reminders:
            await interaction.response.send_message("❌ A reminder is already pending for this user!", ephemeral=True)
            return

        self.pending_reminders.add(reminder_id)

        # Use default message if none provided
        default_message = "You have been requested to come to the server as soon as possible."
        final_message = message.strip() if message.strip() else default_message

        embed = discord.Embed(
            title="⏰ Reminder!",
            description=f"{user.mention}, you have a new reminder.",
            color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
        )
        embed.add_field(name="📢 From", value=interaction.user.mention, inline=True)
        embed.add_field(name="📡 Channel", value=interaction.channel.mention, inline=True)
        embed.add_field(name="💬 Message", value=final_message, inline=False)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        try:
            await interaction.response.defer()

            await user.send(embed=embed)
            await interaction.followup.send(f"✅ Reminder sent to {user.mention}!")

        except discord.Forbidden:
            await interaction.followup.send(f"❌ Could not send DM to {user.mention}!", ephemeral=True)
        finally:
            self.pending_reminders.remove(reminder_id)

    @app_commands.command()
    @app_commands.describe(
        time="Time until reminder (e.g. 1h, 30m, 1d)",
        message="What to remind you about"
    )
    async def remindme(self, interaction: discord.Interaction, time: str, message: str):
        """Set a reminder for yourself"""
        # Convert time string to seconds
        time_seconds = 0
        if 'h' in time:
            time_seconds = int(time.replace('h', '')) * 3600
        elif 'm' in time:
            time_seconds = int(time.replace('m', '')) * 60
        elif 'd' in time:
            time_seconds = int(time.replace('d', '')) * 86400
        else:
            await interaction.response.send_message("❌ Invalid time format! Use 'h' for hours, 'm' for minutes, or 'd' for days", ephemeral=True)
            return

        await interaction.response.defer()

        embed = discord.Embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you in {time}:\n{message}",
            color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.followup.send(embed=embed)

        # Wait for the specified time
        await asyncio.sleep(time_seconds)

        # Send the reminder
        reminder_embed = discord.Embed(
            title="⏰ Reminder",
            description=message,
            color=discord.Color(0xa46ffb)  # Updated color to #a46ffb
        )
        try:
            from footer import FOOTER_TEXT
            reminder_embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            reminder_embed.set_footer(text="Powered by Seculex | © 2025")

        try:
            await interaction.user.send(embed=reminder_embed)
        except discord.Forbidden:
            await interaction.followup.send(f"{interaction.user.mention} Here's your reminder: {message}")

async def setup(bot):
    await bot.add_cog(Reminder(bot))