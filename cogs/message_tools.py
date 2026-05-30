import discord
from discord.ext import commands
from discord import app_commands
import datetime

class MessageTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deleted_messages = {}  # Store deleted messages per channel

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Store deleted message information"""
        if message.author.bot:
            return
        
        self.deleted_messages[message.channel.id] = {
            'content': message.content,
            'author': message.author,
            'created_at': message.created_at,
            'deleted_at': datetime.datetime.utcnow()
        }

    @app_commands.command(
        name="snipe",
        description="Show the last deleted message in this channel"
    )
    async def snipe(self, interaction: discord.Interaction):
        """Show the last deleted message in the channel"""
        channel_id = interaction.channel_id
        
        if channel_id not in self.deleted_messages:
            await interaction.response.send_message("❌ No recently deleted messages found!", ephemeral=True)
            return
            
        msg = self.deleted_messages[channel_id]
        
        embed = discord.Embed(
            description=msg['content'],
            color=0xa46ffb,  # Changed to hex color #a46ffb
            timestamp=msg['deleted_at']
        )
        embed.set_author(
            name=f"{msg['author'].name}#{msg['author'].discriminator}",
            icon_url=msg['author'].display_avatar.url
        )
        embed.set_footer(text=f"Message sent at {msg['created_at'].strftime('%H:%M:%S')}")

        # Move the footer logic here, after the embed is defined
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageTools(bot))