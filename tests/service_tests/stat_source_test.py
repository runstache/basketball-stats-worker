"""
Tests the Source is still accurate.
"""

import json

import pytest
from assertpy import assert_that

from services.stats import BaseService

BOXSCORE_URL = 'https://www.espn.com/womens-college-basketball/boxscore/_/gameId/401713576'
TEAM_URL = 'https://www.espn.com/womens-college-basketball/matchup/_/gameId/401713576'
SCHEDULE_URL = 'https://www.espn.com/womens-college-basketball/schedule/_/date/20241202/group/50'

BASE_URL = 'https://www.espn.com/womens-college-basketball'


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
