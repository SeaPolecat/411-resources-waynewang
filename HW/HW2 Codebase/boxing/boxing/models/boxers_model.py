from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer in the boxers table.

    Args:
        name (str): The boxer's name.
        weight (int): The boxer's weight in lbs.
        height (int): The boxer's height in cm.
        reach (float): The boxer's reach in cm (how far they can punch).
        age (int): The boxer's age.

    Raises:
        ValueError: If any field is invalid.
        sqlite3.IntegrityError: If a boxer with the same name already exists.
        sqlite3.Error: For any other database errors.

    """
    logger.info(f"Received request to create boxer: {name}")

    if weight < 125:
        logger.warning("Invalid weight provided.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.warning("Invalid height provided.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.warning("Invalid reach provided.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.warning("Invalid age provided.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

            logger.info(f"Boxer successfully added: {name}")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer already exists: {name}")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error while creating boxer: {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """Gets the leaderboard of boxers.

    Args:
        sort_by (str): Defines how to sort the leaderboard (in descending order).
            Should be either 'wins' or 'win_pct' (percentage of wins). Defaults to 'wins'.

    Returns:
        List[dict[str, Any]]: A list of dictionaries representing the boxer leaderboard.

    Raises:
        ValueError: If the sort_by argument is invalid, or if the leaderboard is empty.
        sqlite3.Error: If any database error occurs.

    """
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            logger.info("Attempting to retrieve the leaderboard...")

            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []

        if not rows:
            logger.warning("The leaderboard is empty!")
            return []

        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        logger.info(f"Retrieved the leaderboard containing {len(leaderboard)} boxers.")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving the leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Gets a boxer by their name.

    Args:
        boxer_name (str): The boxer's name.

    Returns:
        Boxer: The boxer corresponding to the boxer_name.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            logger.info(f"Attempting to retrieve boxer named {boxer_name}")

            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Boxer named {boxer_name} found")
                return boxer
            else:
                logger.info(f"Boxer named {boxer_name} NOT found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer named {boxer_name}: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Finds a boxer by their ID and increments their number of fights, and wins (if they won a fight).
    
    Args:
        boxer_id (int): The ID of the boxer whose number of fights and wins should be incremented.
        result (str): Indicates whether the boxer won or lost a fight. Should be either 'win' or 'loss'.

    Raises:
        ValueError: If the 'result' argument is invalid, or if the boxer does not exist.
        sqlite3.Error: If any database error occurs.
    
    """
    if result not in {'win', 'loss'}:
        logger.warning(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to update boxer stats for boxer with ID {boxer_id}")

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Cannot update boxer stats: Boxer with ID {boxer_id} not found!")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
                logger.info(f"Added one fight and one win to boxer stats for boxer with ID {boxer_id}")

            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))
                logger.info(f"Added one fight to boxer stats for boxer with ID {boxer_id}")

            conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Database error while updating boxer stats for boxer with ID {boxer_id}: {e}")
        raise e
