import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from utils.storage import JsonStorage
import logging
import asyncio
import re
import aiohttp

# Configure logging for this file
logger = logging.getLogger("discord.cogs.moderation")

class Moderation(commands.Cog):
    """Moderation commands for managing server members"""

    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        self.warnings: Dict[str, Dict[str, list]] = self.storage.load_data('warnings.json') or {}
        self.autoroles: Dict[str, list] = self.storage.load_data('autoroles.json') or {}

    # Helper function to parse duration
    def parse_duration(self, duration: str) -> int:
        """Parse duration string (e.g., 10s, 5m, 2h, 1d) into seconds"""
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        match = re.match(r'(\d+)([smhd])', duration.lower())
        if not match:
            raise ValueError("Invalid duration format! Use: <number><unit> (e.g., 10m, 2h, 1d)")
        value, unit = match.groups()
        return int(value) * time_units[unit]

    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to ban", reason="Reason for the ban")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a member from the server"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot ban someone with a higher or equal role!", ephemeral=True)
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member}** has been banned from the server.",
                color=discord.Color(0xa46ffb)
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Banned by", value=ctx.author.mention)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban members!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(member="The member to kick", reason="Reason for the kick")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member from the server"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot kick someone with a higher or equal role!", ephemeral=True)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member}** has been kicked from the server.",
                color=discord.Color(0xa46ffb)
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Kicked by", value=ctx.author.mention)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick members!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="mute", description="Timeout/mute a member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(member="The member to mute", duration="Duration (e.g., 1h, 30m, 1d, max 28 days)", reason="Reason for the mute")
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        """Timeout/mute a member"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot mute someone with a higher or equal role!", ephemeral=True)
            return

        try:
            duration_seconds = self.parse_duration(duration)
            if duration_seconds > 2419200:  # 28 days
                await ctx.send("❌ Duration cannot exceed 28 days!", ephemeral=True)
                return

            until = datetime.now() + timedelta(seconds=duration_seconds)
            await member.timeout(until, reason=reason)

            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**{member}** has been muted.",
                color=discord.Color(0xa46ffb)
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Muted by", value=ctx.author.mention)
            embed.add_field(name="Duration", value=duration)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except ValueError as e:
            await ctx.send(f"❌ {str(e)}", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute members!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="unmute", description="Remove timeout/mute from a member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(member="The member to unmute")
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        """Remove timeout/mute from a member"""
        try:
            await member.timeout(None, reason=f"Unmuted by {ctx.author}")
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**{member}** has been unmuted.",
                color=discord.Color(0xa46ffb)
            )
            embed.add_field(name="Unmuted by", value=ctx.author.mention)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute members!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="warn", description="Warn a member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(member="The member to warn", reason="Reason for the warning")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a member"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot warn someone with a higher or equal role!", ephemeral=True)
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}

        user_id = str(member.id)
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []

        warning = {
            'reason': reason,
            'moderator': ctx.author.id,
            'timestamp': datetime.now().timestamp()
        }

        self.warnings[guild_id][user_id].append(warning)
        self.storage.save_data('warnings.json', self.warnings)

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=f"**{member}** has been warned.",
            color=discord.Color(0xa46ffb)
        )
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Warned by", value=ctx.author.mention)
        embed.add_field(name="Total Warnings", value=str(len(self.warnings[guild_id][user_id])), inline=False)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="warnings", description="View warnings for a member")
    @app_commands.describe(member="The member to view warnings for")
    async def warnings(self, ctx: commands.Context, member: discord.Member):
        """View warnings for a member"""
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.warnings or user_id not in self.warnings[guild_id] or not self.warnings[guild_id][user_id]:
            embed = discord.Embed(
                title="📋 Warning History",
                description=f"**{member}** has no warnings.",
                color=discord.Color(0xa46ffb)
            )
        else:
            embed = discord.Embed(
                title="📋 Warning History",
                description=f"Warnings for **{member}**",
                color=discord.Color(0xa46ffb)
            )
            for i, warning in enumerate(self.warnings[guild_id][user_id], 1):
                moderator = ctx.guild.get_member(warning['moderator'])
                mod_name = moderator.name if moderator else "Unknown Moderator"
                embed.add_field(
                    name=f"Warning #{i}",
                    value=f"**Reason:** {warning['reason']}\n**By:** {mod_name}\n**When:** <t:{int(warning['timestamp'])}:R>",
                    inline=False
                )

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarnings", description="Clear all warnings for a member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(member="The member to clear warnings for")
    async def clearwarnings(self, ctx: commands.Context, member: discord.Member):
        """Clear all warnings for a member"""
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.warnings or user_id not in self.warnings[guild_id] or not self.warnings[guild_id][user_id]:
            await ctx.send(f"**{member}** has no warnings to clear.")
            return

        self.warnings[guild_id][user_id] = []
        self.storage.save_data('warnings.json', self.warnings)

        embed = discord.Embed(
            title="🧹 Warnings Cleared",
            description=f"All warnings for **{member}** have been cleared.",
            color=discord.Color(0xa46ffb)
        )
        embed.add_field(name="Cleared by", value=ctx.author.mention)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="lock", description="Lock the current channel")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context):
        """Lock the current channel"""
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description="This channel has been locked.",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage channel permissions!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="unlock", description="Unlock the current channel")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context):
        """Unlock the current channel"""
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description="This channel has been unlocked.",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage channel permissions!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="slowmode", description="Set slowmode for the current channel")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(seconds="Number of seconds for slowmode (0 to disable)")
    async def slowmode(self, ctx: commands.Context, seconds: int):
        """Set slowmode for the current channel"""
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours)!", ephemeral=True)
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            response = "✅ Slowmode has been disabled." if seconds == 0 else f"✅ Slowmode set to {seconds} seconds."
            await ctx.send(response)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage channel slowmode!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="unban", description="Unban a member")
    @commands.has_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to unban (username#discriminator)")
    @app_commands.guild_only()
    async def unban(self, ctx: commands.Context, *, member: str):
        """Unban a member"""
        try:
            banned_users = [entry async for entry in ctx.guild.bans()]
            member_name, member_discriminator = member.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    embed = discord.Embed(
                        title="✅ Member Unbanned",
                        description=f"**{user}** has been unbanned.",
                        color=discord.Color(0xa46ffb)
                    )
                    embed.add_field(name="Unbanned by", value=ctx.author.mention)
                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by Seculex | © 2025")
                    await ctx.send(embed=embed)
                    return

            await ctx.send("❌ Member not found in ban list.", ephemeral=True)
        except ValueError:
            await ctx.send("❌ Invalid format. Use: username#discriminator", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban members!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="move_role", description="Move a role to a specified position (1 is topmost)")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="The role to move", position="Position to move to (1 is topmost)")
    async def move_role(self, ctx: commands.Context, role: discord.Role, position: int):
        """Move a role to a specified position (1 is topmost)"""
        if position < 1 or position > len(ctx.guild.roles):
            await ctx.send("❌ Invalid position! Position must be between 1 and the total number of roles.", ephemeral=True)
            return

        bot_member = ctx.guild.me
        if role >= bot_member.top_role:
            await ctx.send("❌ I cannot move a role higher than or equal to my highest role!", ephemeral=True)
            return

        new_position = len(ctx.guild.roles) - 1 - (position - 1)
        try:
            await ctx.guild.edit_role_positions(positions={role: new_position})
            await ctx.send(f"✅ Moved {role.name} to position {position}!", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to move this role!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="invert_roles", description="Invert the order of all manageable roles")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def invert_roles(self, ctx: commands.Context):
        """Invert the order of all manageable roles"""
        roles = ctx.guild.roles
        if len(roles) <= 1:
            await ctx.send("❌ Not enough roles to invert!", ephemeral=True)
            return

        bot_member = ctx.guild.me
        bot_role = bot_member.top_role
        manageable_roles = [role for role in roles if role < bot_role and role != bot_role]

        if not manageable_roles:
            await ctx.send("❌ No manageable roles to invert!", ephemeral=True)
            return

        try:
            new_positions = {}
            total_manageable = len(manageable_roles)
            for index, role in enumerate(reversed(manageable_roles)):
                new_positions[role.id] = total_manageable - 1 - index

            await ctx.guild.edit_role_positions(reordering=True, positions=new_positions)
            await ctx.send("✅ Role order has been inverted for manageable roles!", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to invert roles!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="say", description="Send a message to a specified channel as the bot")
    @commands.has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="The channel to send the message to", message="The message to send")
    async def say(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """Send a message to a specified channel as the bot"""
        try:
            await channel.send(message)
            embed = discord.Embed(
                title="✅ Message Sent",
                description=f"Message sent to {channel.mention} successfully!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages in that channel!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="clone", description="Clone a text or voice channel")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to clone")
    async def clone(self, ctx: commands.Context, channel: discord.TextChannel | discord.VoiceChannel):
        """Clone a text or voice channel"""
        try:
            new_channel = await channel.clone()
            embed = discord.Embed(
                title="📋 Channel Cloned",
                description=f"Cloned {channel.mention} to {new_channel.mention}.",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to clone channels!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="nick", description="Change a user's nickname")
    @commands.has_permissions(manage_nicknames=True)
    @app_commands.checks.has_permissions(manage_nicknames=True)
    @app_commands.describe(member="The member to rename", nickname="The new nickname")
    async def nick(self, ctx: commands.Context, member: discord.Member, *, nickname: str):
        """Change a user's nickname"""
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                title="✏️ Nickname Changed",
                description=f"Changed {member.mention}'s nickname to **{nickname}**.",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to change nicknames!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="hide", description="Hide a channel from @everyone")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to hide (defaults to current)")
    async def hide(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        """Hide a channel from @everyone"""
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, view_channel=False)
            embed = discord.Embed(
                title="👻 Channel Hidden",
                description=f"{channel.mention} is now hidden from @everyone.",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage channel permissions!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="unhide", description="Unhide a channel for @everyone")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to unhide (defaults to current)")
    async def unhide(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        """Unhide a channel for @everyone"""
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, view_channel=True)
            embed = discord.Embed(
                title="👀 Channel Unhidden",
                description=f"{channel.mention} is now visible to @everyone.",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage channel permissions!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="deletechannel", description="Delete a specified channel")
    @commands.has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to delete (defaults to current)")
    async def deletechannel(self, ctx: commands.Context, channel: Optional[discord.TextChannel | discord.VoiceChannel] = None):
        """Delete a specified channel"""
        channel = channel or ctx.channel
        try:
            channel_name = channel.name  # Store name before deletion
            await channel.delete()
            embed = discord.Embed(
                title="🗑️ Channel Deleted",
                description=f"**{channel_name}** has been deleted.",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            # If deleting the current channel, send to author; otherwise, send to invoking channel
            if channel == ctx.channel:
                await ctx.author.send(embed=embed)
            else:
                await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete channels!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.command(name="firstmsg")
    @commands.has_permissions(manage_messages=True)
    async def firstmsg(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        """Get the link to the first message in a channel (Manage Messages required)"""
        channel = channel or ctx.channel
        try:
            # Fetch the oldest message in the channel (limit=1, oldest first)
            async for message in channel.history(limit=1, oldest_first=True):
                embed = discord.Embed(
                    title="📜 First Message",
                    description=f"Here's the link to the first message in {channel.mention}:\n[Click Here]({message.jump_url})",
                    color=discord.Color(0xa46ffb)
                )
                embed.set_footer(text="Powered by Seculex | © 2025")
                await ctx.send(embed=embed)
                return
            # If no messages are found
            await ctx.send(f"❌ No messages found in {channel.mention}!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to read message history in that channel!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.hybrid_command(name="changeserverpfp", description="Change the server's profile picture")
    @commands.has_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(image_url="URL of the new server profile picture")
    async def changeserverpfp(self, ctx: commands.Context, image_url: str):
        """Change the server's profile picture"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Failed to fetch the image!", ephemeral=True)
                    return
                image_data = await resp.read()

        try:
            await ctx.guild.edit(icon=image_data)
            embed = discord.Embed(
                title="🖼️ Server Icon Updated",
                description="The server profile picture has been changed!",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to change the server icon!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="changeserverbanner", description="Change the server's banner")
    @commands.has_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(image_url="URL of the new server banner")
    async def changeserverbanner(self, ctx: commands.Context, image_url: str):
        """Change the server's banner"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Failed to fetch the image!", ephemeral=True)
                    return
                image_data = await resp.read()

        try:
            await ctx.guild.edit(banner=image_data)
            embed = discord.Embed(
                title="🎨 Server Banner Updated",
                description="The server banner has been changed!",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to change the server banner!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="steal", description="Steal an emoji")
    @commands.has_permissions(manage_emojis=True)
    @app_commands.checks.has_permissions(manage_emojis=True)
    @app_commands.describe(item="The emoji to steal (e.g., :emoji:)")
    async def steal(self, ctx: commands.Context, item: str):
        """Steal an emoji"""
        emoji_match = re.match(r'<a?:(\w+):(\d+)>', item)
        if emoji_match:
            name, emoji_id = emoji_match.groups()
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Failed to fetch the emoji!", ephemeral=True)
                        return
                    image_data = await resp.read()
            try:
                emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
                await ctx.send(f"✅ Emoji {emoji} stolen and added to the server!")
            except discord.Forbidden:
                await ctx.send("❌ I don't have permission to add emojis!", ephemeral=True)
            except Exception as e:
                await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        else:
            await ctx.send("❌ Invalid emoji format! Use :emoji_name:.", ephemeral=True)

    @commands.hybrid_command(name="roleicon", description="Change a role's icon")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to change", image_url="URL of the new role icon")
    async def roleicon(self, ctx: commands.Context, role: discord.Role, image_url: str):
        """Change a role's icon"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Failed to fetch the image!", ephemeral=True)
                    return
                image_data = await resp.read()

        try:
            await role.edit(display_icon=image_data)
            embed = discord.Embed(
                title="🎨 Role Icon Updated",
                description=f"The icon for {role.mention} has been changed!",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to edit roles!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @commands.hybrid_command(name="autorole", description="Manage autoroles for new members")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(action="add or remove", role="The role to manage")
    async def autorole(self, ctx: commands.Context, action: str, role: discord.Role):
        """Manage autoroles for new members"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.autoroles:
            self.autoroles[guild_id] = []

        if action.lower() == "add":
            if role.id not in self.autoroles[guild_id]:
                self.autoroles[guild_id].append(role.id)
                self.storage.save_data('autoroles.json', self.autoroles)
                await ctx.send(f"✅ {role.mention} will now be assigned to new members!")
            else:
                await ctx.send("❌ This role is already an autorole!", ephemeral=True)
        elif action.lower() == "remove":
            if role.id in self.autoroles[guild_id]:
                self.autoroles[guild_id].remove(role.id)
                self.storage.save_data('autoroles.json', self.autoroles)
                await ctx.send(f"✅ {role.mention} removed from autoroles!")
            else:
                await ctx.send("❌ This role is not an autorole!", ephemeral=True)
        else:
            await ctx.send("❌ Invalid action! Use 'add' or 'remove'.", ephemeral=True)

    @commands.hybrid_command(name="trole", description="Assign a temporary role to a member")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="The member", role="The role to assign", duration="Duration (e.g., 10m)")
    async def trole(self, ctx: commands.Context, member: discord.Member, role: discord.Role, duration: str):
        """Assign a temporary role to a member"""
        try:
            duration_seconds = self.parse_duration(duration)
            await member.add_roles(role, reason=f"Temporary role by {ctx.author}")
            embed = discord.Embed(
                title="⏳ Temporary Role Assigned",
                description=f"Assigned {role.mention} to {member.mention} for {duration}.",
                color=discord.Color(0xa46ffb)
            )
            embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)

            await asyncio.sleep(duration_seconds)
            await member.remove_roles(role, reason="Temporary role expired")
        except ValueError as e:
            await ctx.send(f"❌ {str(e)}", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    class EmbedBuilderModal(discord.ui.Modal):
        def __init__(self, field_name: str, embed_data: dict):
            super().__init__(title=f"Set {field_name}")
            self.field_name = field_name
            self.embed_data = embed_data
            self.add_item(discord.ui.TextInput(
                label=f"Enter {field_name}",
                placeholder=f"Type the {field_name.lower()} here...",
                required=False
            ))

        async def on_submit(self, interaction: discord.Interaction):
            value = self.children[0].value
            if self.field_name == "Color":
                try:
                    value = value.lstrip('#')
                    self.embed_data[self.field_name.lower()] = int(value, 16)
                except ValueError:
                    await interaction.response.send_message("❌ Invalid color format! Use a hex code (e.g., #a46ffb)", ephemeral=True)
                    return
            else:
                self.embed_data[self.field_name.lower()] = value
            await interaction.response.defer()

    class EmbedBuilderView(discord.ui.View):
        def __init__(self, embed_data: dict):
            super().__init__(timeout=300)
            self.embed_data = embed_data

        @discord.ui.button(label="Title", style=discord.ButtonStyle.primary)
        async def title_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Moderation.EmbedBuilderModal("Title", self.embed_data)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Description", style=discord.ButtonStyle.primary)
        async def description_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Moderation.EmbedBuilderModal("Description", self.embed_data)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Color", style=discord.ButtonStyle.primary)
        async def color_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Moderation.EmbedBuilderModal("Color", self.embed_data)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Image", style=discord.ButtonStyle.secondary)
        async def image_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Moderation.EmbedBuilderModal("Image", self.embed_data)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.secondary)
        async def thumbnail_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Moderation.EmbedBuilderModal("Thumbnail", self.embed_data)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="JSON", style=discord.ButtonStyle.success)
        async def json_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Moderation.EmbedBuilderModal("JSON", self.embed_data)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Save", style=discord.ButtonStyle.success)
        async def save_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                embed = discord.Embed()
                if "title" in self.embed_data and self.embed_data["title"]:
                    embed.title = self.embed_data["title"]
                if "description" in self.embed_data and self.embed_data["description"]:
                    embed.description = self.embed_data["description"]
                if "color" in self.embed_data and self.embed_data["color"]:
                    embed.color = discord.Color(self.embed_data["color"])
                else:
                    embed.color = discord.Color(0xa46ffb)
                if "image" in self.embed_data and self.embed_data["image"]:
                    embed.set_image(url=self.embed_data["image"])
                if "thumbnail" in self.embed_data and self.embed_data["thumbnail"]:
                    embed.set_thumbnail(url=self.embed_data["thumbnail"])
                if "json" in self.embed_data and self.embed_data["json"]:
                    embed.add_field(name="JSON Data", value=self.embed_data["json"], inline=False)

                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by Seculex | © 2025")

                await interaction.channel.send(embed=embed)
                await interaction.response.send_message("✅ Embed sent successfully!", ephemeral=True)
                self.stop()
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to send embed: {str(e)}", ephemeral=True)

        @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
        async def exit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("❌ Embed creation cancelled.", ephemeral=True)
            self.stop()

    @app_commands.command(name="embed", description="Create a custom embed with a modal interface")
    @app_commands.checks.has_permissions(administrator=True)
    async def embed(self, interaction: discord.Interaction):
        """Create a custom embed with a modal interface"""
        embed_data = {}
        view = Moderation.EmbedBuilderView(embed_data)
        await interaction.response.send_message("Use the buttons below to add fields", view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        if guild_id in self.autoroles:
            roles = [member.guild.get_role(role_id) for role_id in self.autoroles[guild_id] if member.guild.get_role(role_id)]
            try:
                await member.add_roles(*roles, reason="Autorole assignment")
            except discord.Forbidden:
                logger.error(f"Failed to assign autoroles to {member} in {member.guild.name}: No permission")

async def setup(bot):
    await bot.add_cog(Moderation(bot))