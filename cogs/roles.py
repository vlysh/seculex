import discord
from discord.ext import commands
from discord import app_commands
import random

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole", description="Assign a role to a user")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        member="The member to assign the role to",
        role="The role to assign"
    )
    async def addrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        """Assign a role to a user. Usage: !addrole <member> <role>"""
        # Defer the response for slash commands to avoid timeout
        if ctx.interaction:
            await ctx.defer()

        # Check if the user has permission to manage the role (role hierarchy)
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You can't assign roles higher than or equal to your highest role!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
            return

        # Check if the member already has the role
        if role in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{member.mention} already has the role {role.mention}!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
            return

        try:
            await member.add_roles(role)
            embed = discord.Embed(
                title="✅ Role Added",
                description=f"Added {role.mention} to {member.mention}",
                color=discord.Color(0xa46ffb)
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
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to manage that role!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="removerole", description="Remove a role from a user")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        member="The member to remove the role from",
        role="The role to remove"
    )
    async def removerole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        """Remove a role from a user. Usage: !removerole <member> <role>"""
        if ctx.interaction:
            await ctx.defer()

        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You can't remove roles higher than or equal to your highest role!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
            return

        if role not in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{member.mention} doesn't have the role {role.mention}!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
            return

        try:
            await member.remove_roles(role)
            embed = discord.Embed(
                title="✅ Role Removed",
                description=f"Removed {role.mention} from {member.mention}",
                color=discord.Color(0xa46ffb)
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
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to manage that role!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="createrole", description="Create a new role")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        name="The name of the role to create",
        color="The color of the role (hex code, optional)"
    )
    async def createrole(self, ctx: commands.Context, name: str, color: str = None):
        """Create a new role. Usage: !createrole <name> [color]"""
        if ctx.interaction:
            await ctx.defer()

        try:
            role_color = discord.Color.random() if not color else discord.Color.from_str(color)
            role = await ctx.guild.create_role(name=name, color=role_color)

            embed = discord.Embed(
                title="✅ Role Created",
                description=f"Created role {role.mention}",
                color=discord.Color(0xa46ffb)
            )
            embed.add_field(name="Name", value=role.name)
            embed.add_field(name="Color", value=str(role.color))
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to create roles!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="deleterole", description="Delete a role")
    @commands.has_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to delete")
    async def deleterole(self, ctx: commands.Context, role: discord.Role):
        """Delete a role. Usage: !deleterole <role>"""
        if ctx.interaction:
            await ctx.defer()

        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Error",
                description="You can't delete roles higher than or equal to your highest role!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
            return

        try:
            role_name = role.name
            await role.delete()
            embed = discord.Embed(
                title="✅ Role Deleted",
                description=f"Deleted role: {role_name}",
                color=discord.Color(0xa46ffb)
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
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to delete that role!",
                color=discord.Color(0xa46ffb)
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="listroles", description="Display all server roles")
    async def listroles(self, ctx: commands.Context):
        """Display all server roles. Usage: !listroles"""
        if ctx.interaction:
            await ctx.defer()

        roles = ctx.guild.roles[1:]  # Exclude @everyone role

        if not roles:
            embed = discord.Embed(
                title="📋 Server Roles",
                description="No roles found in this server.",
                color=discord.Color(0xa46ffb)
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
            return

        embed = discord.Embed(
            title="📋 Server Roles",
            color=discord.Color(0xa46ffb)
        )

        # Sort roles by position (highest to lowest)
        roles.sort(reverse=True, key=lambda x: x.position)

        # Create role list with mentions and member counts
        role_list = []
        for role in roles:
            member_count = len(role.members)
            role_list.append(f"{role.mention} - {member_count} member{'s' if member_count != 1 else ''}")

        # Split into chunks if too long
        chunk_size = 20
        role_chunks = [role_list[i:i + chunk_size] for i in range(0, len(role_list), chunk_size)]

        for i, chunk in enumerate(role_chunks):
            name = f"Roles ({i*chunk_size + 1}-{min((i+1)*chunk_size, len(role_list))})"
            value = "\n".join(chunk)
            embed.add_field(name=name, value=value, inline=False)

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
    await bot.add_cog(RoleManagement(bot))