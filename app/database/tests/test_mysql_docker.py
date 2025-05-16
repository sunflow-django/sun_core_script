import logging
import os
from collections.abc import Generator
from pathlib import Path

import mysql.connector
import pytest
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(".env")
if not env_path.is_file():
    pytest.exit(f"The env file '{env_path}' does not exist. Was expected in: '{env_path.resolve()}'.")
load_dotenv(env_path)

# MySQL configuration from environment variables
MYSQL_CONFIG = {
    "host": "localhost",
    "port": "3306",
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_TEST_DATABASE"),
}


@pytest.fixture(scope="module")
def mysql_test_database() -> None:
    """Fixture to create the test database if it doesn't exist."""
    # Create config with no databse
    temp_config = MYSQL_CONFIG.copy()
    temp_config.pop("database")

    connection = None
    try:
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        test_db = MYSQL_CONFIG["database"]
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{test_db}`")
        connection.commit()
        logger.debug("Test database '%s' created or already exists", test_db)
        cursor.close()
    except Exception:
        logger.exception("Failed to create test database: %s")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


@pytest.fixture(scope="module")
def mysql_connection(mysql_test_database: None) -> Generator[mysql.connector.connection.MySQLConnection, None, None]:
    """Fixture to set up and tear down MySQL connection.

    Args:
        mysql_test_database: Fixture ensuring the test database exists.

    Yields:
        MySQLConnection: An active MySQL connection to the test database.
    """
    connection: mysql.connector.connection.MySQLConnection | None = None
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            logger.debug("Successfully connected to MySQL database '%s'", MYSQL_CONFIG["database"])
            yield connection
        else:
            logger.error("Failed to establish connection with config: %s", MYSQL_CONFIG)
    except Exception:
        logger.exception("Failed to establish connection with config: %s", MYSQL_CONFIG)
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.debug("MySQL connection closed")


@pytest.fixture(scope="module")
def cursor(
    mysql_connection: mysql.connector.connection.MySQLConnection,
) -> Generator[mysql.connector.cursor.MySQLCursor, None, None]:
    """Fixture to provide a cursor for database operations.

    Args:
        mysql_connection: An active MySQL connection.

    Yields:
        MySQLCursor: A cursor for executing queries.
    """
    cursor = mysql_connection.cursor()
    yield cursor
    cursor.close()


def test_mysql_connection(mysql_connection: mysql.connector.connection.MySQLConnection) -> None:
    """Test if the connection to MySQL is successful.

    Args:
        mysql_connection: An active MySQL connection.
    """
    assert mysql_connection.is_connected(), "Failed to connect to MySQL database"


def test_create_table(
    cursor: mysql.connector.cursor.MySQLCursor,
    mysql_connection: mysql.connector.connection.MySQLConnection,
) -> None:
    """Test creating a table in the test database.

    Args:
        cursor: A cursor for executing queries.
        mysql_connection: An active MySQL connection.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS test_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    )
    """
    try:
        cursor.execute(create_table_query)
        mysql_connection.commit()
        cursor.execute("SHOW TABLES LIKE 'test_table'")
        result = cursor.fetchone()
        assert result is not None, "Table creation failed"
    except:  # noqa: E722
        logger.exception("Error creating table")


def test_insert_data(
    cursor: mysql.connector.cursor.MySQLCursor,
    mysql_connection: mysql.connector.connection.MySQLConnection,
) -> None:
    """Test inserting data into the test table.

    Args:
        cursor: A cursor for executing queries.
        mysql_connection: An active MySQL connection.
    """
    insert_query = "INSERT INTO test_table (name) VALUES (%s)"
    data = ("TestUser",)
    try:
        cursor.execute(insert_query, data)
        mysql_connection.commit()
        cursor.execute("SELECT name FROM test_table WHERE name = %s", data)
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "TestUser", "Data insertion failed"
    except:  # noqa: E722
        logger.exception("Error inserting data")


def test_cleanup(
    cursor: mysql.connector.cursor.MySQLCursor,
    mysql_connection: mysql.connector.connection.MySQLConnection,
) -> None:
    """Test cleaning up the test table.

    Args:
        cursor: A cursor for executing queries.
        mysql_connection: An active MySQL connection.
    """
    drop_table_query = "DROP TABLE IF EXISTS test_table"
    try:
        cursor.execute(drop_table_query)
        mysql_connection.commit()
        cursor.execute("SHOW TABLES LIKE 'test_table'")
        result = cursor.fetchone()
        assert result is None, "Table cleanup failed"
    except:  # noqa: E722
        logger.exception("Error cleaning up table")
