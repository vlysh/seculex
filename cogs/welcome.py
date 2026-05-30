import discord
from discord.ext import commands
from discord import app_commands
from utils.storage import JsonStorage
import asyncio
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ServerManagement')

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        settings_data = self.storage.load_data('server_settings.json')
        self.settings = settings_data if settings_data is not None else {}
        invites_data = self.storage.load_data('invites.json')
        self.invites = invites_data if invites_data is not None else {}
        self.stop_join_tasks = {}
        self.invite_cache = {}  # Cache to store invite uses before joins

        self.DEFAULT_GREET_MESSAGE = (
            "<:welcome_1:1352308611048800256> Welcome {user}!\n"
            "<:Right_Purple_Arrow:1352308277291126864> Account Created: {created_at}\n"
            "<:Right_Purple_Arrow:1352308277291126864> They were invited by {inviter}\n"
            "<:Right_Purple_Arrow:1352308277291126864> {server} now has {member_count} members"
        )
        self.DEFAULT_FAREWELL_MESSAGE = (
            "<:a_bye:1352308676496592936> Sorry to see you go, {user}:\n"
            "<:Right_Purple_Arrow:1352308277291126864> {server}:\n"
            "<:Right_Purple_Arrow:1352308277291126864> {server} now has {member_count} members"
        )
        logger.info("ServerManagement cog initialized")
        # Initialize invite cache for all guilds
        self.bot.loop.create_task(self._initialize_invite_cache())

    async def _initialize_invite_cache(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            try:
                self.invite_cache[guild_id] = {inv.code: inv.uses for inv in await guild.invites()}
                logger.info(f"Initialized invite cache for guild {guild_id}")
            except discord.Forbidden:
                logger.error(f"Failed to cache invites for guild {guild_id}: Bot lacks permissions")

    def get_guild_settings(self, guild_id: str):
        if guild_id not in self.settings:
            self.settings[guild_id] = {
                'stop_join': False,
                'greet_enabled': False,
                'greet_channel': None,
                'greet_message': self.DEFAULT_GREET_MESSAGE,
                'farewell_enabled': False,
                'farewell_channel': None,
                'farewell_message': self.DEFAULT_FAREWELL_MESSAGE
            }
            self.storage.save_data('server_settings.json', self.settings)
            logger.info(f"Initialized settings for guild {guild_id}")
        return self.settings[guild_id]

    def get_guild_invites(self, guild_id: str):
        if guild_id not in self.invites:
            self.invites[guild_id] = {}
            self.storage.save_data('invites.json', self.invites)
        return self.invites[guild_id]

    # Stop Join (Prefix only)
    @commands.command(name="stopjoin")
    @commands.has_permissions(kick_members=True)
    async def stop_join(self, ctx, duration: str):
        guild_id = str(ctx.guild.id)
        settings = self.get_guild_settings(guild_id)

        if duration.lower() == "off":
            settings['stop_join'] = False
            if guild_id in self.stop_join_tasks:
                self.stop_join_tasks[guild_id].cancel()
                del self.stop_join_tasks[guild_id]
            self.storage.save_data('server_settings.json', self.settings)
            await ctx.send("Join restriction has been disabled.")
            return

        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        try:
            unit = duration[-1].lower()
            time = int(duration[:-1]) * time_units[unit]
        except (ValueError, KeyError):
            await ctx.send("Invalid duration format. Use: <number><unit> (e.g., 10m, 2h, 1d)")
            return

        settings['stop_join'] = True
        self.storage.save_data('server_settings.json', self.settings)

        if guild_id in self.stop_join_tasks:
            self.stop_join_tasks[guild_id].cancel()

        async def disable_stop_join():
            await asyncio.sleep(time)
            settings['stop_join'] = False
            self.storage.save_data('server_settings.json', self.settings)
            await ctx.send("Join restriction has expired and is now disabled.")

        self.stop_join_tasks[guild_id] = asyncio.create_task(disable_stop_join())
        await ctx.send(f"New joins will be blocked for {duration}.")

    # Invites Command (Prefix and Slash)
    @commands.command(name="invites")
    @commands.guild_only()
    async def invites_prefix(self, ctx, member: discord.Member = None):
        await self._handle_invites(ctx, member, is_prefix=True)

    @app_commands.command(name="invites", description="Check invite statistics for a user or top inviters")
    @app_commands.describe(member="The member to check invites for (leave blank for top inviters)")
    async def invites_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        await self._handle_invites(interaction, member, is_prefix=False)

    async def _handle_invites(self, context, member, is_prefix: bool):
        guild_id = str(context.guild.id)
        guild_invites = self.get_guild_invites(guild_id)
        
        embed = discord.Embed(color=0xa46ffb)
        
        if member is None:
            sorted_invites = sorted(
                guild_invites.items(),
                key=lambda x: (x[1].get('regular', 0) + x[1].get('bonus', 0)),
                reverse=True
            )[:10]
            embed.title = f"Top Inviters - {context.guild.name}"
            leaderboard = []
            for i, (user_id, stats) in enumerate(sorted_invites, 1):
                user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
                total = stats.get('regular', 0) + stats.get('bonus', 0)
                leaderboard.append(f"{i}. {user.name} - {total} invites")
            embed.description = "\n".join(leaderboard) or "No invites recorded yet."
        else:
            user_id = str(member.id)
            stats = guild_invites.get(user_id, {'regular': 0, 'fake': 0, 'bonus': 0})
            embed.title = f"Invite Stats for {member.name}"
            embed.add_field(name="Regular Invites", value=str(stats['regular']), inline=True)
            embed.add_field(name="Fake Invites", value=str(stats['fake']), inline=True)
            embed.add_field(name="Bonus Invites", value=str(stats['bonus']), inline=True)
            embed.add_field(name="Total", value=str(stats['regular'] + stats['bonus']), inline=True)

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
            
        if is_prefix:
            await context.send(embed=embed)
        else:
            await context.response.send_message(embed=embed)

    # Settings Command (Prefix only)
    @commands.command(name="settings")
    @commands.has_permissions(administrator=True)
    async def settings_check(self, ctx):
        guild_id = str(ctx.guild.id)
        settings = self.get_guild_settings(guild_id)
        
        embed = discord.Embed(title=f"Settings for {ctx.guild.name}", color=0xa46ffb)
        embed.add_field(name="Stop Join", value=str(settings['stop_join']), inline=False)
        embed.add_field(name="Greet Enabled", value=str(settings['greet_enabled']), inline=False)
        embed.add_field(name="Greet Channel", value=f"<#{settings['greet_channel']}>" if settings['greet_channel'] else "Not set", inline=False)
        embed.add_field(name="Greet Message", value=f"```{settings['greet_message']}```", inline=False)
        embed.add_field(name="Farewell Enabled", value=str(settings['farewell_enabled']), inline=False)
        embed.add_field(name="Farewell Channel", value=f"<#{settings['farewell_channel']}>" if settings['farewell_channel'] else "Not set", inline=False)
        embed.add_field(name="Farewell Message", value=f"```{settings['farewell_message']}```", inline=False)
        
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        
        await ctx.send(embed=embed)
        logger.info(f"Displayed settings for guild {guild_id}")

    # Greet Command (Prefix and Slash)
    @commands.command(name="greet")
    @commands.has_permissions(administrator=True)
    async def greet_prefix(self, ctx, action: str, channel: discord.TextChannel = None, *, message=None):
        await self._handle_greet(ctx, action, channel, message, is_prefix=True)

    @app_commands.command(name="greet_enable", description="Enable welcome messages in a server channel")
    @app_commands.describe(
        channel="The channel to send welcome messages to",
        message="The welcome message (optional, uses default if not provided)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def greet_slash(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        await self._handle_greet(interaction, "enable", channel, message, is_prefix=False)

    async def _handle_greet(self, context, action: str, channel, message, is_prefix: bool):
        guild_id = str(context.guild.id)
        settings = self.get_guild_settings(guild_id)
        embed = discord.Embed(color=0xa46ffb)

        if action.lower() == "enable":
            if not channel:
                msg = "Usage: `!greet enable #channel [message]`" if is_prefix else "Please provide a channel."
                if is_prefix:
                    await context.send(msg)
                else:
                    await context.response.send_message(msg, ephemeral=True)
                return

            settings['greet_enabled'] = True
            settings['greet_channel'] = str(channel.id)
            settings['greet_message'] = message if message else self.DEFAULT_GREET_MESSAGE
            self.storage.save_data('server_settings.json', self.settings)
            logger.info(f"Greet enabled for guild {guild_id}: channel={channel.id}, message={settings['greet_message']}")

            embed.title = "✅ Welcome Messages Enabled"
            embed.description = f"Welcome messages set to:\n```{settings['greet_message']}```"
            embed.add_field(name="Target", value=f"<#{channel.id}>", inline=False)

        elif action.lower() == "disable":
            settings['greet_enabled'] = False
            self.storage.save_data('server_settings.json', self.settings)
            logger.info(f"Greet disabled for guild {guild_id}")
            embed.title = "✅ Welcome Messages Disabled"
            embed.description = "Welcome messages have been turned off."

        else:
            msg = "Invalid action. Use 'enable' or 'disable'."
            if is_prefix:
                await context.send(msg)
            else:
                await context.response.send_message(msg, ephemeral=True)
            return

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
            
        if is_prefix:
            await context.send(embed=embed)
        else:
            await context.response.send_message(embed=embed)

    # Farewell Command (Prefix and Slash)
    @commands.command(name="farewell")
    @commands.has_permissions(administrator=True)
    async def farewell_prefix(self, ctx, action: str, channel: discord.TextChannel = None, *, message=None):
        await self._handle_farewell(ctx, action, channel, message, is_prefix=True)

    @app_commands.command(name="farewell_enable", description="Enable farewell messages in a server channel")
    @app_commands.describe(
        channel="The channel to send farewell messages to",
        message="The farewell message (optional, uses default if not provided)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def farewell_slash(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        await self._handle_farewell(interaction, "enable", channel, message, is_prefix=False)

    async def _handle_farewell(self, context, action: str, channel, message, is_prefix: bool):
        guild_id = str(context.guild.id)
        settings = self.get_guild_settings(guild_id)
        embed = discord.Embed(color=0xa46ffb)

        if action.lower() == "enable":
            if not channel:
                msg = "Usage: `!farewell enable #channel [message]`" if is_prefix else "Please provide a channel."
                if is_prefix:
                    await context.send(msg)
                else:
                    await context.response.send_message(msg, ephemeral=True)
                return

            settings['farewell_enabled'] = True
            settings['farewell_channel'] = str(channel.id)
            settings['farewell_message'] = message if message else self.DEFAULT_FAREWELL_MESSAGE
            self.storage.save_data('server_settings.json', self.settings)
            logger.info(f"Farewell enabled for guild {guild_id}: channel={channel.id}")

            embed.title = "✅ Farewell Messages Enabled"
            embed.description = f"Farewell messages set to:\n```{settings['farewell_message']}```"
            embed.add_field(name="Target", value=f"<#{channel.id}>", inline=False)

        elif action.lower() == "disable":
            settings['farewell_enabled'] = False
            self.storage.save_data('server_settings.json', self.settings)
            logger.info(f"Farewell disabled for guild {guild_id}")
            embed.title = "✅ Farewell Messages Disabled"
            embed.description = "Farewell messages have been turned off."

        else:
            msg = "Invalid action. Use 'enable' or 'disable'."
            if is_prefix:
                await context.send(msg)
            else:
                await context.response.send_message(msg, ephemeral=True)
            return

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
            
        if is_prefix:
            await context.send(embed=embed)
        else:
            await context.response.send_message(embed=embed)

    # Event Listeners
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        settings = self.get_guild_settings(guild_id)
        logger.info(f"Member joined guild {guild_id}: {member.name}#{member.discriminator}")

        # Stop Join handling
        if settings['stop_join']:
            embed = discord.Embed(
                title="⛔ Join Restricted",
                description=f"Sorry, joining **{member.guild.name}** is temporarily prohibited due to a server restriction. Please try again later!",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            
            await member.kick(reason="Server is currently blocking new joins.")
            logger.info(f"Kicked {member.name}#{member.discriminator} due to stop_join")
            return

        # Welcome message handling
        logger.info(f"Checking greet conditions for guild {guild_id}: enabled={settings['greet_enabled']}, channel={settings['greet_channel']}, message={settings['greet_message']}")
        if settings['greet_enabled'] and settings['greet_message'] and settings['greet_channel']:
            logger.info(f"Greet conditions met, preparing message for guild {guild_id}")
            inviter = await self._track_invite(member)
            try:
                message = settings['greet_message'].format(
                    user=member.mention,
                    server=member.guild.name,
                    created_at=member.created_at.strftime("%Y-%m-%d %H:%M UTC"),
                    inviter=inviter.mention if inviter else "Unknown",
                    member_count=member.guild.member_count
                )
            except KeyError as e:
                logger.error(f"Error formatting greet message for guild {guild_id}: {e}")
                message = f"Welcome {member.mention} to {member.guild.name}!"

            embed = discord.Embed(description=message, color=0xa46ffb)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            channel = member.guild.get_channel(int(settings['greet_channel']))
            if channel:
                logger.info(f"Found greet channel {channel.id} for guild {guild_id}")
                try:
                    await channel.send(embed=embed)
                    logger.info(f"Sent greet message to channel {channel.id} for {member.name}#{member.discriminator}")
                except discord.Forbidden:
                    logger.error(f"Failed to send greet message to channel {channel.id}: Bot lacks permissions")
                except Exception as e:
                    logger.error(f"Unexpected error sending greet to channel {channel.id}: {e}")
            else:
                logger.warning(f"Greet channel {settings['greet_channel']} not found in guild {guild_id}")
        else:
            logger.info(f"Greet not sent for guild {guild_id}: Conditions not met")

        # Update invite cache after join
        try:
            self.invite_cache[guild_id] = {inv.code: inv.uses for inv in await member.guild.invites()}
        except discord.Forbidden:
            logger.error(f"Failed to update invite cache for guild {guild_id}: Bot lacks permissions")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = str(member.guild.id)
        settings = self.get_guild_settings(guild_id)
        guild_invites = self.get_guild_invites(guild_id)
        logger.info(f"Member left guild {guild_id}: {member.name}#{member.discriminator}")

        # Farewell message handling
        if settings['farewell_enabled'] and settings['farewell_message'] and settings['farewell_channel']:
            logger.info(f"Farewell conditions met for guild {guild_id}")
            message = settings['farewell_message'].format(
                user=member.name,
                server=member.guild.name,
                member_count=member.guild.member_count
            )
            
            embed = discord.Embed(description=message, color=0xa46ffb)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            channel = member.guild.get_channel(int(settings['farewell_channel']))
            if channel:
                try:
                    await channel.send(embed=embed)
                    logger.info(f"Sent farewell message to channel {channel.id} for {member.name}#{member.discriminator}")
                except discord.Forbidden:
                    logger.error(f"Failed to send farewell message to channel {channel.id}: Bot lacks permissions")
            else:
                logger.warning(f"Farewell channel {settings['farewell_channel']} not found in guild {guild_id}")

        # Mark as fake invite if member leaves within 24 hours
        for user_id, stats in guild_invites.items():
            if 'recent_invites' in stats and str(member.id) in stats['recent_invites']:
                join_time = stats['recent_invites'][str(member.id)]
                # Convert join_time to datetime if it's a string
                if isinstance(join_time, str):
                    join_time = datetime.datetime.fromisoformat(join_time)
                if (discord.utils.utcnow() - join_time).total_seconds() < 86400:
                    stats['fake'] = stats.get('fake', 0) + 1
                    stats['regular'] = stats.get('regular', 0) - 1
                    del stats['recent_invites'][str(member.id)]
                    self.storage.save_data('invites.json', self.invites)

        # Update invite cache after removal
        try:
            self.invite_cache[guild_id] = {inv.code: inv.uses for inv in await member.guild.invites()}
        except discord.Forbidden:
            logger.error(f"Failed to update invite cache for guild {guild_id}: Bot lacks permissions")

    async def _track_invite(self, member):
        guild_id = str(member.guild.id)
        guild_invites = self.get_guild_invites(guild_id)
        
        try:
            before_invites = self.invite_cache.get(guild_id, {})
            after_invites = {inv.code: inv.uses for inv in await member.guild.invites()}
            
            for code, uses_before in before_invites.items():
                uses_after = after_invites.get(code, 0)
                if uses_after > uses_before:
                    # Found the invite used
                    invite = await self.bot.fetch_invite(code)
                    inviter_id = str(invite.inviter.id)
                    if inviter_id not in guild_invites:
                        guild_invites[inviter_id] = {'regular': 0, 'fake': 0, 'bonus': 0, 'recent_invites': {}}
                    
                    stats = guild_invites[inviter_id]
                    stats['regular'] = stats.get('regular', 0) + 1
                    # Store join time as ISO format string
                    stats['recent_invites'][str(member.id)] = discord.utils.utcnow().isoformat()
                    self.storage.save_data('invites.json', self.invites)
                    return member.guild.get_member(int(inviter_id)) or await member.guild.fetch_member(int(inviter_id))
            logger.info(f"No invite change detected for guild {guild_id}, member {member.id}")
            return None
        except discord.Forbidden:
            logger.error(f"Bot lacks permission to view invites in guild {guild_id}")
            return None
        except discord.HTTPException as e:
            logger.error(f"Error tracking invite in guild {guild_id}: {e}")
            return None

async def setup(bot):
    await bot.add_cog(ServerManagement(bot))