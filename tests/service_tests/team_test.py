"""
Tests for the Team Service
"""

from assertpy import assert_that


def test_team_get_stats(team_service, monkeypatch, team):
    """
    Tests retrieving the stats for a team
    """
    monkeypatch.setattr(team_service, 'get_stats_payload', lambda *args: team)

    result = team_service.get_stats('123456')

    assert_that(result).is_not_empty()
    assert_that(result) \
        .extracting('team_url', 'team', 'opponent', 'statistic_type', 'statistic_name',
                    'statistic_value', 'game_id') \
        .contains(('/womens-college-basketball/team/_/id/2579/south-carolina-gamecocks',
                   'South Carolina Gamecocks', 'Michigan Wolverines', None, 'assists', 12.0,
                   '401713576'),
                  ('/womens-college-basketball/team/_/id/2579/south-carolina-gamecocks',
                   'South Carolina Gamecocks', 'Michigan Wolverines', None, 'fieldGoalsMade', 25.0,
                   '401713576'),
                  ('/womens-college-basketball/team/_/id/2579/south-carolina-gamecocks',
                   'South Carolina Gamecocks', 'Michigan Wolverines', None, 'fieldGoalsAttempted',
                   75.0, '401713576'))
