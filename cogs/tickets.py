import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select, Modal, TextInput
import asyncio
import json
import os
from datetime import datetime
import logging
import re

# Configure logging for this file
logger = logging.getLogger(__name__)

# Import footer text
from footer import FOOTER_TEXT  # Ensure footer.py exists with FOOTER_TEXT defined

# Create directories if they don't exist (relative paths for VPS/RDP compatibility)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TICKETS_DIR = os.path.join(BASE_DIR, 'tickets')
TRANSCRIPTS_DIR = os.path.join(TICKETS_DIR, 'transcripts')
SETTINGS_DIR = os.path.join(BASE_DIR, 'settings')

os.makedirs(TICKETS_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
os.makedirs(SETTINGS_DIR, exist_ok=True)

# Load or initialize settings
def load_settings():
    settings_file = os.path.join(SETTINGS_DIR, 'settings.json')
    try:
        with open(settings_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"transcript_channel_id": None, "custom_ticket_embed": {"global": None, "buy_now": None, "support": None, "partnerships": None, "other": None}, "blacklist": {}}

def save_settings(settings):
    settings_file = os.path.join(SETTINGS_DIR, 'settings.json')
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)

# Load or initialize tickets
def load_tickets():
    tickets_file = os.path.join(TICKETS_DIR, 'tickets.json')
    try:
        with open(tickets_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_tickets(data):
    tickets_file = os.path.join(TICKETS_DIR, 'tickets.json')
    with open(tickets_file, 'w') as f:
        json.dump(data, f, indent=4)

# Modal for Transcript Channel Setup
class TranscriptModal(Modal, title="Set Transcript Channel"):
    channel_input = TextInput(label="Channel ID, Mention, or Name", placeholder="Enter channel ID, #channel, or name", required=True)

    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        settings = load_settings()
        channel_input = self.channel_input.value.strip()

        channel_id_match = re.match(r'<#(\d+)>', channel_input)
        if channel_id_match:
            channel_id = int(channel_id_match.group(1))
            channel = interaction.guild.get_channel(channel_id)
        else:
            channel_id = int(channel_input) if channel_input.isdigit() else None
            channel = (interaction.guild.get_channel(channel_id) if channel_id
                      else discord.utils.get(interaction.guild.channels, name=channel_input, type=discord.ChannelType.text))

        if channel and isinstance(channel, discord.TextChannel):
            settings["transcript_channel_id"] = channel.id
            save_settings(settings)
            await interaction.response.send_message(f"✅ Transcript channel set to {channel.mention}!", ephemeral=True)
            logger.info(f"Transcript channel set to {channel.id} by {interaction.user.name}")
        else:
            await interaction.response.send_message("❌ Invalid channel! Provide a valid channel ID, mention (#channel), or name.", ephemeral=True)
            logger.error(f"Invalid channel provided by {interaction.user.name} for transcript setup")

# Modal for Embed Customization (with Role Ping)
class EmbedModal(Modal, title="Customize Ticket Embed"):
    category_input = TextInput(label="Category", placeholder="global, buy_now, support, partnerships, or other", required=True)
    title_input = TextInput(label="Title", placeholder="e.g., 🎟️ New Ticket", required=True)
    description_input = TextInput(label="Description", placeholder="e.g., Welcome to your ticket!", required=True, style=discord.TextStyle.paragraph)
    color_input = TextInput(label="Color (Hex, e.g., #FF0000)", placeholder="#0000FF", required=False, default="#0000FF")
    role_input = TextInput(label="Role to Ping (ID, Mention, or Name)", placeholder="Leave blank for none", required=False)

    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        settings = load_settings()
        category = self.category_input.value.strip().lower()
        valid_categories = ["global", "buy_now", "support", "partnerships", "other"]
        if category not in valid_categories:
            await interaction.response.send_message("❌ Invalid category! Use 'global', 'buy_now', 'support', 'partnerships', or 'other'.", ephemeral=True)
            return

        role_id = None
        role_input = self.role_input.value.strip() if self.role_input.value else None
        if role_input:
            role_id_match = re.match(r'<@&(\d+)>', role_input)
            if role_id_match:
                role_id = int(role_id_match.group(1))
            else:
                role_id = int(role_input) if role_input.isdigit() else None
                if not role_id:
                    role = discord.utils.get(interaction.guild.roles, name=role_input)
                    if role:
                        role_id = role.id
            if not role_id or not interaction.guild.get_role(role_id):
                await interaction.response.send_message("❌ Invalid role! Provide a valid role ID, mention (@role), or name.", ephemeral=True)
                logger.error(f"Invalid role provided by {interaction.user.name} for embed setup")
                return

        try:
            color = self.color_input.value.strip()
            discord.Color.from_str(color)
            if "custom_ticket_embed" not in settings:
                settings["custom_ticket_embed"] = {"global": None, "buy_now": None, "support": None, "partnerships": None, "other": None}
            settings["custom_ticket_embed"][category] = {
                "title": self.title_input.value.strip(),
                "description": self.description_input.value.strip(),
                "color": color,
                "role_id": role_id  # Save the role ID to ping
            }
            save_settings(settings)
            reloaded_settings = load_settings()
            if reloaded_settings["custom_ticket_embed"][category] == settings["custom_ticket_embed"][category]:
                await interaction.response.send_message(f"✅ Custom ticket embed saved for {category} category!", ephemeral=True)
                logger.info(f"Custom ticket embed updated for {category} by {interaction.user.name}")
            else:
                await interaction.response.send_message(f"❌ Failed to save custom embed for {category} category. Check file permissions or disk space.", ephemeral=True)
                logger.error(f"Save verification failed for {category} by {interaction.user.name}")
        except ValueError as e:
            await interaction.response.send_message("❌ Invalid color format! Use a valid hex code (e.g., #FF0000).", ephemeral=True)
            logger.error(f"Invalid color format provided by {interaction.user.name} for embed setup: {str(e)}")
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred while saving embed: {str(e)}", ephemeral=True)
            logger.error(f"Error in EmbedModal on_submit for {interaction.user.name}: {str(e)}")

# Modal for Editing Ticket Embed
class EditTicketEmbedModal(Modal, title="Edit Ticket Embed"):
    title_input = TextInput(label="Title", placeholder="e.g., 🎟️ New Ticket", required=True)
    description_input = TextInput(label="Description", placeholder="e.g., Welcome to your ticket!", required=True, style=discord.TextStyle.paragraph)

    def __init__(self, interaction, embed):
        super().__init__()
        self.interaction = interaction
        self.embed = embed
        self.title_input.default = embed.title
        self.description_input.default = embed.description

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.embed.title = self.title_input.value.strip()
            self.embed.description = self.description_input.value.strip()
            await interaction.message.edit(embed=self.embed)
            await interaction.response.send_message("✅ Embed updated successfully!", ephemeral=True)
            logger.info(f"Ticket embed edited by {interaction.user.name} in channel {interaction.channel.id}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to update embed: {str(e)}", ephemeral=True)
            logger.error(f"Error editing ticket embed by {interaction.user.name}: {str(e)}")

# Modal for Channel Selection (Default Panel)
class DefaultChannelModal(Modal, title="Select Channel for Default Ticket Panel"):
    channel_input = TextInput(label="Channel ID, Mention, or Name", placeholder="Enter channel ID, #channel, or name", required=True)

    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        channel_input = self.channel_input.value.strip()
        channel_id_match = re.match(r'<#(\d+)>', channel_input)
        if channel_id_match:
            channel_id = int(channel_id_match.group(1))
            channel = interaction.guild.get_channel(channel_id)
        else:
            channel_id = int(channel_input) if channel_input.isdigit() else None
            channel = (interaction.guild.get_channel(channel_id) if channel_id
                      else discord.utils.get(interaction.guild.channels, name=channel_input, type=discord.ChannelType.text))

        if channel and isinstance(channel, discord.TextChannel):
            view = TicketView()
            embed = discord.Embed(
                title="🎟️ Open a Ticket",
                description=f"{interaction.user.mention}, select a category below to create a ticket!\n"
                           f"- 💰 **Buy Now** - For purchasing our services.\n"
                           f"- ✅ **Support** - For general inquiries or help.\n"
                           f"- 🤝 **Partnerships** - For collaborations or business opportunities.\n"
                           f"- ❓ **Other** - For anything else that doesn't fit the above categories.",
                color=discord.Color.blue()
            )
            embed.set_footer(text=FOOTER_TEXT)
            edit_button = Button(label="Edit Embed", style=discord.ButtonStyle.blurple, emoji="✏️", custom_id="edit_ticket_panel_embed")
            view.add_item(edit_button)
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"✅ Default ticket panel sent to {channel.mention}!", ephemeral=True)
            logger.info(f"Default ticket panel sent to {channel.id} by {interaction.user.name}")
        else:
            await interaction.response.send_message("❌ Invalid channel! Provide a valid channel ID, mention (#channel), or name.", ephemeral=True)
            logger.error(f"Invalid channel provided by {interaction.user.name} for default ticket panel")

