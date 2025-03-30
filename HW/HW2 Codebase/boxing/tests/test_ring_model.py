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
def playlist_model():
    """Fixture to provide a new instance of PlaylistModel for each test."""
    return Boxer()

'''
@pytest.fixture
def mock_update_play_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("playlist.models.playlist_model.update_play_count")
'''

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, "Wayne", 200, 100, 5, 20)

@pytest.fixture
def sample_boxer2():
    return Boxer(1, "Wayne", 200, 100, 5, 20)

'''
@pytest.fixture
def sample_playlist(sample_song1, sample_song2):
    return [sample_song1, sample_song2]'
'''


######################################################
#
#    clear_ring
#
######################################################


