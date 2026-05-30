import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_timers = {}

    @commands.hybrid_command(name="timer", description="Start a countdown timer")
    @app_commands.describe(duration="Duration in format: 1h2m3s (e.g., 1h30m, 45s, 2h)")
    async def timer(self, ctx: commands.Context, duration: str):
        """Start a countdown timer"""
        # Determine if this is a slash command or prefix command
        is_slash = isinstance(ctx.interaction, discord.Interaction)
        interaction = ctx.interaction if is_slash else ctx

        # Parse duration string
        total_seconds = 0
        current_num = ""

        for char in duration.lower():
            if char.isdigit():
                current_num += char
            elif char in ['h', 'm', 's'] and current_num:
                num = int(current_num)
                if char == 'h':
                    total_seconds += num * 3600
                elif char == 'm':
                    total_seconds += num * 60
                elif char == 's':
                    total_seconds += num
                current_num = ""

        if total_seconds <= 0:
            if is_slash:
                await interaction.response.send_message(
                    "❌ Invalid duration format! Use format like: 1h30m, 45s, 2h",
                    ephemeral=True
                )
            else:
                await ctx.send("❌ Invalid duration format! Use format like: 1h30m, 45s, 2h")
            return

        # Send initial confirmation
        embed = discord.Embed(
            title="⏰ Timer Started",
            description=f"Timer set for {duration}",
            color=0xa46ffb
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        if is_slash:
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()
        else:
            message = await ctx.send(embed=embed)

        # Start countdown
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
        timer_id = f"{ctx.author.id}-{end_time.timestamp()}"
        self.active_timers[timer_id] = True

        try:
            while total_seconds > 0 and self.active_timers[timer_id]:
                await asyncio.sleep(1)
                total_seconds -= 1

                # Update message every minute or when timer completes
                if total_seconds % 60 == 0 or total_seconds == 0:
                    remaining_hours = total_seconds // 3600
                    remaining_minutes = (total_seconds % 3600) // 60
                    remaining_seconds = total_seconds % 60

                    time_str = []
                    if remaining_hours > 0:
                        time_str.append(f"{remaining_hours}h")
                    if remaining_minutes > 0:
                        time_str.append(f"{remaining_minutes}m")
                    if remaining_seconds > 0 or not time_str:
                        time_str.append(f"{remaining_seconds}s")

                    status = " ".join(time_str) if total_seconds > 0 else "Time's up!"

                    new_embed = discord.Embed(
                        title="⏰ Timer" if total_seconds > 0 else "⏰ Timer Finished!",
                        description=status,
                        color=0xa46ffb
                    )
                    try:
                        from footer import FOOTER_TEXT
                        new_embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        new_embed.set_footer(text="Powered by Seculex | © 2025")

                    try:
                        if is_slash:
                            await interaction.edit_original_response(embed=new_embed)
                        else:
                            await message.edit(embed=new_embed)
                    except discord.NotFound:
                        break

            # Final notification when timer completes
            if total_seconds <= 0:
                try:
                    await ctx.channel.send(
                        f"{ctx.author.mention} Your timer has finished!",
                        embed=new_embed
                    )
                except discord.Forbidden:
                    pass

        finally:
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]

async def setup(bot):
    await bot.add_cog(Timer(bot))