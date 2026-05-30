import discord
from discord.ext import commands
from discord import app_commands
import datetime
import io
import matplotlib.pyplot as plt
import numpy as np

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="invite",
        description="Get Seculex bot and server invite links"
    )
    async def invite(self, interaction: discord.Interaction):
        """Get Seculex bot and server invite links"""
        embed = discord.Embed(
            title="<a:seculex2:1333522172362100788> Seculex Links",
            description="Join our community and add Seculex to your server!",
            color=0xa46ffb  # Updated color
        )

        embed.add_field(
            name="<:purple_arrow:1351298291962220656> Server Invite",
            value="[Join Seculex Server](https://discord.gg/YcUaVwyGcM)",
            inline=False
        )

        embed.add_field(
            name="<:purple_arrow:1351298291962220656> Bot Invite",
            value="[Add Seculex to Your Server](https://discord.com/oauth2/authorize?client_id=1338408460555128925&permissions=8&integration_type=0&scope=applications.commands+bot)",
            inline=False
        )

        embed.add_field(
            name="<:purple_arrow:1351298291962220656> Website",
            value="[Visit Our Website](https://seculex.com)",
            inline=False
        )

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="membercount",
        description="Shows server member statistics"
    )
    async def membercount(self, interaction: discord.Interaction):
        """Shows server member statistics with a graph"""
        await interaction.response.defer()
        guild = interaction.guild

        total = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        online = len([m for m in guild.members if m.status != discord.Status.offline])

        # Create graph
        fig, ax = plt.subplots(figsize=(10, 5))
        labels = ['Total', 'Humans', 'Bots', 'Online']
        values = [total, humans, bots, online]
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f']

        ax.bar(labels, values, color=colors)
        ax.set_title('Server Member Statistics')
        ax.set_ylabel('Count')

        # Save graph to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Create file
        file = discord.File(buf, filename='stats.png')

        embed = discord.Embed(
            title="📊 Server Member Statistics",
            color=0xa46ffb  # Updated color
        )
        embed.add_field(name="Total Members", value=str(total), inline=True)
        embed.add_field(name="Humans", value=str(humans), inline=True)
        embed.add_field(name="Bots", value=str(bots), inline=True)
        embed.add_field(name="Online", value=str(online), inline=True)
        embed.set_image(url="attachment://stats.png")
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.followup.send(embed=embed, file=file)
    
    @app_commands.command(
        name="role_info",
        description="Get information about a role"
    )
    @app_commands.describe(role="The role to get information about")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        """Get information about a role"""
        perms = []
        for perm, value in role.permissions:
            if value:
                perms.append(perm.replace('_', ' ').title())

        embed = discord.Embed(title="👥 Role Information", color=0xa46ffb)  # Updated color
        embed.add_field(name="Name", value=role.name, inline=True)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Created At", value=discord.utils.format_dt(role.created_at), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
        if perms:
            embed.add_field(name="Key Permissions", value=", ".join(perms[:10]) + ("..." if len(perms) > 10 else ""), inline=False)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="server_info",
        description="Get information about the server"
    )
    async def server_info(self, interaction: discord.Interaction):
        """Get information about the server"""
        guild = interaction.guild

        total_members = guild.member_count
        total_channels = len(guild.channels)
        total_roles = len(guild.roles)
        total_emojis = len(guild.emojis)
        boost_count = guild.premium_subscription_count

        embed = discord.Embed(title="🌍 Server Information", color=0xa46ffb)  # Updated color
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created At", value=discord.utils.format_dt(guild.created_at), inline=True)

        embed.add_field(name="Members", value=total_members, inline=True)
        embed.add_field(name="Channels", value=total_channels, inline=True)
        embed.add_field(name="Roles", value=total_roles, inline=True)

        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=boost_count, inline=True)
        embed.add_field(name="Emojis", value=f"{total_emojis}/{guild.emoji_limit}", inline=True)

        if guild.features:
            embed.add_field(name="Features", value=", ".join(guild.features), inline=False)

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="user_info",
        description="Get information about a user"
    )
    @app_commands.describe(user="The user to get information about")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member = None):
        """Get information about a user"""
        user = user or interaction.user

        roles = [role.mention for role in user.roles[1:]]

        embed = discord.Embed(title="👤 User Information", color=0xa46ffb)  # Updated color
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="Name", value=f"{user.name}", inline=True)
        embed.add_field(name="Nickname", value=user.nick or "None", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)

        embed.add_field(name="Account Created", value=discord.utils.format_dt(user.created_at), inline=True)
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(user.joined_at), inline=True)

        status_emoji = {
            "online": "🟢",
            "idle": "🟡",
            "dnd": "🔴",
            "offline": "⚫"
        }
        embed.add_field(name="Status", value=f"{status_emoji.get(str(user.status), '⚫')} {str(user.status).title()}", inline=True)

        if user.activity:
            embed.add_field(name="Activity", value=f"{user.activity.type.name.title()}: {user.activity.name}", inline=True)

        if roles:
            embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles) if len(" ".join(roles)) <= 1024 else f"{len(roles)} roles", inline=False)

        if user.banner:
            embed.set_image(url=user.banner.url)

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))