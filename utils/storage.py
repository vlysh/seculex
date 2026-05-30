import json
import os
import logging

# Configure logging for this module
logger = logging.getLogger("storage")

class JsonStorage:
    def __init__(self):
        """Initialize JsonStorage and ensure data directory exists."""
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)  # Create data directory if it doesn't exist

    def load_data(self, filename):
        """Load JSON data from a file in the data directory

        Args:
            filename: Name of the JSON file to load

        Returns:
            dict: The loaded JSON data, or empty dict if file doesn't exist or is invalid
        """
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logger.info(f"File {filepath} not found, returning empty dict")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning(f"Invalid data format in {filepath}, expected dict, got {type(data)}")
                    return {}
                return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filepath}: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error loading {filepath}: {str(e)}")
            return {}

    def save_data(self, filename, data):
        """Save data to a JSON file in the data directory

        Args:
            filename: Name of the JSON file to save to
            data: The data to save (must be JSON serializable)

        Raises:
            ValueError: If data is not JSON serializable
            IOError: If file cannot be written
        """
        filepath = os.path.join(self.data_dir, filename)
        # Basic check for JSON serializability
        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            logger.error(f"Data for {filepath} is not JSON serializable: {str(e)}")
            raise ValueError(f"Data is not JSON serializable: {str(e)}")

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Successfully saved data to {filepath}")
        except IOError as e:
            logger.error(f"Failed to save data to {filepath}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving {filepath}: {str(e)}")
            raise