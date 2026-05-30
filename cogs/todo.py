import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import json
from utils.storage import JsonStorage
from datetime import datetime, timedelta
import logging
import pytz
from footer import FOOTER_TEXT  # Import the footer text from footer.py

# Configure logging for this file
logger = logging.getLogger(__name__)

class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        self.tasks: dict = self.storage.load_data('todo.json') or {}
        # Migrate old structure ({"guild_id": [tasks]}) to new structure ({"guild_id": {"user_id": [tasks]}})
        migrated_tasks = {}
        for guild_id, guild_tasks in self.tasks.items():
            if isinstance(guild_tasks, list):  # Old structure detected
                logger.info(f"Migrating old task structure for guild {guild_id}")
                migrated_tasks[guild_id] = {}
                for task in guild_tasks:
                    user_id = str(task.get("added_by", 0))  # Use added_by as user_id
                    if user_id not in migrated_tasks[guild_id]:
                        migrated_tasks[guild_id][user_id] = []
                    migrated_tasks[guild_id][user_id].append(task)
            else:  # Already in new structure
                migrated_tasks[guild_id] = guild_tasks
        self.tasks = migrated_tasks
        self.storage.save_data('todo.json', self.tasks)  # Save migrated structure
        logger.info(f"Initial tasks structure after migration: {json.dumps(self.tasks, indent=2)}")
        self.check_deadlines.start()  # Start the deadline checking task

    def cog_unload(self):
        self.check_deadlines.cancel()  # Cancel the task when cog unloads

    @tasks.loop(seconds=60)  # Check every minute
    async def check_deadlines(self):
        """Background task to check and send deadline reminders"""
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist)  # Use timezone-aware current time
        for guild_id, guild_tasks in self.tasks.items():  # guild_id -> {user_id: [tasks]}
            if not isinstance(guild_tasks, dict):
                logger.error(f"Guild {guild_id} tasks is not a dictionary: {guild_tasks}")
                continue
            for user_id, user_tasks in guild_tasks.items():  # user_id -> [tasks]
                if not isinstance(user_tasks, list):
                    logger.error(f"User {user_id} tasks in guild {guild_id} is not a list: {user_tasks}")
                    continue
                for task in user_tasks:
                    if not task.get("completed", False):
                        deadline_str = task.get("deadline")
                        if deadline_str:
                            try:
                                deadline = datetime.fromisoformat(deadline_str)
                                # Ensure both datetimes are in the same timezone for comparison
                                current_time_ist = current_time.astimezone(ist)
                                deadline_ist = deadline.astimezone(ist)
                                warning_time = deadline_ist - timedelta(minutes=15)
                                if current_time_ist >= warning_time and current_time_ist < deadline_ist:  # 15-min warning
                                    guild = self.bot.get_guild(int(guild_id))
                                    if guild:
                                        user = guild.get_member(int(user_id))
                                        if user and not task.get("reminder_sent", False):
                                            deadline_formatted = deadline_ist.strftime('%d/%m/%y %H:%M:%S IST')
                                            embed = discord.Embed(
                                                title="⏰ Task Deadline Approaching!",
                                                description=f"Your task '{task['task']}' is due soon! Deadline: {deadline_formatted}",
                                                color=discord.Color.orange()
                                            )
                                            embed.add_field(name="Assigned by", value=f"<@{task['added_by']}>", inline=True)
                                            embed.set_footer(text=FOOTER_TEXT)  # Use centralized footer
                                            try:
                                                await user.send(embed=embed)
                                                task["reminder_sent"] = True
                                                self.storage.save_data('todo.json', self.tasks)
                                                logger.info(f"Deadline reminder sent to {user.name} ({user_id}) in guild {guild_id}")
                                            except discord.Forbidden:
                                                logger.warning(f"Could not send deadline reminder to {user.name} ({user_id}) in guild {guild_id}")
                            except ValueError:
                                logger.error(f"Invalid deadline format for task in guild {guild_id}, user {user_id}")
                                continue

    # Modal for Add Task
    class AddTaskModal(discord.ui.Modal, title="Add a New Task"):
        task_input = discord.ui.TextInput(label="Task", placeholder="e.g., Finish project", required=True)
        deadline_input = discord.ui.TextInput(label="Deadline (e.g., 1h, 1d, 1w)", placeholder="Optional", required=False, default="")
        priority_input = discord.ui.TextInput(label="Priority (low/medium/high)", placeholder="e.g., high", required=False, default="medium")

        def __init__(self, cog):
            super().__init__()
            self.cog = cog  # Store the cog instance

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            if guild_id not in self.cog.tasks:
                self.cog.tasks[guild_id] = {}
            if user_id not in self.cog.tasks[guild_id]:
                self.cog.tasks[guild_id][user_id] = []

            # Parse deadline
            deadline_dt = None
            deadline = self.deadline_input.value.strip()
            if deadline:
                duration = 0
                if deadline.endswith('h'):
                    duration = int(deadline[:-1]) * 3600
                elif deadline.endswith('d'):
                    duration = int(deadline[:-1]) * 86400
                elif deadline.endswith('w'):
                    duration = int(deadline[:-1]) * 604800
                else:
                    await interaction.response.send_message("❌ Invalid deadline format! Use '1h', '1d', or '1w'.", ephemeral=True)
                    return
                ist = pytz.timezone('Asia/Kolkata')
                deadline_dt = ist.localize(datetime.now() + timedelta(seconds=duration)).isoformat()

            priority = self.priority_input.value.strip().lower()
            valid_priorities = ["low", "medium", "high"]
            if priority not in valid_priorities:
                await interaction.response.send_message("❌ Invalid priority! Use 'low', 'medium', or 'high'.", ephemeral=True)
                return

            self.cog.tasks[guild_id][user_id].append({
                "task": self.task_input.value,
                "deadline": deadline_dt,
                "assigned_to": None,
                "completed": False,
                "priority": priority,
                "added_by": interaction.user.id,
                "timestamp": datetime.now().isoformat(),
                "reminder_sent": False
            })
            self.cog.storage.save_data('todo.json', self.cog.tasks)
            await interaction.response.send_message(f"✅ Added task: '{self.task_input.value}' with deadline {deadline if deadline else 'None'}, Priority: {priority}", ephemeral=True)
            logger.info(f"Task '{self.task_input.value}' added by {interaction.user.name} ({user_id}) in guild {guild_id}")

    # Modal for Edit Task
    class EditTaskModal(discord.ui.Modal, title="Edit a Task"):
        task_input = discord.ui.TextInput(label="New Task", placeholder="e.g., Update project", required=True)
        deadline_input = discord.ui.TextInput(label="New Deadline (e.g., 1h, 1d, 1w)", placeholder="Optional", required=False, default="")
        index_input = discord.ui.TextInput(label="Task Index", placeholder="e.g., 1", required=True)

        def __init__(self, cog):
            super().__init__()
            self.cog = cog  # Store the cog instance

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            if guild_id not in self.cog.tasks or user_id not in self.cog.tasks[guild_id] or not self.cog.tasks[guild_id][user_id]:
                await interaction.response.send_message("❌ No tasks found for you!", ephemeral=True)
                return

            try:
                index = int(self.index_input.value) - 1
                if index < 0 or index >= len(self.cog.tasks[guild_id][user_id]):
                    await interaction.response.send_message("❌ Invalid task index!", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Index must be a number!", ephemeral=True)
                return

            task = self.cog.tasks[guild_id][user_id][index]
            task["task"] = self.task_input.value

            if self.deadline_input.value.strip():
                deadline = self.deadline_input.value.strip()
                duration = 0
                if deadline.endswith('h'):
                    duration = int(deadline[:-1]) * 3600
                elif deadline.endswith('d'):
                    duration = int(deadline[:-1]) * 86400
                elif deadline.endswith('w'):
                    duration = int(deadline[:-1]) * 604800
                else:
                    await interaction.response.send_message("❌ Invalid deadline format! Use '1h', '1d', or '1w'.", ephemeral=True)
                    return
                ist = pytz.timezone('Asia/Kolkata')
                task["deadline"] = ist.localize(datetime.now() + timedelta(seconds=duration)).isoformat()
                task["reminder_sent"] = False  # Reset reminder for new deadline

            self.cog.storage.save_data('todo.json', self.cog.tasks)
            await interaction.response.send_message(f"✅ Task {index + 1} updated to '{self.task_input.value}' with deadline {self.deadline_input.value if self.deadline_input.value else task.get('deadline', 'None')}", ephemeral=True)
            logger.info(f"Task {index + 1} edited by {interaction.user.name} ({user_id}) in guild {guild_id}")

    # Modal for Complete Task
    class CompleteTaskModal(discord.ui.Modal, title="Complete a Task"):
        index_input = discord.ui.TextInput(label="Task Index", placeholder="e.g., 1", required=True)

        def __init__(self, cog):
            super().__init__()
            self.cog = cog  # Store the cog instance

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            if guild_id not in self.cog.tasks or user_id not in self.cog.tasks[guild_id] or not self.cog.tasks[guild_id][user_id]:
                await interaction.response.send_message("❌ No tasks found for you!", ephemeral=True)
                return

            try:
                index = int(self.index_input.value) - 1
                if index < 0 or index >= len(self.cog.tasks[guild_id][user_id]):
                    await interaction.response.send_message("❌ Invalid task index!", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Index must be a number!", ephemeral=True)
                return

            task = self.cog.tasks[guild_id][user_id][index]
            task["completed"] = True
            self.cog.storage.save_data('todo.json', self.cog.tasks)
            await interaction.response.send_message(f"✅ Task {index + 1} marked as completed!", ephemeral=True)
            logger.info(f"Task {index + 1} completed by {interaction.user.name} ({user_id}) in guild {guild_id}")

    # Modal for Delete Task
    class DeleteTaskModal(discord.ui.Modal, title="Delete a Task"):
        index_input = discord.ui.TextInput(label="Task Index", placeholder="e.g., 1", required=True)

        def __init__(self, cog):
            super().__init__()
            self.cog = cog  # Store the cog instance

        async def on_submit(self, interaction: discord.Interaction):
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            if guild_id not in self.cog.tasks or user_id not in self.cog.tasks[guild_id] or not self.cog.tasks[guild_id][user_id]:
                await interaction.response.send_message("❌ No tasks found for you!", ephemeral=True)
                return

            try:
                index = int(self.index_input.value) - 1
                if index < 0 or index >= len(self.cog.tasks[guild_id][user_id]):
                    await interaction.response.send_message("❌ Invalid task index!", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Index must be a number!", ephemeral=True)
                return

            task = self.cog.tasks[guild_id][user_id].pop(index)
            if not self.cog.tasks[guild_id][user_id]:  # If no tasks left, clean up
                del self.cog.tasks[guild_id][user_id]
                if not self.cog.tasks[guild_id]:
                    del self.cog.tasks[guild_id]
            self.cog.storage.save_data('todo.json', self.cog.tasks)
            await interaction.response.send_message(f"🗑️ Task {index + 1} deleted!", ephemeral=True)
            logger.info(f"Task {index + 1} deleted by {interaction.user.name} ({user_id}) in guild {guild_id}")

    # View for Task Actions
    class TaskView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog  # Store the cog instance

        @discord.ui.button(label="Add Task", style=discord.ButtonStyle.green, custom_id="add_task")
        async def add_task_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Todo.AddTaskModal(self.cog)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="View Tasks", style=discord.ButtonStyle.primary, custom_id="view_tasks")
        async def view_tasks_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            if guild_id not in self.cog.tasks or user_id not in self.cog.tasks[guild_id] or not self.cog.tasks[guild_id][user_id]:
                embed = discord.Embed(
                    title="📭 No Tasks Available",
                    description="You don't have any tasks to show. Add a task to get started!",
                    color=discord.Color.orange()
                )
                embed.set_footer(text=FOOTER_TEXT)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = discord.Embed(
                title="📝 Your To-Do List",
                description="Here are your tasks:",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            for i, task_data in enumerate(self.cog.tasks[guild_id][user_id], 1):
                status = "✅" if task_data["completed"] else "⏳"
                embed.add_field(
                    name=f"Task {i} {status}",
                    value=f"**Task**: {task_data['task']}\n**Priority**: {task_data['priority']}\n**Deadline**: {task_data.get('deadline', 'None')}",
                    inline=False
                )
            embed.set_footer(text=FOOTER_TEXT)  # Use centralized footer
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @discord.ui.button(label="Complete Task", style=discord.ButtonStyle.success, custom_id="complete_task")
        async def complete_task_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Todo.CompleteTaskModal(self.cog)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Delete Task", style=discord.ButtonStyle.danger, custom_id="delete_task")
        async def delete_task_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Todo.DeleteTaskModal(self.cog)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Edit Task", style=discord.ButtonStyle.primary, custom_id="edit_task")
        async def edit_task_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = Todo.EditTaskModal(self.cog)
            await interaction.response.send_modal(modal)

    @app_commands.command(name="task", description="Manage your personal to-do list")
    async def task(self, interaction: discord.Interaction):
        """Manage your personal to-do list with interactive buttons"""
        embed = discord.Embed(
            title="📋 To-Do List Manager",
            description="Select an action below to manage your tasks:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Available Actions",
            value="✅ Add Task\nℹ️ View Tasks\n✔️ Complete Task\n🗑️ Delete Task\n✏️ Edit Task",
            inline=False
        )
        embed.set_footer(text=FOOTER_TEXT)  # Use centralized footer

        view = self.TaskView(self)  # Pass the cog instance
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="assign", description="Assign a task to a user with a deadline")
    @app_commands.describe(user="The user to assign the task to", task="The task to assign", deadline="Deadline (e.g., 1h, 1d, 1w)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def assign(self, interaction: discord.Interaction, user: discord.Member, task: str, deadline: str):
        """Assign a task to a user with a deadline and send a DM"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.tasks:
            self.tasks[guild_id] = {}
        user_id = str(user.id)
        if user_id not in self.tasks[guild_id]:
            self.tasks[guild_id][user_id] = []

        # Parse deadline
        duration = 0
        if deadline.endswith('h'):
            duration = int(deadline[:-1]) * 3600
        elif deadline.endswith('d'):
            duration = int(deadline[:-1]) * 86400
        elif deadline.endswith('w'):
            duration = int(deadline[:-1]) * 604800
        else:
            await interaction.response.send_message("❌ Invalid deadline format! Use '1h', '1d', or '1w'.", ephemeral=True)
            return
        # Set to GMT+5:30
        ist = pytz.timezone('Asia/Kolkata')
        deadline_dt = ist.localize(datetime.now() + timedelta(seconds=duration)).isoformat()

        self.tasks[guild_id][user_id].append({
            "task": task,
            "deadline": deadline_dt,
            "assigned_to": user.id,
            "completed": False,  # Fixed: Changed 'false' to 'False'
            "priority": "medium",
            "added_by": interaction.user.id,
            "timestamp": datetime.now().isoformat(),
            "reminder_sent": False  # Fixed: Changed 'false' to 'False'
        })
        self.storage.save_data('todo.json', self.tasks)

        # Send DM to the user with formatted deadline
        deadline_formatted = datetime.fromisoformat(deadline_dt).astimezone(ist).strftime('%d/%m/%y %H:%M:%S IST')
        embed = discord.Embed(
            title="📋 Task Assigned!",
            description=f"You have been assigned a task by {interaction.user.mention}: '{task}'",
            color=discord.Color.green()
        )
        embed.add_field(name="Deadline", value=deadline_formatted, inline=True)
        embed.set_footer(text=FOOTER_TEXT)  # Use centralized footer
        try:
            await user.send(embed=embed)
            await interaction.response.send_message(f"✅ Task '{task}' assigned to {user.mention} with deadline {deadline}!", ephemeral=True)
            logger.info(f"Task '{task}' assigned to {user.name} by {interaction.user.name} in guild {guild_id}")
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ Could not send DM to {user.mention}!", ephemeral=True)
            logger.warning(f"Failed to send DM to {user.name} for task assignment in guild {guild_id}")

async def setup(bot):
    await bot.add_cog(Todo(bot))