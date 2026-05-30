import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
import logging

class HelpView(View):
    def __init__(self, bot: commands.Bot, categories: dict):
        super().__init__(timeout=60)
        self.bot = bot
        self.categories = categories

        # Define the module groups in the desired order
        moderation_cogs = ["moderation", "admin", "nuke", "purge", "verification", "tickets"]
        utility_cogs = ["avatar", "botinfo", "info", "utilities", "webtools", "servermanagement", "rolemanagement", "calculator", "invoice", "messagetools", "reminder", "timer", "todo", "afk"]
        entertainment_cogs = ["fun", "games", "casino", "autoresponder", "socialmedia", "giveaway"]

        # Combine the categories in the correct order
        ordered_categories = []
        for cog in moderation_cogs + utility_cogs + entertainment_cogs:
            if cog in categories:
                ordered_categories.append(cog)

        # Split categories into three dropdowns based on the module groups
        # First dropdown: Moderation Modules
        select1 = Select(
            placeholder="Moderation Modules...",
            options=[
                discord.SelectOption(
                    label=category.replace("_", " ").title(),
                    description=f"{category.replace('_', ' ').title()} commands",
                    value=category,
                    emoji=self.get_emoji(category)
                ) for category in moderation_cogs if category in categories
            ]
        )
        select1.callback = self.select_callback
        self.add_item(select1)

        # Second dropdown: Utility Modules
        select2 = Select(
            placeholder="Utility Modules...",
            options=[
                discord.SelectOption(
                    label=category.replace("_", " ").title(),
                    description=f"{category.replace('_', ' ').title()} commands",
                    value=category,
                    emoji=self.get_emoji(category)
                ) for category in utility_cogs if category in categories
            ]
        )
        select2.callback = self.select_callback
        self.add_item(select2)

        # Third dropdown: Entertainment Modules
        select3 = Select(
            placeholder="Entertainment Modules...",
            options=[
                discord.SelectOption(
                    label=category.replace("_", " ").title(),
                    description=f"{category.replace('_', ' ').title()} commands",
                    value=category,
                    emoji=self.get_emoji(category)
                ) for category in entertainment_cogs if category in categories
            ]
        )
        select3.callback = self.select_callback
        self.add_item(select3)

    def get_emoji(self, category: str) -> str:
        """Map categories to emojis."""
        emoji_map = {
            "moderation": "<:shieldc:1352473244070055936>",
            "admin": "<:shieldc:1352473244070055936>",
            "nuke": "<:shieldc:1352473244070055936>",
            "purge": "<:shieldc:1352473244070055936>",
            "verification": "<:shieldc:1352473244070055936>",
            "tickets": "<:shieldc:1352473244070055936>",
            "general": "<:general:1352478236604371037>",
            "about": "<:aboutowner:1352478351696068702>",
            "afk": "<:AFK:1352478500778676246>",
            "avatar": "<:avatar:1352478621931012128>",
            "botinfo": "<:bot:1352478755100164209>",
            "info": "<:info:1352478856799584277>",
            "utilities": "<:utilities:1352478960469934123>",
            "webtools": "<a:website:1352479260371189810>",
            "welcome": "<a:welcome:1352479080083226655>",
            "servermanagement": "<:management:1352473033704472577>",
            "rolemanagement": "<:management:1352473033704472577>",
            "fun": "<:gamepad:1352472876141379678>",
            "games": "<:gamepad:1352472876141379678>",
            "casino": "<:gamepad:1352472876141379678>",
            "autoresponder": "<:Rombot:1352472681471017090>",
            "extra": "<:starms:1352472514449768541>",
            "calculator": "<:calculator:1352472384439058463>",
            "invoice": "<:bu_invoice:1352472241308172340>",
            "messagetools": "<:Message:1352472124719239200>",
            "reminder": "<:reminder:1352471972130459781>",
            "roles": "<:roles:1352471860524089426>",
            "timer": "<:timery:1352471682157383741>",
            "todo": "<:list:1352471515572211763>",
            "giveaway": "<a:giveaway:1352471407245791233>",
            "socialmedia": "<a:SocialMedia:1352471172733997210>",
        }
        return emoji_map.get(category.lower(), "❓")

    async def select_callback(self, interaction: discord.Interaction):
        category = interaction.data.get("values", [None])[0]
        if not category:
            await interaction.response.send_message("❌ No category selected.", ephemeral=True)
            return

        embed = discord.Embed(color=discord.Color.from_rgb(164, 111, 251))  # #a46ffb
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        if category in self.categories:
            embed.title = f"{self.get_emoji(category)} {category.replace('_', ' ').title()} Modules"
            # Display commands with their descriptions
            command_list = []
            for cmd_name, cmd_desc in self.categories[category]:
                prefix = "!" if cmd_name in [cmd.name for cmd in self.bot.commands] else "/"
                if cmd_desc and cmd_desc != "No description available":
                    command_list.append(f"`{prefix}{cmd_name}` - {cmd_desc}")
                else:
                    command_list.append(f"`{prefix}{cmd_name}`")
            embed.description = f"**Commands:**\n" + "\n".join(command_list) if command_list else "No commands in this category."
        else:
            embed.title = "❌ Error"
            embed.description = "Invalid category selected. Please try again."

        await interaction.response.send_message(embed=embed, ephemeral=True)

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def on_ready(self):
        """Print all commands when the bot starts."""
        print("Bot is ready! Listing all commands:")
        categories = self.get_all_commands_by_category()
        for category, commands in sorted(categories.items()):
            print(f"\nCategory: {category.replace('_', ' ').title()}")
            for cmd_name, cmd_desc in sorted(commands, key=lambda x: x[0]):
                print(f"  - {cmd_name}: {cmd_desc if cmd_desc != 'No description available' else 'No description'}")

    def get_all_commands_by_category(self):
        """Dynamically fetch all commands and group them by cog/category."""
        categories = {}

        # Updated command descriptions based on the output
        command_descriptions = {
            # Admin commands
            "pvt": "Set a channel to private",
            "pvtallow": "Allow a user to access a private channel",
            "pvtremove": "Remove a user from a private channel",
            # Afk commands
            "afk": "Set your AFK status",
            # Autoresponder commands
            "ar": "Add an auto response for this server",
            "dr": "Delete an auto response from this server",
            "lr": "List all auto responses for this server",
            # Avatar commands
            "avatar": "Show a user's avatar",
            "server": "View server icon and banner",
            # Botinfo commands
            "botinfo": "Show information about the bot",
            # Calculator commands
            "calc": "Calculate a mathematical expression",
            # Casino commands
            "addcoins": "[Admin] Add coins to a user",
            "balance": "Check your coin balance",
            "blackjack": "Play Blackjack against the bot",
            "casinocmd": "List all casino commands and their descriptions",
            "casinoguide": "View a guide for all casino games",
            "coinflip": "Play Coinflip, guess heads or tails",
            "crash": "Play Crash, cash out before it crashes",
            "daily": "Claim a daily coin reward",
            "leaderboard": "View the top balances and wins",
            "mines": "Play Mines, avoid mines to win",
            "monthly": "Claim a monthly coin reward",
            "plinko": "Play Plinko with a bet",
            "roulette": "Play Roulette, bet on numbers or colors",
            "sendcoins": "Send coins to another user",
            "slots": "Play the slot machine",
            "weekly": "Claim a weekly coin reward",
            # Fun commands
            "blush": "Show a blushing reaction GIF",
            "clown": "Call a user a clown",
            "cry": "Show a crying reaction GIF",
            "dark": "Get a dark joke (in spoilers)",
            "dicksize": "Measure 'dick size' (joke)",
            "divorce": "Divorce your current spouse",
            "drake": "Generate a Drake meme",
            "funcmd": "List all fun commands and their descriptions",
            "funguide": "View a guide for all fun commands",
            "gayrate": "Rate how gay a user is (joke)",
            "hug": "Hug a user with a GIF",
            "husband": "Check who your husband is",
            "image": "Fetch an image from Unsplash",
            "joke": "Get a safe-for-work joke",
            "kiss": "Kiss a user with a GIF",
            "marry": "Marry another user",
            "marryinfo": "Check your marriage status",
            "meme": "Get a random meme",
            "poll": "Create a yes/no poll",
            "quote": "Get an inspirational quote",
            "reaction": "Post a random reaction GIF",
            "roast": "Roast a user with an insult",
            "roll": "Roll a dice (default 6 sides)",
            "rps": "Play Rock Paper Scissors",
            "sad": "Get a random sad quote",
            "slap": "Slap a user with a GIF",
            "toss": "Flip a coin",
            "wifey": "Check who your wife is",
            # Games commands
            "8ball": "Ask the Magic 8-Ball a question",
            "connect4": "Start a Connect Four game",
            "gamecmd": "Show the list of game commands",
            "gamesguide": "Show rules for all games",
            "guess": "Start a number guessing game",
            "guessanswer": "Submit an answer for trivia",
            "guessnumber": "Submit a guess for the number game",
            "hangman": "Start a Hangman game",
            "reactiongame": "Start a reaction speed game",
            "rockpaperscissors": "Start a Rock Paper Scissors game",
            "rpschoose": "Make a choice in Rock Paper Scissors",
            "scramble": "Start a word scramble game",
            "ship": "Ship two users together",
            "tictactoe": "Start a Tic Tac Toe game",
            "trivia": "Start a trivia game",
            "unscramble": "Submit an answer for word scramble",
            "wyr": "Play Would You Rather",
            # Giveaway commands
            "gstart": "Start a giveaway",
            # Help commands
            "help": "Show all available commands or commands for a specific category",
            # Info commands
            "invite": "Get Seculex bot and server invite links",
            "membercount": "Shows server member statistics",
            "role_info": "Get information about a role",
            "server_info": "Get information about the server",
            "user_info": "Get information about a user",
            # Invoice commands
            "cancelinvoice": "Cancel an invoice",
            "invoice": "Create a new invoice",
            "markpaid": "Mark an invoice as paid",
            "pendinginvoices": "List all pending invoices",
            "set_dm_message": "Set a custom DM message for invoice actions",
            # Messagetools commands
            "snipe": "Snipe the last deleted message",
            # Moderation commands
            "autorole": "Manage autoroles for new members",
            "ban": "Ban a user from the server",
            "changeserverbanner": "Change the server's banner",
            "changeserverpfp": "Change the server's profile picture",
            "clearwarnings": "Clear all warnings for a member",
            "clone": "Clone a text or voice channel",
            "deletechannel": "Delete a specified channel",
            "embed": "Create a custom embed with a modal interface",
            "firstmsg": "Get the first message in a channel",
            "hide": "Hide a channel from @everyone",
            "invert_roles": "Invert the order of all manageable roles",
            "kick": "Kick a user from the server",
            "lock": "Lock the current channel",
            "move_role": "Move a role to a specified position (1 is topmost)",
            "mute": "Mute a user",
            "nick": "Change a user's nickname",
            "roleicon": "Change a role's icon",
            "say": "Send a message to a specified channel as the bot",
            "slowmode": "Set slowmode for the current channel",
            "steal": "Steal an emoji",
            "trole": "Assign a temporary role to a member",
            "unban": "Unban a member",
            "unhide": "Unhide a channel for @everyone",
            "unlock": "Unlock the current channel",
            "unmute": "Unmute a user",
            "warn": "Warn a user",
            "warnings": "View warnings for a member",
            # Nuke commands
            "nuke": "Clear all messages in a channel",
            # Purge commands
            "purge": "Delete a specified number of messages",
            "purge_after": "Delete messages after a specific message ID",
            "purge_user": "Delete messages from a specific user",
            # Reminder commands
            "remind": "Set a reminder",
            "remindme": "Set a reminder for yourself",
            # Rolemanagement commands
            "addrole": "Add a role to a user",
            "createrole": "Create a new role",
            "deleterole": "Delete a role",
            "listroles": "Display all server roles",
            "removerole": "Remove a role from a user",
            # Servermanagement commands
            "farewell": "View the current farewell message settings",
            "farewell_enable": "Enable farewell messages in a server channel",
            "greet": "View the current welcome message settings",
            "greet_enable": "Enable welcome messages in a server channel",
            "invites": "Check invite statistics for a user or top inviters",
            "settings": "View or manage server settings",
            "stopjoin": "Stop join messages for the server",
            # Socialmedia commands
            "instagram_repost": "Reposts an Instagram post or reel",
            "instagram_user": "Fetches details about an Instagram user",
            "pinterest": "Fetch Pinterest content",
            "youtube": "Searches for a YouTube video based on your query",
            # Tickets commands
            "add": "Add a user to a ticket",
            "blacklist": "Blacklist a user or role from creating tickets",
            "blacklist_remove": "Remove a user or role from the blacklist",
            "close": "Close a ticket",
            "delete": "Delete a ticket channel",
            "jumptotop": "Jump to the top of the ticket",
            "open": "Re-open a closed ticket",
            "remove": "Remove a user from the ticket",
            "rename": "Rename the current ticket",
            "reopen": "Reopen a closed ticket",
            "show": "Show blacklist reason for a user",
            "ticket_setup": "Setup or customize the ticket system",
            "transcript": "Create a transcript of the ticket",
            # Timer commands
            "timer": "Set a timer",
            # Todo commands
            "assign": "Assign a task to a user with a deadline",
            "task": "Manage your personal to-do list",
            # Utilities commands
            "lookup": "Look up a domain or IP",
            "timestamp": "Shows the current UTC timestamp",
            "timezone": "View your current timezone settings",
            "timezone_set": "Set your preferred timezone",
            "translate": "Translate text to a specified language",
            # Verification commands
            "verify_setup": "Setup the verification system",
            # Webtools commands
            "screenshot": "Take a screenshot of a website",
            "urban": "Search for a word on Urban Dictionary",
        }

        # Fetch traditional commands (from cogs)
        for command in self.bot.commands:
            cog_name = command.cog_name.lower() if command.cog_name else "other"
            if cog_name not in categories:
                categories[cog_name] = []
            # Add command with its description
            description = command_descriptions.get(command.name, command.description or "No description available")
            categories[cog_name].append((command.name, description))
            # Include aliases
            if command.aliases:
                for alias in command.aliases:
                    description = command_descriptions.get(alias, f"Alias for {command.name}")
                    categories[cog_name].append((alias, description))

        # Fetch slash commands
        for cmd in self.bot.tree.get_commands():
            cog_name = "other"
            if hasattr(cmd, "binding") and cmd.binding:
                cog_name = cmd.binding.__class__.__name__.lower()
            elif hasattr(cmd, "cog") and cmd.cog:
                cog_name = cmd.cog.__class__.__name__.lower()
            if cog_name not in categories:
                categories[cog_name] = []
            description = command_descriptions.get(cmd.name, cmd.description or "No description available")
            categories[cog_name].append((cmd.name, description))

        # Remove duplicates and sort
        for cog in categories:
            categories[cog] = sorted(set(categories[cog]), key=lambda x: x[0])

        return categories

    @commands.hybrid_command(name="help", description="Show all available commands or commands for a specific category")
    @app_commands.describe(category="The category to show commands for (e.g., moderation, fun, casino)")
    async def help_command(self, ctx: commands.Context, category: str = None):
        # Get all commands grouped by category
        categories = self.get_all_commands_by_category()

        # If a category is provided, show commands for that category
        if category:
            category = category.lower()
            # Map common aliases or variations to the correct category
            category_aliases = {
                "auto_responder": "autoresponder",
                "message_tools": "messagetools",
                "social_media": "socialmedia",
                "web_tools": "webtools",
                "roles": "rolemanagement",
            }
            category = category_aliases.get(category, category)

            if category in categories:
                embed = discord.Embed(
                    title=f"{HelpView.get_emoji(None, category)} {category.replace('_', ' ').title()} Modules",
                    color=discord.Color.from_rgb(164, 111, 251)  # #a46ffb
                )
                # Display commands with their descriptions
                command_list = []
                for cmd_name, cmd_desc in categories[category]:
                    prefix = "!" if cmd_name in [cmd.name for cmd in self.bot.commands] else "/"
                    if cmd_desc and cmd_desc != "No description available":
                        command_list.append(f"`{prefix}{cmd_name}` - {cmd_desc}")
                    else:
                        command_list.append(f"`{prefix}{cmd_name}`")
                embed.description = f"**Commands:**\n" + "\n".join(command_list) if command_list else "No commands in this category."
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Category '{category}' not found. Use `!help` to see all available categories.",
                    color=discord.Color.from_rgb(164, 111, 251)
                )

            # Set footer dynamically
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1310618077875929240/1352353836257247362/seculex.png?ex=67ddb528&is=67dc63a8&hm=3f2e029682a64c20bdd51e95f0884f438925bc58f27baeb65ea4fc497e3f38e1&=&format=webp&quality=lossless&width=419&height=438")

            await ctx.send(embed=embed)
            return

        # If no category is provided, show the default help menu with dropdowns
        # Calculate total command count
        total_commands = sum(len(commands) for commands in categories.values())

        # Create the main help embed
        embed = discord.Embed(
            title="<:0_:1352320678325391453><:1_:1352320700710649939><:2_:1352320718213480650><:3_:1352320739910483999><:4_:1352320757383827498><:5_:1352320775709003867> Help Menu",
            description=(
                "<a:rigmt_arrow:1352469955035267206>  Hey, my global prefix is `!` and `/`\n"
                "<a:rigmt_arrow:1352469955035267206>  Use `!help <category>` to view commands for a specific category (e.g., `!help moderation`)\n"
                "<a:rigmt_arrow:1352469955035267206>  Select from the dropdown to view my commands\n"
                "<a:rigmt_arrow:1352469955035267206>  [INVITE Me](https://discord.com/oauth2/authorize?client_id=1338408460555128925&permissions=8&integration_type=0&scope=applications.commands+bot)\n"
                f"<a:rigmt_arrow:1352469955035267206>  **Total Commands:** {total_commands}"
            ),
            color=discord.Color.from_rgb(164, 111, 251)  # #a46ffb
        )

        # Define three module groups
        moderation_cogs = ["moderation", "admin", "nuke", "purge", "verification", "tickets"]
        utility_cogs = ["avatar", "botinfo", "info", "utilities", "webtools", "servermanagement", "rolemanagement", "calculator", "invoice", "messagetools", "reminder", "timer", "todo", "afk"]
        entertainment_cogs = ["fun", "games", "casino", "autoresponder", "socialmedia", "giveaway"]

        # Add categories as fields
        moderation_modules = "\n".join([f"• {cog.replace('_', ' ').title()}" for cog in moderation_cogs if cog in categories])
        embed.add_field(
            name="<:9145shield:1352318692075245709> Moderation Modules",
            value=moderation_modules if moderation_modules else "• No modules available",
            inline=False
        )

        utility_modules = "\n".join([f"• {cog.replace('_', ' ').title()}" for cog in utility_cogs if cog in categories])
        embed.add_field(
            name="<:AceChecklist:1352319385955602636> Utility Modules",
            value=utility_modules if utility_modules else "• No modules available",
            inline=False
        )

        entertainment_modules = "\n".join([f"• {cog.replace('_', ' ').title()}" for cog in entertainment_cogs if cog in categories])
        embed.add_field(
            name="<a:GamepadCat:1352469168745873411> Entertainment Modules",
            value=entertainment_modules if entertainment_modules else "• No modules available",
            inline=False
        )

        # Set footer dynamically
        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1310618077875929240/1352353836257247362/seculex.png?ex=67ddb528&is=67dc63a8&hm=3f2e029682a64c20bdd51e95f0884f438925bc58f27baeb65ea4fc497e3f38e1&=&format=webp&quality=lossless&width=419&height=438")

        # Send the embed with the dropdown view, visible to everyone
        await ctx.send(embed=embed, view=HelpView(self.bot, categories))

async def setup(bot: commands.Bot):
    help_cog = Help(bot)
    await bot.add_cog(help_cog)
    # Register the on_ready event
    bot.add_listener(help_cog.on_ready, "on_ready")