# Modal for Channel Selection (Custom Panel)
class CustomChannelModal(Modal, title="Select Channel for Custom Ticket Panel"):
    channel_input = TextInput(label="Channel ID, Mention, or Name", placeholder="Enter channel ID, #channel, or name", required=True)

    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        settings = load_settings()
        channel_input = self.channel_input.value.strip()
        channel_id_match = re.match(r'<#(\d+)>', channel_input)
        if channel_id_match:
            channel_id = int(channel_id_match.group(1))
            channel = interaction.guild.get_channel(channel_id)
        else:
            channel_id = int(channel_input) if channel_input.isdigit() else None
            channel = (interaction.guild.get_channel(channel_id) if channel_id
                      else discord.utils.get(interaction.guild.channels, name=channel_input, type=discord.ChannelType.text))

        if channel and isinstance(channel, discord.TextChannel):
            custom_embeds = settings.get("custom_ticket_embed", {})
            custom_embed = custom_embeds.get("global")  # Try global first
            if not custom_embed:
                # Fall back to the first available category embed if global is not set
                for category in ["buy_now", "support", "partnerships", "other"]:
                    custom_embed = custom_embeds.get(category)
                    if custom_embed:
                        break
                if not custom_embed:
                    await interaction.response.send_message("❌ No custom embed set! Set one first with 'Customize Embed'.", ephemeral=True)
                    return

            role_mention = ""
            if custom_embed.get("role_id"):
                role = interaction.guild.get_role(custom_embed["role_id"])
                if role:
                    role_mention = role.mention

            view = TicketView()
            embed = discord.Embed(
                title=custom_embed.get("title", "🎟️ New Ticket"),
                description=f"{interaction.user.mention} {role_mention}\n{custom_embed.get('description', 'Select a category to create a ticket!')}",
                color=discord.Color.from_str(custom_embed.get("color", "#0000FF"))
            )
            embed.set_footer(text=FOOTER_TEXT)
            edit_button = Button(label="Edit Embed", style=discord.ButtonStyle.blurple, emoji="✏️", custom_id="edit_ticket_panel_embed")
            view.add_item(edit_button)
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"✅ Custom ticket panel sent to {channel.mention}!", ephemeral=True)
            logger.info(f"Custom ticket panel sent to {channel.id} by {interaction.user.name}")
        else:
            await interaction.response.send_message("❌ Invalid channel! Provide a valid channel ID, mention (#channel), or name.", ephemeral=True)
            logger.error(f"Invalid channel provided by {interaction.user.name} for custom ticket panel")

