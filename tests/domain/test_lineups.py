import pytest

from hoopvision.domain.lineups import LineupReconstructionError, reconstruct_lineups
from hoopvision.domain.models import Player, Substitution


def _players() -> list[Player]:
    return [
        Player(
            player_id=f"home_{number:02}",
            team_id="home",
            name=f"Home Player {number}",
            number=number,
        )
        for number in range(1, 9)
    ] + [
        Player(
            player_id=f"away_{number:02}",
            team_id="away",
            name=f"Away Player {number}",
            number=number,
        )
        for number in range(1, 6)
    ]


def _substitution(
    *,
    event_id: str = "evt_003",
    player_out_id: str = "home_03",
    player_in_id: str = "home_08",
) -> Substitution:
    return Substitution(
        event_id=event_id,
        period=1,
        clock="06:10",
        score={"home": 14, "away": 11},
        team_id="home",
        player_out_id=player_out_id,
        player_in_id=player_in_id,
    )


def test_reconstruct_lineups_returns_snapshot_after_substitution():
    snapshots = reconstruct_lineups(
        game_id="game_001",
        starters={
            "home": ("home_01", "home_02", "home_03", "home_04", "home_05"),
            "away": ("away_01", "away_02", "away_03", "away_04", "away_05"),
        },
        players=_players(),
        substitutions=[_substitution()],
    )

    assert len(snapshots) == 1
    assert snapshots[0].event_id == "evt_003"
    assert snapshots[0].team_id == "home"
    assert snapshots[0].player_ids == (
        "home_01",
        "home_02",
        "home_08",
        "home_04",
        "home_05",
    )


def test_reconstruct_lineups_rejects_unknown_substitution_player():
    with pytest.raises(LineupReconstructionError, match="unknown player 'home_99'"):
        reconstruct_lineups(
            game_id="game_001",
            starters={
                "home": ("home_01", "home_02", "home_03", "home_04", "home_05"),
            },
            players=_players(),
            substitutions=[_substitution(player_in_id="home_99")],
        )


def test_reconstruct_lineups_rejects_player_out_who_is_not_on_court():
    with pytest.raises(LineupReconstructionError, match="not on court"):
        reconstruct_lineups(
            game_id="game_001",
            starters={
                "home": ("home_01", "home_02", "home_03", "home_04", "home_05"),
            },
            players=_players(),
            substitutions=[_substitution(player_out_id="home_07")],
        )


def test_reconstruct_lineups_rejects_invalid_starting_lineup_size():
    with pytest.raises(LineupReconstructionError, match="exactly five unique players"):
        reconstruct_lineups(
            game_id="game_001",
            starters={
                "home": ("home_01", "home_02", "home_03", "home_04"),
            },
            players=_players(),
            substitutions=[_substitution()],
        )
