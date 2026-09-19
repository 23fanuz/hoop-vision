import pytest
from pydantic import ValidationError

from hoopvision.domain.models import (
    EventType,
    Game,
    GameEvent,
    ImpactSummary,
    LineupSnapshot,
    Player,
    PossessionEstimate,
    Substitution,
    Team,
)


def test_team_accepts_valid_data():
    team = Team(team_id="home", name="Home Team", abbreviation="HSH")

    assert team.team_id == "home"
    assert team.abbreviation == "HSH"


def test_team_rejects_empty_team_id():
    with pytest.raises(ValidationError):
        Team(team_id="", name="Home Team", abbreviation="HSH")


def test_player_requires_non_negative_number():
    player = Player(player_id="home_01", team_id="home", name="Test Player", number=1)

    assert player.number == 1

    with pytest.raises(ValidationError):
        Player(player_id="home_01", team_id="home", name="Test Player", number=-1)


def test_game_requires_different_home_and_away_teams():
    game = Game(
        game_id="game_001",
        season="2026",
        date="2026-01-15",
        home_team_id="home",
        away_team_id="away",
    )

    assert game.home_team_id == "home"

    with pytest.raises(ValidationError):
        Game(
            game_id="game_001",
            season="2026",
            date="2026-01-15",
            home_team_id="home",
            away_team_id="home",
        )


def test_scoring_event_requires_team_player_and_points():
    event = GameEvent(
        event_id="evt_002",
        period=1,
        clock="11:32",
        event_type=EventType.MADE_SHOT,
        team_id="home",
        player_id="home_01",
        points=2,
        score={"home": 2, "away": 0},
    )

    assert event.points == 2

    with pytest.raises(ValidationError):
        GameEvent(
            event_id="evt_002",
            period=1,
            clock="11:32",
            event_type=EventType.MADE_SHOT,
            score={"home": 2, "away": 0},
        )


def test_free_throw_points_must_be_zero_or_one():
    GameEvent(
        event_id="evt_010",
        period=1,
        clock="08:10",
        event_type=EventType.FREE_THROW,
        team_id="home",
        player_id="home_01",
        points=1,
        score={"home": 5, "away": 4},
    )

    with pytest.raises(ValidationError):
        GameEvent(
            event_id="evt_011",
            period=1,
            clock="08:09",
            event_type=EventType.FREE_THROW,
            team_id="home",
            player_id="home_01",
            points=2,
            score={"home": 6, "away": 4},
        )


def test_substitution_requires_different_players():
    substitution = Substitution(
        event_id="evt_003",
        period=1,
        clock="06:10",
        score={"home": 14, "away": 11},
        team_id="home",
        player_out_id="home_03",
        player_in_id="home_08",
    )

    assert substitution.event_type == EventType.SUBSTITUTION

    with pytest.raises(ValidationError):
        Substitution(
            event_id="evt_004",
            period=1,
            clock="06:00",
            score={"home": 14, "away": 11},
            team_id="home",
            player_out_id="home_03",
            player_in_id="home_03",
        )


def test_lineup_snapshot_requires_exactly_five_players():
    snapshot = LineupSnapshot(
        game_id="game_001",
        event_id="evt_001",
        team_id="home",
        player_ids=("home_01", "home_02", "home_03", "home_04", "home_05"),
    )

    assert len(snapshot.player_ids) == 5

    with pytest.raises(ValidationError):
        LineupSnapshot(
            game_id="game_001",
            event_id="evt_001",
            team_id="home",
            player_ids=("home_01", "home_02", "home_03", "home_04"),
        )


def test_possession_estimate_and_impact_summary_allow_zero_values():
    possession = PossessionEstimate(
        game_id="game_001",
        team_id="home",
        possessions=0,
    )
    summary = ImpactSummary(
        game_id="game_001",
        team_id="home",
        player_id="home_01",
        possessions_played=0,
        points_for=0,
        points_against=0,
        raw_plus_minus=0,
    )

    assert possession.possessions == 0
    assert summary.net_rating is None