# Modal for Blacklist Appeal
class AppealModal(Modal, title="Appeal Blacklist"):
    repeat_mistake = TextInput(label="Would you repeat the mistake? (yes/no)", placeholder="Enter 'yes' or 'no'", required=True)
    username_input = TextInput(label="Your Username", placeholder="Enter your username", required=True)
    dev_id_input = TextInput(label="Dev ID (Optional)", placeholder="Enter your dev ID (optional)", required=False)

    def __init__(self, interaction, reason):
        super().__init__()
        self.interaction = interaction
        self.reason = reason
        self.description = f"**Blacklist Reason:** {reason}"

    async def on_submit(self, interaction: discord.Interaction):
        settings = load_settings()
        user_id = str(interaction.user.id)
        repeat_mistake = self.repeat_mistake.value.strip().lower()
        username = self.username_input.value.strip()
        dev_id = self.dev_id_input.value.strip() if self.dev_id_input.value else "N/A"

        if repeat_mistake not in ["yes", "no"]:
            await interaction.response.send_message("❌ Please enter 'yes' or 'no' for whether you would repeat the mistake.", ephemeral=True)
            return

        # Use a single appeal channel
        appeal_channel = discord.utils.get(interaction.guild.channels, name="blacklist-appeals")
        if not appeal_channel:
            try:
                appeal_category = discord.utils.get(interaction.guild.categories, name="bl-appeals")
                if not appeal_category:
                    appeal_category = await interaction.guild.create_category("bl-appeals")
                    logger.info(f"Created appeal category 'bl-appeals'")
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
                }
                appeal_channel = await interaction.guild.create_text_channel("blacklist-appeals", category=appeal_category, overwrites=overwrites)
                logger.info(f"Created appeal channel 'blacklist-appeals'")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Bot lacks permission to create channels!", ephemeral=True)
                logger.error("Permission denied creating appeal channel")
                return

        embed = discord.Embed(
            title="Blacklist Appeal",
            description=f"**User:** {username} (ID: {user_id})\n**Dev ID:** {dev_id}\n**Would Repeat Mistake:** {repeat_mistake.capitalize()}\n**Blacklist Reason:** {self.reason}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=FOOTER_TEXT)
        view = AppealReviewView()
        message = await appeal_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Appeal submitted! Check with staff in {appeal_channel.mention}.", ephemeral=True)
        logger.info(f"Appeal submitted by {interaction.user.name} in channel {appeal_channel.id} (Message ID: {message.id})")

# View for Blacklist Appeal Review
class AppealReviewView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept Appeal", style=discord.ButtonStyle.green, custom_id="accept_appeal")
    async def accept_appeal(self, interaction: discord.Interaction, button: Button):
        settings = load_settings()
        user_id = re.search(r"ID: (\d+)", interaction.message.embeds[0].description).group(1)
        if user_id in settings["blacklist"]:
            del settings["blacklist"][user_id]
            save_settings(settings)
            user = await interaction.client.fetch_user(int(user_id))
            try:
                await user.send("✅ Your blacklist appeal has been accepted! You can now create tickets.")
            except discord.Forbidden:
                logger.warning(f"Could not DM user {user_id} about appeal acceptance (DMs disabled)")
            embed = interaction.message.embeds[0]
            embed.description += "\n**Status:** Accepted"
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message("✅ Appeal accepted. User unblacklisted.", ephemeral=True)
            logger.info(f"Appeal accepted for user {user_id} by {interaction.user.name}")
        else:
            await interaction.response.send_message("❌ User not found in blacklist.", ephemeral=True)

    @discord.ui.button(label="Deny Appeal", style=discord.ButtonStyle.red, custom_id="deny_appeal")
    async def deny_appeal(self, interaction: discord.Interaction, button: Button):
        user_id = re.search(r"ID: (\d+)", interaction.message.embeds[0].description).group(1)
        user = await interaction.client.fetch_user(int(user_id))
        try:
            await user.send("❌ Your blacklist appeal has been denied. Contact staff for further assistance.")
        except discord.Forbidden:
            logger.warning(f"Could not DM user {user_id} about appeal denial (DMs disabled)")
        embed = interaction.message.embeds[0]
        embed.description += "\n**Status:** Denied"
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("✅ Appeal denied.", ephemeral=True)
        logger.info(f"Appeal denied for user {user_id} by {interaction.user.name}")

# View for Setup Options
class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Set Transcript Channel", style=discord.ButtonStyle.green, custom_id="set_transcript")
    async def set_transcript_button(self, interaction: discord.Interaction, button: Button):
        modal = TranscriptModal(interaction)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Customize Embed", style=discord.ButtonStyle.primary, custom_id="customize_embed")
    async def customize_embed_button(self, interaction: discord.Interaction, button: Button):
        modal = EmbedModal(interaction)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Send Default Ticket Panel", style=discord.ButtonStyle.grey, custom_id="send_default_panel")
    async def send_default_panel_button(self, interaction: discord.Interaction, button: Button):
        modal = DefaultChannelModal(interaction)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Send Custom Ticket Panel", style=discord.ButtonStyle.blurple, custom_id="send_custom_panel")
    async def send_custom_panel_button(self, interaction: discord.Interaction, button: Button):
        modal = CustomChannelModal(interaction)
        await interaction.response.send_modal(modal)

class CategorySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Buy Now", description="For purchasing our services", emoji="💰", value="buy_now"),
            discord.SelectOption(label="Support", description="For general inquiries or help", emoji="✅", value="support"),
            discord.SelectOption(label="Partnerships", description="For collaborations or business opportunities", emoji="🤝", value="partnerships"),
            discord.SelectOption(label="Other", description="For anything else", emoji="❓", value="other")
        ]
        super().__init__(placeholder="Select a ticket category", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = self.view
        category = self.values[0]
        await view.create_ticket_callback(interaction, category)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())
        
    async def create_ticket_callback(self, interaction: discord.Interaction, category: str):
        settings = load_settings()
        ticket_data = load_tickets()
        user_id = str(interaction.user.id)
        user_tickets = sum(1 for data in ticket_data.values() if data["user_id"] == user_id and data.get("state", "open") == "open")

        # Check blacklist
        blacklist = settings.get("blacklist", {})
        if user_id in blacklist:
            reason = blacklist[user_id].get("reason", "No reason provided")
            embed = discord.Embed(
                title="SECULEX APP",
                description=f"{interaction.user.mention}, you have been blacklisted from creating tickets.",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="From", value="SECULEX", inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.add_field(name="Message", value="Click the 'Appeal Blacklist' button when creating a ticket to appeal.", inline=False)
            embed.set_footer(text=FOOTER_TEXT)
            view = discord.ui.View()
            appeal_button = discord.ui.Button(label="Appeal Blacklist", style=discord.ButtonStyle.red, custom_id="appeal_blacklist")
            view.add_item(appeal_button)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            logger.warning(f"Blacklisted user {interaction.user.name} attempted to create a ticket")
            return

        if user_tickets >= 1:
            await interaction.followup.send("❌ You have reached the maximum number of open tickets!", ephemeral=True)
            logger.warning(f"User {interaction.user.name} hit ticket limit")
            return

        if user_id in ticket_data and ticket_data[user_id].get("state", "open") == "open":
            await interaction.followup.send("❌ You have already an open ticket!", ephemeral=True)
            logger.warning(f"User {interaction.user.name} attempted to create a duplicate ticket")
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        category_name = f"{category.replace('_', ' ').title()} Tickets"
        category_obj = discord.utils.get(interaction.guild.categories, name=category_name)
        if not category_obj:
            try:
                category_obj = await interaction.guild.create_category(category_name)
                logger.info(f"Created category {category_name}")
            except discord.Forbidden:
                await interaction.followup.send("❌ Bot lacks permission to create categories!", ephemeral=True)
                logger.error(f"Permission denied creating category {category_name}")
                return
            except Exception as e:
                await interaction.followup.send(f"❌ Failed to create category: {str(e)}", ephemeral=True)
                logger.error(f"Error creating category {category_name}: {str(e)}")
                return

        try:
            channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.name}-{len(ticket_data) + 1}",
                category=category_obj,
                overwrites=overwrites
            )
            logger.info(f"Created ticket channel {channel.id}")
        except discord.Forbidden:
            await interaction.followup.send("❌ Bot lacks permission to create channels!", ephemeral=True)
            logger.error(f"Permission denied creating channel for {interaction.user.name}")
            return
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create channel: {str(e)}", ephemeral=True)
            logger.error(f"Error creating channel for {interaction.user.name}: {str(e)}")
            return

        ticket_data[str(channel.id)] = {
            "user_id": user_id,
            "category": category,
            "created_at": datetime.utcnow().isoformat(),
            "state": "open",
            "members": [user_id]
        }
        save_tickets(ticket_data)
        logger.debug(f"Ticket data saved for channel {channel.id}: {ticket_data[str(channel.id)]}")

        welcome_message = ""
        role_mention = ""
        custom_embeds = settings.get("custom_ticket_embed", {})
        custom_embed = custom_embeds.get(category) or custom_embeds.get("global")

        if custom_embed and "role_id" in custom_embed and custom_embed["role_id"]:
            role = interaction.guild.get_role(custom_embed["role_id"])
            if role:
                role_mention = role.mention

        if category == "support":
            welcome_message = f"{interaction.user.mention} {role_mention} Support will be with you shortly."
        elif category == "buy_now":
            welcome_message = f"{interaction.user.mention} {role_mention} Please describe what you want to buy now."
        elif category == "partnerships":
            welcome_message = f"{interaction.user.mention} {role_mention} Please provide details about your partnership proposal."
        elif category == "other":
            welcome_message = f"{interaction.user.mention} {role_mention} Please provide more details about your request."

        embed = discord.Embed(
            title=custom_embed.get("title", f"🎟️ New {category.replace('_', ' ').title()} Ticket") if custom_embed else f"🎟️ New {category.replace('_', ' ').title()} Ticket",
            description=custom_embed.get("description", welcome_message) if custom_embed else welcome_message,
            color=discord.Color.from_str(custom_embed.get("color", "#0000FF")) if custom_embed and custom_embed.get("color") else discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=FOOTER_TEXT)

        close_button = Button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
        edit_button = Button(label="Edit Embed", style=discord.ButtonStyle.blurple, emoji="✏️", custom_id="edit_ticket_embed")
        view = View()
        view.add_item(close_button)
        view.add_item(edit_button)
        try:
            if not channel.permissions_for(interaction.guild.me).send_messages:
                raise discord.Forbidden("Bot lacks send_messages permission")
            await channel.send(content="", embed=embed, view=view)
            logger.info(f"Ticket created in channel {channel.id} with category {category}")
        except discord.Forbidden as e:
            logger.error(f"Permission error in channel {channel.id}: {str(e)}")
            await interaction.followup.send(f"❌ Failed to set up ticket in {channel.mention}. Bot lacks permissions.", ephemeral=True)
            await channel.delete()
            return
        except Exception as e:
            logger.error(f"Failed to send ticket message in channel {channel.id}: {str(e)}")
            await interaction.followup.send(f"❌ Failed to set up ticket in {channel.mention}. Contact an admin. Error: {str(e)}", ephemeral=True)
            await channel.delete()
            return

        await interaction.followup.send(f"✅ Your {category.replace('_', ' ').title()} ticket has been created in {channel.mention}!", ephemeral=True)

