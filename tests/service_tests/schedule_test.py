"""
Tests for the schedule service
"""

from assertpy import assert_that
from services.stats import ScheduleService


def test_get_schedule(monkeypatch, schedule, schedule_service):
    """
    Tests retrieving the Schedule information.
    """

    monkeypatch.setattr(ScheduleService, 'get_stats_payload', lambda *args: schedule)
    result = schedule_service.get_schedule()
    assert_that(result).is_not_empty()

    assert_that(result) \
        .extracting('game_id', 'home_team_code', 'away_team_code',
                    'home_team_name', 'away_team_name', 'game_date') \
        .contains(('401724075', 'HAW', 'UCLA', "Hawai'i Rainbow Wahine", 'UCLA Bruins', '2024-12-02T00:30Z'))
