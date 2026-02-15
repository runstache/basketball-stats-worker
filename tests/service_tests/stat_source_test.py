"""
Tests the Source is still accurate.
"""

import json

import pytest
from assertpy import assert_that

from support.services.stats import BaseService

BOXSCORE_URL = 'https://www.espn.com/womens-college-basketball/boxscore/_/gameId/401713576'
TEAM_URL = 'https://www.espn.com/womens-college-basketball/matchup/_/gameId/401713576'
SCHEDULE_URL = 'https://www.espn.com/womens-college-basketball/schedule/_/date/20241202/group/50'
GAME_CAST_URL = 'https://www.espn.com/college-football/playbyplay/_/gameId/401752924'
BASE_URL = 'https://www.espn.com/womens-college-basketball'
ROSTER_URL = 'https://www.espn.com/college-football/team/roster/_/id/221'
PLAYER_URL = 'https://www.espn.com/college-football/player/_/id/4819223/ryan-baer'


@pytest.fixture(scope='module')
def browser() -> BaseService:
    """
    Registers the Base Service for the module to use.
    """

    return BaseService(BASE_URL)


def write_output(path: str, payload: dict) -> None:
    """
    Writes the Payload Output
    :param path: File Path
    :param payload: JSON Object
    :return: None
    """

    with open(path, 'w', encoding='utf-8') as output_file:
        json.dump(payload, output_file)


def test_get_box_score(browser):
    """
    Tests retrieving the Boxscore information
    """

    url = browser._build_url_(['boxscore', '_', 'gameId', '401713576'])
    result = browser.get_stats_payload(url)
    assert_that(result).is_not_none()

    assert_that(
        result.get('page', {}).get('content', {}).get('gamepackage', {}).get('bxscr', {})
    ).is_not_empty()


def test_get_team_stats(browser):
    """
    Tests retrieving the Team Stats section
    """

    url = browser._build_url_(['matchup', '_', 'gameId', '401713576'])
    result = browser.get_stats_payload(url)
    assert_that(result).is_not_none()

    assert_that(result.get('page', {}).get('content', {}).get('gamepackage', {})).is_not_empty()


def test_get_schedule(browser):
    """
    Tests retrieving the Schedule information.
    """
    url = browser._build_url_(['schedule', '_', 'date', '20241202', 'group', '50'])
    result = browser.get_stats_payload(url)
    assert_that(result).is_not_none()
    assert_that(result.get('page', {}).get('content', {}).get('events', {})).is_not_empty()


def test_get_game_cast(browser):
    """
    Tests retrieving the Game Cast and writing it out
    """
    result = browser.get_stats_payload(GAME_CAST_URL)
    assert_that(result).is_not_none()

def test_get_player_card(browser):
    """
    Gets the Player Card Page
    """

    result = browser.get_stats_payload(PLAYER_URL)
    assert_that(result).is_not_none()

def test_get_roster(browser):
    """
    Tests getting the Roster
    """

    result = browser.get_stats_payload(ROSTER_URL)
    assert_that(result).is_not_none()
