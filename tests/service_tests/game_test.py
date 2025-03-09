"""
Tests for the game Service
"""

from assertpy import assert_that

def test_get_game_info(team, game_service, monkeypatch):
    """
    Tests retrieving the Game information
    """

    monkeypatch.setattr(game_service, 'get_stats_payload', lambda *args: team)


    result = game_service.get_game_info('401713576')
    assert_that(result).is_not_none()

    assert_that([result]) \
        .extracting('game_id', 'home_team', 'away_team', 'location', 'city', 'state',
                    'game_date', 'is_conference', 'note', 'home_score', 'away_score',
                    'line', 'over_under') \
        .contains(('401713576', 'South Carolina Gamecocks', 'Michigan Wolverines', 'T-Mobile Arena',
                   'Las Vegas', 'NV', '2024-11-05T00:30Z', False, 'Hall of Fame Series - Las Vegas',
                   68, 62, 'SC -20.5', 133.5))


def test_get_game_info_no_payload(game_service, monkeypatch):
    """
    Test no Payload
    """

    monkeypatch.setattr(game_service, 'get_stats_payload', lambda *args: None)

    result = game_service.get_game_info('401713576')
    assert_that(result).is_none()


def test_get_game_info_no_game_package(game_service, monkeypatch):
    payload = {
        'page': {
            'content': {
                'tm': '123455'
            }
        }
    }
    monkeypatch.setattr(game_service, 'get_stats_payload', lambda *args: payload)
    result = game_service.get_game_info('401713576')
    assert_that(result).is_none()
