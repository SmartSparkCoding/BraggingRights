from collections import defaultdict
from datetime import date

from database import(
    get_db,
    get_competition_goals,
    get_games_between_dates,
    get_game_players
)

DEFAULT_RANKING_POINTS = {
    1: 5,
    2: 4,
    3: 3,
    4: 2,
    5: 1
}

SUPPORTED_GOAL_TYPES = {
    "overall_ranking",
    "highest_score",
    "most_games",
    "most_first_places",
    "highest_average_score"
}

def get_ranking_points(
        ranking,
        ranking_points=None
):
    if ranking_points is None:
        ranking_points = DEFAULT_RANKING_POINTS

    return ranking_points.get(ranking, 0)

def get_competition(
        competition_id
):
    with get_db() as db:
        return db.execute("""
            SELECT *
            FROM competitions
            WHERE id = ?
        """, (
            competition_id,
        )).fetchone()

def get_competition_games(
        competition
):
    return get_games_between_dates(
        competition["start_date"],
        competition["end_date"]
    )

def get_game_players_for_games(
        games
):
    players = []

    for game in games:
        game_players = get_game_players(
            game["id"]
        )

        for player in game_players:
            players.append({
                "game_id": game["id"],
                "game_type_id": game["game_type_id"],
                "game_name": game["game_name"],
                "played_at": game["played_at"],
                "player_name": player["player_name"],
                "ranking": player["ranking"],
                "score": player["score"]
            })

    return players

def calculate_overall_ranking(
        games,
        ranking_points=None
):
    scores = defaultdict(int)
    games_played = defaultdict(int)
    first_places = defaultdict(int)
    if ranking_points is None:
        ranking_points = DEFAULT_RANKING_POINTS
    for game in games:
        players = get_game_players(
            game["id"]
        )
        for player in players:
            name = player["player_name"]
            ranking = player["ranking"]
            points = get_ranking_points(
                ranking,
                ranking_points
            )
            scores[name] += points
            games_played[name] += 1
            if ranking == 1:
                first_places[name] += 1
    
    leaderboard = []
    for player_name in scores:
        leaderboard.append({
            "player_name": player_name,
            "points": scores[player_name],
            "games_played": games_played[player_name],
            "first_places": first_places[player_name]
        })
    leaderboard.sort(
        key=lambda player: (
            -player["points"],
            -player["first_places"],
            -player["games_played"],
            player["player_name"].lower()
        )
    )

    for index, player in enumerate(
        leaderboard,
        start=1
    ):
        player["position"] = index

    return leaderboard

def calculate_highest_score(
        games,
        game_type_id=None
): 
    highest_scores = {}
    for game in games:
        if (
            game_type_id is not None
            and game ["game_type_id"] != game_type_id
        ):
            continue
        players = get_game_players(
            game["id"]
        )
        for player in players:
            if player["score"] is None:
                continue
            name = player["player_name"]
            score = float(player["score"])
            if (
                name not in highest_scores
                or score > highest_scores[name]["score"]
            ):
                highest_scores[name] = {
                    "player_name": name,
                    "score": score,
                    "game_id": game["id"],
                    "game_name": game["game_name"],
                    "played_at": game["played_at"]
                }

    leaderboard = list(
        highest_scores.values()
    )

    leaderboard.sort(
        key=lambda player: (
            -player["score"],
            player["player_name"].lower()
        )
    )

    for index, player in enumerate(
        leaderboard,
        start=1
    ):
        player["position"] = index
    
    return leaderboard

def calculate_most_games(
        games,
        game_type_id=None
): 
    games_played = defaultdict(int)
    for game in games:
        if (
            game_type_id is not None
            and game["game_type_id"] != game_type_id
        ):
            continue 

        players = get_game_players(
            game["id"]
        )
        for player in players:
            games_played[
                player["player_name"]
            ] += 1
    
    leaderboard = []
    for player_name, count in games_played.items():
        leaderboard.append({
            "player_name": player_name,
            "games_played": count
        })
    
    leaderboard.sort(
        key=lambda player: (
            -player["games_played"],
            player["player_name"].lower()
        )
    )

    for index, player in enumerate(
        leaderboard,
        start=1
    ):
        player["position"] = index
    
    return leaderboard

def calculate_most_first_places(
    games,
    game_type_id=None
):
    first_places = defaultdict(int)

    for game in games:

        if (
            game_type_id is not None
            and game["game_type_id"] != game_type_id
        ):
            continue

        players = get_game_players(
            game["id"]
        )

        for player in players:

            if player["ranking"] == 1:
                first_places[
                    player["player_name"]
                ] += 1

    leaderboard = []

    for player_name, count in first_places.items():
        leaderboard.append({
            "player_name": player_name,
            "first_places": count
        })

    leaderboard.sort(
        key=lambda player: (
            -player["first_places"],
            player["player_name"].lower()
        )
    )

    for index, player in enumerate(
        leaderboard,
        start=1
    ):
        player["position"] = index

    return leaderboard

def calculate_highest_average_score(
        games,
        game_type_id=None
):
    scores = defaultdict(list)
    for game in games:
        if (
            game_type_id is not None
            and game["game_type_id"] != game_type_id
        ):
            continue
        
        players = get_game_players(
            game["id"]
        )

        for player in players:
            if player["score"] is None:
                continue
            
            scores[
                player["player_name"]
            ].append(
                float(player["score"])
            )

    leaderboard = []

    for player_name, player_scores in scores.items():
        if not player_scores:
            continue
        average = sum(
            player_scores
        ) / len(player_scores)

        leaderboard.append({
            "player_name": player_name,
            "average_score": average,
            "games_with_scores": len(
                player_scores
            ),
            "scores": player_scores
        })
    
    leaderboard.sort(
        key=lambda player: (
            -player["average_score"],
            player["player_name"].lower()
        )
    )

    for index, player in enumerate(
        leaderboard,
        start=1
    ):
        player["position"] = index
    
    return leaderboard

