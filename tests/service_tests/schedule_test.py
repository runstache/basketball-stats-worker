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

    assert_that(result).extracting(
        'game_id',
        'home_team_code',
        'away_team_code',
        'home_team_name',
        'away_team_name',
        'game_date',
    ).contains(
        ('401724075', 'HAW', 'UCLA', "Hawai'i Rainbow Wahine", 'UCLA Bruins', '2024-12-02T00:30Z')
    )


def test_event_empty(schedule_service):
    """
    Tests no event sent to build schedule
    """

    result = schedule_service._build_schedule_({})
    assert_that(result).is_none()


def test_event_no_teams(schedule_service):
    """
    Tests the event has no teams
    """

    result = schedule_service._build_schedule_({'teams': []})
    assert_that(result).is_none()


def test_get_schedule_all_args(monkeypatch, schedule_service):
    """
    Tests retrieving the Schedule information with all the arguments
    """

    def _mock_url(a, parts: list):
        """
        Mock function for checking the url pieces
        """

        assert_that(parts).contains(
            '1',
            '2',
            '20240101',
            '50',
            'week',
            'seasontype',
            'schedule',
            '_',
            'year',
            'date',
            'group',
            '2020',
        )

    monkeypatch.setattr(ScheduleService, 'get_stats_payload', lambda *args: None)
    monkeypatch.setattr(ScheduleService, '_build_url_', _mock_url)

    result = schedule_service.get_schedule(
        week=1, game_type=2, date='20240101', group='50', year=2020
    )
    assert_that(result).is_empty()
