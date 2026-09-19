from collections.abc import Iterable, Mapping, Sequence

from hoopvision.domain.models import LineupSnapshot, Player, Substitution


class LineupReconstructionError(ValueError):
    """Raised when lineup reconstruction finds inconsistent game data."""


def reconstruct_lineups(
    *,
    game_id: str,
    starters: Mapping[str, Sequence[str]],
    players: Iterable[Player],
    substitutions: Iterable[Substitution],
) -> list[LineupSnapshot]:
    """Calculate each team's on-court lineup after every substitution."""

    players_by_id = {player.player_id: player for player in players}
    current_lineups = {
        team_id: _validate_starting_lineup(team_id, player_ids, players_by_id)
        for team_id, player_ids in starters.items()
    }

    snapshots: list[LineupSnapshot] = []

    for substitution in substitutions:
        lineup = current_lineups.get(substitution.team_id)
        if lineup is None:
            raise LineupReconstructionError(
                f"substitution {substitution.event_id} references unknown team "
                f"{substitution.team_id!r}"
            )

        _validate_substitution_players(substitution, players_by_id)

        if substitution.player_out_id not in lineup:
            raise LineupReconstructionError(
                f"substitution {substitution.event_id} removes player "
                f"{substitution.player_out_id!r} who is not on court"
            )

        if substitution.player_in_id in lineup:
            raise LineupReconstructionError(
                f"substitution {substitution.event_id} adds player "
                f"{substitution.player_in_id!r} who is already on court"
            )

        next_lineup = tuple(
            substitution.player_in_id
            if player_id == substitution.player_out_id
            else player_id
            for player_id in lineup
        )

        if len(next_lineup) != 5 or len(set(next_lineup)) != 5:
            raise LineupReconstructionError(
                f"substitution {substitution.event_id} produced invalid lineup size"
            )

        current_lineups[substitution.team_id] = next_lineup
        snapshots.append(
            LineupSnapshot(
                game_id=game_id,
                event_id=substitution.event_id,
                team_id=substitution.team_id,
                player_ids=next_lineup,
            )
        )

    return snapshots


def _validate_starting_lineup(
    team_id: str,
    player_ids: Sequence[str],
    players_by_id: Mapping[str, Player],
) -> tuple[str, str, str, str, str]:
    if len(player_ids) != 5 or len(set(player_ids)) != 5:
        raise LineupReconstructionError(
            f"team {team_id!r} must start exactly five unique players"
        )

    for player_id in player_ids:
        player = players_by_id.get(player_id)
        if player is None:
            raise LineupReconstructionError(
                f"team {team_id!r} starter {player_id!r} is unknown"
            )
        if player.team_id != team_id:
            raise LineupReconstructionError(
                f"team {team_id!r} starter {player_id!r} belongs to team "
                f"{player.team_id!r}"
            )

    return (player_ids[0], player_ids[1], player_ids[2], player_ids[3], player_ids[4])


def _validate_substitution_players(
    substitution: Substitution,
    players_by_id: Mapping[str, Player],
) -> None:
    for player_id in (substitution.player_out_id, substitution.player_in_id):
        player = players_by_id.get(player_id)
        if player is None:
            raise LineupReconstructionError(
                f"substitution {substitution.event_id} references unknown player "
                f"{player_id!r}"
            )
        if player.team_id != substitution.team_id:
            raise LineupReconstructionError(
                f"substitution {substitution.event_id} references player "
                f"{player_id!r} from team {player.team_id!r}, not "
                f"{substitution.team_id!r}"
            )
