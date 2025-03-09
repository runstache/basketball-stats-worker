"""
Tests for extracting the Player Stats
"""

from assertpy import assert_that


def test_player_stats(player_service, monkeypatch, boxscore):
    """
    Tests the Player stats extraction
    """
    monkeypatch.setattr(player_service, 'get_stats_payload', lambda *args: boxscore)

    result = player_service.get_stats('401713576')
    assert_that(result).is_not_empty()

    assert_that(result) \
        .extracting('player_url', 'team', 'opponent', 'statistic_name', 'statistic_value',
                    'game_id') \
        .contains(('https://www.espn.com/womens-college-basketball/player/_/id/5240185/syla-swords',
                   'Michigan Wolverines', 'South Carolina Gamecocks', 'minutes', 36, '401713576'),
                  ('https://www.espn.com/womens-college-basketball/player/_/id/5240185/syla-swords',
                   'Michigan Wolverines', 'South Carolina Gamecocks', 'fieldGoalsMade', 9,
                   '401713576'),
                  ('https://www.espn.com/womens-college-basketball/player/_/id/5240185/syla-swords',
                   'Michigan Wolverines', 'South Carolina Gamecocks', 'fieldGoalsAttempted', 19,
                   '401713576'))
