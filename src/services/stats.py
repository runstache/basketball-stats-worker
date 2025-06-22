"""
Services for working with Stats retrieval.
"""

import logging
import os
import posixpath
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from data.entities import BaseStatistic, Game, PlayerStatistic, Schedule, TeamStatistic


class BaseService:
    """
    Base Service Class
    """

    browser: webdriver.Chrome
    logger: logging.Logger
    base_url: str

    def __init__(self, base_url: str) -> None:
        """
        Base Service Constructor to establish a Web Browser.
        """
        self.base_url = base_url
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')

        if os.getenv('SELENIUM_DRIVER'):
            service = Service(os.getenv('SELENIUM_DRIVER'))
            self.browser = webdriver.Chrome(options=options, service=service)
        else:
            self.browser = webdriver.Chrome(options=options)
        self.logger = logging.getLogger(__name__)

    def get_stats_payload(self, url: str) -> dict | None:
        """
        Retrieves the Stats Payload from the Provided URL.
        :param url: URL to request.
        :return: Dictionary or None.
        """
        self.browser.get(url)
        return self.browser.execute_script('return window.__espnfitt__')

    def __del__(self):
        """
        Destructor for Closing up the Selenium Web Browser.
        """
        self.browser.quit()

    def _build_url_(self, parts: list[str]) -> str:
        """
        Adds additional pieces to the base url
        :param parts: Parts to add to the base url
        :return: Final URL
        """
        return posixpath.join(self.base_url, *parts)

    @staticmethod
    def _explode_stat_(stat: BaseStatistic, entry: tuple) -> list[TeamStatistic | PlayerStatistic]:
        """
        Updates a Statistic entry for multi-statistic values
        :param stat: Base Statistic
        :param entry: multi-statistic value
        :return: List of Statistics
        """

        # Handle Time values to seconds
        if ':' in entry[1]:
            parts = entry[1].split(':')
            time_value = (int(parts[0]) * 60) + int(parts[1])
            return [
                stat.copy(update={'statistic_name': entry[0], 'statistic_value': float(time_value)})
            ]

        pattern = r'[-/]'
        names = re.split(pattern, entry[0])
        values = re.split(pattern, entry[1])
        stats = []
        items = zip(names, values, strict=False)

        for item in items:
            value = item[1]
            if not value:
                value = 0
            stats.append(
                stat.copy(update={'statistic_name': item[0], 'statistic_value': float(value)})
            )

        return stats


class TeamService(BaseService):
    """
    Service for retrieving Team Level Stats
    """

    def _extract_stats_(self, game_id: str, team: dict, opponent: dict, stats: dict) -> list:
        """
        Extracts the Statistics for a Team
        :param game_id: Game Id
        :param team: Team Information
        :param opponent: Opponent Information
        :param stats: Stats collection
        :return: List of Team Stats
        """

        result = []
        for item in stats.items():
            value = (item[1].get('n'), item[1].get('d'))

            stat = TeamStatistic(
                team_url=team.get('lnk'),
                team=team.get('dspNm'),
                opponent=opponent.get('dspNm'),
                game_id=game_id,
            )
            result.extend(self._explode_stat_(stat, value))

        return result

    def get_stats(self, game_id: str) -> list[TeamStatistic]:
        """
        Retrieves the statistics from the provided Game ID.
        :param game_id: Game ID
        :return: Collection of Teams Statistics
        """
        parts = ['matchup', '_', 'gameId', game_id]
        url = self._build_url_(parts)

        payload = self.get_stats_payload(url)
        if not payload:
            return []
        game_info = (
            payload.get('page', {}).get('content', {}).get('gamepackage', {}).get('gmStrp', {})
        )
        stats = payload.get('page', {}).get('content', {}).get('gamepackage', {}).get('tmStats', {})

        home = stats.get('home', {})
        away = stats.get('away', {})

        away_team = away.get('t', {})
        home_team = home.get('t', {})

        results = []
        results.extend(
            self._extract_stats_(game_info.get('gid'), home_team, away_team, home.get('s', {}))
        )
        results.extend(
            self._extract_stats_(game_info.get('gid'), away_team, home_team, away.get('s', {}))
        )

        return results


