import os
from dotenv import load_dotenv

class ConfigurationManager:
    """
    Centralized manager for application configuration.
    Responsible for loading environment variables and providing access to settings.
    """

    def __init__(self):
        # Set the base directory of the application
        self.base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # Initialize configurations
        self._db_connections = self._load_database_connections()

    def _load_database_connections(self):
        """
        Dynamically loads all database connection strings from environment variables
        that start with 'SQL_SERVER'.

        :return: A dictionary of database keys and connection strings.
        """
        return {
            key[len("SQL_SERVER_"):]: value  # Strip "SQL_SERVER_" prefix from keys
            for key, value in os.environ.items()
            if key.startswith("SQL_SERVER_")
        }

    def get_database_connection_string(self, db_key: str) -> str:
        """
        Returns the connection string for the specified database key.

        :param db_key: The key identifying the database (e.g., 'DbLogs').
        :return: The database connection string.
        """
        connection_string = self._db_connections.get(db_key)
        if not connection_string:
            raise ValueError(f"Connection string for '{db_key}' not found.")
        return connection_string

    def get_all_database_connections(self):
        """
        Returns all database connections.

        :return: A dictionary of all database keys and their connection strings.
        """
        return self._db_connections

    def get(self, key: str) -> str:
        """
        Returns the value for the given key from the environment variables.

        :param key: The key identifying the configuration setting.
        :return: The configuration value.
        """
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found in the environment variables.")
        return value