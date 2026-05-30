import os
import sys
import time
import subprocess
import logging
from replit import db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bot_manager')

def run_bot():
    while True:
        try:
            # Check if restart was requested
            restart_requested = db.get("restart", False)
            if restart_requested:
                logger.info("Restart flag detected, clearing flag...")
                db["restart"] = False
                time.sleep(5)  # Wait 5 seconds before restarting
            
            logger.info("Starting bot process...")
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Monitor the process
            while process.poll() is None:
                # Check for restart flag while bot is running
                if db.get("restart", False):
                    logger.info("Restart requested, terminating current process...")
                    process.terminate()
                    try:
                        process.wait(timeout=10)  # Wait up to 10 seconds for clean shutdown
                    except subprocess.TimeoutExpired:
                        process.kill()  # Force kill if it doesn't shut down cleanly
                    break
                time.sleep(1)  # Check every second
            
            # If process ended without restart flag, wait before restarting
            if not db.get("restart", False):
                logger.warning("Bot process ended unexpectedly")
                time.sleep(5)  # Wait 5 seconds before restarting
            
        except Exception as e:
            logger.error(f"Error in bot manager: {str(e)}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    logger.info("Bot manager starting...")
    # Initialize restart flag to False on startup
    db["restart"] = False
    run_bot()
