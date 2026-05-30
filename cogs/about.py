import discord
from discord.ext import commands
from discord import app_commands
from footer import FOOTER_TEXT  # Import the footer text from footer.py

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='about',
        description='Get information about the bot'
    )
    async def about_slash(self, interaction: discord.Interaction):
        """Get information about the bot"""
        # Calculate total users across all servers
        total_users = sum(guild.member_count for guild in self.bot.guilds)

        embed = discord.Embed(
            title="About Seculex Bot",
            description="A powerful Discord bot designed to enhance server interaction through intelligent automation.",
            color=discord.Color.blue()
        )

        # Add statistics
        embed.add_field(
            name="📊 Statistics",
            value=f"Servers: {len(self.bot.guilds)}\n"
                  f"Users: {total_users}\n"
                  f"Latency: {round(self.bot.latency * 1000)}ms",
            inline=True
        )

        # Add creator info
        embed.add_field(
            name="👨‍💻 Creator",
            value="<@riyalayu>",
            inline=True
        )

        # Add website
        embed.add_field(
            name="🌐 Website",
            value="[Seculex Website](https://seculex.com)",
            inline=True
        )

        embed.set_footer(
            text=FOOTER_TEXT,  # Use centralized footer
            icon_url="https://cdn.discordapp.com/emojis/1333522233766842489.png?v=1"
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(About(bot))