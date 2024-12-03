import os
from config.configuration_manager import ConfigurationManager
from helpers.database_connector import DatabaseConnector
from services.json_file_manager import JsonFileManager
from config.constants import COMPANY, APP_NAME, VERSION, set_app_metadata


def main():
    # Initialize the ConfigurationManager
    config_manager = ConfigurationManager()
    json_manager = JsonFileManager(config_manager)


if __name__ == "__main__":
    main()
