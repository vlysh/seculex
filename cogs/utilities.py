import discord
from discord.ext import commands
from discord import app_commands
import socket
import dns.resolver
import datetime
import pytz
import json
import os
from typing import Optional
from googletrans import Translator, LANGUAGES

class Utilities(commands.Cog):
    """Utility commands for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.timezone_file = 'data/user_timezones.json'
        os.makedirs('data', exist_ok=True)
        self._load_timezones()
        self.translator = Translator()

    def _load_timezones(self):
        try:
            with open(self.timezone_file, 'r') as f:
                self.user_timezones = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.user_timezones = {}
            self._save_timezones()

    def _save_timezones(self):
        with open(self.timezone_file, 'w') as f:
            json.dump(self.user_timezones, f, indent=4)

    @app_commands.command()
    async def timestamp(self, interaction: discord.Interaction):
        """Shows the current UTC timestamp"""
        current_time = datetime.datetime.now(datetime.timezone.utc)
        unix_timestamp = int(current_time.timestamp())

        embed = discord.Embed(
            title="🕒 Current Timestamp",
            description=f"Unix Timestamp: `{unix_timestamp}`\n"
                       f"UTC Time: `{current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}`",
            color=0xa46ffb
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe(timezone="The timezone to set (e.g., 'Asia/Kolkata', 'America/New_York')")
    async def timezone_set(self, interaction: discord.Interaction, timezone: str):
        """Set your preferred timezone"""
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.datetime.now(tz)

            user_id = str(interaction.user.id)
            self.user_timezones[user_id] = timezone
            self._save_timezones()

            embed = discord.Embed(
                title="✅ Timezone Set",
                description=f"Your timezone has been set to: `{timezone}`\n"
                           f"Current time in your timezone: `{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}`",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

        except pytz.exceptions.UnknownTimeZoneError:
            embed = discord.Embed(
                title="❌ Error",
                description="Invalid timezone! Please use a valid timezone identifier (e.g., 'Asia/Kolkata', 'America/New_York').",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def timezone(self, interaction: discord.Interaction):
        """View your current timezone settings"""
        user_id = str(interaction.user.id)
        user_tz = self.user_timezones.get(user_id)

        if not user_tz:
            embed = discord.Embed(
                title="❌ No Timezone Set",
                description="You haven't set a timezone yet! Use `/timezone_set` to set your timezone.",
                color=0xa46ffb
            )
        else:
            tz = pytz.timezone(user_tz)
            current_time = datetime.datetime.now(tz)
            embed = discord.Embed(
                title="🌍 Your Timezone",
                description=f"Your timezone is set to: `{user_tz}`\n"
                           f"Current time: `{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}`",
                color=0xa46ffb
            )

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe(
        lookup_type="Type of lookup (domain/ip)",
        target="Domain name or IP address to look up"
    )
    async def lookup(self, interaction: discord.Interaction, lookup_type: str, target: str):
        """Look up information about a domain or IP address"""
        if lookup_type.lower() not in ['domain', 'ip']:
            await interaction.response.send_message("❌ Invalid lookup type! Use 'domain' or 'ip'.", ephemeral=True)
            return

        await interaction.response.defer()

        embed = discord.Embed(
            title=f"🔍 {lookup_type.upper()} Lookup",
            color=0xa46ffb
        )

        try:
            if lookup_type.lower() == 'domain':
                # Get A records
                a_records = dns.resolver.resolve(target, 'A')
                ips = [str(record) for record in a_records]
                embed.add_field(name="IP Addresses", value='\n'.join(ips) or 'None found', inline=False)

                try:
                    # Get MX records
                    mx_records = dns.resolver.resolve(target, 'MX')
                    mx = [f"{str(record.exchange)} (priority: {record.preference})" for record in mx_records]
                    embed.add_field(name="Mail Servers", value='\n'.join(mx) or 'None found', inline=False)
                except dns.resolver.NoAnswer:
                    embed.add_field(name="Mail Servers", value='None found', inline=False)

                try:
                    # Get NS records
                    ns_records = dns.resolver.resolve(target, 'NS')
                    ns = [str(record) for record in ns_records]
                    embed.add_field(name="Nameservers", value='\n'.join(ns) or 'None found', inline=False)
                except dns.resolver.NoAnswer:
                    embed.add_field(name="Nameservers", value='None found', inline=False)

            else:  # IP lookup
                try:
                    hostname = socket.gethostbyaddr(target)[0]
                    embed.add_field(name="Hostname", value=hostname, inline=False)
                except socket.herror:
                    embed.add_field(name="Hostname", value="Not found", inline=False)

                embed.add_field(name="IP Address", value=target, inline=False)

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            embed.description = "❌ No records found!"
        except Exception as e:
            embed.description = f"❌ An error occurred: {str(e)}"

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await interaction.followup.send(embed=embed)

    @commands.hybrid_command(name="translate")
    @app_commands.describe(
        text="Text to translate",
        dest_lang="Destination language code (e.g., 'es' for Spanish, 'fr' for French)",
        src_lang="Source language code (optional, defaults to auto-detect)"
    )
    async def translate(self, ctx: commands.Context, text: str, dest_lang: str, src_lang: Optional[str] = 'auto'):
        """Translate text to a specified language"""
        # Defer the response for slash commands or send a typing indicator for prefix commands
        if ctx.interaction:
            await ctx.interaction.response.defer()
        else:
            await ctx.typing()

        try:
            # Validate destination language code
            if dest_lang.lower() not in LANGUAGES:
                error_msg = "❌ Invalid destination language code! Use codes like 'es' (Spanish), 'fr' (French), 'de' (German), etc."
                if ctx.interaction:
                    await ctx.interaction.followup.send(error_msg, ephemeral=True)
                else:
                    await ctx.send(error_msg)
                return

            # Perform translation
            translation = self.translator.translate(text, dest=dest_lang.lower(), src=src_lang.lower())
            
            embed = discord.Embed(
                title="🌐 Translation",
                color=0xa46ffb
            )
            embed.add_field(
                name=f"Original ({translation.src})",
                value=text,
                inline=False
            )
            embed.add_field(
                name=f"Translated ({dest_lang})",
                value=translation.text,
                inline=False
            )

            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            # Send response based on command type
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Translation Error",
                description=f"An error occurred: {str(e)}",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))