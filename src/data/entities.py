"""
Data Entities Module
"""

import copy
from dataclasses import dataclass
from typing import NamedTuple


class GameType(NamedTuple):
    """
    Game Type
    """

    type_id: int
    game_type: str


@dataclass
class BaseEntity:
    """
    Base Data Class
    """

    week: int = 0
    year: int = 0
    game_type: int = 0

    def copy(self, *, update: dict | None = None):
        """
        Creates a deep copy of the entity and performs an update of the provided fields
        :keyword update: Dictionary of keys to update
        :return: Copy of the entity
        """

        item = copy.deepcopy(self)
        if not update:
            return item

        upd = {k: v for k, v in update.items() if v}
        for entry in upd.items():
            if entry[0] in item.__dict__:
                setattr(item, entry[0], entry[1])
        return item


@dataclass
class BaseStatistic(BaseEntity):
    """
    Base Statistic Data Entity
    """

    team: str | None = None
    opponent: str | None = None
    statistic_type: str | None = None
    statistic_name: str | None = None
    statistic_code: str | None = None
    statistic_value: float = 0
    game_id: str | None = None


@dataclass
class TeamStatistic(BaseStatistic):
    """
    Team level statistics class
    """

    team_url: str | None = None


@dataclass
class PlayerStatistic(BaseStatistic):
    """
    Player Level Statistic Data Entity
    """

    player_name: str | None = None
    player_url: str | None = None


@dataclass
class Schedule(BaseEntity):
    """
    Schedule Data Entity
    """

    game_id: str = ''
    home_team_code: str | None = None
    away_team_code: str | None = None
    home_team_name: str | None = None
    away_team_name: str | None = None
    game_date: str | None = None


@dataclass
class Game(BaseEntity):
    """
    Game Info Data Entity
    """

    game_id: str | None = None
    home_team: str | None = None
    away_team: str | None = None
    location: str | None = None
    city: str | None = None
    state: str | None = None
    game_date: str | None = None
    is_conference: bool = False
    note: str | None = None
    home_score: int = 0
    away_score: int = 0
    line: str | None = None
    over_under: float = 0