class JumpToTopView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Jump to Top", style=discord.ButtonStyle.primary, emoji="⬆️", custom_id="jumptotop")
    async def jump_to_top(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Scrolling to the top...", ephemeral=True)
        await interaction.channel.send("This message is at the top! Use the scrollbar to navigate.", delete_after=5)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket_setup", description="Setup or customize the ticket system")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎟️ Ticket System Setup",
            description="Use the buttons below to configure the ticket system:\n"
                       "- **Set Transcript Channel**: Configure where transcripts are sent.\n"
                       "- **Customize Embed**: Customize the ticket creation embed message.\n"
                       "- **Send Default Ticket Panel**: Send the default ticket panel to a specified channel.\n"
                       "- **Send Custom Ticket Panel**: Send a panel with the custom embed (requires global embed setup).",
            color=discord.Color.blue()
        )
        embed.set_footer(text=FOOTER_TEXT)
        view = SetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="open", description="Re-open a closed ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_open(self, interaction: discord.Interaction):
        ticket_data = load_tickets()
        if str(interaction.channel.id) not in ticket_data or ticket_data[str(interaction.channel.id)].get("state") != "closed":
            await interaction.response.send_message("❌ This channel is not a closed ticket!", ephemeral=True)
            return
        ticket_data[str(interaction.channel.id)]["state"] = "open"
        overwrites = interaction.channel.overwrites
        overwrites[interaction.guild.get_member(int(ticket_data[str(interaction.channel.id)]["user_id"]))] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        await interaction.channel.edit(overwrites=overwrites)
        save_tickets(ticket_data)
        await interaction.response.send_message("✅ Ticket re-opened!", ephemeral=True)

    @app_commands.command(name="delete", description="Delete a ticket channel")
    @app_commands.checks.has_permissions(administrator=True, manage_channels=True)
    async def ticket_delete(self, interaction: discord.Interaction):
        ticket_data = load_tickets()
        if str(interaction.channel.id) not in ticket_data:
            await interaction.response.send_message("❌ This channel is not a ticket!", ephemeral=True)
            logger.error(f"Channel {interaction.channel.id} not found in ticket_data")
            return
        del ticket_data[str(interaction.channel.id)]
        save_tickets(ticket_data)
        await interaction.channel.send("⏳ Deleting ticket in 5 seconds...")
        for i in range(5, 0, -1):
            await asyncio.sleep(1)
            await interaction.channel.send(f"⏳ Deleting ticket in {i} seconds...", delete_after=1)
        await interaction.channel.delete()

    @app_commands.command(name="transcript", description="Create a transcript of the ticket")
    @app_commands.describe(option="Where to send the transcript (optional)", target="Channel ID, user ID, mention, or leave blank for default")
    @app_commands.choices(option=[
        app_commands.Choice(name="Channel", value="channel"),
        app_commands.Choice(name="User", value="user")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_transcript(self, interaction: discord.Interaction, option: app_commands.Choice[str] = None, target: str = None):
        await interaction.response.defer(ephemeral=True)
        settings = load_settings()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        transcript_file = os.path.join(TRANSCRIPTS_DIR, f"transcript_{interaction.channel.id}_{timestamp}.html")
        logger.info(f"Starting transcript for channel {interaction.channel.id}")

        try:
            # Fetch messages
            messages = []
            last_message = None
            max_messages = 500
            batch_size = 100

            while len(messages) < max_messages:
                batch = [msg async for msg in interaction.channel.history(limit=batch_size, before=last_message)]
                if not batch:
                    break
                messages.extend(batch)
                last_message = batch[-1]
                if len(batch) < batch_size:
                    break
                await asyncio.sleep(1)

            if not messages:
                await interaction.followup.send("❌ No messages found in this channel to transcribe!", ephemeral=True)
                logger.warning(f"No messages found in channel {interaction.channel.id}")
                return
            logger.debug(f"Fetched {len(messages)} messages for transcript")

            # Count messages per user
            user_message_counts = {}
            for msg in messages:
                user_id = str(msg.author.id)
                user_message_counts[user_id] = user_message_counts.get(user_id, 0) + 1

            # Generate user list with counts
            users_in_transcript = "\n".join(
                f"{count} - {msg.author.mention} - {msg.author.name}#{msg.author.discriminator}"
                for user_id, count in sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
            )

            # Determine ticket owner and panel name from ticket data
            ticket_data = load_tickets()
            ticket_info = ticket_data.get(str(interaction.channel.id), {})
            ticket_owner_id = ticket_info.get("user_id")
            ticket_owner = interaction.guild.get_member(int(ticket_owner_id)) if ticket_owner_id else None
            ticket_name = interaction.channel.name
            panel_name = ticket_info.get("category", "Unknown").replace("_", " ").title()

            # Attachment details
            attachments_saved = sum(1 for msg in messages for attachment in msg.attachments if attachment.size <= 54000)  # 54 KB limit
            attachments_skipped = sum(1 for msg in messages for attachment in msg.attachments if attachment.size > 54000)

            # Create transcript embed
            embed = discord.Embed(
                title=">Server-Info<",
                description=(
                    f"Server: {interaction.guild.name} ({interaction.guild.id})\n"
                    f"Channel: {interaction.channel.mention} ({interaction.channel.id})\n"
                    f"Messages: {len(messages)}\n"
                    f"Attachments Saved: {attachments_saved}\n"
                    f"Attachments Skipped: {attachments_skipped} (due maximum file size limits). . . ({54 - attachments_saved} KB left)"
                ),
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="Ticket Owner | Ticket Name | Panel Name",
                value=(
                    f"{ticket_owner.mention if ticket_owner else 'Unknown'} | {ticket_name} | {panel_name}"
                ),
                inline=False
            )
            embed.add_field(
                name="Direct Transcript",
                value="Download the attached file",
                inline=False
            )
            embed.add_field(
                name="Users in transcript",
                value=users_in_transcript if users_in_transcript else "No users found",
                inline=False
            )
            embed.set_footer(text=FOOTER_TEXT)

            # Generate HTML transcript
            server_icon = interaction.guild.icon.url if interaction.guild.icon else "https://via.placeholder.com/50"
            css = """
<style>
    @font-face { font-family: Whitney; src: url('https://discordapp.com/assets/6c6374bad0b0b6d204d8d6dc4a18d820.woff'); font-weight: 300; }
    @font-face { font-family: Whitney; src: url('https://discordapp.com/assets/e8acd7d9bf6207f99350ca9f9e23b168.woff'); font-weight: 400; }
    @font-face { font-family: Whitney; src: url('https://discordapp.com/assets/3bdef1251a424500c1b3a78dea9b7e57.woff'); font-weight: 500; }
    @font-face { font-family: Whitney; src: url('https://discordapp.com/assets/be0060dafb7a0e31d2a1ca17c0708636.woff'); font-weight: 600; }
    @font-face { font-family: Whitney; src: url('https://discordapp.com/assets/8e12fb4f14d9c4592eb8ec9f22337b04.woff'); font-weight: 700; }
    body { background-color: #36393e; color: #dcddde; font-family: Whitney, Helvetica Neue, Helvetica, Arial, sans-serif; font-size: 16px; margin: 0; padding: 0; }
    .header { background-color: #202225; color: #ffffff; padding: 25px; display: flex; align-items: center; border-bottom: 1px solid #2f3136; }
    .header img { width: 50px; height: 50px; margin-right: 15px; border-radius: 50%; }
    .header h1 { margin: 0; font-size: 20px; font-weight: 600; }
    .message-count { font-size: 14px; color: #b9bbbe; margin-left: auto; }
    .parent-container { padding: 25px; display: flex; }
    .message-container { display: flex; flex-direction: column; padding-left: 15px; }
    .message-content { background-color: #2f3136; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; }
    .message-content .username { color: #00aff4; font-weight: 500; margin-right: 5px; }
    .message-content .timestamp { color: #72767d; font-size: 12px; }
    .message-content img { max-width: 100%; height: auto; border-radius: 5px; margin-top: 5px; }
</style>
"""
            html_head = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcript for #{interaction.channel.name}</title>
    {css}
</head>
<body>
    <div class="header">
        <img src="{server_icon}" alt="Server Icon">
        <h1>{interaction.guild.name}</h1>
        <span class="message-count">{len(messages)} messages</span>
    </div>
    <div class="parent-container">
        <div class="message-container">
"""
            html_body = ""
            for msg in reversed(messages):
                avatar_url = msg.author.avatar.url if msg.author.avatar else msg.author.default_avatar.url
                timestamp = msg.created_at.strftime('%Y-%m-d %H:%M:%S UTC')
                content = msg.content.replace('<', '<').replace('>', '>')
                attachments_html = "".join(f'<img src="{attachment.url}" alt="Attachment">' for attachment in msg.attachments if attachment.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')))
                html_body += f"""
            <div class="message-content">
                <span class="username">{msg.author.name}</span>
                <span class="timestamp">[{timestamp}]</span><br>
                <span>{content}</span>
                {attachments_html}
            </div>
"""
            html_tail = """
        </div>
    </div>
</body>
</html>
"""
            html_content = html_head + html_body + html_tail

            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Determine destination
            destination = None
            if not option and settings.get("transcript_channel_id"):
                # Default to the set transcript channel if no option is provided
                destination = interaction.guild.get_channel(settings["transcript_channel_id"])
                if not destination or not isinstance(destination, discord.TextChannel):
                    await interaction.followup.send("❌ Invalid or unset transcript channel! Please set a transcript channel with `/ticket_setup`.", ephemeral=True)
                    logger.error(f"Invalid or unset transcript channel for {interaction.channel.id}")
                    return
            elif option:
                if option.value == "channel":
                    if target:
                        channel_id_match = re.match(r'<#(\d+)>', target)
                        target_id = int(channel_id_match.group(1)) if channel_id_match else (int(target) if target.isdigit() else None)
                        destination = interaction.guild.get_channel(target_id) if target_id else interaction.guild.get_channel(settings.get("transcript_channel_id"))
                    else:
                        destination = interaction.guild.get_channel(settings.get("transcript_channel_id"))
                    if not destination or not isinstance(destination, discord.TextChannel):
                        await interaction.followup.send("❌ Invalid channel or no transcript channel set!", ephemeral=True)
                        logger.error(f"Invalid channel or no transcript channel set for {interaction.channel.id}")
                        return
                elif option.value == "user":
                    if target:
                        user_id_match = re.match(r'<@!?(\d+)>', target)
                        target_id = int(user_id_match.group(1)) if user_id_match else (int(target) if target.isdigit() else None)
                        destination = await self.bot.fetch_user(target_id) if target_id else interaction.user
                    else:
                        destination = interaction.user
                    if not destination:
                        await interaction.followup.send("❌ Invalid user!", ephemeral=True)
                        logger.error(f"Invalid user for transcript in {interaction.channel.id}")
                        return

            # Send embed with file
            with open(transcript_file, "rb") as f:
                file = discord.File(f, filename=f"transcript-{interaction.channel.name}.html")
                if isinstance(destination, discord.TextChannel):
                    await destination.send(embed=embed, file=file)
                    await interaction.followup.send(f"✅ Transcript sent to {destination.mention}!", ephemeral=True)
                    logger.info(f"Transcript sent to channel {destination.id}")
                elif isinstance(destination, discord.User):
                    await destination.send(embed=embed, file=file)
                    await interaction.followup.send("✅ Transcript sent to you via DM!", ephemeral=True)
                    logger.info(f"Transcript sent to user {destination.id}")

        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to access history or send messages!", ephemeral=True)
            logger.error(f"Forbidden error in transcript for {interaction.channel.id}")
        except discord.HTTPException as e:
            if e.status == 429:
                await interaction.followup.send("❌ Rate limit exceeded! Please try again later.", ephemeral=True)
                logger.error(f"Rate limit hit for transcript in channel {interaction.channel.id}: {str(e)}")
            else:
                await interaction.followup.send(f"❌ An HTTP error occurred: {str(e)}", ephemeral=True)
                logger.error(f"HTTP error in transcript for {interaction.channel.id}: {str(e)}")
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            logger.error(f"Transcript error in channel {interaction.channel.id}: {str(e)}")

    @app_commands.command(name="add", description="Add a user or role to the ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_add(self, interaction: discord.Interaction, member: discord.Member):
        ticket_data = load_tickets()
        if str(interaction.channel.id) not in ticket_data:
            await interaction.response.send_message("❌ This channel is not a ticket!", ephemeral=True)
            return
        overwrites = interaction.channel.overwrites
        bot_highest_role = interaction.guild.me.top_role
        target_role = max(member.roles, key=lambda r: r.position) if member.roles else interaction.guild.default_role
        if not bot_highest_role > target_role:
            await interaction.response.send_message("❌ I cannot add this member because their highest role is equal to or above mine. Move my role to the top!", ephemeral=True)
            logger.warning(f"Cannot add member {member.name} due to hierarchy (bot role: {bot_highest_role.name}, target role: {target_role.name})")
            return
        overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        await interaction.channel.edit(overwrites=overwrites)
        ticket_data[str(interaction.channel.id)]["members"].append(str(member.id))
        save_tickets(ticket_data)
        await interaction.response.send_message(f"✅ Added {member.mention} to the ticket!", ephemeral=True)

    @app_commands.command(name="close", description="Close the current ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_close(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        await interaction.response.defer()
        ticket_data = load_tickets()
        if str(interaction.channel.id) not in ticket_data:
            await interaction.followup.send("❌ This channel is not a ticket!", ephemeral=True)
            return
        ticket_data[str(interaction.channel.id)]["state"] = "closed"
        overwrites = interaction.channel.overwrites
        for member_id in ticket_data[str(interaction.channel.id)]["members"]:
            member = interaction.guild.get_member(int(member_id))
            if member and member != interaction.user:
                overwrites[member] = discord.PermissionOverwrite(read_messages=False)
        await interaction.channel.edit(overwrites=overwrites)
        save_tickets(ticket_data)
        await interaction.followup.send(f"⏳ Closing ticket in 5 seconds... Reason: {reason}")
        for i in range(5, 0, -1):
            await asyncio.sleep(1)
            await interaction.channel.send(f"⏳ Closing ticket in {i} seconds...", delete_after=1)
        await interaction.channel.delete()

    @app_commands.command(name="jumptotop", description="Jump to the top of the ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_jumptotop(self, interaction: discord.Interaction):
        await interaction.response.send_message("Scrolling to the top...", ephemeral=True)
        await interaction.channel.send("This message is at the top! Use the scrollbar to navigate.", delete_after=5)

    @app_commands.command(name="remove", description="Remove a user from the ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_remove(self, interaction: discord.Interaction, member: discord.Member):
        ticket_data = load_tickets()
        if str(interaction.channel.id) not in ticket_data:
            await interaction.response.send_message("❌ This channel is not a ticket!", ephemeral=True)
            return
        overwrites = interaction.channel.overwrites
        if str(member.id) in ticket_data[str(interaction.channel.id)]["members"]:
            bot_highest_role = interaction.guild.me.top_role
            target_role = max(member.roles, key=lambda r: r.position) if member.roles else interaction.guild.default_role
            if not bot_highest_role > target_role:
                await interaction.response.send_message("❌ I cannot remove this member because their highest role is equal to or above mine. Move my role to the top!", ephemeral=True)
                logger.warning(f"Cannot remove member {member.name} due to hierarchy (bot role: {bot_highest_role.name}, target role: {target_role.name})")
                return
            overwrites[member] = discord.PermissionOverwrite(read_messages=False, send_messages=False)
            ticket_data[str(interaction.channel.id)]["members"].remove(str(member.id))
            save_tickets(ticket_data)
            await interaction.channel.edit(overwrites=overwrites)
            await interaction.response.send_message(f"✅ Removed {member.mention} from the ticket!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ This user is not part of the ticket!", ephemeral=True)

    @app_commands.command(name="rename", description="Rename the current ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_rename(self, interaction: discord.Interaction, new_ticket_name: str):
        ticket_data = load_tickets()
        if str(interaction.channel.id) not in ticket_data:
            await interaction.response.send_message("❌ This channel is not a ticket!", ephemeral=True)
            return
        await interaction.channel.edit(name=new_ticket_name)
        await interaction.response.send_message(f"✅ Ticket renamed to {new_ticket_name}!", ephemeral=True)

    @app_commands.command(name="reopen", description="Reopen a closed ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_reopen(self, interaction: discord.Interaction, ticket_id: str):
        ticket_data = load_tickets()
        channel = interaction.guild.get_channel(int(ticket_id))
        if not channel or str(ticket_id) not in ticket_data or ticket_data[str(ticket_id)].get("state") != "closed":
            await interaction.response.send_message("❌ Invalid or not a closed ticket ID!", ephemeral=True)
            return
        ticket_data[str(ticket_id)]["state"] = "open"
        overwrites = channel.overwrites
        overwrites[interaction.guild.get_member(int(ticket_data[str(ticket_id)]["user_id"]))] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        await channel.edit(overwrites=overwrites)
        save_tickets(ticket_data)
        await interaction.response.send_message(f"✅ Ticket {channel.mention} re-opened!", ephemeral=True)

    @app_commands.command(name="blacklist", description="Blacklist a user or role from creating tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_blacklist(self, interaction: discord.Interaction, target: discord.Member | discord.Role, reason: str):
        settings = load_settings()
        guild = interaction.guild
        target_id = str(target.id)
        if "blacklist" not in settings:
            settings["blacklist"] = {}
        elif not isinstance(settings["blacklist"], dict):  # Convert list to dict if needed
            settings["blacklist"] = {str(k): v for k, v in enumerate(settings["blacklist"])}

        if target_id not in settings["blacklist"]:
            settings["blacklist"][target_id] = {"reason": reason}
            blacklisted_role = discord.utils.get(guild.roles, name="blacklisted")
            if not blacklisted_role:
                await guild.create_role(name="blacklisted", color=discord.Color.dark_red())
                blacklisted_role = discord.utils.get(guild.roles, name="blacklisted")
            if isinstance(target, discord.Member):
                await target.add_roles(blacklisted_role)
                embed = discord.Embed(
                    title="SECULEX APP",
                    description=f"{target.mention}, you have been blacklisted from creating tickets.",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="From", value="SECULEX", inline=True)
                embed.add_field(name="Reason", value=reason, inline=True)
                embed.add_field(name="Message", value="Click the 'Appeal Blacklist' button when creating a ticket to appeal.", inline=False)
                embed.set_footer(text=FOOTER_TEXT)
                try:
                    await target.send(embed=embed)
                except discord.Forbidden:
                    logger.warning(f"Could not DM user {target.id} about blacklist (DMs disabled)")
            await interaction.response.send_message(f"✅ {target.name} has been blacklisted. Reason: {reason}\nUse `/blacklist_remove` to undo this.", ephemeral=False)
            logger.info(f"User {target.name} blacklisted by {interaction.user.name} with reason: {reason}")
        else:
            await interaction.response.send_message(f"❌ {target.name} is already blacklisted!", ephemeral=True)

        save_settings(settings)

    @app_commands.command(name="blacklist_remove", description="Remove a user or role from the blacklist")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_blacklist_remove(self, interaction: discord.Interaction, target: discord.Member | discord.Role):
        settings = load_settings()
        guild = interaction.guild
        target_id = str(target.id)
        if "blacklist" not in settings:
            settings["blacklist"] = {}

        blacklisted_role = discord.utils.get(guild.roles, name="blacklisted")
        if target_id in settings["blacklist"]:
            del settings["blacklist"][target_id]
            if blacklisted_role and isinstance(target, discord.Member):
                await target.remove_roles(blacklisted_role)
            await interaction.response.send_message(f"✅ {target.name} has been removed from the blacklist.", ephemeral=False)
            logger.info(f"User {target.name} unblacklisted by {interaction.user.name}")
        else:
            await interaction.response.send_message(f"❌ {target.name} is not blacklisted!", ephemeral=True)

        save_settings(settings)

    @app_commands.command(name="show", description="Show blacklist reason for a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_show(self, interaction: discord.Interaction, user: discord.Member):
        settings = load_settings()
        user_id = str(user.id)
        if "blacklist" not in settings or user_id not in settings["blacklist"]:
            await interaction.response.send_message(f"❌ {user.name} is not blacklisted!", ephemeral=True)
            return
        reason = settings["blacklist"][user_id]["reason"]
        await interaction.response.send_message(f"✅ Blacklist reason for {user.name}: {reason}", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        if interaction.data["custom_id"] == "close_ticket":
            await interaction.response.defer()
            ticket_data = load_tickets()
            if str(interaction.channel.id) not in ticket_data:
                await interaction.followup.send("❌ This channel is not a ticket!", ephemeral=True)
                logger.error(f"Channel {interaction.channel.id} not found in ticket_data")
                return
            ticket_data[str(interaction.channel.id)]["state"] = "closed"
            overwrites = interaction.channel.overwrites
            for member_id in ticket_data[str(interaction.channel.id)]["members"]:
                member = interaction.guild.get_member(int(member_id))
                if member and member != interaction.user:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=False)
            await interaction.channel.edit(overwrites=overwrites)
            save_tickets(ticket_data)
            await interaction.followup.send("⏳ Closing ticket in 5 seconds...")
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await interaction.channel.send(f"⏳ Closing ticket in {i} seconds...", delete_after=1)
            await interaction.channel.delete()

        if interaction.data["custom_id"] == "edit_ticket_embed":
            if not interaction.permissions.manage_channels:
                await interaction.response.send_message("❌ You need Manage Channels permission to edit the embed!", ephemeral=True)
                return
            embed = interaction.message.embeds[0]
            modal = EditTicketEmbedModal(interaction, embed)
            await interaction.response.send_modal(modal)

        if interaction.data["custom_id"] == "edit_ticket_panel_embed":
            if not interaction.permissions.manage_channels:
                await interaction.response.send_message("❌ You need Manage Channels permission to edit the embed!", ephemeral=True)
                return
            embed = interaction.message.embeds[0]
            modal = EditTicketEmbedModal(interaction, embed)
            await interaction.response.send_modal(modal)

        if interaction.data["custom_id"] == "appeal_blacklist":
            settings = load_settings()
            user_id = str(interaction.user.id)
            if user_id not in settings["blacklist"]:
                await interaction.response.send_message("❌ You are not blacklisted!", ephemeral=True)
                return
            reason = settings["blacklist"][user_id]["reason"]
            modal = AppealModal(interaction, reason)
            await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Tickets(bot)) 