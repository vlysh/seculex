import discord
from discord.ext import commands
from discord import app_commands
from utils.storage import JsonStorage
import logging

# Configure logging for this file
logger = logging.getLogger("discord.cogs.auto_responder")

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        # Load guild-specific responses, initializing an empty dict if none exists
        self.responses = self.storage.load_data('auto_responses.json') or {}

    @app_commands.command(
        name='ar',
        description='Add an auto response for this server'
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        trigger="The word or phrase that triggers the auto response",
        response="The message to send when the trigger is detected"
    )
    async def add_response(self, interaction: discord.Interaction, trigger: str, response: str):
        """Add an auto response specific to this server"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.responses:
            self.responses[guild_id] = {}

        self.responses[guild_id][trigger.lower()] = response
        self.storage.save_data('auto_responses.json', self.responses)

        embed = discord.Embed(
            title="✅ Auto Response Added",
            description=f"Added auto response for '{trigger}' in this server",
            color=discord.Color.green()
        )
        embed.add_field(name="Trigger", value=trigger)
        embed.add_field(name="Response", value=response)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='dr',
        description='Delete an auto response from this server'
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(trigger="The trigger word/phrase to delete")
    async def delete_response(self, interaction: discord.Interaction, trigger: str):
        """Delete an auto response from this server"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.responses or trigger.lower() not in self.responses[guild_id]:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Trigger '{trigger}' not found in this server!",
                color=discord.Color.orange()
            )
        else:
            del self.responses[guild_id][trigger.lower()]
            if not self.responses[guild_id]:  # Clean up empty guild dict
                del self.responses[guild_id]
            self.storage.save_data('auto_responses.json', self.responses)

            embed = discord.Embed(
                title="✅ Auto Response Deleted",
                description=f"Deleted auto response for '{trigger}' in this server",
                color=discord.Color.red()
            )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='lr',
        description='List all auto responses for this server'
    )
    async def list_responses(self, interaction: discord.Interaction):
        """List all auto responses for this server"""
        guild_id = str(interaction.guild.id)
        guild_responses = self.responses.get(guild_id, {})

        if not guild_responses:
            embed = discord.Embed(
                title="📋 Auto Responses",
                description="No auto responses set for this server!",
                color=discord.Color.blue()
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by SECULEX | © 2025")
            await interaction.response.send_message(embed=embed)
            return

        # Create paginated embeds if there are many responses
        responses_per_page = 10
        responses_list = list(guild_responses.items())

        for i in range(0, len(responses_list), responses_per_page):
            page_responses = responses_list[i:i + responses_per_page]

            embed = discord.Embed(
                title="📋 Auto Responses",
                description=f"Page {i//responses_per_page + 1}/{(len(responses_list)-1)//responses_per_page + 1} for this server",
                color=discord.Color.blue()
            )

            for trigger, response in page_responses:
                embed.add_field(
                    name=f"Trigger: {trigger}",
                    value=f"Response: {response}",
                    inline=False
                )

            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by SECULEX | © 2025")

            if i == 0:  # Only send the first page as a response
                await interaction.response.send_message(embed=embed)
            else:  # Send following pages as follow-up messages
                await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:  # Ignore bot messages and DMs
            return

        content = message.content.lower()
        guild_id = str(message.guild.id)
        guild_responses = self.responses.get(guild_id, {})

        for trigger, response in guild_responses.items():
            if trigger in content:
                await message.channel.send(response)
                break

async def setup(bot):
    await bot.add_cog(AutoResponder(bot))