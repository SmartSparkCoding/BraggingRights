import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import date, timedelta


DATABASE_PATH = Path(__file__).parent / "bragging_rights.db"


@contextmanager
def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS game_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS game_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_type TEXT NOT NULL DEFAULT 'number',
            required INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (game_type_id)
                REFERENCES game_list(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type_id INTEGER NOT NULL,
            played_at TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_type_id)
                REFERENCES game_list(id)
        );

        CREATE TABLE IF NOT EXISTS game_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            ranking INTEGER NOT NULL,
            score REAL,
            FOREIGN KEY (game_id)
                REFERENCES games(id)
                ON DELETE CASCADE,
            UNIQUE (game_id, player_name),
            UNIQUE (game_id, ranking)
        );

        CREATE TABLE IF NOT EXISTS game_player_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_player_id INTEGER NOT NULL,
            field_id INTEGER NOT NULL,
            value TEXT,
            FOREIGN KEY (game_player_id)
                REFERENCES game_players(id)
                ON DELETE CASCADE,
            FOREIGN KEY (field_id)
                REFERENCES game_fields(id)
                ON DELETE CASCADE,
            UNIQUE (game_player_id, field_id)
        );

        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS competition_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id INTEGER NOT NULL,
            goal_type TEXT NOT NULL,
            name TEXT NOT NULL,
            prize TEXT NOT NULL,
            game_type_id INTEGER,
            FOREIGN KEY (competition_id)
                REFERENCES competitions(id)
                ON DELETE CASCADE,
            FOREIGN KEY (game_type_id)
                REFERENCES game_list(id)
        );

        CREATE INDEX IF NOT EXISTS idx_games_played_at
            ON games(played_at);

        CREATE INDEX IF NOT EXISTS idx_games_game_type
            ON games(game_type_id);

        CREATE INDEX IF NOT EXISTS idx_game_players_game
            ON game_players(game_id);

        CREATE INDEX IF NOT EXISTS idx_game_players_player
            ON game_players(player_name);

        CREATE INDEX IF NOT EXISTS idx_competition_dates
            ON competitions(start_date, end_date);
        """)


def get_all_games():
    with get_db() as db:
        return db.execute("""
            SELECT *
            FROM game_list
            ORDER BY name COLLATE NOCASE
        """).fetchall()


def get_game(game_id):
    with get_db() as db:
        return db.execute("""
            SELECT *
            FROM game_list
            WHERE id = ?
        """, (game_id,)).fetchone()


def add_game_type(name, description=None):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO game_list (
                name,
                description
            )
            VALUES (?, ?)
        """, (
            name,
            description
        ))

        return cursor.lastrowid


def add_game_field(
    game_type_id,
    field_name,
    field_type="number",
    required=False
):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO game_fields (
                game_type_id,
                field_name,
                field_type,
                required
            )
            VALUES (?, ?, ?, ?)
        """, (
            game_type_id,
            field_name,
            field_type,
            int(required)
        ))

        return cursor.lastrowid


def get_game_fields(game_type_id):
    with get_db() as db:
        return db.execute("""
            SELECT *
            FROM game_fields
            WHERE game_type_id = ?
            ORDER BY id
        """, (game_type_id,)).fetchall()


def create_game(
    game_type_id,
    played_at,
    players
):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO games (
                game_type_id,
                played_at
            )
            VALUES (?, ?)
        """, (
            game_type_id,
            played_at
        ))

        game_id = cursor.lastrowid

        for player in players:
            db.execute("""
                INSERT INTO game_players (
                    game_id,
                    player_name,
                    ranking,
                    score
                )
                VALUES (?, ?, ?, ?)
            """, (
                game_id,
                player["name"],
                player["ranking"],
                player.get("score")
            ))

        return game_id


