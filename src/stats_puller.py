"""
Script for retrieving Statistics and storing in S3
"""

import argparse
import logging
import os
import posixpath
import sys
from io import BytesIO

import polars
from boto3 import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from polars import DataFrame

from data.entities import Schedule
from services.stats import GameService, PlayerService, TeamService


def create_client(session: Session) -> BaseClient:
    """
    Creates a Boto S3 Client
    :param session: Boto session
    :return: Client
    """
    if os.getenv('S3_ENDPOINT'):
        return session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT'))
    return session.client('s3')


def get_season_types() -> dict:
    """
    Returns the Season Type Hash
    :return: Dictionary
    """
    return {1: 'preseason', 2: 'regular', 3: 'postseason'}


def make_key(
    file_name: str,
    category: str,
    week: int = 0,
    year: int = 0,
    season: int = 0,
) -> str:
    """
    Creates an S3 Key for the Parquet File
    :param file_name: Name of the Parquet File
    :param category: Category of the Parquet File
    :param week: Week Number
    :param year: Season Year
    :param season: Season Number
    :return: S3 Key
    """
    parts = []
    seasons = get_season_types()

    if year:
        parts.append(str(year))
    if season:
        parts.append(seasons[season])
    if week:
        parts.append(str(week))
    parts.append(file_name)
    return posixpath.join(category, *parts)


def load_schedule(bucket: str, key: str, session: Session) -> DataFrame:
    """
    Loads the Schedule file to a Dataframe
    :param bucket: S3 Bucket
    :param key: S3 Key
    :param session: Boto session
    :return: Optional Dataframe
    """

    client = create_client(session)
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read()
        return polars.read_parquet(content)
    except ClientError as ex:
        logging.error('Failed to load schedule: %s : %s', key, ex.args)
        raise ex


def write_output(bucket: str, key: str, records: list, session: Session) -> None:
    """
    Writes the Records to the S3 bucket
    :param bucket: S3 Bucket
    :param key: S3 Key
    :param records: Records
    :param session: Boto session
    :return: None
    """
    client = create_client(session)
    stream = BytesIO()

    frame = DataFrame([x.__dict__ for x in records])
    frame.write_parquet(stream)
    try:
        client.put_object(Bucket=bucket, Key=key, Body=stream.getvalue())
    except ClientError as ex:
        logging.error('Failed to write records to bucket: %s : %s', key, ex.args)
        raise ex


def main(bucket: str, schedule_key: str) -> None:
    """
    Retrieves the Stats for the provided Schedule file
    :param bucket: S3 Bucket for Schedule and Destination
    :param schedule_key: Schedule File key
    :return: None
    """

    if not bucket or not schedule_key:
        logging.error('Bucket and Schedule Key are required')
        sys.exit(1)

    session = Session(region_name='us-east-1')
    schedule_frame = load_schedule(bucket, schedule_key, session)
    schedule_entries = [Schedule(**x) for x in schedule_frame.to_dicts()]
    base_url = os.getenv('BASE_URL', '')

    player_service = PlayerService(base_url)
    team_service = TeamService(base_url)
    game_service = GameService(base_url)

    player_stats = []
    games = []
    team_stats = []

    logging.info('Retrieving Stats...(%s)', len(schedule_entries))
    for schedule in schedule_entries:
        upd = {'week': schedule.week, 'game_type': schedule.game_type, 'year': schedule.year}

        player_stats.extend(
            [x.copy(update=upd) for x in player_service.get_stats(schedule.game_id) if x]
        )
        games.extend(
            [x.copy(update=upd) for x in [game_service.get_game_info(schedule.game_id)] if x]
        )
        team_stats.extend(
            [x.copy(update=upd) for x in team_service.get_stats(schedule.game_id) if x]
        )

    # Get the first Schedule for the Partitions
    schedule = schedule_entries[0]

    # Write the Frames
    logging.info('Writing Output Files...')
    player_file_name = make_key(
        f'players-{os.path.basename(schedule_key)}',
        'players',
        schedule.week,
        schedule.year,
        schedule.game_type,
    )
    write_output(bucket, player_file_name, player_stats, session)

    game_file_name = make_key(
        f'games-{os.path.basename(schedule_key)}',
        'games',
        schedule.week,
        schedule.year,
        schedule.game_type,
    )
    write_output(bucket, game_file_name, games, session)

    team_file_name = make_key(
        f'teams-{os.path.basename(schedule_key)}',
        'teams',
        schedule.week,
        schedule.year,
        schedule.game_type,
    )
    write_output(bucket, team_file_name, team_stats, session)

    logging.info('DONE')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('botocore').setLevel(logging.FATAL)
    logging.getLogger('boto3').setLevel(logging.FATAL)

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bucket', type=str, required=True, help='S3 Bucket')
    parser.add_argument('-s', '--schedule_key', type=str, required=True, help='Schedule File Key')
    args = parser.parse_args()
    main(bucket=args.bucket, schedule_key=args.schedule_key)
