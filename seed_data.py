from database import (
    init_db,
    get_db,
    add_game_type,
    create_game,
    create_competition,
    add_competition_goal
)


init_db()


def get_or_create_game(name, description=None):
    with get_db() as db:
        existing = db.execute(
            """
            SELECT id
            FROM game_list
            WHERE name = ?
            """,
            (name,)
        ).fetchone()

    if existing:
        return existing["id"]

    return add_game_type(
        name,
        description
    )


scrabble_id = get_or_create_game(
    "Scrabble",
    "A classic word game."
)

monopoly_id = get_or_create_game(
    "Monopoly",
    "The classic property trading game."
)

mario_kart_id = get_or_create_game(
    "Mario Kart",
    "A racing game."
)

uno_id = get_or_create_game(
    "UNO",
    "A classic card game."
)

cluedo_id = get_or_create_game(
    "Cluedo",
    "A murder mystery board game."
)


games = [
    {
        "game_type_id": scrabble_id,
        "played_at": "2026-07-01",
        "players": [
            {
                "name": "Jacob",
                "ranking": 1,
                "score": 245
            },
            {
                "name": "Sarah",
                "ranking": 2,
                "score": 198
            },
            {
                "name": "Ollie",
                "ranking": 3,
                "score": 176
            }
        ]
    },
    {
        "game_type_id": monopoly_id,
        "played_at": "2026-07-02",
        "players": [
            {
                "name": "Sarah",
                "ranking": 1,
                "score": 4200
            },
            {
                "name": "Jacob",
                "ranking": 2,
                "score": 3100
            },
            {
                "name": "Leroy",
                "ranking": 3,
                "score": 2100
            },
            {
                "name": "Ollie",
                "ranking": 4,
                "score": 1500
            }
        ]
    },
    {
        "game_type_id": mario_kart_id,
        "played_at": "2026-07-03",
        "players": [
            {
                "name": "Jacob",
                "ranking": 1,
                "score": 12
            },
            {
                "name": "Leroy",
                "ranking": 2,
                "score": 9
            },
            {
                "name": "Sarah",
                "ranking": 3,
                "score": 7
            }
        ]
    },
    {
        "game_type_id": uno_id,
        "played_at": "2026-07-04",
        "players": [
            {
                "name": "Ollie",
                "ranking": 1
            },
            {
                "name": "Jacob",
                "ranking": 2
            },
            {
                "name": "Sarah",
                "ranking": 3
            },
            {
                "name": "Leroy",
                "ranking": 4
            }
        ]
    },
    {
        "game_type_id": scrabble_id,
        "played_at": "2026-07-05",
        "players": [
            {
                "name": "Sarah",
                "ranking": 1,
                "score": 289
            },
            {
                "name": "Jacob",
                "ranking": 2,
                "score": 241
            }
        ]
    },
    {
        "game_type_id": monopoly_id,
        "played_at": "2026-07-06",
        "players": [
            {
                "name": "Jacob",
                "ranking": 1,
                "score": 5500
            },
            {
                "name": "Ollie",
                "ranking": 2,
                "score": 4300
            },
            {
                "name": "Sarah",
                "ranking": 3,
                "score": 2900
            }
        ]
    },
    {
        "game_type_id": cluedo_id,
        "played_at": "2026-07-07",
        "players": [
            {
                "name": "Leroy",
                "ranking": 1
            },
            {
                "name": "Sarah",
                "ranking": 2
            },
            {
                "name": "Jacob",
                "ranking": 3
            }
        ]
    },
    {
        "game_type_id": mario_kart_id,
        "played_at": "2026-07-08",
        "players": [
            {
                "name": "Ollie",
                "ranking": 1,
                "score": 15
            },
            {
                "name": "Jacob",
                "ranking": 2,
                "score": 11
            },
            {
                "name": "Sarah",
                "ranking": 3,
                "score": 8
            }
        ]
    },
    {
        "game_type_id": scrabble_id,
        "played_at": "2026-07-09",
        "players": [
            {
                "name": "Jacob",
                "ranking": 1,
                "score": 312
            },
            {
                "name": "Sarah",
                "ranking": 2,
                "score": 301
            },
            {
                "name": "Leroy",
                "ranking": 3,
                "score": 250
            }
        ]
    },
    {
        "game_type_id": uno_id,
        "played_at": "2026-07-10",
        "players": [
            {
                "name": "Sarah",
                "ranking": 1
            },
            {
                "name": "Leroy",
                "ranking": 2
            },
            {
                "name": "Jacob",
                "ranking": 3
            }
        ]
    }
]


for game in games:
    create_game(
        game_type_id=game["game_type_id"],
        played_at=game["played_at"],
        players=game["players"]
    )


competition_id = create_competition(
    name="Summer Bragging Rights",
    start_date="2026-07-01",
    end_date="2026-07-22"
)


add_competition_goal(
    competition_id=competition_id,
    goal_type="overall_ranking",
    name="Overall Champion",
    prize="£20"
)


add_competition_goal(
    competition_id=competition_id,
    goal_type="highest_score",
    name="Best Scrabble Score",
    prize="Chocolate Bar",
    game_type_id=scrabble_id
)


add_competition_goal(
    competition_id=competition_id,
    goal_type="most_games",
    name="Most Games Played",
    prize="Choose the next game",
)


competition_id_2 = create_competition(
    name="July Game Master",
    start_date="2026-07-01",
    end_date="2026-07-22"
)


add_competition_goal(
    competition_id=competition_id_2,
    goal_type="most_first_places",
    name="Most Victories",
    prize="£10"
)


add_competition_goal(
    competition_id=competition_id_2,
    goal_type="highest_average_score",
    name="Best Average Scrabble Score",
    prize="Winner's Trophy",
    game_type_id=scrabble_id
)


print("Temporary test data added successfully!")
print()
print("Game types added: 5")
print("Games added: 10")
print("Competitions added: 2")
print()
print("You can now run:")
print("python3 app.py")