def create_competition(
    name,
    start_date,
    end_date
):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO competitions (
                name,
                start_date,
                end_date
            )
            VALUES (?, ?, ?)
        """, (
            name,
            start_date,
            end_date
        ))

        return cursor.lastrowid


def add_competition_goal(
    competition_id,
    goal_type,
    name,
    prize,
    game_type_id=None
):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO competition_goals (
                competition_id,
                goal_type,
                name,
                prize,
                game_type_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            competition_id,
            goal_type,
            name,
            prize,
            game_type_id
        ))

        return cursor.lastrowid


def get_active_competitions(date):
    with get_db() as db:
        return db.execute("""
            SELECT *
            FROM competitions
            WHERE start_date <= ?
              AND end_date >= ?
            ORDER BY start_date
        """, (
            date,
            date
        )).fetchall()


def get_competition_goals(competition_id):
    with get_db() as db:
        return db.execute("""
            SELECT
                competition_goals.*,
                game_list.name AS game_name
            FROM competition_goals
            LEFT JOIN game_list
                ON competition_goals.game_type_id = game_list.id
            WHERE competition_goals.competition_id = ?
            ORDER BY competition_goals.id
        """, (
            competition_id,
        )).fetchall()


def get_games_between_dates(
    start_date,
    end_date,
    game_type_id=None
):
    with get_db() as db:

        if game_type_id is not None:
            return db.execute("""
                SELECT
                    games.*,
                    game_list.name AS game_name
                FROM games
                JOIN game_list
                    ON games.game_type_id = game_list.id
                WHERE games.played_at >= ?
                  AND games.played_at <= ?
                  AND games.game_type_id = ?
                ORDER BY games.played_at
            """, (
                start_date,
                end_date,
                game_type_id
            )).fetchall()

        return db.execute("""
            SELECT
                games.*,
                game_list.name AS game_name
            FROM games
            JOIN game_list
                ON games.game_type_id = game_list.id
            WHERE games.played_at >= ?
              AND games.played_at <= ?
            ORDER BY games.played_at
        """, (
            start_date,
            end_date
        )).fetchall()


def get_game_players(game_id):
    with get_db() as db:
        return db.execute("""
            SELECT *
            FROM game_players
            WHERE game_id = ?
            ORDER BY ranking
        """, (
            game_id,
        )).fetchall()
    
def get_home_stats():
    with get_db() as db:
        games_played = db.execute("""
            SELECT COUNT(*) AS count
            FROM games
        """).fetchone()["count"]

        most_played = db.execute("""
            SELECT
                game_list.name,
                COUNT(games.id) AS count
            FROM games
            JOIN game_list
                ON games.game_type_id = game_list.id
            GROUP BY games.game_type_id
            ORDER BY count DESC, game_list.name ASC
            LIMIT 1
        """).fetchone()

        ranking_points = db.execute("""
            SELECT
                game_players.player_name,
                SUM(
                    CASE game_players.ranking
                        WHEN 1 THEN 5
                        WHEN 2 THEN 4
                        WHEN 3 THEN 3
                        WHEN 4 THEN 2
                        WHEN 5 THEN 1
                        ELSE 0
                    END
                ) AS points
            FROM game_players
            GROUP BY game_players.player_name
            ORDER BY points DESC, game_players.player_name ASC
            LIMIT 1
        """).fetchone()

        return {
            "games_played": games_played,
            "most_played": (
                most_played["name"]
                if most_played
                else "None"
            ),
            "current_leader": (
                ranking_points["player_name"]
                if ranking_points
                else "No-one"
            )
        }

def should_blur_general_stats():
    today = date.today()

    with get_db() as db:
        competition = db.execute("""
            SELECT *
            FROM competitions
            WHERE start_date <= ?
              AND end_date >= ?
            ORDER BY end_date ASC
            LIMIT 1
        """, (
            today.isoformat(),
            today.isoformat()
        )).fetchone()

    if competition is None:
        return False

    end_date = date.fromisoformat(
        competition["end_date"]
    )

    days_remaining = (
        end_date - today
    ).days

    return 0 <= days_remaining <= 3