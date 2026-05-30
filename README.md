<div align="center">

# 🤖 Seculex Bot

**A powerful, feature-rich Discord bot built for modern servers.**

[![Discord](https://img.shields.io/badge/Support_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/F5s2XDmKZx)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Made by Ayush • Powered by Seculex*

</div>

---

## ✨ Features

- 🎰 **Casino & Economy** — Slots, blackjack, roulette, crash, mines, plinko, and more with a full coin economy
- 🎮 **Games** — Tic-tac-toe, connect four, hangman, trivia, word scramble, and more
- 🎉 **Fun** — Memes, GIFs, marriage system, polls, roasts, and reaction commands
- 🛡️ **Moderation** — Ban, kick, mute, warn, purge, nuke, and role management
- 🎫 **Tickets** — Full ticket system with transcripts, blacklisting, and custom panels
- 📋 **Invoices** — Create and track payment invoices with DM notifications
- 🔔 **Reminders & Timers** — Personal reminders and countdown timers
- ✅ **Verification** — Role-gated verification system
- 👋 **Welcome/Farewell** — Custom welcome and farewell messages with invite tracking
- 🌐 **Web Tools** — Website screenshots, Urban Dictionary, domain/IP lookup, translation
- 📸 **Social Media** — Instagram repost support
- ⚙️ **Auto Responder** — Custom trigger/response pairs per server

---

## 🚀 Setup

### Prerequisites
- Python 3.11+
- A Discord bot token — [Discord Developer Portal](https://discord.com/developers/applications)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/seculex-bot.git
cd seculex-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env   # then fill in your values
```

### Environment Variables

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_bot_token_here
APPLICATION_ID=your_application_id_here
```

### Running the Bot

```bash
python main.py
```

---

## 📖 Commands

> `<required>` &nbsp;|&nbsp; `[optional]`
>
> Slash commands use `/` &nbsp;•&nbsp; Prefix commands use `!`

---

### 🎰 Casino & Economy

| Command | Description |
|---------|-------------|
| `!balance` | Check your current coin balance |
| `!daily` | Claim daily reward (100–200 coins, 24h cooldown) |
| `!weekly` | Claim weekly reward (500–1000 coins, 7d cooldown) |
| `!monthly` | Claim monthly reward (2000–5000 coins, 30d cooldown) |
| `!leaderboard` | View top balances and wins |
| `!slots <bet>` | Play the slot machine |
| `!blackjack <bet>` | Play blackjack against the dealer |
| `!coinflip <bet> <heads/tails>` | Flip a coin and bet on the outcome |
| `!roulette <bet> <type> <choice>` | Bet on numbers, colors, or ranges |
| `!crash <bet> [multiplier]` | Cash out before the multiplier crashes |
| `!mines <bet> [mines] [difficulty]` | Avoid the mines to multiply your bet |
| `!plinko <bet>` | Drop a ball through the pegged board |
| `!sendcoins <user> <amount>` | Send coins to another user |
| `!addcoins <user> <amount>` | *(Admin)* Add coins to a user's balance |
| `!casinoguide` | Detailed guide for all casino games |
| `!casinocmd` | List all casino commands |

---

### 🎮 Games

| Command | Description |
|---------|-------------|
| `!tictactoe <opponent>` | Start a Tic Tac Toe match |
| `!connect4 <opponent>` | Start a Connect Four match |
| `!hangman` | Start a game of Hangman |
| `!rockpaperscissors <opponent>` | Challenge someone to RPS |
| `!rpschoose <rock/paper/scissors>` | Make your RPS choice |
| `!trivia` | Start a trivia question |
| `!guessanswer <answer>` | Submit your trivia answer |
| `!scramble` | Start a word scramble game |
| `!unscramble <answer>` | Submit your unscramble answer |
| `!guess` | Start number guessing |
| `!guessnumber <number>` | Submit your number guess |
| `!reactiongame` | Test your reaction speed |
| `!ship <user1> <user2>` | Check the compatibility of two users |
| `!wyr` | Play Would You Rather? |
| `!8ball <question>` | Ask the Magic 8-Ball |
| `!gamesguide` | View rules for all games |
| `!gamecmd` | List all game commands |

---

### 🎉 Fun

| Command | Description |
|---------|-------------|
| `!meme` | Get a random meme |
| `!joke` | Get a random SFW joke |
| `!dark` | Get a dark joke (spoiler-tagged) |
| `!quote` | Get a random inspirational quote |
| `!sad` | Get a random sad quote |
| `!roast <user>` | Roast a user with a sharp insult |
| `!clown <user>` | Call someone a clown |
| `!gayrate [user]` | Rate how gay a user is (joke) |
| `!dicksize [user]` | A completely scientific measurement (joke) |
| `!roll [sides]` | Roll a dice (default 6 sides) |
| `!rps <rock/paper/scissors>` | Play Rock Paper Scissors against the bot |
| `!toss` | Flip a coin |
| `!poll <question>` | Create a yes/no poll |
| `!image <query>` | Fetch an image from Unsplash |
| `!drake <top>, <bottom>` | Generate a Drake meme |
| `!blush` | Post a blushing reaction GIF |
| `!cry` | Post a crying reaction GIF |
| `!hug <user>` | Hug another user |
| `!kiss <user>` | Kiss another user |
| `!slap <user>` | Slap another user |
| `!reaction` | Post a random reaction GIF |
| `!marry <user>` | Propose to a user |
| `!divorce` | Divorce your current spouse |
| `!wifey` | Check who your wife is |
| `!husband` | Check who your husband is |
| `!marryinfo` | View your full marriage status |
| `!funguide` | Detailed guide for fun commands |
| `!funcmd` | List all fun commands |

---

### 🛡️ Moderation

| Command | Description |
|---------|-------------|
| `/ban <member> [reason]` | Ban a member from the server |
| `/kick <member> [reason]` | Kick a member from the server |
| `/mute <member> <duration> [reason]` | Timeout a member |
| `/unmute <member>` | Remove a member's timeout |
| `/warn <member> [reason]` | Warn a member |
| `/purge <amount>` | Delete a number of messages |
| `/purge_after <message_id>` | Delete all messages after a specific message |
| `/purge_user <user> [amount]` | Delete messages from a specific user |
| `/nuke` | Recreate the current channel (wipes all messages) |
| `/snipe` | Show the last deleted message in this channel |

---

### 🎫 Tickets

| Command | Description |
|---------|-------------|
| `/ticket_setup` | Set up or customize the ticket panel |
| `/open` | Re-open a closed ticket |
| `/close` | Close a ticket |
| `/delete` | Delete a ticket channel |
| `/rename` | Rename the current ticket |
| `/add <user>` | Add a user to a ticket |
| `/remove <user>` | Remove a user from a ticket |
| `/transcript` | Generate an HTML transcript of the ticket |
| `/blacklist` | Blacklist a user or role from creating tickets |
| `/blacklist_remove` | Remove a user or role from the blacklist |

---

### 📋 Invoices

| Command | Description |
|---------|-------------|
| `/invoice <user> <service> <amount> <payment_method>` | Create a new invoice |
| `/markpaid <invoice_id>` | Mark an invoice as paid |
| `/cancelinvoice <invoice_id>` | Cancel an invoice |
| `/pendinginvoices` | List all pending invoices |
| `/set_dm_message <action> <message>` | Set a custom DM message for invoice actions |

---

### 🔔 Reminders & Timers

| Command | Description |
|---------|-------------|
| `/remindme <time> <message>` | Set a personal reminder (e.g. `1h`, `30m`, `1d`) |
| `/remind <user> [message]` | Send a reminder to another user |
| `/timer <duration>` | Start a public countdown timer |

---

### ✅ Tasks & Todo

| Command | Description |
|---------|-------------|
| `/task` | Manage your personal to-do list |
| `/assign <user> <task> <deadline>` | Assign a task to a user with a deadline |

---

### 👋 Welcome & Farewell

| Command | Description |
|---------|-------------|
| `/greet_enable <channel>` | Enable welcome messages in a channel |
| `/farewell_enable <channel>` | Enable farewell messages in a channel |
| `/greet` | View current welcome message settings |
| `/farewell` | View current farewell message settings |
| `/invites [member]` | Check invite statistics for a user or the server |
| `!stopjoin <duration>` | Pause join messages temporarily |

---

### ⚙️ Server Settings & Auto Responder

| Command | Description |
|---------|-------------|
| `/settings` | View or manage server settings |
| `/ar <trigger> <response>` | Add an auto-response trigger |
| `/dr <trigger>` | Delete an auto-response trigger |
| `/lr` | List all auto-responses for this server |

---

### 🔐 Roles & Verification

| Command | Description |
|---------|-------------|
| `!addrole <member> <role>` | Assign a role to a member |
| `!removerole <member> <role>` | Remove a role from a member |
| `!createrole <name> [color]` | Create a new role |
| `!deleterole <role>` | Delete a role |
| `!listroles` | Display all server roles |
| `!verify_setup <role> <channel> [message]` | Set up the verification system |

---

### ℹ️ Info & Utilities

| Command | Description |
|---------|-------------|
| `/about` | About the bot |
| `/botinfo` | Bot statistics and analytics |
| `/server_info` | Information about the server |
| `/user_info [user]` | Information about a user |
| `/role_info <role>` | Information about a role |
| `/membercount` | Server member statistics |
| `/invite` | Get bot and server invite links |
| `/avatar [user]` | View a user's avatar and banner |
| `/server` | View the server icon and banner |
| `/timestamp` | Show the current UTC timestamp |
| `/timezone_set <timezone>` | Set your preferred timezone |
| `/timezone` | View your timezone settings |
| `/translate` | Translate text to another language |
| `/lookup <type> <target>` | Look up a domain or IP address |
| `/calc <expression>` | Calculate a math expression |

---

### 🌐 Web Tools

| Command | Description |
|---------|-------------|
| `!screenshot <url>` | Take a screenshot of a website |
| `!urban <word>` | Look up a word on Urban Dictionary |
| `/instagram_repost <url>` | Repost an Instagram post or reel |

---

### 🔒 Admin-Only

| Command | Description |
|---------|-------------|
| `!pvt` | Toggle maintenance mode |
| `!pvtallow <user_id>` | Allow a user to use the bot during maintenance |
| `!pvtremove <user_id>` | Remove a user from the maintenance allowlist |
| `!gstart <duration> <winners> <prize>` | Start a giveaway |

---

## 📁 Project Structure

```
seculex-bot/
├── main.py              # Bot entry point
├── footer.py            # Shared footer text
├── requirements.txt     # Python dependencies
├── cogs/                # Command modules
│   ├── admin.py
│   ├── afk.py
│   ├── auto_responder.py
│   ├── avatar.py
│   ├── casino.py
│   ├── fun.py
│   ├── games.py
│   ├── giveaway.py
│   ├── help.py
│   ├── info.py
│   ├── invoice.py
│   ├── moderation.py
│   ├── tickets.py
│   ├── verification.py
│   ├── welcome.py
│   └── ...
├── utils/               # Shared utilities
│   ├── storage.py
│   ├── backup.py
│   └── analytics.py
└── data/                # Runtime data (gitignored)
```

---

## 💬 Support

Join the support server: **[discord.gg/F5s2XDmKZx](https://discord.gg/F5s2XDmKZx)**

---

<div align="center">

*Bot made by Ayush | Powered by Seculex*

</div>
