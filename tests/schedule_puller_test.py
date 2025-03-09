"""
Tests pulling the schedules
"""

from assertpy import assert_that

import schedule_puller
from services.stats import ScheduleService


def test_schedule_puller(s3, monkeypatch, schedule, session):
    """
    Tests pulling the schedule
    """
    monkeypatch.setattr(ScheduleService, 'get_stats_payload', lambda *args: schedule)
    monkeypatch.setenv('BASE_URL', 'https://www.espn.com/womens-college-basketball')
    client = session.client('s3')

    schedule_puller.main('test-bucket', date='20240101')
    response = client.list_objects_v2(Bucket='test-bucket', Prefix='schedule/')
    assert_that(response['Contents']).is_not_empty()


def test_schedule_puller_no_bucket(session, monkeypatch):
    """
    Tests pulling the schedule without a Bucket
    """
    monkeypatch.setenv('BASE_URL', 'https://www.espn.com/womens-college-basketball')
    assert_that(schedule_puller.main).raises(SystemExit).when_called_with(None)
