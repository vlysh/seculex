import discord
from discord.ext import commands
from discord import app_commands
import math
import re
import logging

logger = logging.getLogger('discord')

class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Calculator cog initialized")

    async def cog_load(self):
        """Called when the cog is loaded"""
        logger.info("Calculator cog loaded")

    def calculate(self, expression: str) -> float:
        """Safely evaluate a mathematical expression"""
        # Remove all whitespace
        expression = ''.join(expression.split())

        # Check for valid characters
        if not re.match(r'^[\d\+\-\*\/\(\)\.\^\s]*$', expression):
            raise ValueError("Invalid characters in expression")

        # Convert ^ to ** for exponentiation
        expression = expression.replace('^', '**')

        # Basic security check
        if any(keyword in expression.lower() for keyword in ['import', 'eval', 'exec', '__']):
            raise ValueError("Invalid expression")

        try:
            # Use eval with limited scope for basic arithmetic
            allowed_names = {
                "math": math,
                "pi": math.pi,  # Add pi as a standalone constant
                "e": math.e     # Add e as a standalone constant
            }
            code = compile(expression, "<string>", "eval")

            for name in code.co_names:
                if name not in allowed_names and name not in dir(math):
                    raise NameError(f"Use of {name} not allowed")

            result = eval(code, {"__builtins__": {}}, allowed_names)

            # Handle formatting for readability
            if isinstance(result, (int, float)):
                # For very large or small numbers, use scientific notation
                if abs(result) > 1e6 or (0 < abs(result) < 1e-6):
                    formatted_result = f"{result:.6e}"
                else:
                    # Round to 6 decimal places for readability
                    formatted_result = f"{result:.6f}".rstrip('0').rstrip('.')
                return formatted_result
            return str(result)

        except Exception as e:
            raise ValueError(f"Error calculating result: {str(e)}")

    @app_commands.command()
    @app_commands.describe(
        expression="The mathematical expression to calculate (e.g., 2 + 2 or 5 * (3 + 2))"
    )
    async def calc(self, interaction: discord.Interaction, expression: str):
        """Calculate a mathematical expression"""
        try:
            await interaction.response.defer()

            result = self.calculate(expression)

            embed = discord.Embed(
                title="📊 Calculator",
                description=(
                    f"**Expression:** `{expression}`\n"
                    f"**Result:** `{result}`\n\n"
                ),
                color=discord.Color.blue()
            )
            try:
                from footer import FOOTER_TEXT
                embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                embed.set_footer(text="Powered by SECULEX | © 2025")

            await interaction.followup.send(embed=embed)

        except ValueError as e:
            error_embed = discord.Embed(
                title="❌ Calculator Error",
                description=str(e),
                color=discord.Color.red()
            )
            try:
                from footer import FOOTER_TEXT
                error_embed.set_footer(text=FOOTER_TEXT)
            except ImportError:
                error_embed.set_footer(text="Powered by SECULEX | © 2025")
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Calculator(bot))