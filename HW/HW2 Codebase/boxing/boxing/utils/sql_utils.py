from contextlib import contextmanager
import logging
import os
import sqlite3

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


# load the db path from the environment with a default value
DB_PATH = os.getenv("DB_PATH", "/app/sql/boxing.db")


def check_database_connection():
    """
    Checks whether a connection to the database can be successfully established
    by executing a simple test query.

    Raises:
        Exception: If the database connection or query execution fails.
    """

    logger.info("Checking database connection")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
	
        logger.debug("Executing test query: SELECT 1;")
        
	# Execute a simple query to verify the connection is active
        cursor.execute("SELECT 1;")
        conn.close()

    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        error_message = f"Database connection error: {e}"
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    """
    Check if the table exists by querying the SQLite master table.

    Args:
        tablename (str): The name of the table to check.

    Raises:
        Exception: If the table does not exist.

    """
    try:
        logger.info(f"Checking if table '{tablename}' exists in {DB_PATH}...")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Use parameterized query to avoid SQL injection
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
        result = cursor.fetchone()

        conn.close()

        if result is None:
            error_message = f"Table '{tablename}' does not exist."
            logger.error(error_message)
            raise Exception(error_message)
        
        logger.info(f"Table '{tablename}' exists.")

    except sqlite3.Error as e:
        error_message = f"Table check error for '{tablename}': {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():

    """
    Context manager that establishes and yields a SQLite database connection.

    Yields:
        sqlite3.Connection: A connection object to interact with the SQLite database.

    Raises:
        sqlite3.Error: If the connection to the database fails.
    """

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info("Database connection established")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise e
    finally:
        if conn:
            conn.close()
