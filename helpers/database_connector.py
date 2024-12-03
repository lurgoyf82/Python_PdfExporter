# helpers/database_connector.py
import re

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus
from typing import Optional

class DatabaseConnector:
    """
    A class to manage database connections using a provided connection string.
    """

    def __init__(self, connection_string: str):
        """
        Initializes the DatabaseConnector with the provided connection string.

        :param connection_string: The database connection string.
        """
        self.connection_string = connection_string
        self.engine: Optional[Engine] = None
        self.database_name = None

    def connect(self):
        """
        Establishes a connection to the database using the provided connection string.
        """
        connection_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(self.connection_string)}"
        self.engine = create_engine(connection_url)
        match = re.search(r"DATABASE=([^;]+)", connection_url, re.IGNORECASE)
        if match:
            self.database_name = match.group(1)

    def dispose(self):
        """
        Disposes of the database connection engine.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
