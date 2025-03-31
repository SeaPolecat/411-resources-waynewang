from dataclasses import asdict
import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


######################################################
#
#    Fixtures
#
######################################################


@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for testing purposes."""
    return mocker.patch("boxer.models.boxer_model.update_boxer_stats")


"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, "Wayne", 200, 100, 5, 20)

@pytest.fixture
def sample_boxer2():
    return Boxer(2, "Machamp", 300, 280, 8, 25)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]


######################################################
#
#    clear_ring
#
######################################################


def test_clear_ring(ring_model, sample_boxer1, sample_boxer2):
    """
    Test clearing the ring.
    """
    ring_model.ring.append(sample_boxer1)
    ring_model.ring.append(sample_boxer2)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"


def test_clear_ring_empty_ring(ring_model, caplog):
    """
    Test that clearing an empty leaderboard logs a warning.
    """
    ring_model.clear_ring()
    assert "Clearing an empty ring" in caplog.text, "Expected warning about empty leaderboard not found in logs."


######################################################
#
#    get_boxers
#
######################################################


def test_get_boxers(ring_model, sample_ring):
    """
    Test successfully retrieving boxers from the ring.
    """
    ring_model.ring.extend(sample_ring)

    boxers = ring_model.get_boxers()
    
    assert len(boxers) == 2
    assert boxers[0].id == 1
    assert boxers[1].id == 2