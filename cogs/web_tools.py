import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import time
import asyncio
from io import BytesIO

class WebTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    async def cog_check(self, ctx):
        return True

    @commands.hybrid_command(
        name="screenshot",
        description="Take a screenshot of a website"
    )
    @app_commands.describe(url="The URL of the website to screenshot")
    async def screenshot(self, ctx: commands.Context, url: str):
        """Takes a screenshot of the specified website"""
        try:
            if isinstance(ctx, discord.Interaction):
                await ctx.response.defer()
            else:
                await ctx.message.add_reaction('⏳')
        except discord.NotFound:
            pass

        try:
            # Add http:// if not present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Use Thum.io free tier (no signup, 1000 impressions/month)
            api_url = f"https://image.thum.io/get/width/1920/crop/1080/{url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        raise Exception(f"Thum.io API returned status {response.status}")
                    screenshot = await response.read()

            img_io = BytesIO(screenshot)
            file = discord.File(fp=img_io, filename='screenshot.png')

            # Create embed
            embed = discord.Embed(
                title="📸 Website Screenshot",
                description=f"Screenshot of {url}",
                color=0xa46ffb
            )
            embed.set_image(url="attachment://screenshot.png")
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            # Send response
            if isinstance(ctx, discord.Interaction):
                try:
                    await ctx.followup.send(embed=embed, file=file)
                except discord.NotFound:
                    await ctx.channel.send(embed=embed, file=file)
            else:
                await ctx.send(embed=embed, file=file)
                await ctx.message.remove_reaction('⏳', self.bot.user)
                await ctx.message.add_reaction('✅')

        except Exception as e:
            error_msg = f"❌ Failed to take screenshot: {str(e)}"
            if isinstance(ctx, discord.Interaction):
                try:
                    await ctx.followup.send(error_msg, ephemeral=True)
                except discord.NotFound:
                    await ctx.channel.send(error_msg)
            else:
                await ctx.send(error_msg)
                try:
                    await ctx.message.remove_reaction('⏳', self.bot.user)
                except discord.NotFound:
                    pass

    @commands.hybrid_command(
        name="urban",
        description="Search for a word on Urban Dictionary"
    )
    @app_commands.describe(word="The word to look up")
    async def urban(self, ctx: commands.Context, word: str):
        """Search for a word definition on Urban Dictionary"""
        try:
            if isinstance(ctx, discord.Interaction):
                await ctx.response.defer()
            else:
                await ctx.message.add_reaction('⏳')
        except discord.NotFound:
            pass

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.urbandictionary.com/v0/define?term={word}') as response:
                    if response.status == 200:
                        data = await response.json()

                        if not data['list']:
                            msg = f"❌ No definition found for '{word}'"
                            if isinstance(ctx, discord.Interaction):
                                try:
                                    await ctx.followup.send(msg)
                                except discord.NotFound:
                                    await ctx.channel.send(msg)
                            else:
                                await ctx.send(msg)
                                await ctx.message.remove_reaction('⏳', self.bot.user)
                            return

                        definition = data['list'][0]

                        embed = discord.Embed(
                            title=f"📚 Urban Dictionary: {word}",
                            color=0xa46ffb
                        )

                        def_text = definition['definition'][:1024] + '...' if len(definition['definition']) > 1024 else definition['definition']
                        example = definition['example'][:1024] + '...' if len(definition['example']) > 1024 else definition['example']

                        embed.add_field(name="Definition", value=def_text, inline=False)
                        if example:
                            embed.add_field(name="Example", value=example, inline=False)

                        embed.add_field(name="👍", value=str(definition['thumbs_up']), inline=True)
                        embed.add_field(name="👎", value=str(definition['thumbs_down']), inline=True)

                        try:
                            from footer import FOOTER_TEXT
                            embed.set_footer(text=FOOTER_TEXT)
                        except ImportError:
                            embed.set_footer(text="Powered by Seculex | © 2025")

                        if isinstance(ctx, discord.Interaction):
                            try:
                                await ctx.followup.send(embed=embed)
                            except discord.NotFound:
                                await ctx.channel.send(embed=embed)
                        else:
                            await ctx.send(embed=embed)
                            await ctx.message.remove_reaction('⏳', self.bot.user)
                            await ctx.message.add_reaction('✅')
                    else:
                        msg = "❌ Failed to fetch definition"
                        if isinstance(ctx, discord.Interaction):
                            try:
                                await ctx.followup.send(msg, ephemeral=True)
                            except discord.NotFound:
                                await ctx.channel.send(msg)
                        else:
                            await ctx.send(msg)
                            await ctx.message.remove_reaction('⏳', self.bot.user)
        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            if isinstance(ctx, discord.Interaction):
                try:
                    await ctx.followup.send(error_msg, ephemeral=True)
                except discord.NotFound:
                    await ctx.channel.send(error_msg)
            else:
                await ctx.send(error_msg)
                try:
                    await ctx.message.remove_reaction('⏳', self.bot.user)
                except discord.NotFound:
                    pass

async def setup(bot):
    await bot.add_cog(WebTools(bot))