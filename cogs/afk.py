import discord
from discord.ext import commands
from discord import app_commands
from utils.storage import JsonStorage
from datetime import datetime

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        self.afk_data = self.storage.load_data('afk_data.json')
        self.processed_messages = set()  # Track processed messages to prevent duplicates

    @app_commands.command(
        name='afk',
        description='Set your AFK status'
    )
    @app_commands.describe(reason="Reason for going AFK (optional)")
    async def afk(self, interaction: discord.Interaction, reason: str = "AFK"):
        """Set your AFK status"""
        user_id = str(interaction.user.id)
        self.afk_data[user_id] = {
            'reason': reason,
            'timestamp': datetime.now().timestamp(),
            'mentions': []
        }
        self.storage.save_data('afk_data.json', self.afk_data)

        embed = discord.Embed(
            title="AFK Status Set",
            description=f"<@{user_id}> is now AFK: {reason}",
            color=discord.Color(0xa46ffb)  # Set embed color to #a46ffb
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Prevent duplicate processing
        if message.id in self.processed_messages:
            return
        self.processed_messages.add(message.id)

        # Clean up processed messages set (keep last 1000 messages)
        if len(self.processed_messages) > 1000:
            self.processed_messages.clear()

        # Check if author was AFK
        author_id = str(message.author.id)
        if author_id in self.afk_data:
            # Remove AFK status
            afk_info = self.afk_data[author_id]
            duration = datetime.now().timestamp() - afk_info['timestamp']
            seconds = int(duration)  # Calculate duration in seconds

            # Create the embed with the desired format
            embed = discord.Embed(
                title=f"Welcome back, {message.author.name}!",  # Dynamically use the username
                color=discord.Color(0xa46ffb)  # Set embed color to #a46ffb
            )
            description = (
                "➤ I removed your AFK.\n"
                f"➤ You were AFK for {seconds} seconds.\n"
            )

            # Add mentions if any
            if afk_info['mentions']:
                # Use the most recent mention for the jump link
                recent_mention = afk_info['mentions'][-1]  # Get the last mention
                jump_link = f"https://discord.com/channels/{recent_mention['guild_id']}/{recent_mention['channel_id']}/{recent_mention['message_id']}"
                description += f"➤ You were mentioned while AFK:\n[Jump to Message]({jump_link})"
            else:
                description = description.rstrip("\n")  # Remove trailing newline if no mentions

            embed.description = description

            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            await message.channel.send(embed=embed)
            del self.afk_data[author_id]
            self.storage.save_data('afk_data.json', self.afk_data)

        # Check for mentions of AFK users
        for mentioned in message.mentions:
            mentioned_id = str(mentioned.id)
            if mentioned_id in self.afk_data:
                afk_info = self.afk_data[mentioned_id]
                afk_info['mentions'].append({
                    'user': message.author.name,
                    'channel': message.channel.name,
                    'channel_id': message.channel.id,  # Store channel ID for jump link
                    'message_id': message.id,  # Store message ID for jump link
                    'guild_id': message.guild.id  # Store guild ID for jump link
                })
                self.storage.save_data('afk_data.json', self.afk_data)

                embed = discord.Embed(
                    title="User is AFK",
                    description=f"💤 {mentioned.name} is AFK: {afk_info['reason']}",
                    color=discord.Color(0xa46ffb)  # Set embed color to #a46ffb
                )
                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by Seculex | © 2025")
                await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AFK(bot))