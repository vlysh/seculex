import discord
from discord.ext import commands
import asyncio
import os
import logging
import traceback
from dotenv import load_dotenv
from footer import FOOTER_TEXT  # Import the footer text from footer.py

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("discord_bot.log")],
)
logger = logging.getLogger("discord")

class SeculexBot(commands.Bot):
    def __init__(self):
        logger.info("Initializing SeculexBot...")
        # Explicitly enable required intents
        intents = discord.Intents.all()
        intents.message_content = True  # Explicitly enable for AFK and message processing
        intents.members = True  # For member-related features
        intents.messages = True  # Ensure message events are enabled

        application_id = os.getenv("APPLICATION_ID")
        token = os.getenv("DISCORD_TOKEN")

        if not application_id or not token:
            raise ValueError("Missing required environment variables: APPLICATION_ID or DISCORD_TOKEN")

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            application_id=int(application_id),
            help_command=None
        )
        self.token = token
        self.owner_ids = {1444558632107769978, 1399700915006476419}  # Your owner IDs

    async def setup_hook(self):
        """Initial bot setup and force sync slash commands"""
        logger.info("Starting bot setup...")

        essential_cogs = [
            "help",
            "fun",
            "games",
            "moderation",
            "reminder",
            "botinfo",
            "admin",
            "afk",
            "auto_responder",
            "avatar",
            "calculator",
            "casino",
            "giveaway",
            "info",
            "invoice",
            "message_tools",
            "nuke",
            "purge",
            "roles",
            "social_media",
            "tickets",
            "utilities",
            "verification",
            "web_tools",
            "welcome",
            "timer",
            "todo"
        ]

        for cog in essential_cogs:
            try:
                await self.load_extension(f"cogs.{cog}")
                logger.info(f"[+] Loaded {cog}")
            except commands.errors.CommandRegistrationError as e:
                logger.error(f"[-] Failed to load {cog}: Command conflict - {str(e)}. Check for duplicate commands.")
                traceback.print_exc()
            except Exception as e:
                logger.error(f"[-] Failed to load {cog}: {str(e)}")
                traceback.print_exc()

        try:
            os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
            os.environ["JISHAKU_HIDE"] = "True"
            os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
            os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
            await self.load_extension("jishaku")
            logger.info("[+] Successfully loaded Jishaku")
        except Exception as e:
            logger.error(f"[-] Failed to load Jishaku: {str(e)}")
            traceback.print_exc()

        try:
            logger.info("Force syncing slash commands globally...")
            # Sync with the first guild (if available) to test
            if self.guilds:
                guild = self.guilds[0]
                await self.tree.sync(guild=guild)
                logger.info(f"[+] Synced commands for guild {guild.id}")
            # Force global sync with a small delay to avoid rate limits
            await asyncio.sleep(1)  # Brief delay to prevent API rate limiting
            synced = await self.tree.sync()
            logger.info(f"[+] Force synced {len(synced)} slash command(s) globally")
        except Exception as e:
            logger.error(f"[-] Failed to force sync commands: {str(e)}")
            traceback.print_exc()

    async def on_ready(self):
        """Bot is ready"""
        app_info = await self.application_info()
        self.owner_ids.add(app_info.owner.id)

        logger.info(f"Bot {self.user.name} is ready! Connected to {len(self.guilds)} guilds.")
        await self.change_presence(activity=discord.Game(name="Type /help for commands"))

    async def on_message(self, message):
        """Handle bot mentions and process commands"""
        if message.author.bot:
            return

        # Handle bot mention
        if self.user.mentioned_in(message) and message.content.strip() == f"<@{self.user.id}>":
            embed = discord.Embed(
                title="👋 Hey there!",
                description=f"My latency is {round(self.latency * 1000)}ms\n\nType `/help` to see my commands!",
                color=discord.Color.green()
            )
            embed.set_footer(text=FOOTER_TEXT)
            await message.reply(embed=embed)

        # Process commands to allow cog listeners (like AFK) to work
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        """Handle command errors properly with embeds"""
        embed = discord.Embed(color=discord.Color.red())

        if isinstance(error, commands.CommandNotFound):
            embed.title = "❌ Command Not Found"
            embed.description = "Try `/help` for a list of available commands."
        elif isinstance(error, commands.MissingPermissions):
            embed.title = "🚫 Missing Permissions"
            embed.description = "You don't have permission to use this command."
        elif isinstance(error, commands.BotMissingPermissions):
            embed.title = "⚠️ Bot Lacks Permissions"
            embed.description = "I don't have the required permissions to execute this command."
        elif isinstance(error, commands.CommandOnCooldown):
            embed.title = "⏳ Command on Cooldown"
            embed.description = f"Try again in `{round(error.retry_after, 2)}` seconds."
        else:
            embed.title = "⚠️ Unexpected Error"
            embed.description = f"An unexpected error occurred: ```{str(error)}```"
            logger.error(f"Unhandled error in command {ctx.command}: {str(error)}")
            traceback.print_exc()

        embed.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=embed)

    async def close(self):
        """Handle bot shutdown"""
        logger.info("Shutting down bot...")
        await super().close()

    async def is_owner(self, user: discord.User) -> bool:
        """Allow multiple owners"""
        return user.id in self.owner_ids

    # Test command to verify prefix commands work
    @commands.command(name="test", help="Test if prefix commands work")
    async def test_command(self, ctx):
        """Simple test command"""
        await ctx.send("✅ Test command works! Prefix commands are functioning.")

    # Sync command with ! prefix
    @commands.command(name="sync", help="Sync bot commands (Admin only)")
    @commands.has_permissions(administrator=True)
    async def sync_command(self, ctx):
        """Manually sync slash commands"""
        await ctx.message.delete()  # Delete the command message for cleanliness
        await ctx.send("🔄 Syncing commands... (This may take a moment)", delete_after=5)
        try:
            # Sync with the guild first (if applicable)
            if ctx.guild:
                guild = ctx.guild
                await self.tree.sync(guild=guild)
                logger.info(f"✓ Synced commands for guild {guild.id}")
            # Force global sync
            await asyncio.sleep(1)  # Brief delay to prevent API rate limiting
            synced = await self.tree.sync()
            await ctx.send(f"✅ Synced {len(synced)} slash command(s) globally!", delete_after=10)
            logger.info(f"Manually synced {len(synced)} slash commands by {ctx.author.name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to sync commands: {str(e)}", delete_after=10)
            logger.error(f"Failed to manually sync commands by {ctx.author.name}: {str(e)}")
            traceback.print_exc()

# Create and run the bot
bot = SeculexBot()

async def main():
    try:
        logger.info("Starting bot...")
        await bot.start(bot.token)
    except discord.LoginFailure:
        logger.error("Failed to login: Invalid token")
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())