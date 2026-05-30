import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

class AvatarView(View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=60)
        self.user = user

        # Add buttons for different avatar types
        self.add_item(Button(label="User Avatar", custom_id="user_avatar", style=discord.ButtonStyle.blurple))
        self.add_item(Button(label="Server Avatar", custom_id="server_avatar", style=discord.ButtonStyle.green))
        self.add_item(Button(label="Banner", custom_id="banner", style=discord.ButtonStyle.red))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        button_id = interaction.data["custom_id"]

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{self.user.name}'s {button_id.replace('_', ' ').title()}")

        if button_id == "user_avatar":
            embed.set_image(url=self.user.display_avatar.url)
        elif button_id == "server_avatar":
            if self.user.guild_avatar:
                embed.set_image(url=self.user.guild_avatar.url)
            else:
                embed.description = "This user doesn't have a server-specific avatar!"
                embed.set_image(url=self.user.display_avatar.url)
        elif button_id == "banner":
            if self.user.banner:
                embed.set_image(url=self.user.banner.url)
            else:
                embed.description = "This user doesn't have a banner!"

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return True

class ServerView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=60)
        self.guild = guild

        # Add buttons for different server images
        self.add_item(Button(label="Server Icon", custom_id="server_icon", style=discord.ButtonStyle.blurple))
        self.add_item(Button(label="Server Banner", custom_id="server_banner", style=discord.ButtonStyle.green))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        button_id = interaction.data["custom_id"]

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{self.guild.name}'s {button_id.replace('_', ' ').title()}")

        if button_id == "server_icon":
            if self.guild.icon:
                embed.set_image(url=self.guild.icon.url)
            else:
                embed.description = "This server doesn't have an icon!"
        elif button_id == "server_banner":
            if self.guild.banner:
                embed.set_image(url=self.guild.banner.url)
            else:
                embed.description = "This server doesn't have a banner!"

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return True

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(user="The user to get avatars from")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """View a user's different avatars and banner"""
        user = user or interaction.user
        view = AvatarView(user)

        embed = discord.Embed(
            title="🖼️ Avatar Viewer",
            description="Click the buttons below to view different types of avatars!",
            color=discord.Color.blue()
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command()
    async def server(self, interaction: discord.Interaction):
        """View server icon and banner"""
        view = ServerView(interaction.guild)

        embed = discord.Embed(
            title="🖼️ Server Image Viewer",
            description="Click the buttons below to view server images!",
            color=discord.Color.blue()
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Avatar(bot))