import discord
from discord.ext import commands
import random
import asyncio
import time

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tictactoe_games = {}
        self.connectfour_games = {}
        self.hangman_games = {}
        self.rps_challenges = {}
        self.guessing_games = {}
        self.reaction_games = {}

    class TicTacToe:
        def __init__(self):
            self.board = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            self.current_player = None
            self.players = {}
            self.game_over = False

        def make_move(self, position: int, player) -> bool:
            if self.board[position] in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"] and not self.game_over:
                self.board[position] = ":regional_indicator_x:" if self.players[player] == "X" else ":o2:"
                return True
            return False

        def check_winner(self):
            win_combinations = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
            for combo in win_combinations:
                if all(self.board[combo[i]] == self.board[combo[0]] and self.board[combo[0]] not in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"] for i in range(3)):
                    return True
            return False

        def is_board_full(self):
            return all(square not in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"] for square in self.board)

        def get_board_string(self):
            return "\n".join([" ".join(self.board[i:i+3]) for i in range(0, 9, 3)])

    class TicTacToeView(discord.ui.View):
        def __init__(self, game, message, timeout=60):
            super().__init__(timeout=timeout)
            self.game = game
            self.message = message
            for i in range(9):
                button = discord.ui.Button(style=discord.ButtonStyle.secondary, label=str(i + 1), custom_id=f"ttt_{i}")
                button.callback = self.button_callback
                self.add_item(button)

        async def button_callback(self, interaction: discord.Interaction):
            if interaction.user != self.game.current_player:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return
            position = int(interaction.custom_id.split('_')[1])
            if self.game.make_move(position, interaction.user):
                if self.game.check_winner():
                    embed = discord.Embed(title="🎉 Game Over!", description=f"{interaction.user.mention} wins!\n\n{self.game.get_board_string()}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                    self.game.game_over = True
                    self.stop()
                elif self.game.is_board_full():
                    embed = discord.Embed(title="🤝 Game Over!", description=f"It's a draw!\n\n{self.game.get_board_string()}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                    self.game.game_over = True
                    self.stop()
                else:
                    self.game.current_player = [p for p in self.game.players if p != interaction.user][0]
                    embed = discord.Embed(title="Tic Tac Toe", description=f"{self.game.get_board_string()}\n\n{self.game.current_player.mention}'s turn!", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("That position is already taken!", ephemeral=True)

        async def on_timeout(self):
            if self.message:
                embed = discord.Embed(title="⏰ Game Over!", description="The game timed out due to inactivity.", color=0xa46ffb)
                try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                await self.message.edit(embed=embed, view=None)

    class ConnectFour:
        def __init__(self):
            self.board = [["⬜" for _ in range(7)] for _ in range(6)]
            self.current_player = None
            self.players = {}
            self.game_over = False

        def make_move(self, column: int, player) -> bool:
            if column < 0 or column >= 7 or self.game_over:
                return False
            for row in range(5, -1, -1):
                if self.board[row][column] == "⬜":
                    self.board[row][column] = self.players[player]
                    return True
            return False

        def check_winner(self):
            for row in range(6):
                for col in range(4):
                    if all(self.board[row][col + i] == self.board[row][col] and self.board[row][col] != "⬜" for i in range(4)):
                        return True
            for row in range(3):
                for col in range(7):
                    if all(self.board[row + i][col] == self.board[row][col] and self.board[row][col] != "⬜" for i in range(4)):
                        return True
            for row in range(3):
                for col in range(4):
                    if all(self.board[row + i][col + i] == self.board[row][col] and self.board[row][col] != "⬜" for i in range(4)):
                        return True
            for row in range(3, 6):
                for col in range(4):
                    if all(self.board[row - i][col + i] == self.board[row][col] and self.board[row][col] != "⬜" for i in range(4)):
                        return True
            return False

        def is_board_full(self):
            return all(cell != "⬜" for row in self.board for cell in row)

        def get_board_string(self):
            return "\n".join([" ".join(row) for row in self.board])

    class ConnectFourView(discord.ui.View):
        def __init__(self, game, message, timeout=60):
            super().__init__(timeout=timeout)
            self.game = game
            self.message = message
            for col in range(7):
                button = discord.ui.Button(style=discord.ButtonStyle.secondary, label=str(col + 1), custom_id=f"cf_{col}")
                button.callback = self.button_callback
                self.add_item(button)

        async def button_callback(self, interaction: discord.Interaction):
            if interaction.user != self.game.current_player:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return
            column = int(interaction.custom_id.split('_')[1])
            if self.game.make_move(column, interaction.user):
                if self.game.check_winner():
                    embed = discord.Embed(title="🎉 Game Over!", description=f"{interaction.user.mention} wins!\n\n{self.game.get_board_string()}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                    self.game.game_over = True
                    self.stop()
                elif self.game.is_board_full():
                    embed = discord.Embed(title="🤝 Game Over!", description=f"It's a draw!\n\n{self.game.get_board_string()}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                    self.game.game_over = True
                    self.stop()
                else:
                    self.game.current_player = [p for p in self.game.players if p != interaction.user][0]
                    embed = discord.Embed(title="Connect Four", description=f"{self.game.get_board_string()}\n\n{self.game.current_player.mention}'s turn!", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("Column is full or invalid!", ephemeral=True)

        async def on_timeout(self):
            if self.message:
                embed = discord.Embed(title="⏰ Game Over!", description="The game timed out due to inactivity.", color=0xa46ffb)
                try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                await self.message.edit(embed=embed, view=None)

    class Hangman:
        def __init__(self):
            self.words = ["python", "discord", "gaming", "bot", "server"]
            self.word = random.choice(self.words)
            self.guessed = set()
            self.attempts = 6
            self.game_over = False

        def get_display(self):
            return " ".join(letter if letter in self.guessed else "_" for letter in self.word)

        def make_guess(self, letter: str) -> bool:
            if self.game_over or letter in self.guessed or not letter.isalpha() or len(letter) != 1:
                return False
            self.guessed.add(letter.lower())
            if letter.lower() not in self.word:
                self.attempts -= 1
            return True

        def is_won(self):
            return all(letter in self.guessed for letter in self.word)

        def is_lost(self):
            return self.attempts <= 0

    class HangmanView(discord.ui.View):
        def __init__(self, game, message, timeout=60):
            super().__init__(timeout=timeout)
            self.game = game
            self.message = message
            self.add_item(discord.ui.Button(label="Guess", style=discord.ButtonStyle.primary, custom_id="hangman_guess"))

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return True

        async def on_timeout(self):
            if self.message:
                embed = discord.Embed(title="⏰ Game Over!", description="The game timed out due to inactivity.", color=0xa46ffb)
                try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                await self.message.edit(embed=embed, view=None)

        async def button_callback(self, interaction: discord.Interaction):
            await interaction.response.send_modal(HangmanModal(self.game, self.message))

    class HangmanModal(discord.ui.Modal, title="Guess a Letter"):
        def __init__(self, game, message):
            super().__init__()
            self.game = game
            self.message = message
            self.add_item(discord.ui.TextInput(label="Letter", placeholder="Enter a single letter", max_length=1))

        async def on_submit(self, interaction: discord.Interaction):
            letter = self.children[0].value
            if self.game.make_guess(letter):
                if self.game.is_won():
                    embed = discord.Embed(title="🎉 You Won!", description=f"Word: {self.game.word}\nAttempts left: {self.game.attempts}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                    self.game.game_over = True
                elif self.game.is_lost():
                    embed = discord.Embed(title="😢 You Lost!", description=f"Word was: {self.game.word}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=None)
                    self.game.game_over = True
                else:
                    hangman_stages = ["```\n  O\n  |\n  |\n ===```", "```\n  O\n  |\\\n  |\n ===```", "```\n  O\n  /|\\\n  |\n ===```", "```\n  O\n  /|\\\n  /\n ===```", "```\n  O\n  /|\\\n  / \\\n ===```"]
                    stage = 5 - self.game.attempts if self.game.attempts < 6 else 0
                    embed = discord.Embed(title="Hangman", description=f"Word: {self.game.get_display()}\nAttempts left: {self.game.attempts}\n{hangman_stages[stage]}", color=0xa46ffb)
                    try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
                    except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
                    await interaction.response.edit_message(embed=embed, view=self.view)
            else:
                await interaction.response.send_message("Invalid guess! Use a single letter you haven't guessed.", ephemeral=True)

    @commands.command(name="tictactoe")
    async def tictactoe(self, ctx, opponent: discord.Member):
        if opponent.bot or opponent == ctx.author:
            await ctx.send("❌ You can't play against a bot or yourself!")
            return
        game = self.TicTacToe()
        game.players = {ctx.author: "X", opponent: "O"}
        game.current_player = ctx.author
        self.tictactoe_games[ctx.message.id] = game
        embed = discord.Embed(title="Tic Tac Toe", description=f"{ctx.author.mention} (X) vs {opponent.mention} (O)\n\n{game.get_board_string()}\n\n{ctx.author.mention}'s turn!", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        message = await ctx.send(embed=embed)
        view = self.TicTacToeView(game, message)
        await message.edit(view=view)

    @commands.command(name="connect4")
    async def connect4(self, ctx, opponent: discord.Member):
        if opponent.bot or opponent == ctx.author:
            await ctx.send("❌ You can't play against a bot or yourself!")
            return
        game = self.ConnectFour()
        game.players = {ctx.author: "🔴", opponent: "🟡"}
        game.current_player = ctx.author
        self.connectfour_games[ctx.message.id] = game
        embed = discord.Embed(title="Connect Four", description=f"{ctx.author.mention} (🔴) vs {opponent.mention} (🟡)\n\n{game.get_board_string()}\n\n{ctx.author.mention}'s turn!", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        message = await ctx.send(embed=embed)
        view = self.ConnectFourView(game, message)
        await message.edit(view=view)

    @commands.command(name="hangman")
    async def hangman(self, ctx):
        game = self.Hangman()
        self.hangman_games[ctx.message.id] = game
        embed = discord.Embed(title="Hangman", description=f"Word: {game.get_display()}\nAttempts left: {game.attempts}", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        view = self.HangmanView(game, None)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @commands.command(name="rockpaperscissors")
    async def rockpaperscissors(self, ctx, opponent: discord.Member):
        if opponent.bot or opponent == ctx.author:
            await ctx.send("❌ You can't play against a bot or yourself!")
            return
        if ctx.author.id in self.rps_challenges or opponent.id in self.rps_challenges:
            await ctx.send("❌ One of the players is already in a game!")
            return
        self.rps_challenges[ctx.author.id] = {"opponent": opponent, "choice": None}
        self.rps_challenges[opponent.id] = {"opponent": ctx.author, "choice": None}
        embed = discord.Embed(title="Rock, Paper, Scissors Challenge!", description=f"{opponent.mention}, {ctx.author.mention} has challenged you!\nUse `!rpschoose` to play!", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="rpschoose")
    async def rpschoose(self, ctx, choice: str):
        if ctx.author.id not in self.rps_challenges:
            await ctx.send("❌ You're not in a game!")
            return
        if choice.lower() not in ["rock", "paper", "scissors"]:
            await ctx.send("❌ Invalid choice! Use 'rock', 'paper', or 'scissors'.")
            return
        game = self.rps_challenges[ctx.author.id]
        game["choice"] = choice.lower()
        opponent_game = self.rps_challenges[game["opponent"].id]
        await ctx.send("✅ Choice registered!")
        if opponent_game["choice"]:
            result = self.determine_winner(game["choice"], opponent_game["choice"])
            embed = discord.Embed(title="🎮 Rock, Paper, Scissors Results!", description=f"{ctx.author.mention} chose: {game['choice']}\n{game['opponent'].mention} chose: {opponent_game['choice']}\n\n{result}", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
            del self.rps_challenges[ctx.author.id]
            del self.rps_challenges[game["opponent"].id]

    @commands.command(name="ship")
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member):
        if user1 == user2:
            await ctx.send("❌ You can't ship someone with themselves!")
            return
        ship_seed = int(str(user1.id) + str(user2.id))
        random.seed(ship_seed)
        ship_percentage = random.randint(0, 100)
        random.seed()
        progress = '█' * (ship_percentage // 10) + '░' * (10 - ship_percentage // 10)
        rating = "Perfect Match! 💘" if ship_percentage >= 90 else "Great Match! 💖" if ship_percentage >= 70 else "Good Match! 💝" if ship_percentage >= 45 else "Not Bad! 💓" if ship_percentage >= 20 else "Needs Work! 💔"
        embed = discord.Embed(title="💕 Shipping Calculator", description=f"Shipping {user1.mention} with {user2.mention}...\n\n**{ship_percentage}%** `{progress}`\n**Rating:** {rating}", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="wyr")
    async def wyr(self, ctx):
        options = [("Eat pizza every day or never eat pizza again?", "Pizza every day", "Never again"), ("Have a pet dragon or a pet unicorn?", "Dragon", "Unicorn")]
        question, opt1, opt2 = random.choice(options)
        embed = discord.Embed(title="🤔 Would You Rather?", description=f"{question}\n1. {opt1}\n2. {opt2}", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def eightball(self, ctx, *, question: str):
        responses = ["Yes", "No", "Maybe", "Ask again later", "Cannot predict now", "Most likely", "Outlook good", "Very doubtful"]
        embed = discord.Embed(title="🎱 Magic 8-Ball", description=f"Question: {question}\nAnswer: {random.choice(responses)}", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="reactiongame")
    async def reactiongame(self, ctx):
        emojis = ["🍑", "🥤", "🍒", "🍪", "🎉", "😊"]
        target_emoji = random.choice(emojis)
        delay = random.uniform(5, 10)
        self.reaction_games[ctx.message.id] = {
            "start_time": time.time() + delay,
            "target_emoji": target_emoji,
            "winner": None,
            "fastest": float('inf')
        }
        embed = discord.Embed(
            title="⏳ Reaction Game",
            description="After 5-10 seconds, I will reveal the emoji you need to react with!\nGet ready...",
            color=0xa46ffb
        )
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        message = await ctx.send(embed=embed)
        await asyncio.sleep(delay)
        embed.description = f"Go! React with {target_emoji} now!"
        await message.edit(embed=embed)
        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == target_emoji and reaction.message.id == message.id
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=10.0, check=check)
            reaction_time = time.time() - self.reaction_games[ctx.message.id]["start_time"]
            if reaction_time < self.reaction_games[ctx.message.id]["fastest"]:
                self.reaction_games[ctx.message.id]["winner"] = user
                self.reaction_games[ctx.message.id]["fastest"] = reaction_time
            winner = self.reaction_games[ctx.message.id]["winner"]
            fastest = self.reaction_games[ctx.message.id]["fastest"]
            embed = discord.Embed(
                title="🏁 Reaction Game Results",
                description=f"🎉 {winner.mention} got the {target_emoji} in {fastest:.2f} seconds!\nYou Won!" if winner else "No one reacted in time!",
                color=0xa46ffb
            )
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await message.edit(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Reaction Game Over",
                description="No one reacted in time!",
                color=0xa46ffb
            )
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await message.edit(embed=embed)
        finally:
            del self.reaction_games[ctx.message.id]

    @commands.command(name="trivia")
    async def trivia(self, ctx):
        questions = [{"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin"], "answer": "Paris"}, {"question": "Which planet is known as the Red Planet?", "options": ["Mars", "Jupiter", "Venus"], "answer": "Mars"}]
        question = random.choice(questions)
        self.guessing_games[ctx.author.id] = {"type": "trivia", "question": question, "attempts": 1}
        embed = discord.Embed(title="❓ Trivia Quiz", description=f"Question: {question['question']}\nOptions: {', '.join(question['options'])}\nUse `!guessanswer` with your answer.", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="guessanswer")
    async def guessanswer(self, ctx, *, answer: str):
        if ctx.author.id not in self.guessing_games or self.guessing_games[ctx.author.id]["type"] != "trivia":
            await ctx.send("❌ You're not in a trivia game! Start with `!trivia`.")
            return
        game = self.guessing_games[ctx.author.id]
        if game["attempts"] <= 0:
            await ctx.send("❌ You've already used your attempt!")
            del self.guessing_games[ctx.author.id]
            return
        game["attempts"] -= 1
        if answer.lower() == game["question"]["answer"].lower():
            embed = discord.Embed(title="🎉 Correct!", description=f"Answer: {game['question']['answer']}", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="😢 Wrong!", description=f"Correct answer: {game['question']['answer']}", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
        del self.guessing_games[ctx.author.id]

    @commands.command(name="scramble")
    async def scramble(self, ctx):
        words = ["python", "discord", "gaming", "bot"]
        word = random.choice(words)
        scrambled = "".join(random.sample(word, len(word)))
        self.guessing_games[ctx.author.id] = {"type": "scramble", "word": word, "scrambled": scrambled, "attempts": 3, "timeout": time.time() + 30}
        embed = discord.Embed(title="🔤 Word Scramble", description=f"Unscramble: {scrambled}\nAttempts left: 3\nYou have 30 seconds!", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="unscramble")
    async def unscramble(self, ctx, *, answer: str):
        if ctx.author.id not in self.guessing_games or self.guessing_games[ctx.author.id]["type"] != "scramble":
            await ctx.send("❌ You're not in a scramble game! Start with `!scramble`.")
            return
        game = self.guessing_games[ctx.author.id]
        if time.time() > game["timeout"]:
            embed = discord.Embed(title="⏰ Time Out!", description=f"Time's up! The word was {game['word']}.", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
            del self.guessing_games[ctx.author.id]
            return
        game["attempts"] -= 1
        if answer.lower() == game["word"].lower():
            embed = discord.Embed(title="🎉 Correct!", description=f"Word: {game['word']}\nAttempts left: {game['attempts']}", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
            del self.guessing_games[ctx.author.id]
        elif game["attempts"] == 0:
            embed = discord.Embed(title="😢 Out of Attempts!", description=f"The word was {game['word']}.", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
            del self.guessing_games[ctx.author.id]
        else:
            embed = discord.Embed(title="🔤 Try Again", description=f"Wrong! Unscramble: {game['scrambled']}\nAttempts left: {game['attempts']}", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)

    @commands.command(name="guess")
    async def guess(self, ctx):
        number = random.randint(1, 100)
        self.guessing_games[ctx.author.id] = {"type": "number", "number": number, "attempts": 6}
        embed = discord.Embed(title="🎲 Number Guessing Game", description="I've picked a number between 1 and 100. Guess it!\nUse `!guessnumber` with your guess.\nYou have 6 attempts.", color=0xa46ffb)
        try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
        except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="guessnumber")
    async def guessnumber(self, ctx, guess: int):
        if ctx.author.id not in self.guessing_games or self.guessing_games[ctx.author.id]["type"] != "number":
            await ctx.send("❌ You're not in a number guessing game! Start with `!guess`.")
            return
        game = self.guessing_games[ctx.author.id]
        game["attempts"] -= 1
        attempts_left = game["attempts"]
        if guess < 1 or guess > 100:
            await ctx.send("❌ Guess must be between 1 and 100!")
            return
        if guess == game["number"]:
            embed = discord.Embed(title="🎉 You Won!", description=f"Correct! The number was {game['number']}.\nYou took {6 - attempts_left} attempts!", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
            del self.guessing_games[ctx.author.id]
        elif attempts_left == 0:
            embed = discord.Embed(title="😢 Game Over!", description=f"Out of attempts! The number was {game['number']}.", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)
            del self.guessing_games[ctx.author.id]
        else:
            hint = "higher" if guess < game["number"] else "lower"
            embed = discord.Embed(title="📉 Guess Again", description=f"Wrong! Guess {hint}.\nAttempts left: {attempts_left}", color=0xa46ffb)
            try: from footer import FOOTER_TEXT; embed.set_footer(text=FOOTER_TEXT)
            except ImportError: embed.set_footer(text="Powered by SECULEX | © 2025")
            await ctx.send(embed=embed)

    @commands.command(name="gamesguide")
    async def gamesguide(self, ctx):
        embed = discord.Embed(title="📖 Games Guide", description="Here’s how to play each game:", color=0xa46ffb)
        embed.add_field(
            name="Tic Tac Toe (!tictactoe @opponent)",
            value="A classic 3x3 game. Players take turns marking a square with 'X' or 'O'. First to get three in a row wins! Use the number buttons to select a position (1-9).",
            inline=False
        )
        embed.add_field(
            name="Connect Four (!connect4 @opponent)",
            value="Drop discs into a 6x7 grid. First to connect four discs horizontally, vertically, or diagonally wins! Use the number buttons (1-7) to drop.",
            inline=False
        )
        embed.add_field(
            name="Hangman (!hangman)",
            value="Guess the word by suggesting letters. You have 6 wrong attempts before the hangman is complete. Use the 'Guess' button to input a letter.",
            inline=False
        )
        embed.add_field(
            name="Rock Paper Scissors (!rockpaperscissors @opponent, !rpschoose <rock/paper/scissors>)",
            value="Challenge an opponent with `!rockpaperscissors @opponent`. Both players use `!rpschoose <rock/paper/scissors>` to pick. Rock beats scissors, scissors beats paper, paper beats rock.",
            inline=False
        )
        embed.add_field(
            name="Ship (!ship @user1 @user2)",
            value="Check the compatibility percentage between two users. Purely for fun with a random rating!",
            inline=False
        )
        embed.add_field(
            name="Would You Rather? (!wyr)",
            value="Presented with two tough choices. Think about it and discuss with others!",
            inline=False
        )
        embed.add_field(
            name="Magic 8-Ball (!8ball <question>)",
            value="Ask a yes/no question and get a mystical answer!",
            inline=False
        )
        embed.add_field(
            name="Reaction Game (!reactiongame)",
            value="After a 5-10 second delay, react with the revealed emoji (e.g., 🍒) as fast as possible. Fastest reaction wins!",
            inline=False
        )
        embed.add_field(
            name="Trivia (!trivia, !guessanswer <answer>)",
            value="Answer a multiple-choice question. You get one attempt per question.",
            inline=False
        )
        embed.add_field(
            name="Word Scramble (!scramble, !unscramble <answer>)",
            value="Unscramble the given word in 30 seconds with 3 attempts.",
            inline=False
        )
        embed.add_field(
            name="Number Guessing (!guess, !guessnumber <number>)",
            value="Guess a number between 1 and 100 in 6 attempts. Get hints after each guess!",
            inline=False
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="gamecmd")
    async def gamecmd(self, ctx):
        embed = discord.Embed(title="🎮 Game Commands", description="List of available game commands:", color=0xa46ffb)
        embed.add_field(
            name="Game Commands",
            value="```css\n"
                  "!tictactoe @opponent - Start Tic Tac Toe\n"
                  "!connect4 @opponent - Start Connect Four\n"
                  "!hangman - Start Hangman\n"
                  "!rockpaperscissors @opponent - Start Rock Paper Scissors\n"
                  "!rpschoose <rock/paper/scissors> - Make RPS choice\n"
                  "!ship @user1 @user2 - Ship two users\n"
                  "!wyr - Play Would You Rather?\n"
                  "!8ball <question> - Ask Magic 8-Ball\n"
                  "!reactiongame - Start Reaction Game\n"
                  "!trivia - Start Trivia\n"
                  "!guessanswer <answer> - Submit Trivia answer\n"
                  "!scramble - Start Word Scramble\n"
                  "!unscramble <answer> - Submit Scramble answer\n"
                  "!guess - Start Number Guessing\n"
                  "!guessnumber <number> - Submit Number guess\n"
                  "!gamesguide - Show game rules\n"
                  "!gamecmd - Show this command list\n"
                  "```",
            inline=False
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    def determine_winner(self, choice1, choice2):
        if choice1 == choice2: return "It's a tie! 🤝"
        winning_moves = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        return f"{choice1.title()} beats {choice2}! Player 1 wins! 🎉" if winning_moves[choice1] == choice2 else f"{choice2.title()} beats {choice1}! Player 2 wins! 🎉"

async def setup(bot):
    await bot.add_cog(Games(bot))