import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import random

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}

    @commands.command(name="gstart")
    @commands.has_permissions(administrator=True)
    async def gstart(self, ctx, duration: str = None, winners: int = None, *, prize: str = None):
        """Start a giveaway with specified duration, number of winners, and prize"""
        # Check for missing arguments
        if duration is None or winners is None or prize is None:
            embed = discord.Embed(
                title="❌ Missing Arguments/Options",
                description="You missed required arguments.\n\n"
                           "**Correct Usage:**\n"
                           "`!gstart <duration> <winners> <prize>`\n\n"
                           "**Examples:**\n"
                           "• `!gstart 1w 2 $50 Gift Card` (1 week, 2 winners)\n"
                           "• `!gstart 3d 1 Nitro` (3 days, 1 winner)\n"
                           "• `!gstart 12h 3 Cash Prize` (12 hours, 3 winners)",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
            return

        # Validate winners
        if winners < 1:
            embed = discord.Embed(
                title="❌ Invalid Number of Winners",
                description="Please specify at least 1 winner!",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
            return

        # Parse duration
        try:
            duration_seconds = 0
            duration = duration.lower()
            if 'w' in duration:
                weeks = int(duration.replace('w', ''))
                duration_seconds = weeks * 604800
            elif 'd' in duration:
                days = int(duration.replace('d', ''))
                duration_seconds = days * 86400
            elif 'h' in duration:
                hours = int(duration.replace('h', ''))
                duration_seconds = hours * 3600
            elif 'm' in duration:
                minutes = int(duration.replace('m', ''))
                duration_seconds = minutes * 60
            else:
                embed = discord.Embed(
                    title="❌ Invalid Duration Format",
                    description="Please use a valid duration format:\n"
                               "• Weeks: `1w` (e.g., 2w for 2 weeks)\n"
                               "• Days: `1d` (e.g., 3d for 3 days)\n"
                               "• Hours: `1h` (e.g., 12h for 12 hours)\n"
                               "• Minutes: `1m` (e.g., 30m for 30 minutes)",
                    color=0xa46ffb
                )
                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by Seculex | © 2025")
                await ctx.send(embed=embed)
                return
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Duration Format",
                description="Please use numbers followed by a time unit:\n"
                           "• Weeks: `1w` (e.g., 2w for 2 weeks)\n"
                           "• Days: `1d` (e.g., 3d for 3 days)\n"
                           "• Hours: `1h` (e.g., 12h for 12 hours)\n"
                           "• Minutes: `1m` (e.g., 30m for 30 minutes)",
                color=0xa46ffb
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")
            await ctx.send(embed=embed)
            return

        end_time = datetime.now() + timedelta(seconds=duration_seconds)

        # Create giveaway embed
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**{prize}**",
            color=0xa46ffb
        )
        embed.add_field(name="Ends in", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
        embed.add_field(name="Hosted by", value=ctx.author.mention, inline=True)
        embed.add_field(name="Winners", value=f"{winners}", inline=True)
        embed.set_footer(text=f"Ends at • {end_time.strftime('%Y/%m/%d %H:%M:%S')}")

        # Send giveaway message
        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("🎉")

        # Store giveaway info
        self.active_giveaways[giveaway_msg.id] = {
            'end_time': end_time,
            'prize': prize,
            'message': giveaway_msg,
            'host': ctx.author,
            'channel': ctx.channel,
            'winners': winners,
            'participants': set()
        }

        # Start giveaway timer
        await self.run_giveaway(giveaway_msg.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle reaction adds for giveaway entries"""
        if user.bot:
            return

        message_id = reaction.message.id
        if message_id in self.active_giveaways and reaction.emoji == "🎉":
            giveaway = self.active_giveaways[message_id]
            giveaway['participants'].add(user.id)

            # Send DM to user confirming entry
            try:
                embed = discord.Embed(
                    title="🎉 Giveaway Entry Confirmed!",
                    description=f"You have entered the giveaway for **{giveaway['prize']}** in {reaction.message.guild.name}!",
                    color=0xa46ffb
                )
                embed.add_field(name="Channel", value=f"{reaction.message.channel.mention}", inline=False)  # Updated to include clickable channel link
                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by Seculex | © 2025")
                await user.send(embed=embed)
            except discord.Forbidden:
                pass  # User has DMs disabled

    async def run_giveaway(self, message_id):
        """Handle the giveaway timer and winner selection"""
        giveaway = self.active_giveaways[message_id]
        await discord.utils.sleep_until(giveaway['end_time'])

        try:
            message = await giveaway['channel'].fetch_message(message_id)
            reaction = discord.utils.get(message.reactions, emoji="🎉")

            if not reaction or reaction.count <= 1:
                embed = discord.Embed(
                    title="🎉 GIVEAWAY ENDED 🎉",
                    description=f"**{giveaway['prize']}**",
                    color=0xa46ffb
                )
                embed.add_field(name="Ended at", value=f"<t:{int(giveaway['end_time'].timestamp())}:R>", inline=True)
                embed.add_field(name="Winners", value="No winners - not enough participants!", inline=True)
                embed.add_field(name="Hosted by", value=giveaway['host'].mention, inline=True)
                embed.set_footer(text=f"Ended at • {giveaway['end_time'].strftime('%Y-%m-%d %H:%M:%S')} (IST)")
                await message.edit(embed=embed)
                return

            # Get winners
            users = [user async for user in reaction.users() if not user.bot]
            if not users:
                return

            num_winners = min(giveaway['winners'], len(users))
            winners = random.sample(users, num_winners)
            winners_mention = ", ".join(winner.mention for winner in winners)

            # Update embed
            embed = discord.Embed(
                title="🎉 GIVEAWAY ENDED 🎉",
                description=f"**{giveaway['prize']}**",
                color=0xa46ffb
            )
            embed.add_field(name="Ended at", value=f"<t:{int(giveaway['end_time'].timestamp())}:R>", inline=True)
            embed.add_field(name="Winners", value=winners_mention, inline=True)
            embed.add_field(name="Hosted by", value=giveaway['host'].mention, inline=True)
            embed.set_footer(text=f"Ended at • {giveaway['end_time'].strftime('%Y-%m-%d %H:%M:%S')} (IST)")
            await message.edit(embed=embed)

            # Announce winners in channel
            await giveaway['channel'].send(
                f"🎉 Congratulations {winners_mention}! You won: **{giveaway['prize']}**!"
            )

            # Send DM to winners
            for winner in winners:
                try:
                    winner_embed = discord.Embed(
                        title="🎉 You Won!",
                        description=f"Congratulations! You won the giveaway in {giveaway['channel'].guild.name}!\n"
                                   f"Prize: **{giveaway['prize']}**",
                        color=0xa46ffb
                    )
                    winner_embed.add_field(name="Channel", value=f"{giveaway['channel'].mention}", inline=False)  # Updated to include clickable channel link
                    try:
                        from footer import FOOTER_TEXT
                        winner_embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        winner_embed.set_footer(text="Powered by Seculex | © 2025")
                    await winner.send(embed=winner_embed)
                except discord.Forbidden:
                    await giveaway['channel'].send(f"⚠️ Could not send DM to {winner.mention}")

        except discord.NotFound:
            pass
        finally:
            if message_id in self.active_giveaways:
                del self.active_giveaways[message_id]

async def setup(bot):
    await bot.add_cog(Giveaway(bot))