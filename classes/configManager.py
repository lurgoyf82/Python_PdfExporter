import json
import os
import time
from sqlalchemy.sql.functions import concat


# Configuration Manager Class
class ConfigManager:
    def __init__(self, config_file, logger):
        self.config_file = config_file
        self.logger = logger
        self.config = {}
        self.load_config()

    def load_config(self):
        try:
            if not os.path.exists(self.config_file):
                self.create_default_config()
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            self.logger.info("Configuration loaded successfully.")
        except Exception as e:
            self.logger.exception(f"Failed to load configuration: {e}")
            self.config = {}
            self.create_default_config()

    def create_default_config(self):
        default_config = {
            "input_folder": r"C:\Program Files\PdfExporter\Input",
            "destination_folder": r"\\NAS\Shared\Destination",
            "waiting_folder": r"C:\Program Files\PdfExporter\Waiting",
            "error_folder": r"C:\Program Files\PdfExporter\Error"
        }
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        self.logger.info("Default configuration created.")
        self.config = default_config

    def get_input_folder(self):
        return self.config.get('input_folder')

    def get_destination_folder(self):
        return self.config.get('destination_folder')

    def get_waiting_folder(self):
        return self.config.get('waiting_folder')

    def get_error_folder(self):
        return self.config.get('error_folder')

    def get_current_progressive_number(self):
        return self.config.get(concat('progressive_number_', time.strftime('%Y')))