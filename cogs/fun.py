import discord
from discord.ext import commands
import random
import aiohttp
import json
import os

class Fun(commands.Cog):
    """Fun commands for entertainment and roleplay interactions"""

    def __init__(self, bot):
        self.bot = bot
        self.marriage_file = "marriages.json"
        self.load_marriages()
        # Fallback quotes in case the Quotable API fails
        self.fallback_quotes = [
            {"content": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
            {"content": "Success is not final, failure is not fatal: It is the courage to continue that counts.", "author": "Winston Churchill"},
            {"content": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"}
        ]
        # Sad quotes for the !sad command
        self.sad_quotes = [
            {"content": "The hardest thing is not talking to someone you used to talk to every day.", "author": "Unknown"},
            {"content": "Sometimes, you just have to accept that some people can stay in your heart but not in your life.", "author": "Unknown"},
            {"content": "Tears are words that need to be written.", "author": "Paulo Coelho"},
            {"content": "The pain of parting is nothing to the joy of meeting again.", "author": "Charles Dickens"},
            {"content": "A broken heart is just the growing pains necessary so that you can love more completely when the real thing comes along.", "author": "J.S.B. Morse"}
        ]
        # GIF collections for roleplay actions
        self.action_gifs = {
            'blush': [
                'https://media.giphy.com/media/klmpEcFgXzrYQ/giphy.gif',
                'https://media.giphy.com/media/UUjkoeNhnn0K4/giphy.gif',
                'https://media.giphy.com/media/T3Vvyi6SHJtXW/giphy.gif',
                'https://media.giphy.com/media/6CBGoJnEBbEWs/giphy.gif',
                'https://media.giphy.com/media/ulWUgCk4F1GGA/giphy.gif'
            ],
            'cry': [
                'https://media.giphy.com/media/ROF8OQvDmxytW/giphy.gif',
                'https://media.giphy.com/media/3fmRTfVIKMRiM/giphy.gif',
                'https://media.giphy.com/media/ShPv5tt0EM396/giphy.gif',
                'https://media.giphy.com/media/d2lcHJTG5Tscg/giphy.gif',
                'https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif'
            ],
            'kiss': [
                'https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif',
                'https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif',
                'https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif',
                'https://media.giphy.com/media/zkppEMFvRX5FC/giphy.gif',
                'https://media.giphy.com/media/Ka2NAhphLdqXC/giphy.gif'
            ],
            'slap': [
                'https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif',
                'https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif',
                'https://media.giphy.com/media/k1uYB5LvlBZqU/giphy.gif',
                'https://media.giphy.com/media/xUNd9HZq1itMkiK652/giphy.gif',
                'https://media.giphy.com/media/RrLbvyvatbi36/giphy.gif'
            ],
            'hug': [
                'https://media.giphy.com/media/3oEdv6syhM98TVlD2o/giphy.gif',
                'https://media.giphy.com/media/od5HFrsNgWt8k/giphy.gif',
                'https://media.giphy.com/media/l4FGni2G8KvQYX0Kk/giphy.gif',
                'https://media.giphy.com/media/5eyhBKLvYhafu/giphy.gif',
                'https://media.giphy.com/media/143v0Z4767T15e/giphy.gif',
                'https://media.giphy.com/media/JxsF8g9bWZNm/giphy.gif',
                'https://media.giphy.com/media/xUPGcoxveOMcjWjLLa/giphy.gif'
            ]
        }

    def load_marriages(self):
        """Load marriages from JSON file"""
        if os.path.exists(self.marriage_file):
            with open(self.marriage_file, 'r') as f:
                self.bot.marriages = json.load(f)
        else:
            self.bot.marriages = {}

    def save_marriages(self):
        """Save marriages to JSON file"""
        with open(self.marriage_file, 'w') as f:
            json.dump(self.bot.marriages, f)

    @commands.command(name="clown", description="Tag a user and call them a clown")
    async def clown(self, ctx: commands.Context, user: discord.Member):
        """Tag a user and call them a clown"""
        clown_emojis = ["🤡", "🎪", "🎭"]
        embed = discord.Embed(
            title="Clown Alert!",
            description=f"{random.choice(clown_emojis)} {user.mention} is a certified clown! {random.choice(clown_emojis)}",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="meme", description="Get a random meme")
    async def meme(self, ctx: commands.Context):
        """Get a random meme from Meme API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("nsfw", False):  # Skip NSFW memes
                            await ctx.send("❌ Skipped an NSFW meme. Trying again...", delete_after=5)
                            return await self.meme(ctx)  # Recursive call to try again
                        title = data["title"]
                        url = data["url"]
                        embed = discord.Embed(
                            title=f"😂 {title}",
                            description="Enjoy this meme!",
                            color=discord.Color(0xa46ffb)
                        )
                        embed.set_image(url=url)
                        try:
                            from footer import FOOTER_TEXT
                            embed.set_footer(text=FOOTER_TEXT)
                        except ImportError:
                            embed.set_footer(text="Powered by SECULEX | © 2025")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Failed to fetch a meme. Try again later!", delete_after=10)
        except Exception as e:
            await ctx.send(f"❌ An error occurred while fetching a meme: {str(e)}", delete_after=10)

    @commands.command(name="roll", description="Roll a dice with a specified number of sides")
    async def roll(self, ctx: commands.Context, sides: int = 6):
        """Roll a dice with a specified number of sides (default 6)"""
        if sides < 1:
            await ctx.send("❌ Number of sides must be at least 1!", delete_after=10)
            return
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a {result} on a {sides}-sided die!",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="rps", description="Play Rock Paper Scissors against the bot")
    async def rps(self, ctx: commands.Context, choice: str):
        """Play Rock Paper Scissors against the bot"""
        choices = ["rock", "paper", "scissors"]
        choice = choice.lower()
        if choice not in choices:
            await ctx.send("❌ Choose 'rock', 'paper', or 'scissors'!", delete_after=10)
            return
        bot_choice = random.choice(choices)
        embed = discord.Embed(
            title="✂️ Rock Paper Scissors",
            description=f"You chose: **{choice}**\nBot chose: **{bot_choice}**\n\n",
            color=discord.Color(0xa46ffb)
        )
        if choice == bot_choice:
            embed.description += "🤝 It's a tie!"
        elif (choice == "rock" and bot_choice == "scissors") or \
             (choice == "paper" and bot_choice == "rock") or \
             (choice == "scissors" and bot_choice == "paper"):
            embed.description += "🎉 You win!"
        else:
            embed.description += "😢 Bot wins!"
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="quote", description="Get a random inspirational quote")
    async def quote(self, ctx: commands.Context):
        """Get a random inspirational quote from Quotable API with fallback"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.quotable.io/random") as response:
                    if response.status == 200:
                        data = await response.json()
                        quote_text = data["content"]
                        author = data["author"]
                    else:
                        await ctx.send(f"⚠️ Quote API returned status {response.status}. Using a fallback quote.", delete_after=10)
                        quote = random.choice(self.fallback_quotes)
                        quote_text = quote["content"]
                        author = quote["author"]
        except Exception as e:
            await ctx.send(f"⚠️ Network error with quote API: {str(e)}. Using a fallback quote.", delete_after=10)
            quote = random.choice(self.fallback_quotes)
            quote_text = quote["content"]
            author = quote["author"]

        embed = discord.Embed(
            title="💡 Random Quote",
            description=f"\"{quote_text}\" - {author}",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="joke", description="Get a random safe-for-work joke")
    async def joke(self, ctx: commands.Context):
        """Get a random safe-for-work joke from an API"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit") as response:
                if response.status == 200:
                    joke = await response.json()
                    if joke["type"] == "single":
                        joke_text = joke["joke"]
                        description = f"😂 {joke_text}"
                    else:
                        setup = joke["setup"]
                        delivery = joke["delivery"]
                        description = f"😄 **Setup:** {setup}\n**Punchline:** {delivery}"
                    embed = discord.Embed(
                        title="🎤 Here's a Joke for You!",
                        description=description,
                        color=discord.Color(0xa46ffb)
                    )
                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by SECULEX | © 2025")
                    await ctx.send(embed=embed)
                    await ctx.message.delete()
                else:
                    await ctx.send("❌ Failed to fetch a joke. Try again later!", delete_after=10)

    @commands.command(name="dark", description="Get a dark joke (potentially sensitive, hidden in spoilers)")
    async def dark(self, ctx: commands.Context):
        """Get a dark joke from an API, wrapped in spoilers"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://v2.jokeapi.dev/joke/Dark") as response:
                if response.status == 200:
                    joke = await response.json()
                    if joke["type"] == "single":
                        joke_text = joke["joke"]
                        description = f"||{joke_text}||"
                    else:
                        setup = joke["setup"]
                        delivery = joke["delivery"]
                        description = f"**Setup:** ||{setup}||\n**Punchline:** ||{delivery}||"
                    embed = discord.Embed(
                        title="😈 A Dark Joke for You (Click to Reveal)",
                        description=description,
                        color=discord.Color(0xa46ffb)
                    )
                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT + " | Warning: This joke may contain sensitive content.")
                    except ImportError:
                        embed.set_footer(text="Powered by SECULEX | © 2025 | Warning: This joke may contain sensitive content.")
                    await ctx.send(embed=embed)
                    await ctx.message.delete()
                else:
                    await ctx.send("❌ Failed to fetch a dark joke. Try again later!", delete_after=10)

    @commands.command(name="image", description="Fetch an image based on a search query")
    async def image(self, ctx: commands.Context, *, query: str):
        """Fetch a landscape image from Unsplash based on a search query"""
        await ctx.message.delete()
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape"
        }
        headers = {
            "Authorization": "Client-ID F1kSmh4MALfMKjHRxk38dZmPEV0OxsHdzuruBS_Y7to"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.unsplash.com/search/photos", headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["results"]:
                            image_url = data["results"][0]["urls"]["regular"]
                            embed = discord.Embed(
                                title=f"📸 Image for: {query}",
                                description="Here’s a beautiful landscape image from Unsplash!",
                                color=discord.Color(0xa46ffb)
                            )
                            embed.set_image(url=image_url)
                            try:
                                from footer import FOOTER_TEXT
                                embed.set_footer(text=FOOTER_TEXT)
                            except ImportError:
                                embed.set_footer(text="Powered by SECULEX | © 2025")
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send(f"No images found for `{query}`.", delete_after=10)
                    else:
                        await ctx.send(f"❌ Failed to fetch an image. Status code: {response.status}", delete_after=10)
        except Exception as e:
            await ctx.send(f"❌ Error fetching image: {str(e)}", delete_after=10)

    @commands.command(name="roast", description="Roast a user with a dark, unfiltered insult")
    async def roast(self, ctx: commands.Context, user: discord.Member):
        """Roast a user with a dark, unfiltered insult"""
        roasts = [
            f"||{user.mention}, your existence is a mistake even nature regrets!||",
            f"||{user.mention}, you’re so pathetic, even your shadow leaves the room!||",
            f"||{user.mention}, your life’s a tragedy—hope you enjoy the rerun!||",
            f"||{user.mention}, you’re a walking disaster zone—evacuate your soul!||",
            f"||{user.mention}, your brain’s so dead, it’s a zombie convention in there!||"
        ]
        embed = discord.Embed(
            title="🔥 Roast Alert! (Click to Reveal)",
            description=random.choice(roasts),
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT + " | Warning: This roast contains dark content.")
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025 | Warning: This roast contains dark content.")
        await ctx.send(embed=embed)

    @commands.command(name="sad", description="Get a random sad or heartbroken quote")
    async def sad(self, ctx: commands.Context):
        """Get a random sad or heartbroken quote"""
        quote = random.choice(self.sad_quotes)
        quote_text = quote["content"]
        author = quote["author"]
        embed = discord.Embed(
            title="💔 Sad Quote",
            description=f"\"{quote_text}\" - {author}",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="blush")
    async def blush(self, ctx: commands.Context):
        """Show a blushing reaction"""
        gif_url = random.choice(self.action_gifs['blush'])
        embed = discord.Embed(
            description=f"{ctx.author.mention} blushes 😊",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=gif_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="kiss")
    async def kiss(self, ctx: commands.Context, target: discord.Member = None):
        """Kiss another user"""
        if target is None:
            await ctx.send("❌ Please mention a user to kiss! Usage: `!kiss @user`")
            return
        if target == ctx.author:
            await ctx.send("❌ You can't kiss yourself!")
            return
        gif_url = random.choice(self.action_gifs['kiss'])
        embed = discord.Embed(
            description=f"{ctx.author.mention} kisses {target.mention} 💋",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=gif_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="slap")
    async def slap(self, ctx: commands.Context, target: discord.Member = None):
        """Slap another user"""
        if target is None:
            await ctx.send("❌ Please mention a user to slap! Usage: `!slap @user`")
            return
        if target == ctx.author:
            await ctx.send("❌ You can't slap yourself!")
            return
        gif_url = random.choice(self.action_gifs['slap'])
        embed = discord.Embed(
            description=f"{ctx.author.mention} slaps {target.mention} 👋",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=gif_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="cry")
    async def cry(self, ctx: commands.Context):
        """Show a crying reaction"""
        gif_url = random.choice(self.action_gifs['cry'])
        embed = discord.Embed(
            description=f"{ctx.author.mention} cries 😢",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=gif_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="gayrate", description="Rate how gay a user is (joke)")
    async def gayrate(self, ctx: commands.Context, user: discord.Member = None):
        """Rate how gay a user is (joke)"""
        target = user or ctx.author
        rate = random.randint(0, 100)
        embed = discord.Embed(
            title="🌈 Gay Rate",
            description=f"{target.mention} is {rate}% gay! 🏳️‍🌈",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="poll", description="Create a simple yes/no poll")
    async def poll(self, ctx: commands.Context, *, question: str):
        """Create a simple yes/no poll"""
        embed = discord.Embed(
            title="📊 Poll",
            description=f"**Question:** {question}\n\n👍 Yes\n👎 No",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @commands.command(name="dicksize", description="Measure a user's 'dick size' (joke)")
    async def dicksize(self, ctx: commands.Context, user: discord.Member = None):
        """Measure a user's 'dick size' (joke)"""
        target = user or ctx.author
        size = random.randint(1, 20)
        embed = discord.Embed(
            title="📏 Dick Size Measurement",
            description=f"{target.mention}'s dick size is {size} inches! 😂",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="marry", description="Marry another user")
    async def marry(self, ctx: commands.Context, target: discord.Member):
        """Marry another user"""
        if target == ctx.author:
            await ctx.send("❌ You can't marry yourself!")
            return
        user_id = str(ctx.author.id)
        target_id = str(target.id)
        if user_id in self.bot.marriages:
            await ctx.send(f"❌ You're already married to <@{self.bot.marriages[user_id]}>!")
            return
        if target_id in self.bot.marriages.values():
            await ctx.send(f"❌ {target.mention} is already married!")
            return
        self.bot.marriages[user_id] = target_id
        self.save_marriages()
        embed = discord.Embed(
            title="💍 Marriage",
            description=f"{ctx.author.mention} has married {target.mention}! Congratulations! 🎉",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="divorce", description="Divorce your current spouse")
    async def divorce(self, ctx: commands.Context):
        """Divorce your current spouse"""
        user_id = str(ctx.author.id)
        if user_id not in self.bot.marriages:
            await ctx.send("❌ You're not married!")
            return
        spouse_id = self.bot.marriages.pop(user_id)
        self.save_marriages()
        embed = discord.Embed(
            title="💔 Divorce",
            description=f"{ctx.author.mention} has divorced <@{spouse_id}>! 😢",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="wifey", description="Check who your wife is")
    async def wifey(self, ctx: commands.Context):
        """Check who your wife is"""
        user_id = str(ctx.author.id)
        if user_id not in self.bot.marriages:
            await ctx.send("❌ You don't have a wife!")
            return
        spouse_id = self.bot.marriages[user_id]
        embed = discord.Embed(
            title="👰 Your Wifey",
            description=f"Your wife is <@{spouse_id}>! 💕",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="husband", description="Check who your husband is")
    async def husband(self, ctx: commands.Context):
        """Check who your husband is"""
        user_id = str(ctx.author.id)
        if user_id not in self.bot.marriages:
            await ctx.send("❌ You don't have a husband!")
            return
        spouse_id = self.bot.marriages[user_id]
        embed = discord.Embed(
            title="🤵 Your Husband",
            description=f"Your husband is <@{spouse_id}>! 💕",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="marryinfo", description="Check your marriage status")
    async def marryinfo(self, ctx: commands.Context):
        """Check your marriage status"""
        user_id = str(ctx.author.id)
        if user_id not in self.bot.marriages:
            embed = discord.Embed(
                title="💍 Marriage Info",
                description="You're not married! 😢",
                color=discord.Color(0xa46ffb)
            )
        else:
            spouse_id = self.bot.marriages[user_id]
            embed = discord.Embed(
                title="💍 Marriage Info",
                description=f"You're married to <@{spouse_id}>! 💕",
                color=discord.Color(0xa46ffb)
            )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="hug", description="Hug another user")
    async def hug(self, ctx: commands.Context, target: discord.Member = None):
        """Hug another user"""
        if target is None:
            await ctx.send("❌ Please mention a user to hug! Usage: `!hug @user`")
            return
        if target == ctx.author:
            await ctx.send("❌ You can't hug yourself!")
            return
        gif_url = random.choice(self.action_gifs['hug'])
        embed = discord.Embed(
            description=f"{ctx.author.mention} hugs {target.mention} 🤗",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=gif_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="reaction", description="Post a random reaction GIF")
    async def reaction(self, ctx: commands.Context):
        """Post a random reaction GIF"""
        all_gifs = [gif for action in self.action_gifs.values() for gif in action]
        gif_url = random.choice(all_gifs)
        embed = discord.Embed(
            description=f"{ctx.author.mention} reacts!",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=gif_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="drake", description="Generate a Drake meme with custom text using memegen.link")
    async def drake(self, ctx: commands.Context, *, text: str):
        """Generate a Drake meme with custom text (e.g., 'top text, bottom text') using memegen.link"""
        try:
            top_text, bottom_text = text.split(",", 1)  # Changed from "|" to ","
            top_text = top_text.strip().replace(" ", "_")
            bottom_text = bottom_text.strip().replace(" ", "_")
        except ValueError:
            await ctx.send("❌ Please provide text in the format: `!drake top text, bottom text`")
            return

        # Construct the memegen.link URL
        meme_url = f"https://memegen.link/drake/{top_text}/{bottom_text}.jpg"

        # Create and send the embed
        embed = discord.Embed(
            title="🎤 Drake Meme",
            color=discord.Color(0xa46ffb)
        )
        embed.set_image(url=meme_url)
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="toss", description="Flip a coin")
    async def toss(self, ctx: commands.Context):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="🪙 Coin Toss",
            description=f"The coin landed on **{result}**!",
            color=discord.Color(0xa46ffb)
        )
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by SECULEX | © 2025")
        await ctx.send(embed=embed)

    @commands.command(name="funguide", description="View a guide for all fun commands")
    async def funguide(self, ctx: commands.Context):
        """View a guide for all fun commands, including roleplay commands"""
        # First Embed (up to 25 fields)
        embed1 = discord.Embed(
            title="🎉 Fun Command Guide (Part 1)",
            description="Welcome to the Fun section! Below is a guide to fun and roleplay commands (Part 1).",
            color=discord.Color(0xa46ffb)
        )

        embed1.add_field(
            name="🤡 Clown (!clown)",
            value="**Description:** Tag a user and call them a clown with random emojis.\n**Usage:** `!clown <user>`",
            inline=False
        )
        embed1.add_field(
            name="😂 Meme (!meme)",
            value="**Description:** Fetch a random meme using Meme API (NSFW filtered).\n**Usage:** `!meme`",
            inline=False
        )
        embed1.add_field(
            name="🎲 Roll (!roll)",
            value="**Description:** Roll a dice with a specified number of sides (default 6).\n**Usage:** `!roll [sides]`",
            inline=False
        )
        embed1.add_field(
            name="✂️ Rock Paper Scissors (!rps)",
            value="**Description:** Play Rock Paper Scissors against the bot.\n**Usage:** `!rps <rock/paper/scissors>`",
            inline=False
        )
        embed1.add_field(
            name="💡 Quote (!quote)",
            value="**Description:** Get a random inspirational quote from Quotable API (with fallback).\n**Usage:** `!quote`",
            inline=False
        )
        embed1.add_field(
            name="🎤 Joke (!joke)",
            value="**Description:** Get a random safe-for-work joke from JokeAPI.\n**Usage:** `!joke`",
            inline=False
        )
        embed1.add_field(
            name="😈 Dark Joke (!dark)",
            value="**Description:** Get a dark joke (potentially sensitive, hidden in spoilers).\n**Usage:** `!dark`",
            inline=False
        )
        embed1.add_field(
            name="📸 Image (!image)",
            value="**Description:** Fetch a landscape image from Unsplash based on a search query.\n**Usage:** `!image <query>`\n**Example:** `!image sunset`",
            inline=False
        )
        embed1.add_field(
            name="🔥 Roast (!roast)",
            value="**Description:** Roast a user with a dark, unfiltered insult (hidden in spoilers).\n**Usage:** `!roast <user>`",
            inline=False
        )
        embed1.add_field(
            name="💔 Sad Quote (!sad)",
            value="**Description:** Get a random sad or heartbroken quote.\n**Usage:** `!sad`",
            inline=False
        )
        embed1.add_field(
            name="😊 Blush (!blush)",
            value="**Description:** Show a blushing reaction with a random GIF.\n**Usage:** `!blush`",
            inline=False
        )
        embed1.add_field(
            name="💋 Kiss (!kiss)",
            value="**Description:** Kiss another user with a random GIF.\n**Usage:** `!kiss <user>`",
            inline=False
        )
        embed1.add_field(
            name="👋 Slap (!slap)",
            value="**Description:** Slap another user with a random GIF.\n**Usage:** `!slap <user>`",
            inline=False
        )
        embed1.add_field(
            name="😢 Cry (!cry)",
            value="**Description:** Show a crying reaction with a random GIF.\n**Usage:** `!cry`",
            inline=False
        )
        embed1.add_field(
            name="🌈 Gay Rate (!gayrate)",
            value="**Description:** Rate how gay a user is (joke).\n**Usage:** `!gayrate [user]`",
            inline=False
        )
        embed1.add_field(
            name="📊 Poll (!poll)",
            value="**Description:** Create a simple yes/no poll.\n**Usage:** `!poll <question>`\n**Example:** `!poll Are you having fun?`",
            inline=False
        )
        embed1.add_field(
            name="📏 Dick Size (!dicksize)",
            value="**Description:** Measure a user's 'dick size' (joke).\n**Usage:** `!dicksize [user]`",
            inline=False
        )
        embed1.add_field(
            name="💍 Marry (!marry)",
            value="**Description:** Marry another user (persistent across restarts).\n**Usage:** `!marry <user>`",
            inline=False
        )
        embed1.add_field(
            name="💔 Divorce (!divorce)",
            value="**Description:** Divorce your current spouse.\n**Usage:** `!divorce`",
            inline=False
        )
        embed1.add_field(
            name="👰 Wifey (!wifey)",
            value="**Description:** Check who your wife is.\n**Usage:** `!wifey`",
            inline=False
        )
        embed1.add_field(
            name="🤵 Husband (!husband)",
            value="**Description:** Check who your husband is.\n**Usage:** `!husband`",
            inline=False
        )
        embed1.add_field(
            name="💍 Marriage Info (!marryinfo)",
            value="**Description:** Check your marriage status.\n**Usage:** `!marryinfo`",
            inline=False
        )

        # Second Embed (remaining fields)
        embed2 = discord.Embed(
            title="🎉 Fun Command Guide (Part 2)",
            description="Continuation of the Fun Command Guide (Part 2).",
            color=discord.Color(0xa46ffb)
        )

        embed2.add_field(
            name="🤗 Hug (!hug)",
            value="**Description:** Hug another user with a random GIF.\n**Usage:** `!hug <user>`",
            inline=False
        )
        embed2.add_field(
            name="🎬 Reaction (!reaction)",
            value="**Description:** Post a random reaction GIF.\n**Usage:** `!reaction`",
            inline=False
        )
        embed2.add_field(
            name="🎤 Drake (!drake)",
            value="**Description:** Generate a Drake meme with custom text.\n**Usage:** `!drake top text, bottom text`\n**Example:** `!drake I like this, I hate that`",
            inline=False
        )
        embed2.add_field(
            name="🪙 Toss (!toss)",
            value="**Description:** Flip a coin.\n**Usage:** `!toss`",
            inline=False
        )

        # Set footers
        try:
            from footer import FOOTER_TEXT
            embed1.set_footer(text=FOOTER_TEXT + " | Part 1 of 2")
            embed2.set_footer(text=FOOTER_TEXT + " | Part 2 of 2")
        except ImportError:
            embed1.set_footer(text="Powered by SECULEX | © 2025 | Part 1 of 2")
            embed2.set_footer(text="Powered by SECULEX | © 2025 | Part 2 of 2")

        # Send both embeds
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)

    @commands.command(name="funcmd", description="List all fun commands and their descriptions")
    async def funcmd(self, ctx: commands.Context):
        """List all fun commands, including roleplay commands, and their descriptions"""
        embed = discord.Embed(
            title="🎮 Fun Commands",
            description="Below is a list of all fun and roleplay commands and what they do. Use `!funguide` for detailed guides.",
            color=discord.Color(0xa46ffb)
        )

        # Split Fun Commands into multiple fields to stay under 1024 characters
        embed.add_field(
            name="Fun Commands (Part 1)",
            value=(
                "`!clown <user>` - Tag a user and call them a clown.\n"
                "`!meme` - Get a random meme.\n"
                "`!roll [sides]` - Roll a dice (default 6 sides).\n"
                "`!rps <rock/paper/scissors>` - Play Rock Paper Scissors.\n"
                "`!quote` - Get a random inspirational quote.\n"
                "`!joke` - Get a random safe-for-work joke.\n"
                "`!dark` - Get a dark joke (in spoilers).\n"
                "`!image <query>` - Fetch an image from Unsplash.\n"
                "`!roast <user>` - Roast a user with a dark insult.\n"
                "`!sad` - Get a random sad quote.\n"
                "`!blush` - Show a blushing reaction GIF.\n"
                "`!kiss <user>` - Kiss another user with a GIF.\n"
                "`!slap <user>` - Slap another user with a GIF."
            ),
            inline=False
        )

        embed.add_field(
            name="Fun Commands (Part 2)",
            value=(
                "`!cry` - Show a crying reaction GIF.\n"
                "`!gayrate [user]` - Rate how gay a user is (joke).\n"
                "`!poll <question>` - Create a yes/no poll.\n"
                "`!dicksize [user]` - Measure 'dick size' (joke).\n"
                "`!marry <user>` - Marry another user (persistent).\n"
                "`!divorce` - Divorce your current spouse.\n"
                "`!wifey` - Check who your wife is.\n"
                "`!husband` - Check who your husband is.\n"
                "`!marryinfo` - Check your marriage status.\n"
                "`!hug <user>` - Hug another user with a GIF.\n"
                "`!reaction` - Post a random reaction GIF.\n"
                "`!drake <top text>, <bottom text>` - Generate a Drake meme.\n"
                "`!toss` - Flip a coin."
            ),
            inline=False
        )

        embed.add_field(
            name="Information Commands",
            value=(
                "`!funguide` - View a detailed guide for fun commands.\n"
                "`!funcmd` - List all fun commands (this command)."
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
    await bot.add_cog(Fun(bot))