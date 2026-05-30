import os
import shutil
from datetime import datetime
import json

class BackupManager:
    def __init__(self):
        self.backup_dir = 'backups'
        self.current_backup = None
        self.backup_manifest = 'backup_manifest.json'
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self, name=None):
        """Create a new backup with optional name"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{name}_{timestamp}" if name else timestamp
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Create backup directory
            os.makedirs(backup_path)
            
            # Copy all Python files from cogs directory
            if os.path.exists('cogs'):
                shutil.copytree('cogs', os.path.join(backup_path, 'cogs'))
            
            # Copy main configuration and python files
            important_files = ['main.py', 'config.json']
            for file in important_files:
                if os.path.exists(file):
                    shutil.copy2(file, backup_path)
            
            # Save backup info
            backup_info = {
                'timestamp': timestamp,
                'name': name,
                'files': [
                    os.path.relpath(os.path.join(root, file), backup_path)
                    for root, _, files in os.walk(backup_path)
                    for file in files
                ]
            }
            
            with open(os.path.join(backup_path, 'backup_info.json'), 'w') as f:
                json.dump(backup_info, f, indent=4)
            
            self.current_backup = backup_path
            return True, f"Backup created successfully at {backup_path}"
            
        except Exception as e:
            return False, f"Failed to create backup: {str(e)}"
    
    def list_backups(self):
        """List all available backups"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for backup in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup)
            info_path = os.path.join(backup_path, 'backup_info.json')
            
            if os.path.isdir(backup_path) and os.path.exists(info_path):
                with open(info_path) as f:
                    info = json.load(f)
                    backups.append(info)
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def restore_backup(self, backup_name):
        """Restore from a specific backup"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return False, "Backup not found"
        
        try:
            # Restore cogs directory
            cogs_backup = os.path.join(backup_path, 'cogs')
            if os.path.exists(cogs_backup):
                if os.path.exists('cogs'):
                    shutil.rmtree('cogs')
                shutil.copytree(cogs_backup, 'cogs')
            
            # Restore main files
            for file in os.listdir(backup_path):
                if file in ['main.py', 'config.json']:
                    shutil.copy2(os.path.join(backup_path, file), file)
            
            return True, f"Successfully restored from backup {backup_name}"
            
        except Exception as e:
            return False, f"Failed to restore backup: {str(e)}"
