"""
Pytest Fixtures
"""

import json
import os

import pytest
from boto3 import Session
from moto import mock_aws

from services.stats import GameService, PlayerService, ScheduleService, TeamService


@pytest.fixture
def boxscore() -> dict:
    """
    Returns the box score payload
    """

    with open('./tests/test_files/boxscore.json') as input:
        content = json.load(input)
        return content


@pytest.fixture
def schedule() -> dict:
    """
    Returns the Schedule payload
    """

    with open('./tests/test_files/schedule.json') as input:
        content = json.load(input)
        return content


@pytest.fixture
def team() -> dict:
    """
    Returns the team payload
    """

    with open('./tests/test_files/team.json') as input:
        content = json.load(input)
        return content


@pytest.fixture(scope='module')
def schedule_service() -> ScheduleService:
    """
    Registers a Schedule Service
    """

    return ScheduleService('http://locahost/schedule')


@pytest.fixture(scope='module')
def team_service() -> TeamService:
    """
    Registers a Team Service
    """

    return TeamService('http://locahost/team')


@pytest.fixture(scope='module')
def game_service() -> GameService:
    """
    Registers a Game Service
    """
    return GameService('http://locahost/game')


@pytest.fixture(scope='module')
def player_service() -> PlayerService:
    """
    Registers a Player Service
    """
    return PlayerService('http://locahost/player')


@pytest.fixture
def credentials() -> None:
    """
    Sets default credentials
    """

    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture
def session(credentials):
    """
    Creates the mock session
    """
    with mock_aws():
        session = Session()
        yield session


@pytest.fixture
def s3(session):
    """
    Creates the S3 Buckets
    """

    client = session.client('s3')
    client.create_bucket(Bucket='test-bucket')


@pytest.fixture
def schedule_file(s3, session):
    """
    Stages the Schedule file to S3
    """

    with open('./tests/test_files/20241201.parquet', 'rb') as input:
        content = input.read()

    client = session.client('s3')
    client.put_object(Bucket='test-bucket', Key='schedule/20241201.parquet', Body=content)
