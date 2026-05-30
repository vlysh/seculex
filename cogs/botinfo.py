import discord
import psutil
import time
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    def get_bot_uptime(self):
        """Returns formatted bot uptime."""
        uptime_seconds = int(time.time() - self.start_time)
        uptime = str(timedelta(seconds=uptime_seconds))
        return uptime.split(".")[0]  # Remove milliseconds

    def get_system_stats(self):
        """Returns CPU, RAM, and memory usage."""
        process = psutil.Process()
        memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
        cpu_usage = psutil.cpu_percent(interval=None)  # Get CPU usage
        ram_usage = psutil.virtual_memory().percent  # Get RAM usage
        return {
            "cpu": f"{cpu_usage:.1f}%",
            "ram": f"{ram_usage:.1f}%",
            "memory": f"{memory_usage:.2f} MB"
        }

    @app_commands.command(
        name='botinfo',
        description='View bot statistics and analytics'
    )
    async def botinfo(self, interaction: discord.Interaction):
        """View bot statistics and analytics"""
        # Get bot statistics
        total_guilds = len(self.bot.guilds)
        total_users = sum(g.member_count or 0 for g in self.bot.guilds)
        latency = round(self.bot.latency * 1000, 2)  # Convert to ms
        system_stats = self.get_system_stats()
        uptime = self.get_bot_uptime()
        total_commands = len(self.bot.tree.get_commands())

        # Create the embed with stats in the description using triple backticks
        embed = discord.Embed(
            title="Seculex Stats",
            description=(
                "**Seculex is an all-in-one Discord companion, offering robust management, engaging features, and seamless integration. Discover more with `/help`**.\n\n"
                f"**<:purple_arrow:1351298291962220656> Seculex Stats**\n"
                f"```\n"
                f"Total Guilds: {total_guilds}\n"
                f"Total Users: {total_users}\n"
                f"Total Commands: {total_commands}\n"
                f"WebSocket Ping: {latency}ms\n"
                f"Uptime: {uptime}\n"
                f"```\n\n"
                f"**<:purple_arrow:1351298291962220656> System Stats**\n"
                f"```\n"
                f"CPU Usage: {system_stats['cpu']}\n"
                f"RAM Usage: {system_stats['ram']}\n"
                f"Memory Usage: {system_stats['memory']}\n"
                f"```"
            ),
            color=discord.Color(0xa46ffb)  # Fixed syntax error
        )

        # Add the footer
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))