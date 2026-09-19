from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class EventType(StrEnum):
    PERIOD_START = "period_start"
    MADE_SHOT = "made_shot"
    MISSED_SHOT = "missed_shot"
    FREE_THROW = "free_throw"
    REBOUND = "rebound"
    TURNOVER = "turnover"
    SUBSTITUTION = "substitution"
    PERIOD_END = "period_end"


class Team(BaseModel):
    team_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    abbreviation: str = Field(min_length=1, max_length=5)


class Player(BaseModel):
    player_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    number: int = Field(ge=0)


class Game(BaseModel):
    game_id: str = Field(min_length=1)
    season: str = Field(min_length=1)
    date: date
    home_team_id: str = Field(min_length=1)
    away_team_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def teams_must_be_different(self) -> "Game":
        if self.home_team_id == self.away_team_id:
            raise ValueError("home_team_id and away_team_id must be different")
        return self


class Score(BaseModel):
    home: int = Field(ge=0)
    away: int = Field(ge=0)


class GameEvent(BaseModel):
    event_id: str = Field(min_length=1)
    period: int = Field(ge=1)
    clock: str = Field(pattern=r"^\d{1,2}:\d{2}$")
    event_type: EventType
    score: Score
    team_id: str | None = None
    player_id: str | None = None
    points: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def scoring_events_include_required_fields(self) -> "GameEvent":
        if self.event_type in {EventType.MADE_SHOT, EventType.FREE_THROW}:
            if self.team_id is None or self.player_id is None or self.points is None:
                raise ValueError("scoring events require team_id, player_id, and points")

        if self.event_type == EventType.FREE_THROW and self.points not in {0, 1}:
            raise ValueError("free_throw points must be 0 or 1")

        return self


class Substitution(GameEvent):
    event_type: EventType = Field(default=EventType.SUBSTITUTION, frozen=True)
    team_id: str = Field(min_length=1)
    player_out_id: str = Field(min_length=1)
    player_in_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def players_must_be_different(self) -> "Substitution":
        if self.player_out_id == self.player_in_id:
            raise ValueError("player_out_id and player_in_id must be different")
        return self


class LineupSnapshot(BaseModel):
    game_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    player_ids: tuple[str, str, str, str, str]


class PossessionEstimate(BaseModel):
    game_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    possessions: float = Field(ge=0)


class ImpactSummary(BaseModel):
    game_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    player_id: str = Field(min_length=1)
    possessions_played: float = Field(ge=0)
    points_for: int = Field(ge=0)
    points_against: int = Field(ge=0)
    raw_plus_minus: int
    offensive_rating: float | None = None
    defensive_rating: float | None = None
    net_rating: float | None = None
