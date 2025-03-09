"""
Tests for the Data Entities
"""

from assertpy import assert_that

from data.entities import Game


def test_copy_item():
    """
    Tests Copying the items
    """
    game = Game(game_id='12345', home_team='Baltimore', away_team='Kansas City')
    result = game.copy()
    assert_that(result) \
        .has_game_id('12345') \
        .has_home_team('Baltimore') \
        .has_away_team('Kansas City')


def test_copy_with_update():
    """
    Tests Copying the item with update
    """

    game = Game(game_id='12345', home_team='Baltimore', away_team='Kansas City')

    update = {
        'home_team': 'Pittsburgh'
    }
    result = game.copy(update=update)
    assert_that(result) \
        .has_game_id('12345') \
        .has_home_team('Pittsburgh') \
        .has_away_team('Kansas City')


def test_copy_item_with_extra_fields():
    """
    Tests copying an item with extra fields in the update
    """

    game = Game(game_id='12345', home_team='Baltimore', away_team='Kansas City')
    update = {
        'home_team': 'Pittsburgh',
        'chicken': 'wing'
    }

    result = game.copy(update=update)
    assert_that(result) \
        .has_game_id('12345') \
        .has_home_team('Pittsburgh') \
        .has_away_team('Kansas City')

    assert_that(result.__dict__).does_not_contain_key('chicken')


def test_copy_item_with_none_entries():
    """
    Tests Copying an item with None updates for a populated field
    """

    game = Game(game_id='12345', home_team='Baltimore', away_team='Kansas City')
    update = {
        'home_team': 'Pittsburgh',
        'away_team': None
    }

    result = game.copy(update=update)
    assert_that(result) \
        .has_game_id('12345') \
        .has_home_team('Pittsburgh') \
        .has_away_team('Kansas City')
