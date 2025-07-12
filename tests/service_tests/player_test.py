"""
Tests for extracting the Player Stats
"""

from assertpy import assert_that

from data.entities import PlayerStatistic


def test_player_stats(player_service, monkeypatch, boxscore):
    """
    Tests the Player stats extraction
    """
    monkeypatch.setattr(player_service, 'get_stats_payload', lambda *args: boxscore)

    result = player_service.get_stats('401713576')
    assert_that(result).is_not_empty()

    assert_that(result).extracting(
        'player_url', 'team', 'opponent', 'statistic_name', 'statistic_value', 'game_id'
    ).contains(
        (
            'https://www.espn.com/womens-college-basketball/player/_/id/5240185/syla-swords',
            'Michigan Wolverines',
            'South Carolina Gamecocks',
            'minutes',
            36,
            '401713576',
        ),
        (
            'https://www.espn.com/womens-college-basketball/player/_/id/5240185/syla-swords',
            'Michigan Wolverines',
            'South Carolina Gamecocks',
            'fieldGoalsMade',
            9,
            '401713576',
        ),
        (
            'https://www.espn.com/womens-college-basketball/player/_/id/5240185/syla-swords',
            'Michigan Wolverines',
            'South Carolina Gamecocks',
            'fieldGoalsAttempted',
            19,
            '401713576',
        ),
    )


def test_player_stats_no_payload(player_service, monkeypatch):
    """
    Tests retrieving the Player Stats with no payload
    """

    monkeypatch.setattr(player_service, 'get_stats_payload', lambda *args: None)
    result = player_service.get_stats('401713576')
    assert_that(result).is_empty()


def test_player_stats_no_boxscore(player_service, monkeypatch):
    payload = {'page': {'content': {'gamepackage': {'tm': '12345'}}}}
    monkeypatch.setattr(player_service, 'get_stats_payload', lambda *args: payload)
    result = player_service.get_stats('401713576')
    assert_that(result).is_empty()


def test_player_stats_not_enough_teams(player_service, monkeypatch):
    """
    Tests retrieving the Player Stats with not enough teams
    """

    payload = {'page': {'content': {'gamepackage': {'bxscr': [{'stats': [], 'tm': {}}]}}}}
    monkeypatch.setattr(player_service, 'get_stats_payload', lambda *args: payload)
    result = player_service.get_stats('401713576')
    assert_that(result).is_empty()


def test_explode_stat_dash_delimiter(player_service):
    """
    Tests Explodiung the Stat with a Dash Delimiter
    """

    stat = PlayerStatistic(1, 2023, 2, 'Bull Dogs', 'Shepherds', 'PA', 'test stat', 'tst')
    result = player_service._explode_stat_(stat, ('PA-PT', '3-4'))
    assert_that(result).is_not_empty().is_length(2)

    assert_that(
        [x for x in result if x.statistic_name == 'PA' and x.statistic_value == 3]
    ).is_not_empty()
    assert_that(
        [x for x in result if x.statistic_name == 'PT' and x.statistic_value == 4]
    ).is_not_empty()


def test_explode_stat_slash_delimiter(player_service):
    """
    Tests exploding a stat with a slash delimiter
    """

    stat = PlayerStatistic(1, 2023, 2, 'Bull Dogs', 'Shepherds', 'PA', 'test stat', 'tst')
    result = player_service._explode_stat_(stat, ('PA/PT', '3/4'))
    assert_that(result).is_not_empty().is_length(2)

    assert_that(
        [x for x in result if x.statistic_name == 'PA' and x.statistic_value == 3]
    ).is_not_empty()
    assert_that(
        [x for x in result if x.statistic_name == 'PT' and x.statistic_value == 4]
    ).is_not_empty()


def test_explode_stat_time(player_service):
    """
    Tests exploding a stat with a time delimiter
    """
    stat = PlayerStatistic(1, 2023, 2, 'Bull Dogs', 'Shepherds', 'PA', 'test stat', 'tst')
    result = player_service._explode_stat_(stat, ('TP', '1:20'))
    assert_that(result).is_not_empty().is_length(1)

    assert_that(
        [x for x in result if x.statistic_name == 'TP' and x.statistic_value == 80]
    ).is_not_empty()


def test_extract_string_stat(player_service):
    """
    Tests extracting a Stat Value that is a string
    """
    stat = PlayerStatistic(1,2023,2,'Bull Dogs', 'Shepherds','PA','Test Stat','TST')
    result = player_service._explode_stat_(stat, ('TS', 'W1'))

    assert_that(result).extracting('statistic_value').contains_only(0)
