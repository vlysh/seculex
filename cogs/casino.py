import discord
from discord import ButtonStyle
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta
from utils.storage import JsonStorage

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        
        # Load currency data
        self.currency_data = self.storage.load_data('currency_data.json')
        if not self.currency_data:  # If file is empty or doesn't exist
            self.currency_data = {}
            self.storage.save_data('currency_data.json', self.currency_data)
        
        # Load leaderboard data, manually handle default
        self.leaderboard_data = self.storage.load_data('leaderboard.json')
        if not self.leaderboard_data:  # If file is empty or doesn't exist
            self.leaderboard_data = {'balances': {}, 'wins': {}}
            self.storage.save_data('leaderboard.json', self.leaderboard_data)

        self.daily_cooldowns = {}
        self.game_cooldowns = {}
        self.weekly_cooldowns = {}
        self.monthly_cooldowns = {}

    def get_balance(self, user_id: str) -> int:
        """Get user's current balance"""
        return self.currency_data.get(str(user_id), {}).get('balance', 0)

    def update_balance(self, user_id: str, amount: int):
        """Update user's balance"""
        if str(user_id) not in self.currency_data:
            self.currency_data[str(user_id)] = {'balance': 0}
        self.currency_data[str(user_id)]['balance'] += amount
        self.storage.save_data('currency_data.json', self.currency_data)

        # Update balance leaderboard
        self.leaderboard_data['balances'][str(user_id)] = self.currency_data[str(user_id)]['balance']
        self.storage.save_data('leaderboard.json', self.leaderboard_data)

    def update_win(self, user_id: str, amount: int):
        """Update user's total wins"""
        if str(user_id) not in self.leaderboard_data['wins']:
            self.leaderboard_data['wins'][str(user_id)] = 0
        self.leaderboard_data['wins'][str(user_id)] += amount
        self.storage.save_data('leaderboard.json', self.leaderboard_data)

    def check_game_cooldown(self, user_id: str, command: str, cooldown_hours: int = 1):
        """Check if a user is on cooldown for a specific game"""
        user_id = f"{user_id}_{command}"
        now = datetime.now()
        if user_id in self.game_cooldowns:
            last_play = self.game_cooldowns[user_id]
            if now - last_play < timedelta(hours=cooldown_hours):
                remaining = timedelta(hours=cooldown_hours) - (now - last_play)
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                return False, f"⏳ Wait {hours}h {minutes}m before playing again!"
        return True, None

    def set_game_cooldown(self, user_id: str, command: str):
        """Set a cooldown for a specific game"""
        user_id = f"{user_id}_{command}"
        self.game_cooldowns[user_id] = datetime.now()

    def check_reward_cooldown(self, user_id: str, cooldown_dict: dict, cooldown_period: timedelta):
        """Check if a user is on cooldown for a reward"""
        now = datetime.now()
        if user_id in cooldown_dict:
            last_claim = cooldown_dict[user_id]
            if now - last_claim < cooldown_period:
                remaining = cooldown_period - (now - last_claim)
                days = remaining.days
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                time_str = f"{days}d " if days else ""
                time_str += f"{hours}h {minutes}m"
                return False, f"⏳ Wait {time_str} before claiming again!"
        return True, None

    def set_reward_cooldown(self, user_id: str, cooldown_dict: dict):
        """Set a cooldown for a reward"""
        cooldown_dict[user_id] = datetime.now()

    @commands.command(name="balance", description="Check your current balance")
    async def balance(self, ctx: commands.Context):
        """Check your current balance"""
        balance = self.get_balance(str(ctx.author.id))
        embed = discord.Embed(
            title="<a:MONEY:1351423998252290150> Your Balance",
            description=f"You have {balance} coins",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, ctx: commands.Context):
        """Claim your daily reward"""
        user_id = str(ctx.author.id)
        can_claim, cooldown_msg = self.check_reward_cooldown(user_id, self.daily_cooldowns, timedelta(days=1))
        if not can_claim:
            await ctx.send(cooldown_msg)
            return

        reward = random.randint(100, 200)
        self.update_balance(user_id, reward)
        self.set_reward_cooldown(user_id, self.daily_cooldowns)

        embed = discord.Embed(
            title="<a:gifts:1351424240267821066> Daily Reward",
            description=f"You received {reward} coins!\nNew balance: {self.get_balance(user_id)} coins",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="weekly", description="Claim your weekly reward")
    async def weekly(self, ctx: commands.Context):
        """Claim your weekly reward"""
        user_id = str(ctx.author.id)
        can_claim, cooldown_msg = self.check_reward_cooldown(user_id, self.weekly_cooldowns, timedelta(days=7))
        if not can_claim:
            await ctx.send(cooldown_msg)
            return

        reward = random.randint(500, 1000)
        self.update_balance(user_id, reward)
        self.set_reward_cooldown(user_id, self.weekly_cooldowns)

        embed = discord.Embed(
            title="<a:gifts:1351424240267821066> Weekly Reward",
            description=f"You received {reward} coins!\nNew balance: {self.get_balance(user_id)} coins",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="monthly", description="Claim your monthly reward")
    async def monthly(self, ctx: commands.Context):
        """Claim your monthly reward"""
        user_id = str(ctx.author.id)
        can_claim, cooldown_msg = self.check_reward_cooldown(user_id, self.monthly_cooldowns, timedelta(days=30))
        if not can_claim:
            await ctx.send(cooldown_msg)
            return

        reward = random.randint(2000, 5000)
        self.update_balance(user_id, reward)
        self.set_reward_cooldown(user_id, self.monthly_cooldowns)

        embed = discord.Embed(
            title="<a:gifts:1351424240267821066> Monthly Reward",
            description=f"You received {reward} coins!\nNew balance: {self.get_balance(user_id)} coins",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", description="View the top balances and wins leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        """View the top balances and wins leaderboard"""
        balances = dict(sorted(self.leaderboard_data['balances'].items(), key=lambda x: x[1], reverse=True)[:5])
        wins = dict(sorted(self.leaderboard_data['wins'].items(), key=lambda x: x[1], reverse=True)[:5])

        embed = discord.Embed(
            title="<a:Trophy:1351424481801011251> Leaderboard",
            color=discord.Color(0xa46ffb)
        )
        embed.add_field(
            name="Top Balances",
            value="\n".join([f"{await self.bot.fetch_user(int(uid))}: {bal} coins" for uid, bal in balances.items()]) or "No data yet!",
            inline=False
        )
        embed.add_field(
            name="Top Wins",
            value="\n".join([f"{await self.bot.fetch_user(int(uid))}: {win} coins" for uid, win in wins.items()]) or "No data yet!",
            inline=False
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="slots", description="Play the slot machine. Usage: !slots <bet>")
    async def slots(self, ctx: commands.Context, bet: int):
        """Play the slot machine"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "slots")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        symbols = ["🍒", "🍊", "🍋", "🍇", "💎", "7️⃣"]
        weights = [30, 25, 20, 15, 7, 3]

        results = random.choices(symbols, weights=weights, k=3)

        winnings = 0
        if results[0] == results[1] == results[2]:
            if results[0] == "7️⃣":
                winnings = bet * 10
            elif results[0] == "💎":
                winnings = bet * 7
            else:
                winnings = bet * 4
        elif results[0] == results[1] or results[1] == results[2]:
            winnings = bet * 2

        net_change = winnings - bet
        self.update_balance(user_id, net_change)
        if winnings > 0:
            self.update_win(user_id, winnings)

        self.set_game_cooldown(user_id, "slots")

        result_line = " ".join(results)
        embed = discord.Embed(
            title="🎰 Slots",
            description=f"**[ {result_line} ]**\n\n",
            color=discord.Color(0xa46ffb)
        )

        if winnings > 0:
            embed.description += f"🎉 You won {winnings} coins!\n"
        else:
            embed.description += f"😢 You lost {bet} coins\n"

        embed.description += f"New balance: {self.get_balance(user_id)} coins"
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="plinko", description="Play Plinko. Usage: !plinko <bet>")
    async def plinko(self, ctx: commands.Context, bet: int):
        """Play Plinko"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "plinko")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        ROWS = 8
        COLS = 9
        board = [[" " for _ in range(COLS)] for _ in range(ROWS)]

        for row in range(ROWS):
            for col in range(COLS):
                if row % 2 == 1 or col % 2 == 1:
                    board[row][col] = "⚪"

        multipliers = [0.5, 1, 1.5, 2, 5, 2, 1.5, 1, 0.5]

        col = 4  # Start from middle
        path = []
        current_pos = (0, col)
        path.append(current_pos)

        for row in range(ROWS-1):
            if random.random() < 0.5:
                col = max(0, col - 1)
            else:
                col = min(COLS - 1, col + 1)
            current_pos = (row + 1, col)
            path.append(current_pos)

        multiplier = multipliers[col]
        winnings = int(bet * multiplier)
        net_change = winnings - bet

        visual_board = [row[:] for row in board]
        for row, col in path[:-1]:
            visual_board[row][col] = "⚪"
        final_row, final_col = path[-1]
        visual_board[final_row][final_col] = "🔵"

        board_str = "\n".join("".join(row) for row in visual_board)
        multiplier_display = " ".join(f"{m}x" for m in multipliers)

        self.update_balance(user_id, net_change)
        if winnings > bet:
            self.update_win(user_id, winnings)

        self.set_game_cooldown(user_id, "plinko")

        embed = discord.Embed(
            title="🎯 Plinko",
            description=f"{board_str}\n\n{multiplier_display}\n\n",
            color=discord.Color(0xa46ffb)
        )

        if winnings > bet:
            embed.description += f"🎉 You won {winnings} coins! (Multiplier: {multiplier}x)\n"
        else:
            embed.description += f"😢 You lost {bet - winnings} coins (Multiplier: {multiplier}x)\n"

        embed.description += f"New balance: {self.get_balance(user_id)} coins"
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="mines", description="Play Mines - Avoid mines to increase your winnings. Usage: !mines <bet> [mines] [difficulty]")
    async def mines(self, ctx: commands.Context, bet: int, mines: int = 3, difficulty: int = 1):
        """Play Mines"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "mines")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        if mines < 1 or mines > 5:
            await ctx.send("❌ Number of mines must be between 1 and 5!")
            return

        if difficulty < 1 or difficulty > 3:
            await ctx.send("❌ Difficulty must be between 1 and 3!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        GRID_SIZE = 5
        total_cells = GRID_SIZE * GRID_SIZE
        if mines >= total_cells:
            mines = total_cells - 1

        cells = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
        mine_positions = set(random.sample(cells, mines))
        revealed = set()

        class MinesView(discord.ui.View):
            def __init__(self, cog, user_id, bet, mines, difficulty):
                super().__init__(timeout=60.0)
                self.cog = cog
                self.user_id = user_id
                self.bet = bet
                self.mines = mines
                self.difficulty = difficulty
                self.picks = 0
                self.max_picks = 5 // difficulty  # Adjust max picks based on difficulty

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                await ctx.message.reply(embed=discord.Embed(
                    title="💣 Mines",
                    description=f"⏳ Timeout! You lost {self.bet} coins!\nNew balance: {self.cog.get_balance(self.user_id)} coins",
                    color=discord.Color(0xa46ffb)
                ).set_footer(text="Powered by SECULEX | © 2025"), view=self)
                self.cog.update_balance(self.user_id, -self.bet)
                self.cog.set_game_cooldown(self.user_id, "mines")

            @discord.ui.button(label="Pick a Cell", style=ButtonStyle.primary, custom_id="pick_cell")
            async def pick_cell(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != int(self.user_id):
                    await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
                    return
                if self.picks >= self.max_picks:
                    await interaction.response.send_message("❌ Maximum picks reached!", ephemeral=True)
                    return

                pick = random.choice([cell for cell in cells if cell not in revealed])
                revealed.add(pick)
                self.picks += 1

                hit_mine = pick in mine_positions
                multiplier = 1.5 if not hit_mine else 0
                winnings = int(self.bet * multiplier * (1 + 0.2 * self.picks)) if not hit_mine else 0
                net_change = winnings - self.bet

                grid = [["⬜" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                for row, col in revealed:
                    grid[row][col] = "✅" if not hit_mine else "💣"
                grid_str = "\n".join("".join(row) for row in grid)

                embed = discord.Embed(
                    title="💣 Mines",
                    description=f"{grid_str}\n\nPicks remaining: {self.max_picks - self.picks}",
                    color=discord.Color(0xa46ffb)
                )

                if hit_mine or self.picks >= self.max_picks:
                    self.stop()
                    self.cog.update_balance(self.user_id, net_change)
                    if winnings > self.bet:
                        self.cog.update_win(self.user_id, winnings)
                    self.cog.set_game_cooldown(self.user_id, "mines")
                    if hit_mine:
                        embed.description += f"\n💥 You hit a mine and lost {self.bet} coins!"
                    else:
                        embed.description += f"\n🎉 You won {winnings} coins! (Multiplier: {multiplier * (1 + 0.2 * self.picks)}x)"
                    embed.description += f"\nNew balance: {self.cog.get_balance(self.user_id)} coins"
                else:
                    embed.description += f"\n✅ Safe pick! Continue or wait for max picks."

                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by SECULEX | © 2025")
                await interaction.response.edit_message(embed=embed, view=self)

        view = MinesView(self, user_id, bet, mines, difficulty)
        embed = discord.Embed(
            title="💣 Mines",
            description="Click 'Pick a Cell' to start! Avoid mines to increase your winnings.\nPicks remaining: 5",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed, view=view)

    @mines.error
    async def mines_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument! Usage: `!mines <bet> [mines] [difficulty]` (e.g., `!mines 200 3 1`)")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument! Bet must be a valid integer (e.g., `!mines 200 3 1`)")

    @commands.command(name="coinflip", description="Play Coinflip - Heads or Tails. Usage: !coinflip <bet> <heads/tails>")
    async def coinflip(self, ctx: commands.Context, bet: int, choice: str):
        """Play Coinflip"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "coinflip")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        choice = choice.lower()
        if choice not in ["heads", "tails"]:
            await ctx.send("❌ Choice must be 'heads' or 'tails'!")
            return

        result = random.choice(["heads", "tails"])
        won = result == choice
        winnings = bet * 2 if won else 0
        net_change = winnings - bet

        self.update_balance(user_id, net_change)
        if winnings > 0:
            self.update_win(user_id, winnings)

        self.set_game_cooldown(user_id, "coinflip")

        embed = discord.Embed(
            title="🪙 Coinflip",
            description=f"You chose: **{choice.capitalize()}**\nResult: **{result.capitalize()}**\n\n",
            color=discord.Color(0xa46ffb)
        )

        if won:
            embed.description += f"🎉 You won {winnings} coins!\n"
        else:
            embed.description += f"😢 You lost {bet} coins!\n"

        embed.description += f"New balance: {self.get_balance(user_id)} coins"
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @coinflip.error
    async def coinflip_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument! Usage: `!coinflip <bet> <heads/tails>` (e.g., `!coinflip 150 heads`)")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument! Bet must be a valid integer (e.g., `!coinflip 150 heads`)")

    @commands.command(name="roulette", description="Play Roulette - Bet on numbers, colors, or ranges. Usage: !roulette <bet> <bet_type> <choice>")
    async def roulette(self, ctx: commands.Context, bet: int, bet_type: str, choice: str):
        """Play Roulette"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "roulette")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        number = random.randint(0, 36)
        color = "green" if number == 0 else ("red" if number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36] else "black")

        won = False
        multiplier = 0
        bet_type = bet_type.lower()
        if bet_type == "number":
            try:
                chosen_number = int(choice)
                if chosen_number < 0 or chosen_number > 36:
                    await ctx.send("❌ Number must be between 0 and 36!")
                    return
                won = (chosen_number == number)
                multiplier = 35
            except ValueError:
                await ctx.send("❌ Invalid number!")
                return
        elif bet_type == "color":
            choice = choice.lower()
            if choice not in ["red", "black"]:
                await ctx.send("❌ Color must be 'red' or 'black'!")
                return
            won = (color == choice)
            multiplier = 2
        elif bet_type == "range":
            choice = choice.lower()
            if choice not in ["even", "odd", "1-18", "19-36"]:
                await ctx.send("❌ Range must be 'even', 'odd', '1-18', or '19-36'!")
                return
            if choice == "even":
                won = number != 0 and number % 2 == 0
            elif choice == "odd":
                won = number != 0 and number % 2 != 0
            elif choice == "1-18":
                won = 1 <= number <= 18
            elif choice == "19-36":
                won = 19 <= number <= 36
            multiplier = 2
        else:
            await ctx.send("❌ Bet type must be 'number', 'color', or 'range'!")
            return

        winnings = int(bet * multiplier) if won else 0
        net_change = winnings - bet

        self.update_balance(user_id, net_change)
        if winnings > 0:
            self.update_win(user_id, winnings)

        self.set_game_cooldown(user_id, "roulette")

        embed = discord.Embed(
            title="🎡 Roulette",
            description=f"Result: **{number} ({color.capitalize()})**\nYour bet: **{choice}** ({bet_type.capitalize()})\n\n",
            color=discord.Color(0xa46ffb)
        )

        if won:
            embed.description += f"🎉 You won {winnings} coins! (Multiplier: {multiplier}x)\n"
        else:
            embed.description += f"😢 You lost {bet} coins!\n"

        embed.description += f"New balance: {self.get_balance(user_id)} coins"
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="crash", description="Play Crash - Cash out before the multiplier crashes. Usage: !crash <bet> [custom_multiplier]")
    async def crash(self, ctx: commands.Context, bet: int, custom_multiplier: float = None):
        """Play Crash"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "crash")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        if custom_multiplier is not None and (custom_multiplier < 1.0 or custom_multiplier > 10.0):
            await ctx.send("❌ Custom multiplier must be between 1.0 and 10.0!")
            return

        class CrashView(discord.ui.View):
            def __init__(self, cog, user_id, bet, custom_multiplier):
                super().__init__(timeout=30.0)
                self.cog = cog
                self.user_id = user_id
                self.bet = bet
                self.custom_multiplier = custom_multiplier
                self.crash_point = 1.0
                self.running = True
                self.update_multiplier()

            def update_multiplier(self):
                if self.running and random.random() < 0.95:  # 5% chance to crash
                    self.crash_point += 0.1
                else:
                    self.running = False

            @discord.ui.button(label="Cash Out", style=ButtonStyle.success, custom_id="cash_out")
            async def cash_out(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != int(self.user_id):
                    await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
                    return
                self.stop()
                cashout_point = round(self.crash_point, 2)
                winnings = int(self.bet * cashout_point) if cashout_point < (self.custom_multiplier or 10.0) else 0
                net_change = winnings - self.bet
                self.cog.update_balance(self.user_id, net_change)
                if winnings > self.bet:
                    self.cog.update_win(self.user_id, winnings)
                self.cog.set_game_cooldown(self.user_id, "crash")

                embed = discord.Embed(
                    title="🚀 Crash",
                    description=f"Crash Point: **{(self.custom_multiplier or 10.0)}x**\nYou cashed out at: **{cashout_point}x**\n\n",
                    color=discord.Color(0xa46ffb)
                )
                if cashout_point < (self.custom_multiplier or 10.0):
                    embed.description += f"🎉 You won {winnings} coins! (Multiplier: {cashout_point}x)\n"
                else:
                    embed.description += f"💥 Crashed! You lost {self.bet} coins!\n"
                embed.description += f"New balance: {self.cog.get_balance(self.user_id)} coins"
                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by SECULEX | © 2025")
                await interaction.response.edit_message(embed=embed, view=None)

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                if self.running:
                    self.cog.update_balance(self.user_id, -bet)
                    self.cog.set_game_cooldown(self.user_id, "crash")
                    embed = discord.Embed(
                        title="🚀 Crash",
                        description=f"Crash Point: **{(self.custom_multiplier or 10.0)}x**\nYou failed to cash out! Crash occurred!\n\n💥 You lost {bet} coins!\nNew balance: {self.cog.get_balance(self.user_id)} coins",
                        color=discord.Color(0xa46ffb)
                    )
                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by SECULEX | © 2025")
                    await ctx.message.reply(embed=embed, view=self)

        view = CrashView(self, user_id, bet, custom_multiplier if custom_multiplier and 1.0 <= custom_multiplier <= 10.0 else None)
        if view.custom_multiplier is None:
            view.custom_multiplier = 10.0
        embed = discord.Embed(
            title="🚀 Crash",
            description=f"Current Multiplier: **{round(view.crash_point, 2)}x**\nClick 'Cash Out' to secure your winnings!\n(Timeout: 30s or custom max: {view.custom_multiplier}x)",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed, view=view)

    @commands.command(name="blackjack", description="Play Blackjack against the bot dealer. Usage: !blackjack <bet>")
    async def blackjack(self, ctx: commands.Context, bet: int):
        """Play Blackjack"""
        user_id = str(ctx.author.id)
        can_play, cooldown_msg = self.check_game_cooldown(user_id, "blackjack")
        if not can_play:
            await ctx.send(cooldown_msg)
            return

        if bet <= 0:
            await ctx.send("❌ Minimum bet is 1 coin!")
            return

        balance = self.get_balance(user_id)
        if balance < bet:
            await ctx.send("❌ You don't have enough coins!")
            return

        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
        random.shuffle(deck)

        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        def get_value(hand):
            value = 0
            aces = 0
            for card in hand:
                rank = card[:-1]
                if rank in ['J', 'Q', 'K']:
                    value += 10
                elif rank == 'A':
                    aces += 1
                else:
                    value += int(rank)
            for _ in range(aces):
                if value + 11 <= 21:
                    value += 11
                else:
                    value += 1
            return value

        class BlackjackView(discord.ui.View):
            def __init__(self, cog, user_id, bet, player_hand, dealer_hand, deck):
                super().__init__(timeout=60.0)
                self.cog = cog
                self.user_id = user_id
                self.bet = bet
                self.player_hand = player_hand
                self.dealer_hand = dealer_hand
                self.deck = deck
                self.player_value = get_value(player_hand)
                self.dealer_value = get_value(dealer_hand[:1])  # Show only one dealer card initially

            @discord.ui.button(label="Hit", style=ButtonStyle.primary, custom_id="hit")
            async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != int(self.user_id):
                    await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
                    return
                self.player_hand.append(self.deck.pop())
                self.player_value = get_value(self.player_hand)
                if self.player_value > 21:
                    self.stop()
                    self.cog.update_balance(self.user_id, -self.bet)
                    self.cog.set_game_cooldown(self.user_id, "blackjack")
                    embed = discord.Embed(
                        title="🃏 Blackjack",
                        description=(
                            f"**Your Hand:** {' '.join(self.player_hand)} (Value: {self.player_value})\n"
                            f"**Dealer's Hand:** {' '.join(self.dealer_hand)} (Value: {get_value(self.dealer_hand)})\n\n"
                            f"💥 You busted and lost {self.bet} coins!\n"
                            f"New balance: {self.cog.get_balance(self.user_id)} coins"
                        ),
                        color=discord.Color(0xa46ffb)
                    )
                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    embed = discord.Embed(
                        title="🃏 Blackjack",
                        description=(
                            f"**Your Hand:** {' '.join(self.player_hand)} (Value: {self.player_value})\n"
                            f"**Dealer's Hand:** {self.dealer_hand[0]} ?? (Value: {self.dealer_value})\n\n"
                            f"Choose to Hit or Stand!"
                        ),
                        color=discord.Color(0xa46ffb)
                    )
                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=self)

            @discord.ui.button(label="Stand", style=ButtonStyle.secondary, custom_id="stand")
            async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != int(self.user_id):
                    await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
                    return
                self.stop()
                while get_value(self.dealer_hand) < 17:
                    self.dealer_hand.append(self.deck.pop())
                dealer_value = get_value(self.dealer_hand)
                if dealer_value > 21:
                    winnings = self.bet * 2
                elif self.player_value > dealer_value:
                    winnings = self.bet * 2
                elif dealer_value > self.player_value:
                    winnings = 0
                else:
                    winnings = self.bet
                net_change = winnings - self.bet
                self.cog.update_balance(self.user_id, net_change)
                if winnings > self.bet:
                    self.cog.update_win(self.user_id, winnings)
                self.cog.set_game_cooldown(self.user_id, "blackjack")

                embed = discord.Embed(
                    title="🃏 Blackjack",
                    description=(
                        f"**Your Hand:** {' '.join(self.player_hand)} (Value: {self.player_value})\n"
                        f"**Dealer's Hand:** {' '.join(self.dealer_hand)} (Value: {dealer_value})\n\n"
                    ),
                    color=discord.Color(0xa46ffb)
                )
                if self.player_value > 21:
                    embed.description += f"💥 You busted and lost {self.bet} coins!\n"
                elif dealer_value > 21:
                    embed.description += f"🎉 Dealer busted! You won {winnings} coins!\n"
                elif self.player_value > dealer_value:
                    embed.description += f"🎉 You won {winnings} coins!\n"
                elif dealer_value > self.player_value:
                    embed.description += f"😢 Dealer wins! You lost {self.bet} coins!\n"
                else:
                    embed.description += f"🤝 Push! You get your {self.bet} coins back.\n"
                embed.description += f"New balance: {self.cog.get_balance(self.user_id)} coins"
                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by SECULEX | © 2025")
                await interaction.response.edit_message(embed=embed, view=None)

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                self.cog.update_balance(self.user_id, -bet)
                self.cog.set_game_cooldown(self.user_id, "blackjack")
                embed = discord.Embed(
                    title="🃏 Blackjack",
                    description=(
                        f"**Your Hand:** {' '.join(self.player_hand)} (Value: {self.player_value})\n"
                        f"**Dealer's Hand:** {' '.join(self.dealer_hand)} (Value: {get_value(self.dealer_hand)})\n\n"
                        f"⏳ Timeout! You lost {self.bet} coins!\n"
                        f"New balance: {self.cog.get_balance(self.user_id)} coins"
                    ),
                    color=discord.Color(0xa46ffb)
                )
                try:
                    from footer import FOOTER_TEXT
                    embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    embed.set_footer(text="Powered by SECULEX | © 2025")
                await ctx.message.reply(embed=embed, view=self)

        view = BlackjackView(self, user_id, bet, player_hand, dealer_hand, deck)
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=(
                f"**Your Hand:** {' '.join(player_hand)} (Value: {view.player_value})\n"
                f"**Dealer's Hand:** {dealer_hand[0]} ?? (Value: {view.dealer_value})\n\n"
                f"Choose to Hit or Stand!"
            ),
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed, view=view)

    @commands.command(name="sendcoins", description="Send coins to another user. Usage: !sendcoins <user> <amount>")
    async def sendcoins(self, ctx: commands.Context, user: discord.Member, amount: int):
        """Send coins to another user"""
        if amount <= 0:
            await ctx.send("❌ Amount must be greater than 0!")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)

        if self.get_balance(sender_id) < amount:
            await ctx.send("❌ You don't have enough coins!")
            return

        self.update_balance(sender_id, -amount)
        self.update_balance(receiver_id, amount)

        embed = discord.Embed(
            title="💸 Coins Sent!",
            description=f"{ctx.author.mention} sent {amount} coins to {user.mention}",
            color=discord.Color(0xa46ffb)
        )
        embed.add_field(
            name="New Balances",
            value=f"{ctx.author.mention}: {self.get_balance(sender_id)} coins\n"
                  f"{user.mention}: {self.get_balance(receiver_id)} coins"
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="addcoins", description="[Admin] Add coins to a user's balance. Usage: !addcoins <user> <amount>")
    @commands.has_permissions(administrator=True)
    async def addcoins(self, ctx: commands.Context, user: discord.Member, amount: int):
        """[Admin] Add coins to a user's balance"""
        if amount <= 0:
            await ctx.send("❌ Amount must be greater than 0!")
            return

        user_id = str(user.id)
        self.update_balance(user_id, amount)

        embed = discord.Embed(
            title="💰 Coins Added",
            description=f"Added {amount} coins to {user.mention}'s account",
            color=discord.Color(0xa46ffb)
        )
        embed.add_field(
            name="New Balance",
            value=f"{user.mention}: {self.get_balance(user_id)} coins"
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="casinoguide", description="View a guide for all casino games")
    async def casinoguide(self, ctx: commands.Context):
        """View a guide for all casino games"""
        embed = discord.Embed(
            title="🎲 Casino Guide",
            description="Welcome to the Casino! Below is a guide to all available games, including rules, bet limits, and payouts.",
            color=discord.Color(0xa46ffb)
        )

        embed.add_field(
            name="🎰 Slots (!slots)",
            value=(
                "**Rules:** Bet coins to spin the slot machine. Match symbols to win.\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Payouts:**\n"
                "- 3x 7️⃣: 10x bet\n"
                "- 3x 💎: 7x bet\n"
                "- 3x any other symbol: 4x bet\n"
                "- 2x matching symbols: 2x bet\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="🎯 Plinko (!plinko)",
            value=(
                "**Rules:** Bet coins and drop a ball through a pegged board. Multipliers determine winnings.\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Payouts:** 0.5x to 5x.\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="💣 Mines (!mines)",
            value=(
                "**Rules:** Bet coins and pick cells on a 5x5 grid. Avoid mines to win (max 5 picks based on difficulty).\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Mines:** 1-5, Difficulty 1-3 (higher = fewer picks).\n"
                "**Payouts:** 1.5x + 0.2x per safe pick if successful, 0x if mine hit.\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="🪙 Coinflip (!coinflip)",
            value=(
                "**Rules:** Bet coins and choose heads or tails.\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Payouts:** 2x bet if win, 0x if lose.\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="🎡 Roulette (!roulette)",
            value=(
                "**Rules:** Bet on a number (0-36), color (red/black), or range (even/odd, 1-18/19-36).\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Payouts:**\n"
                "- Number: 35x bet\n"
                "- Color/Range: 2x bet\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="🚀 Crash (!crash)",
            value=(
                "**Rules:** Bet coins and cash out before the multiplier crashes (or reaches custom max).\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Payouts:** Multiplier at cashout (default max 10x, customizable 1-10x).\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="🃏 Blackjack (!blackjack)",
            value=(
                "**Rules:** Bet coins and get closer to 21 than the dealer without busting.\n"
                "**Bet Limits:** Minimum 1 coin, no maximum.\n"
                "**Payouts:**\n"
                "- Win: 2x bet\n"
                "- Push: Bet returned\n"
                "- Loss: 0x bet\n"
                "**Cooldown:** 1 hour"
            ),
            inline=False
        )

        embed.add_field(
            name="💰 Currency Commands",
            value=(
                "**Balance (!balance):** Check your coin balance.\n"
                "**Daily (!daily):** Claim 100-200 coins every 24h.\n"
                "**Weekly (!weekly):** Claim 500-1000 coins every 7d.\n"
                "**Monthly (!monthly):** Claim 2000-5000 coins every 30d.\n"
                "**Sendcoins (!sendcoins):** Transfer coins to another user.\n"
                "**Addcoins (!addcoins):** [Admin] Add coins to a user’s balance."
            ),
            inline=False
        )

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="casinocmd", description="List all casino commands and their descriptions")
    async def casinocmd(self, ctx: commands.Context):
        """List all casino commands and their descriptions"""
        embed = discord.Embed(
            title="<a:GamepadCat:1351423757528334386> Casino Commands",
            description="Below is a list of all casino commands and what they do. Use `!casinoguide` for detailed game rules.",
            color=discord.Color(0xa46ffb)
        )

        embed.add_field(
            name="<:purple_arrow:1351298291962220656> Currency Commands",
            value=(
                "`!balance` - Check your current coin balance.\n"
                "`!daily` - Claim a daily reward (100-200 coins, 24h cooldown).\n"
                "`!weekly` - Claim a weekly reward (500-1000 coins, 7d cooldown).\n"
                "`!monthly` - Claim a monthly reward (2000-5000 coins, 30d cooldown).\n"
                "`!sendcoins <user> <amount>` - Send coins to another user.\n"
                "`!addcoins <user> <amount>` - [Admin] Add coins to a user's balance."
            ),
            inline=False
        )

        embed.add_field(
            name="<:purple_arrow:1351298291962220656> Game Commands",
            value=(
                "`!slots <bet>` - Play the slot machine.\n"
                "`!plinko <bet>` - Play Plinko with a pegged board.\n"
                "`!mines <bet> [mines] [difficulty]` - Play Mines, avoid mines to win.\n"
                "`!coinflip <bet> <heads/tails>` - Play Coinflip, guess heads or tails.\n"
                "`!roulette <bet> <bet_type> <choice>` - Play Roulette, bet on numbers, colors, or ranges.\n"
                "`!crash <bet> [custom_multiplier]` - Play Crash, cash out before it crashes.\n"
                "`!blackjack <bet>` - Play Blackjack against the bot dealer."
            ),
            inline=False
        )

        embed.add_field(
            name="<:purple_arrow:1351298291962220656> Information Commands",
            value=(
                "`!leaderboard` - View the top balances and wins leaderboard.\n"
                "`!casinoguide` - View a detailed guide for all casino games.\n"
                "`!casinocmd` - List all casino commands (this command)."
            ),
            inline=False
        )

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Casino(bot))