class PlayerService(BaseService):
    """
    Services for retrieving the Player Level Statistics
    """

    def _build_stats_(self, team: dict, opponent: dict, stats: list[dict]) -> list:
        """
        Extracts the Player stats from the object
        :param team: Team Info
        :param opponent: Opponent
        :param stats: Stats Listing
        :return: List of Player Stats
        """

        result = []
        for stat in stats:
            athletes = stat.get('athlts', [])
            labels = stat.get('keys', [])

            for athlete in athletes:
                player = athlete.get('athlt', {})
                values = athlete.get('stats', [])

                stat_values = zip(labels, values, strict=False)
                item = PlayerStatistic(
                    player_url=player.get('lnk'),
                    player_name=player.get('dspNm'),
                    team=team.get('dspNm'),
                    opponent=opponent.get('dspNm'),
                )
                for stat_value in stat_values:
                    result.extend(self._explode_stat_(item, stat_value))

        return result

    def get_stats(self, game_id: str) -> list:
        """
        Retrieves the statistics for the provided Game ID.
        :param game_id: Game ID
        :return: Collection of Players Statistics
        """
        parts = ['boxscore', '_', 'gameId', game_id]
        url = self._build_url_(parts)
        payload = self.get_stats_payload(url)

        if not payload:
            return []
        stats = []

        bxscore = payload.get('page', {}).get('content', {}).get('gamepackage', {}).get('bxscr', [])
        if not bxscore or len(bxscore) < 2:
            return []

        away_stats = bxscore[0]
        home_stats = bxscore[1]

        stats.extend(
            self._build_stats_(
                away_stats.get('tm', {}), home_stats.get('tm', {}), away_stats.get('stats', [])
            )
        )
        stats.extend(
            self._build_stats_(
                home_stats.get('tm', {}), away_stats.get('tm', {}), home_stats.get('stats', [])
            )
        )
        return [x.copy(update={'game_id': game_id}) for x in stats]


class GameService(BaseService):
    """
    Service for retrieving the Game Level Information
    """

    def get_game_info(self, game_id: str) -> Game | None:
        """
        Retrieves the Game Info from the provided Game ID.
        :param game_id: Game ID
        :return: Optional Game
        """

        parts = ['matchup', '_', 'gameId', game_id]
        url = self._build_url_(parts)

        payload = self.get_stats_payload(url)
        if not payload:
            return None

        pkg = payload.get('page', {}).get('content', {}).get('gamepackage', {})

        if not pkg:
            return None

        gm_info = pkg.get('gmInfo', {})
        gm_strip = pkg.get('gmStrp', {})
        teams = pkg.get('prsdTms', {})

        return Game(
            game_id=game_id,
            home_team=teams.get('home', {}).get('displayName'),
            away_team=teams.get('away', {}).get('displayName'),
            location=gm_info.get('loc'),
            city=gm_info.get('locAddr', {}).get('city'),
            state=gm_info.get('locAddr', {}).get('state'),
            game_date=gm_strip.get('dt'),
            is_conference=gm_strip.get('isConferenceGame', False),
            note=gm_strip.get('nte'),
            home_score=int(teams.get('home', {}).get('score', 0)),
            away_score=int(teams.get('away', {}).get('score', 0)),
            line=gm_info.get('lne'),
            over_under=float(gm_info.get('ovUnd', 0)),
        )


class ScheduleService(BaseService):
    """
    Service for retrieving the Schedule Information
    """

    @staticmethod
    def _build_schedule_(event: dict) -> Schedule | None:
        """
        Transforms the Event to a collection of Schedule entries
        :param event: Schedule Event
        :return: List of Schedule Entries
        """
        if not event:
            return None
        teams = event.get('teams', [])
        home_team = [x for x in teams if x.get('isHome', False) is True]
        away_team = [x for x in teams if x.get('isHome', False) is False]

        if not home_team and not away_team:
            return None

        return Schedule(
            game_id=event.get('id', ''),
            home_team_code=home_team[0].get('abbrev'),
            away_team_code=away_team[0].get('abbrev'),
            home_team_name=home_team[0].get('displayName'),
            away_team_name=away_team[0].get('displayName'),
            game_date=event.get('date'),
            year=event.get('season', {}).get('year', 0),
            game_type=event.get('season', {}).get('type', 0),
        )

    def get_schedule(
        self,
        *,
        week: int = 0,
        year: int = 0,
        game_type: int = 0,
        date: str | None = None,
        group: str | None = None,
    ) -> list[Schedule]:
        """
        Retrieves the Schedule information for the week, year, and type
        :keyword week: Week Number
        :keyword year: Year Number
        :keyword game_type: Game Type Number (1,2,3)
        :keyword date: Starting Date Value
        :keyword group: Group ID
        :return: List of Schedule Information
        """

        parts = ['schedule', '_']
        if week:
            parts.append('week')
            parts.append(str(week))
        if year:
            parts.append('year')
            parts.append(str(year))
        if game_type:
            parts.append('seasontype')
            parts.append(str(game_type))
        if date:
            parts.append('date')
            parts.append(date)
        if group:
            parts.append('group')
            parts.append(group)

        url = self._build_url_(parts)
        payload = self.get_stats_payload(url)

        if not payload:
            return []

        entries = []
        events = payload.get('page', {}).get('content', {}).get('events', {})
        for item in events.items():
            entries.extend([self._build_schedule_(x) for x in item[1]])
        return [x for x in entries if x]
