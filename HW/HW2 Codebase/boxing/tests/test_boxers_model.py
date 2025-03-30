from contextlib import contextmanager
import re
import sqlite3
import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)


######################################################
#
#    Fixtures
#
######################################################


def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_boxer(mock_cursor):
    """
    Test creating a new boxer.
    """
    create_boxer(name="Wayne", weight=200, height=100, reach=5, age=20)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Wayne", 200, 100, 5, 20)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_boxer_invalid_weight(mock_cursor):
    """
    Test error when trying to create a boxer with an invalid weight (e.g., weight below 125)  
    """
    with pytest.raises(ValueError, match="Invalid weight: 100. Must be at least 125."):
        create_boxer(name="Wayne", weight=100, height=100, reach=5, age=20)


def test_create_boxer_invalid_height(mock_cursor):
    """
    Test error when trying to create a boxer with an invalid height (e.g., height below 0)
    """
    with pytest.raises(ValueError, match="Invalid height: -2. Must be greater than 0."):
        create_boxer(name="Wayne", weight=200, height=-2, reach=5, age=20)


def test_create_boxer_invalid_reach(mock_cursor):
    """
    Test error when trying to create a boxer with an invalid reach (e.g., raech below 0)
    """
    with pytest.raises(ValueError, match="Invalid reach: -12. Must be greater than 0."):
        create_boxer(name="Wayne", weight=200, height=100, reach=-12, age=20)


def test_create_boxer_invalid_age(mock_cursor):
    """
    Test error when trying to create a boxer with an invalid age (e.g., age not between 18 and 40)
    """
    with pytest.raises(ValueError, match="Invalid age: 10. Must be between 18 and 40."):
        create_boxer(name="Wayne", weight=200, height=100, reach=5, age=10)

    with pytest.raises(ValueError, match="Invalid age: 69. Must be between 18 and 40."):
        create_boxer(name="Wayne", weight=200, height=100, reach=5, age=69)


def test_create_boxer_duplicate(mock_cursor):
    """
    Test creating a boxer with the same name (should raise an error).
    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxer.name")

    with pytest.raises(ValueError, match="Boxer with name 'Wayne' already exists"):
        create_boxer(name="Wayne", weight=150, height=200, reach=4, age=30)


