import discord
from discord.ext import commands
from discord import app_commands
import random
import string
from datetime import datetime
from typing import Dict, Any
from utils.storage import JsonStorage

class Invoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processing_invoices = set()  # Prevent duplicate processing

    def generate_invoice_id(self):
        """Generate a unique invoice ID"""
        chars = string.ascii_uppercase + string.digits
        return 'INV-' + ''.join(random.choices(chars, k=5))

    async def get_or_create_channel(self, guild, channel_name):
        """Get existing channel or create new one with private permissions"""
        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Hide from @everyone
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),  # Bot access
            }
            # Optionally grant access to admins or a moderator role
            admin_role = discord.utils.get(guild.roles, name="Admin") or discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True))
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        return channel

    def parse_amount(self, amount_str: str) -> tuple:
        """Parse and validate the amount string"""
        amount_str = amount_str.strip()
        currency_symbol = '$'  # Default
        if '₹' in amount_str:
            currency_symbol = '₹'
        cleaned_amount = amount_str.replace('$', '').replace('₹', '').strip()
        try:
            amount_float = float(cleaned_amount)
            if amount_float <= 0:
                raise ValueError("❌ Amount must be greater than 0")
            return amount_float, currency_symbol
        except ValueError as e:
            if str(e).startswith("❌"):
                raise ValueError(str(e))
            raise ValueError("❌ Invalid amount format. Please enter a number (e.g., 7000 or ₹7000)")

    def get_custom_dm_message(self, guild_id: str, action: str, guild: discord.Guild) -> str:
        """Get custom DM message for a specific action, falling back to default"""
        settings = JsonStorage().load_data('settings.json') or {}
        custom_messages = settings.get('custom_dm_messages', {})
        guild_messages = custom_messages.get(str(guild_id), {})
        default_messages = {
            'invoice': "📋 A new invoice has been created for you in {guild}. Please check it in the server!",
            'markpaid': "💰 Thank you for your purchase, come again! Your invoice ({invoice_id}) has been marked as paid in {guild}.",
            'cancelinvoice': "🚫 Your invoice ({invoice_id}) has been cancelled in {guild}. Contact support if needed."
        }
        return guild_messages.get(action, default_messages[action]).format(guild=guild.name, invoice_id="{invoice_id}")

    @app_commands.command(
        name='invoice',
        description='Create a new invoice'
    )
    @app_commands.describe(
        user="The user to invoice",
        service="Service being provided",
        amount="Amount to charge (e.g., 100 or ₹100)",
        payment_method="Method of payment"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def invoice(self, interaction: discord.Interaction, user: discord.Member, service: str, amount: str, payment_method: str):
        """Create a new invoice"""
        if interaction.id in self.processing_invoices:
            await interaction.response.send_message("⏳ Please wait, processing previous invoice...", ephemeral=True)
            return
        self.processing_invoices.add(interaction.id)

        try:
            amount_float, currency_symbol = self.parse_amount(amount)
            invoice_id = self.generate_invoice_id()
            pending_channel = await self.get_or_create_channel(interaction.guild, 'pending-invoices')

            embed = discord.Embed(
                title=f"📋 Invoice {invoice_id}",
                color=0xa46ffb
            )
            embed.add_field(name="👤 Client", value=user.mention, inline=True)
            embed.add_field(name="🔧 Service", value=service, inline=True)
            embed.add_field(name="💰 Amount", value=f"{currency_symbol}{amount_float:.2f}", inline=True)
            embed.add_field(name="💳 Payment Method", value=payment_method, inline=True)
            embed.add_field(name="📊 Status", value="⏳ Unpaid", inline=True)
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by Seculex | © 2025")

            await interaction.response.defer()
            await pending_channel.send(embed=embed)
            await interaction.followup.send(f"✅ Invoice {invoice_id} created successfully!")

            # Send DM to the user
            try:
                dm_message = self.get_custom_dm_message(str(interaction.guild.id), 'invoice', interaction.guild)
                dm_embed = discord.Embed(
                    title="📋 New Invoice",
                    description=dm_message,
                    color=0xa46ffb
                )
                dm_embed.add_field(name="Service", value=service, inline=True)
                dm_embed.add_field(name="Amount", value=f"{currency_symbol}{amount_float:.2f}", inline=True)
                dm_embed.add_field(name="Payment Method", value=payment_method, inline=True)
                try:
                    from footer import FOOTER_TEXT
                    dm_embed.set_footer(text=FOOTER_TEXT)
                except ImportError:
                    dm_embed.set_footer(text="Powered by Seculex | © 2025")
                await user.send(embed=dm_embed)
                logger.info(f"DM sent to {user.name} ({user.id}) for invoice {invoice_id}")
            except discord.Forbidden:
                await interaction.followup.send(f"⚠️ Could not send DM to {user.mention} (DMs disabled or blocked)", ephemeral=True)
                logger.warning(f"Failed to send DM to {user.name} ({user.id}) for invoice {invoice_id} due to Forbidden")
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error sending DM to {user.mention}: {str(e)}", ephemeral=True)
                logger.error(f"Error sending DM to {user.name} ({user.id}) for invoice {invoice_id}: {str(e)}")

        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
        finally:
            self.processing_invoices.remove(interaction.id)

    @app_commands.command(
        name='markpaid',
        description='Mark an invoice as paid'
    )
    @app_commands.describe(invoice_id="The ID of the invoice to mark as paid")
    @app_commands.checks.has_permissions(administrator=True)
    async def markpaid(self, interaction: discord.Interaction, invoice_id: str):
        """Mark an invoice as paid"""
        if invoice_id in self.processing_invoices:
            await interaction.response.send_message("⏳ Please wait, processing previous request...", ephemeral=True)
            return
        self.processing_invoices.add(invoice_id)

        try:
            await interaction.response.defer()

            pending_channel = await self.get_or_create_channel(interaction.guild, 'pending-invoices')
            paid_channel = await self.get_or_create_channel(interaction.guild, 'paid-invoices')
            invoice_found = False

            async for message in pending_channel.history(limit=None):
                if not message.embeds:
                    continue

                embed = message.embeds[0]
                if invoice_id in embed.title:
                    invoice_found = True
                    embed.color = 0xa46ffb

                    user_mention = None
                    for field in embed.fields:
                        if field.name == "👤 Client":
                            user_mention = field.value
                            break

                    for field in embed.fields:
                        if field.name == "📊 Status":
                            embed.remove_field(embed.fields.index(field))
                            embed.add_field(name="📊 Status", value="✅ Paid", inline=True)
                            break

                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by Seculex | © 2025")

                    await paid_channel.send(embed=embed)
                    await message.delete()
                    await interaction.followup.send(f"✅ Invoice {invoice_id} marked as paid!")

                    if user_mention:
                        try:
                            user = await commands.MemberConverter().convert(interaction, user_mention)
                            dm_message = self.get_custom_dm_message(str(interaction.guild.id), 'markpaid', interaction.guild).format(invoice_id=invoice_id)
                            dm_embed = discord.Embed(
                                title="💰 Invoice Paid",
                                description=dm_message,
                                color=0xa46ffb
                            )
                            try:
                                from footer import FOOTER_TEXT
                                dm_embed.set_footer(text=FOOTER_TEXT)
                            except ImportError:
                                dm_embed.set_footer(text="Powered by Seculex | © 2025")
                            await user.send(embed=dm_embed)
                            logger.info(f"DM sent to {user.name} ({user.id}) for paid invoice {invoice_id}")
                        except discord.Forbidden:
                            await interaction.followup.send(f"⚠️ Could not send DM to {user_mention} (DMs disabled or blocked)", ephemeral=True)
                            logger.warning(f"Failed to send DM to {user_mention} for paid invoice {invoice_id} due to Forbidden")
                        except Exception as e:
                            await interaction.followup.send(f"⚠️ Error sending DM to {user_mention}: {str(e)}", ephemeral=True)
                            logger.error(f"Error sending DM to {user_mention} for paid invoice {invoice_id}: {str(e)}")
                    break

            if not invoice_found:
                await interaction.followup.send("❌ Invoice not found!", ephemeral=True)

        finally:
            self.processing_invoices.remove(invoice_id)

    @app_commands.command(
        name='cancelinvoice',
        description='Cancel an invoice'
    )
    @app_commands.describe(invoice_id="The ID of the invoice to cancel")
    @app_commands.checks.has_permissions(administrator=True)
    async def cancelinvoice(self, interaction: discord.Interaction, invoice_id: str):
        """Cancel an invoice and move it to the cancelled-invoices channel"""
        if invoice_id in self.processing_invoices:
            await interaction.response.send_message("⏳ Please wait, processing previous request...", ephemeral=True)
            return
        self.processing_invoices.add(invoice_id)

        try:
            await interaction.response.defer()

            pending_channel = await self.get_or_create_channel(interaction.guild, 'pending-invoices')
            cancelled_channel = await self.get_or_create_channel(interaction.guild, 'cancelled-invoices')
            invoice_found = False

            async for message in pending_channel.history(limit=None):
                if not message.embeds:
                    continue

                embed = message.embeds[0]
                if invoice_id in embed.title:
                    invoice_found = True
                    embed.color = 0xa46ffb

                    user_mention = None
                    for field in embed.fields:
                        if field.name == "👤 Client":
                            user_mention = field.value
                            break

                    for field in embed.fields:
                        if field.name == "📊 Status":
                            embed.remove_field(embed.fields.index(field))
                            embed.add_field(name="📊 Status", value="❌ Cancelled", inline=True)
                            break

                    try:
                        from footer import FOOTER_TEXT
                        embed.set_footer(text=FOOTER_TEXT)
                    except ImportError:
                        embed.set_footer(text="Powered by Seculex | © 2025")

                    await cancelled_channel.send(embed=embed)
                    await message.delete()
                    await interaction.followup.send(f"✅ Invoice {invoice_id} cancelled!")

                    if user_mention:
                        try:
                            user = await commands.MemberConverter().convert(interaction, user_mention)
                            dm_message = self.get_custom_dm_message(str(interaction.guild.id), 'cancelinvoice', interaction.guild).format(invoice_id=invoice_id)
                            dm_embed = discord.Embed(
                                title="🚫 Invoice Cancelled",
                                description=dm_message,
                                color=0xa46ffb
                            )
                            try:
                                from footer import FOOTER_TEXT
                                dm_embed.set_footer(text=FOOTER_TEXT)
                            except ImportError:
                                dm_embed.set_footer(text="Powered by Seculex | © 2025")
                            await user.send(embed=dm_embed)
                            logger.info(f"DM sent to {user.name} ({user.id}) for cancelled invoice {invoice_id}")
                        except discord.Forbidden:
                            await interaction.followup.send(f"⚠️ Could not send DM to {user_mention} (DMs disabled or blocked)", ephemeral=True)
                            logger.warning(f"Failed to send DM to {user_mention} for cancelled invoice {invoice_id} due to Forbidden")
                        except Exception as e:
                            await interaction.followup.send(f"⚠️ Error sending DM to {user_mention}: {str(e)}", ephemeral=True)
                            logger.error(f"Error sending DM to {user_mention} for cancelled invoice {invoice_id}: {str(e)}")
                    break

            if not invoice_found:
                await interaction.followup.send("❌ Invoice not found!", ephemeral=True)

        finally:
            self.processing_invoices.remove(invoice_id)

    @app_commands.command(
        name='pendinginvoices',
        description='List all pending invoices'
    )
    async def pendinginvoices(self, interaction: discord.Interaction):
        """List all pending invoices"""
        await interaction.response.defer()

        pending_channel = await self.get_or_create_channel(interaction.guild, 'pending-invoices')

        embed = discord.Embed(
            title="📋 Pending Invoices",
            color=0xa46ffb
        )

        count = 0
        async for message in pending_channel.history():
            if message.embeds:
                invoice_embed = message.embeds[0]
                embed.add_field(
                    name=invoice_embed.title,
                    value=f"👤 Client: {invoice_embed.fields[0].value}\n"
                          f"💰 Amount: {invoice_embed.fields[2].value}",
                    inline=False
                )
                count += 1

        if count == 0:
            embed.description = "📭 No pending invoices"

        try:
            from footer import FOOTER_TEXT
            embed.set_footer(text=FOOTER_TEXT)
        except ImportError:
            embed.set_footer(text="Powered by Seculex | © 2025")
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='set_dm_message',
        description='Set a custom DM message for invoice actions'
    )
    @app_commands.describe(
        action="Action to set message for (invoice/markpaid/cancelinvoice)",
        message="Custom message (use {guild} for guild name, {invoice_id} for invoice ID)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Invoice Created", value="invoice"),
        app_commands.Choice(name="Mark Paid", value="markpaid"),
        app_commands.Choice(name="Cancel Invoice", value="cancelinvoice")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def set_dm_message(self, interaction: discord.Interaction, action: app_commands.Choice[str], message: str):
        """Set a custom DM message for a specific invoice action per guild"""
        settings = JsonStorage().load_data('settings.json') or {}
        guild_id = str(interaction.guild.id)
        if 'custom_dm_messages' not in settings:
            settings['custom_dm_messages'] = {}
        if guild_id not in settings['custom_dm_messages']:
            settings['custom_dm_messages'][guild_id] = {}
        settings['custom_dm_messages'][guild_id][action.value] = message
        JsonStorage().save_data('settings.json', settings)
        await interaction.response.send_message(f"✅ Custom DM message set for {action.name} in {interaction.guild.name}!", ephemeral=True)
        logger.info(f"Custom DM message set for {action.value} by {interaction.user.name} in guild {guild_id}")

async def setup(bot):
    await bot.add_cog(Invoice(bot))