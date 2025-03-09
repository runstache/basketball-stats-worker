"""
Pytest Fixtures
"""

import json

import pytest

from data.entities import Schedule
from services.stats import ScheduleService, TeamService, GameService, PlayerService


@pytest.fixture
def boxscore() -> dict:
    """
    Returns the box score payload
    """

    with open("./tests/test_files/boxscore.json") as input:
        content = json.load(input)
        return content


@pytest.fixture
def schedule() -> dict:
    """
    Returns the Schedule payload
    """

    with open("./tests/test_files/schedule.json") as input:
        content = json.load(input)
        return content


@pytest.fixture
def team() -> dict:
    """
    Returns the team payload
    """

    with open("./tests/test_files/team.json") as input:
        content = json.load(input)
        return content

@pytest.fixture(scope='module')
def schedule_service() -> ScheduleService:
    """
    Registers a Schedule Service
    """

    return ScheduleService('http://locahost/schedule')

@pytest.fixture(scope='module')
def team_service() -> TeamService:
    """
    Registers a Team Service
    """

    return TeamService('http://locahost/team')

@pytest.fixture(scope='module')
def game_service() -> GameService:
    """
    Registers a Game Service
    """
    return GameService('http://locahost/game')

@pytest.fixture(scope='module')
def player_service() -> PlayerService:
    """
    Registers a Player Service
    """
    return PlayerService('http://locahost/player')
