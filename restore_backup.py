import sys
from utils.backup import BackupManager

def main():
    if len(sys.argv) < 2:
        # List available backups if no backup name provided
        backup_manager = BackupManager()
        backups = backup_manager.list_backups()
        
        if not backups:
            print("No backups found!")
            return
        
        print("\nAvailable backups:")
        for backup in backups:
            name = backup['name'] or 'Unnamed backup'
            timestamp = backup['timestamp']
            print(f"- {name} (Created: {timestamp})")
        print("\nTo restore a backup, run: python restore_backup.py <backup_name>")
        return

    backup_name = sys.argv[1]
    backup_manager = BackupManager()
    success, message = backup_manager.restore_backup(backup_name)
    
    if success:
        print(f"✅ {message}")
        print("\nPlease restart your bot for the changes to take effect.")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    main()
