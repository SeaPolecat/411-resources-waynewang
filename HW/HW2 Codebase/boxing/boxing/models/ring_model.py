import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    def __init__(self):
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers in the ring, determines a winner based on their
        fighting skill and a randomized outcome, updates their stats, and clears the ring.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """
        Clears the boxers from the ring. If the ring is empty, logs a warning.
        """
        logger.info("Received request to clear the ring")

        if not self.ring:
            logger.warning("Clearing an empty ring")
            return

        self.ring.clear()
        logger.info("Successfully cleared the ring")

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer object to the ring. A maximum of two boxers are allowed in the ring.

        Args:
            boxer (Boxer): The Boxer object to add to the ring.

        Returns:
            None

        Raises:
            TypeError: If the input is not a Boxer instance.
            ValueError: If the ring already contains two boxers.
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Retrieves the list of boxers currently in the ring.

        Returns:
            List[Boxer]: A list of Boxer objects currently in the ring.
        """
        logger.info("Retrieving the boxers in the ring")

        if not self.ring:
            logger.warning("The ring is empty")
        else:
            logger.info("Successfully retrieved the boxers in the ring")

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates the fighting skill of a boxer using a custom formula
        based on weight, name length, reach, and age.

        Args:
            boxer (Boxer): The Boxer object whose skill is to be calculated.

        Returns:
            float: The calculated fighting skill score.
        """
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill

