import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CommandAnalytics:
    def __init__(self):
        self.analytics_file = 'data/command_analytics.json'
        self.analytics_data = self._load_analytics()

    def _load_analytics(self) -> Dict:
        """Load analytics data from file"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._initialize_analytics()
        return self._initialize_analytics()

    def _initialize_analytics(self) -> Dict:
        """Initialize analytics data structure"""
        return {
            'commands': {},
            'total_slash_commands': 0,
            'total_prefix_commands': 0,
            'daily_usage': {}
        }

    def _save_analytics(self):
        """Save analytics data to file"""
        os.makedirs(os.path.dirname(self.analytics_file), exist_ok=True)
        with open(self.analytics_file, 'w') as f:
            json.dump(self.analytics_data, f, indent=4)

    def log_command(self, command_name: str, is_slash: bool, guild_id: Optional[str] = None):
        """Log a command usage"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Initialize command data if not exists
        if command_name not in self.analytics_data['commands']:
            self.analytics_data['commands'][command_name] = {
                'slash_uses': 0,
                'prefix_uses': 0,
                'guild_usage': {}
            }

        # Update command-specific stats
        cmd_data = self.analytics_data['commands'][command_name]
        if is_slash:
            cmd_data['slash_uses'] += 1
            self.analytics_data['total_slash_commands'] += 1
        else:
            cmd_data['prefix_uses'] += 1
            self.analytics_data['total_prefix_commands'] += 1

        # Update guild-specific stats if guild_id provided
        if guild_id:
            if guild_id not in cmd_data['guild_usage']:
                cmd_data['guild_usage'][guild_id] = {
                    'slash_uses': 0,
                    'prefix_uses': 0
                }
            if is_slash:
                cmd_data['guild_usage'][guild_id]['slash_uses'] += 1
            else:
                cmd_data['guild_usage'][guild_id]['prefix_uses'] += 1

        # Update daily usage
        if today not in self.analytics_data['daily_usage']:
            self.analytics_data['daily_usage'][today] = {
                'slash_commands': 0,
                'prefix_commands': 0
            }
        if is_slash:
            self.analytics_data['daily_usage'][today]['slash_commands'] += 1
        else:
            self.analytics_data['daily_usage'][today]['prefix_commands'] += 1

        self._save_analytics()

    def get_command_stats(self, command_name: str) -> Dict:
        """Get usage statistics for a specific command"""
        return self.analytics_data['commands'].get(command_name, {
            'slash_uses': 0,
            'prefix_uses': 0,
            'guild_usage': {}
        })

    def get_daily_stats(self, date: str = None) -> Dict:
        """Get daily usage statistics"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        return self.analytics_data['daily_usage'].get(date, {
            'slash_commands': 0,
            'prefix_commands': 0
        })

    def get_preferred_style(self) -> str:
        """Get the overall preferred command style"""
        slash = self.analytics_data['total_slash_commands']
        prefix = self.analytics_data['total_prefix_commands']
        
        if slash == prefix == 0:
            return "No commands used yet"
        elif slash > prefix:
            percentage = (slash / (slash + prefix)) * 100
            return f"Slash Commands ({percentage:.1f}%)"
        else:
            percentage = (prefix / (slash + prefix)) * 100
            return f"Prefix Commands ({percentage:.1f}%)"
