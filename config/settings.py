import os

# Define the path to the .env file
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

# Environment Variables Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Database Configuration
DATABASE = {
    'engine': os.getenv('DB_ENGINE', 'sqlite'),
    'name': os.getenv('DB_NAME', 'local_database.db'),  # Default to an SQLite database file
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', ''),
    'port': os.getenv('DB_PORT', ''),
}

def get_database_uri():
    """Construct the appropriate database URI based on the environment settings."""
    engine = DATABASE['engine'].lower()

    if engine == 'sqlite':
        # SQLite URI
        return f"sqlite:///{DATABASE['name']}"
    elif engine == 'postgresql':
        # PostgreSQL URI
        return (
            f"postgresql://{DATABASE['user']}:{DATABASE['password']}"
            f"@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['name']}"
        )
    elif engine == 'mysql':
        # MySQL URI
        return (
            f"mysql+pymysql://{DATABASE['user']}:{DATABASE['password']}"
            f"@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['name']}"
        )
    elif engine == 'mssql':
        # SQL Server URI
        return (
            f"mssql+pyodbc://{DATABASE['user']}:{DATABASE['password']}"
            f"@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['name']}"
        )
    else:
        raise ValueError(f"Unsupported database engine: {engine}")

# Construct the database URI using the defined function
DATABASE_URI = get_database_uri()

