"""
Data Entities Module
"""
import copy
from dataclasses import dataclass
from typing import Optional, NamedTuple


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
    team: Optional[str] = None
    opponent: Optional[str] = None
    statistic_type: Optional[str] = None
    statistic_name: Optional[str] = None
    statistic_code: Optional[str] = None
    statistic_value: float = 0
    game_id: Optional[str] = None


@dataclass
class TeamStatistic(BaseStatistic):
    """
    Team level statistics class
    """

    team_url: Optional[str] = None


@dataclass
class PlayerStatistic(BaseStatistic):
    """
    Player Level Statistic Data Entity
    """

    player_name: Optional[str] = None
    player_url: Optional[str] = None


@dataclass
class Schedule(BaseEntity):
    """
    Schedule Data Entity
    """

    game_id: str = ''
    home_team_code: Optional[str] = None
    away_team_code: Optional[str] = None
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    game_date: Optional[str] = None


@dataclass
class Game(BaseEntity):
    """
    Game Info Data Entity
    """

    game_id: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    game_date: Optional[str] = None
    is_conference: bool = False
    note: Optional[str] = None
    home_score: int = 0
    away_score: int = 0
    line: Optional[str] = None
    over_under: float = 0