def calculate_goal(
        goal, 
        competition
):
    goal_type = goal["goal_type"]

    if goal_type not in SUPPORTED_GOAL_TYPES:
        raise ValueError(
            f"Unsupported goal type: {goal_type}"
        )
    
    games = get_competition_games(
        competition
    )

    game_type_id = goal["game_type_id"]
    if goal_type == "overall_ranking":
        return calculate_overall_ranking(
            games
        )
    
    if goal_type == "highest_score":
        return calculate_highest_score(
            games,
            game_type_id
        )
    
    if goal_type == "most_games":
        return calculate_most_games(
            games,
            game_type_id
        )
    
    if goal_type == "most_first_places":
        return calculate_most_first_places(
            games,
            game_type_id
        )
    
    if goal_type == "highest_average_score":
        return calculate_highest_average_score(
            games,
            game_type_id
        )
    
    return []

def find_winners(
        leaderboard
):
    if not leaderboard:
        return []
    
    if "points" in leaderboard[0]:
        winning_value = leaderboard[0]["points"]

        return [
            player
            for player in leaderboard
            if player["points"] == winning_value
        ]
    
    if "score" in leaderboard[0]:
        winning_value = leaderboard[0]["score"]

        return [
            player
            for player in leaderboard
            if player["score"] == winning_value
        ]
    
    if "games_played" in leaderboard[0]:
        winning_value = leaderboard[0]["games_played"]

        return [
            player
            for player in leaderboard
            if player["games_played"] == winning_value
        ]
    
    if "first_places" in leaderboard[0]:
        winning_value = leaderboard[0]["first_places"]

        return [
            player
            for player in leaderboard
            if player["first_places"] == winning_value
        ]
    
    if "average_score" in leaderboard[0]:
        winning_value = leaderboard[0]["average_score"]

        return [
            player
            for player in leaderboard
            if player["average_score"] == winning_value
        ]
    
    return []

def calculate_competition(
        competition_id
):
    competition = get_competition(
        competition_id
    )

    if competition is None:
        raise ValueError(
            "Competition not found"
        )
    
    goals = get_competition_goals(
        competition_id
    )

    results = []

    for goal in goals:
        leaderboard = calculate_goal(
            goal,
            competition
        )

        winners = find_winners(
            leaderboard
        )

        results.append({
            "goal": dict(goal),
            "leaderboard": leaderboard,
            "winners": winners
        })

    return {
        "competition": dict(
            competition
        ),
        "goals": results
    }

def get_current_competition():
    today = date.today().isoformat()

    with get_db() as db:
        competitions = db.execute("""
            SELECT *
            FROM competitions
            WHERE start_date <= ?
              AND end_date >= ?
            ORDER BY start_date
        """, (
            today,
            today
        )).fetchall()

    return [
        calculate_competition(
            competition["id"]
        )
        for competition in competitions
    ]

def get_all_competitions():
    with get_db() as db:
        competitions = db.execute("""
            SELECT *
            FROM competitions
            ORDER BY start_date DESC
        """).fetchall()

    return [
        calculate_competition(
            competition["id"]
        )
        for competition in competitions
    ]

def get_player_competition_stats(
        player_name,
        competition_id
): 
    competition = get_competition(
        competition_id
    )

    if competition is None:
        raise ValueError(
            "Competition not found"
        )
    
    games = get_competition_games(
        competition
    )

    total_points = 0
    games_played = 0
    first_places = 0
    scores = []

    for game in games:
        players = get_game_players(
            game["id"]
        )

        for player in players:
            if (
                player["player_name"]
                != player_name
            ):
                continue

            games_played += 1

            total_points += get_ranking_points(
                player["ranking"]
            )

            if player["ranking"] == 1:
                first_places += 1

            if player["score"] is not None:
                scores.append(
                    float(player["score"])
                )

    average_score = None

    if scores:
        average_score = (
            sum(scores) / len(scores)
        )

    return {
        "player_name": player_name,
        "competition_id": competition_id,
        "games_played": games_played,
        "total_points": total_points,
        "first_places": first_places,
        "scores": scores,
        "average_score": average_score
    }

def get_player_global_stats(
        player_name
): 
    with get_db() as db:
       games = db.execute("""
            SELECT
                games.id,
                games.played_at,
                games.game_type_id,
                game_list.name AS game_name,
                game_players.ranking,
                game_players.score
            FROM game_players

            JOIN games
                ON game_players.game_id = games.id

            JOIN game_list
                ON games.game_type_id = game_list.id

            WHERE game_players.player_name = ?

            ORDER BY games.played_at DESC
        """, (
            player_name,
        )).fetchall()

    total_points = 0
    games_played = len(games)
    first_places = 0
    scores = []

    for game in games:
        total_points += get_ranking_points(
            game["ranking"]
        ) 

        if game["ranking"] == 1:
            first_places += 1

        if game["score"] is not None:
            scores.append(
                float(game["score"])
            )

    average_score = None
    if scores:
        average_score = (
            sum(scores) / len(scores)
        )

    return {
        "player_name": player_name,
        "games_played": games_played,
        "total_points": total_points,
        "first_places": first_places,
        "average_score": average_score,
        "games": [
            dict(game)
            for game in games
        ]
    }