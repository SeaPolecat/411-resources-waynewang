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
#    create_boxer
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


######################################################
#
#    get_leaderboard
#
######################################################


def test_get_leaderboard_sort_by_wins(mock_cursor):
    """
    Test getting the leaderboard, if it's sorted by wins.
    """

    mock_cursor.fetchall.return_value = [
        (1, "Wayne", 200, 100, 5, 20, 5, 4, 4/5)
    ]

    leaderboard = get_leaderboard(sort_by="wins")

    expected_result = [
        {
            'id': 1,
            'name': 'Wayne',
            'weight': 200,
            'height': 100,
            'reach': 5,
            'age': 20,
            'weight_class': get_weight_class(200),  # Calculate weight class
            'fights': 5,
            'wins': 4,
            'win_pct': round(4/5 * 100, 1)  # Convert to percentage
        } 
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


######################################################
#
#    get_boxer_by_name
#
######################################################


def test_get_boxer_by_name(mock_cursor):
    """
    Test getting a boxer by name.
    """
    mock_cursor.fetchone.return_value = (1, "Wayne", 200, 100, 5, 20)

    result = get_boxer_by_name("Wayne")

    expected_result = Boxer(1, "Wayne", 200, 100, 5, 20)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Wayne",)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_bad_name(mock_cursor):
    """
    Test error when getting a non-existent boxer.
    """
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer 'wiwiwi' not found."):
        get_boxer_by_name("wiwiwi")


######################################################
#
#    update_boxer_stats
#
######################################################


def test_update_boxer_stats_win(mock_cursor):
    """
    Test updating the stats of a boxer when they won.
    """
    mock_cursor.fetchone.return_value = True

    boxer_id = 1
    result = 'win'
    update_boxer_stats(boxer_id, result)

    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_boxer_stats_loss(mock_cursor):
    """
    Test updating the stats of a boxer when they lost.
    """
    mock_cursor.fetchone.return_value = True

    boxer_id = 1
    result = 'loss'
    update_boxer_stats(boxer_id, result)

    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_boxer_stats_invalid_id(mock_cursor):
    """
    Test error when trying to update the stats of a boxer that does not exist.
    """
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer with ID HUH not found."):
        boxer_id = 'HUH'
        result = 'loss'
        update_boxer_stats(boxer_id, result)


def test_update_boxer_stats_invalid_result(mock_cursor):
    """
    Test error when trying to update the stats of a boxer with an invalid result.
    """
    mock_cursor.fetchone.return_value = True
    
    with pytest.raises(ValueError, match="Invalid result: and they both died. Expected 'win' or 'loss'."):
        boxer_id = 1
        result = 'and they both died'
        update_boxer_stats(boxer_id, result)