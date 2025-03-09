"""
Tests for the Stat Puller
"""

from assertpy import assert_that
from polars import DataFrame

import stats_puller
from data.entities import Schedule
from services.stats import PlayerService, TeamService, GameService
from stats_puller import ClientError


def test_pull_stats(monkeypatch, boxscore, team, session, schedule_file):
    """
    Tests Pulling stats for a schedule file
    """

    monkeypatch.setenv('BASE_URL', '')
    monkeypatch.setattr(PlayerService, 'get_stats_payload', lambda *args: boxscore)
    monkeypatch.setattr(TeamService, 'get_stats_payload', lambda *args: team)
    monkeypatch.setattr(GameService, 'get_stats_payload', lambda *args: team)

    stats_puller.main('test-bucket', 'schedule/20241201.parquet')

    client = session.client('s3')
    response = client.list_objects_v2(Bucket='test-bucket', Prefix='players/')
    assert_that(response['Contents']).is_not_empty()
    response = client.list_objects_v2(Bucket='test-bucket', Prefix='teams/')
    assert_that(response['Contents']).is_not_empty()
    response = client.list_objects_v2(Bucket='test-bucket', Prefix='games/')
    assert_that(response['Contents']).is_not_empty()


def test_pull_schedule_failure(monkeypatch, boxscore, team, session, schedule_file):
    """
    Tests failing to find the schedule file
    """

    monkeypatch.setenv('BASE_URL', '')
    monkeypatch.setattr(PlayerService, 'get_stats_payload', lambda *args: boxscore)
    monkeypatch.setattr(TeamService, 'get_stats_payload', lambda *args: team)
    monkeypatch.setattr(GameService, 'get_stats_payload', lambda *args: team)

    assert_that(stats_puller.main) \
        .raises(ClientError) \
        .when_called_with('test-bucket-2', 'schedule/20241201.parquet')


def test_write_failure(monkeypatch, boxscore, team, session, schedule_file):
    """
    Tests a failure on the write operation
    """

    monkeypatch.setenv('BASE_URL', '')
    monkeypatch.setattr(PlayerService, 'get_stats_payload', lambda *args: boxscore)
    monkeypatch.setattr(TeamService, 'get_stats_payload', lambda *args: team)
    monkeypatch.setattr(GameService, 'get_stats_payload', lambda *args: team)
    monkeypatch.setattr(stats_puller, 'load_schedule', lambda *args: DataFrame([Schedule(game_id='12345')]))

    assert_that(stats_puller.main) \
        .raises(ClientError) \
        .when_called_with('test-bucket-2', 'schedule/20241201.parquet')


def test_build_key():
    """
    Tests building the S3 Key
    """

    result = stats_puller.make_key('test.parquet', 'players', 1,2020,3)
    assert_that(result).is_equal_to('players/2020/postseason/1/test.parquet')

def test_no_bucket_or_schedule():
    """
    Tests no bucket or schedule
    """

    assert_that(stats_puller.main).raises(SystemExit).when_called_with('', '')