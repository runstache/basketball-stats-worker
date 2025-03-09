"""
Script for retrieving schedule information
"""
import argparse
import logging
import os
import posixpath
import sys
import uuid
from io import BytesIO

import polars
from boto3 import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from data.entities import Schedule
from services.stats import ScheduleService


def create_client(session: Session) -> BaseClient:
    """
    Creates an S3 Client
    :param session: Boto3 Session
    :return: S3 Client
    """

    if os.getenv('S3_ENDPOINT'):
        return session.client('s3', endpoint_url=os.getenv('S3_ENDPOINT'))
    return session.client('s3')


def write_output(bucket: str, key: str, records: list[Schedule], session: Session) -> None:
    """
    Writes the Schedule records to S3 Parquet
    :param bucket: S3 Bucket
    :param key: S3 Key
    :param records: Records
    :param session: Boto3 Session
    :return: None
    """

    client = create_client(session)
    stream = BytesIO()

    df = polars.DataFrame([x.__dict__ for x in records])
    df.write_parquet(stream, compression='snappy')
    try:
        client.put_object(Bucket=bucket, Key=key, Body=stream.getvalue())
    except ClientError as ex:
        logging.error('Failed to write records to bucket: %s : %s', key, ex.args)
        raise ex


def main(bucket: str, *, week: int = 0, year: int = 0, season: int = 0, group: str | None = None,
         date: str | None = None) -> None:
    """
    Main Retrieval Function
    :param bucket: S3 Bucket
    :param week: Week Number
    :param year: Year Value
    :param season: Season Type Number
    :param group: Group Number
    :param date: Date Start value
    :return: None
    """

    if not bucket:
        logging.error('Bucket Name Required')
        sys.exit(1)

    base_url = os.getenv('BASE_URL', '')
    logging.info('Retrieving Schedule....(%s)', base_url)
    service = ScheduleService(base_url)
    session = Session(region_name='us-east-1')
    results = service.get_schedule(week=week, year=year, game_type=season, group=group, date=date)
    if not results:
        logging.warning('No Schedule Entries found.')
        sys.exit(0)

    results = [x.copy(update={'week': week, 'year': year, 'game_type': season}) for x in results]
    logging.info('Outputting Schedule File...(%s)', len(results))

    file_name = f"{uuid.uuid4()}.parquet"
    if date:
        file_name = f"{date}-{file_name}"
    key = posixpath.join('schedule', str(week), str(year), file_name)
    write_output(bucket, key, results, session)
    logging.info('Done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('botocore').setLevel(logging.FATAL)
    logging.getLogger('boto3').setLevel(logging.FATAL)

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bucket', type=str, required=True, help='S3 Bucket')
    parser.add_argument('-y', '--year', type=int, required=False, default=0,
                        help='Year of schedule')
    parser.add_argument('-w', '--week', type=int, required=False, default=0,
                        help='Week of schedule')
    parser.add_argument('-s', '--season', type=int, required=False, default=0,
                        help='Season Type of Schedule')
    parser.add_argument('-g', '--group', type=int, required=False, default=0,
                        help='Group Type of Schedule')
    parser.add_argument('-d', '--date', type=str, required=False, help='Start Date of Schedule')
    args = parser.parse_args()

    main(args.bucket, week=args.week, year=args.year, season=args.season, group=args.group,
         date=args.date)
