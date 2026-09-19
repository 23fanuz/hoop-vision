# Synthetic Game Fixtures

## Purpose

Synthetic game fixtures are hand-authored JSON files used to test HoopVision's first analytics pipeline.

A fixture should describe one basketball game using source-independent data:
game metadata, teams, players, starting lineups, and an ordered list of events.

## Top-Level Shape

Each fixture is a JSON object with these fields:

- `schema_version`: Fixture format version.
- `game`: Metadata for one game.
- `teams`: The two teams in the game.
- `players`: Players available for the game.
- `starters`: The five starting players for each team.
- `events`: Ordered game events.

```json
{
  "schema_version": "0.1",
  "game": {},
  "teams": [],
  "players": [],
  "starters": {},
  "events": []
}
```

## Identifiers

IDs should be stable strings inside a fixture.

Examples:

- `game_id`: `game_001`
- `team_id`: `home`, `away`, `sharks`, `comets`
- `player_id`: `home_01`, `away_04`
- `event_id`: `evt_001`

IDs do not need to be globally unique yet. They only need to be unique within one fixture.

## Game

```json
{
  "game": {
    "game_id": "game_001",
    "season": "2026",
    "date": "2026-01-15",
    "home_team_id": "home",
    "away_team_id": "away"
  }
}
```

## Teams

```json
{
  "teams": [
    {
      "team_id": "home",
      "name": "Home Team",
      "abbreviation": "HSH"
    },
    {
      "team_id": "away",
      "name": "Away Team",
      "abbreviation": "ACT"
    }
  ]
}
```

## Players

Players are listed in one flat collection. Each player references the team they belong to.

```json
{
  "players": [
    {
      "player_id": "home_01",
      "team_id": "home",
      "name": "Test Player",
      "number": 1
    }
  ]
}
```

## Starters

Starters define the initial on-court lineup for each team.

```json
{
  "starters": {
    "home": ["home_01", "home_02", "home_03", "home_04", "home_05"],
    "away": ["away_01", "away_02", "away_03", "away_04", "away_05"]
  }
}
```

## Event Ordering

Events must be listed in game order. Within a period, clocks should move from
higher remaining time to lower remaining time.

The `score` field represents the game score after the event has been applied.

## Event Types

Initial event types:

- `period_start`
- `made_shot`
- `missed_shot`
- `free_throw`
- `rebound`
- `turnover`
- `substitution`
- `period_end`

```json
[
  {
    "event_id": "evt_001",
    "period": 1,
    "clock": "12:00",
    "event_type": "period_start",
    "score": {
      "home": 0,
      "away": 0
    }
  },
  {
    "event_id": "evt_002",
    "period": 1,
    "clock": "11:32",
    "event_type": "made_shot",
    "team_id": "home",
    "player_id": "home_01",
    "points": 2,
    "score": {
      "home": 2,
      "away": 0
    }
  },
  {
    "event_id": "evt_003",
    "period": 1,
    "clock": "06:10",
    "event_type": "substitution",
    "team_id": "home",
    "player_out_id": "home_03",
    "player_in_id": "home_08",
    "score": {
      "home": 14,
      "away": 11
    }
  }
]
```

## Validation Rules

A valid fixture must satisfy these rules:

- `schema_version` must be present.
- A fixture must contain exactly two teams.
- Every player must reference an existing `team_id`.
- Each team must have exactly five starters.
- Starter IDs must reference existing players on that team.
- Event IDs must be unique.
- Events must be listed in game order.
- Every event must include `period`, `clock`, `event_type`, and `score`.
- `made_shot` events must include `team_id`, `player_id`, and `points`.
- `free_throw` events must include `team_id`, `player_id`, and `points`.
- `free_throw` points must be `0` for a miss or `1` for a make.
- Substitution events must include `team_id`, `player_out_id`, and `player_in_id`.
- Substitution players must belong to the substitution team.
- A substitution cannot remove a player who is not currently on the court.
- A substitution cannot add a player who is already on the court.
