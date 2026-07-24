from flask import (
    Flask,
    render_template,
    jsonify,
    Response,
    request,
    redirect,
    url_for,
    session
)

import json
from feedgen.feed import FeedGenerator
import subprocess
import datetime

from database import (
    init_db,
    get_home_stats,
    should_blur_general_stats,
    get_all_games,
    add_game_type,
    update_game_type,
    create_competition,
    update_competition,
    get_competition_goals,
    get_db,
    get_active_competitions,
    add_competition_goal
)
from leaderboard import get_player_global_stats


app = Flask(__name__)

app.secret_key = "my-name-is-jacoooooob-an-d-i-can-access-this-not-you"

init_db()


profiles = {
    "sarah": {
        "name": "Sarah",
        "pin": "2302"
    },
    "leroy": {
        "name": "Leroy",
        "pin": "1105"
    },
    "jacob": {
        "name": "Jacob",
        "pin": "2905"
    },
    "ollie": {
        "name": "Ollie",
        "pin": "1502"
    },
    "grannie_grandad": {
        "name": "Grannie + Grandad",
        "pin": "1948"
    }
}


@app.route("/")
def index():
    stats = get_home_stats()
    blur_general_stats = should_blur_general_stats()

    return render_template(
        "home.html",
        stats=stats,
        blur_general_stats=blur_general_stats
    )


@app.route("/profile-selector")
def profile_selector():
    return render_template(
        "profile-selector.html"
    )


@app.route("/admin")
def admin():
    stats = get_home_stats()

    with get_db() as db:
        game_types = db.execute("""
            SELECT *
            FROM game_list
            ORDER BY name COLLATE NOCASE
        """).fetchall()

        competitions = db.execute("""
            SELECT *
            FROM competitions
            ORDER BY start_date DESC
        """).fetchall()

        today = datetime.date.today()
        competition_list = []

        for competition in competitions:
            competition_data = dict(competition)

            start_date = datetime.date.fromisoformat(
                competition["start_date"]
            )

            end_date = datetime.date.fromisoformat(
                competition["end_date"]
            )

            if today < start_date:
                competition_data["status"] = "upcoming"
                competition_data["status_label"] = "Upcoming"
            elif today > end_date:
                competition_data["status"] = "finished"
                competition_data["status_label"] = "Finished"
            else:
                competition_data["status"] = "active"
                competition_data["status_label"] = "Active"

            competition_data["goals"] = [
                dict(goal)
                for goal in get_competition_goals(
                    competition["id"]
                )
            ]

            competition_list.append(
                competition_data
            )

        recorded_games = db.execute("""
            SELECT COUNT(*) AS count
            FROM games
        """).fetchone()["count"]

        total_players = db.execute("""
            SELECT COUNT(DISTINCT player_name) AS count
            FROM game_players
        """).fetchone()["count"]

    return render_template(
        "admin.html",
        stats=stats,
        game_types=game_types,
        competitions=competition_list,
        recorded_games=recorded_games,
        total_players=total_players
    )


@app.route(
    "/admin/api/games",
    methods=["POST"]
)
def admin_add_game():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided."
        }), 400

    name = data.get(
        "name",
        ""
    ).strip()

    description = data.get(
        "description",
        ""
    ).strip()

    if not name:
        return jsonify({
            "error": "Game name is required."
        }), 400

    try:
        game_id = add_game_type(
            name=name,
            description=description or None
        )

        return jsonify({
            "success": True,
            "game_id": game_id,
            "message": "Game added successfully."
        }), 201

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return jsonify({
                "error": "A game with that name already exists."
            }), 409

        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/games/<int:game_id>",
    methods=["PUT"]
)
def admin_edit_game(game_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided."
        }), 400

    name = data.get(
        "name",
        ""
    ).strip()

    description = data.get(
        "description",
        ""
    ).strip()

    if not name:
        return jsonify({
            "error": "Game name is required."
        }), 400

    try:
        updated = update_game_type(
            game_id=game_id,
            name=name,
            description=description or None
        )

        if not updated:
            return jsonify({
                "error": "Game not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Game updated successfully."
        })

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return jsonify({
                "error": "A game with that name already exists."
            }), 409

        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/games/<int:game_id>",
    methods=["DELETE"]
)
def admin_delete_game(game_id):
    try:
        with get_db() as db:
            game = db.execute("""
                SELECT *
                FROM game_list
                WHERE id = ?
            """, (
                game_id,
            )).fetchone()

            if game is None:
                return jsonify({
                    "error": "Game not found."
                }), 404

            db.execute("""
                DELETE FROM game_list
                WHERE id = ?
            """, (
                game_id,
            ))

        return jsonify({
            "success": True,
            "message": "Game deleted successfully."
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/competitions",
    methods=["POST"]
)
def admin_add_competition():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided."
        }), 400

    name = data.get(
        "name",
        ""
    ).strip()

    start_date = data.get(
        "start_date",
        ""
    ).strip()

    end_date = data.get(
        "end_date",
        ""
    ).strip()

    big_goal = data.get("big_goal") or {}
    small_goals = data.get(
        "small_goals",
        []
    )

    if not name:
        return jsonify({
            "error": "Competition name is required."
        }), 400

    if not start_date:
        return jsonify({
            "error": "Start date is required."
        }), 400

    if not end_date:
        return jsonify({
            "error": "End date is required."
        }), 400

    if end_date < start_date:
        return jsonify({
            "error": "End date cannot be before the start date."
        }), 400

    if not big_goal.get("name"):
        return jsonify({
            "error": "A big goal is required."
        }), 400

    if not big_goal.get("prize"):
        return jsonify({
            "error": "The big goal prize or additional information is required."
        }), 400

    if len(small_goals) != 2:
        return jsonify({
            "error": "Exactly 2 smaller goals are required."
        }), 400

    for goal in small_goals:
        if not goal.get("name"):
            return jsonify({
                "error": "Both smaller goals need a name."
            }), 400

        if not goal.get("prize"):
            return jsonify({
                "error": "Both smaller goals need a prize or additional information."
            }), 400

    try:
        competition_id = create_competition(
            name=name,
            start_date=start_date,
            end_date=end_date,
            big_goal=big_goal,
            small_goals=small_goals
        )

        return jsonify({
            "success": True,
            "competition_id": competition_id,
            "message": "Competition created successfully."
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/competitions/<int:competition_id>",
    methods=["GET"]
)
def admin_get_competition(competition_id):
    with get_db() as db:
        competition = db.execute("""
            SELECT *
            FROM competitions
            WHERE id = ?
        """, (
            competition_id,
        )).fetchone()

    if competition is None:
        return jsonify({
            "error": "Competition not found."
        }), 404

    return jsonify({
        "competition": dict(competition),
        "goals": [
            dict(goal)
            for goal in get_competition_goals(
                competition_id
            )
        ]
    })


@app.route(
    "/admin/api/competitions/<int:competition_id>",
    methods=["PUT"]
)
def admin_edit_competition(competition_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided."
        }), 400

    name = data.get(
        "name",
        ""
    ).strip()

    start_date = data.get(
        "start_date",
        ""
    ).strip()

    end_date = data.get(
        "end_date",
        ""
    ).strip()

    big_goal = data.get("big_goal") or {}
    small_goals = data.get(
        "small_goals",
        []
    )

    if not name:
        return jsonify({
            "error": "Competition name is required."
        }), 400

    if not start_date or not end_date:
        return jsonify({
            "error": "Start and end dates are required."
        }), 400

    if end_date < start_date:
        return jsonify({
            "error": "End date cannot be before the start date."
        }), 400

    if not big_goal.get("name"):
        return jsonify({
            "error": "A big goal is required."
        }), 400

    if not big_goal.get("prize"):
        return jsonify({
            "error": "The big goal prize or additional information is required."
        }), 400

    if len(small_goals) != 2:
        return jsonify({
            "error": "Exactly 2 smaller goals are required."
        }), 400

    for goal in small_goals:
        if not goal.get("name") or not goal.get("prize"):
            return jsonify({
                "error": "Both smaller goals need a name and prize or additional information."
            }), 400

    try:
        updated = update_competition(
            competition_id=competition_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            big_goal=big_goal,
            small_goals=small_goals
        )

        if not updated:
            return jsonify({
                "error": "Competition not found."
            }), 404

        return jsonify({
            "success": True,
            "message": "Competition updated successfully."
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/competitions/<int:competition_id>",
    methods=["DELETE"]
)
def admin_delete_competition(
    competition_id
):
    try:
        with get_db() as db:
            competition = db.execute("""
                SELECT *
                FROM competitions
                WHERE id = ?
            """, (
                competition_id,
            )).fetchone()

            if competition is None:
                return jsonify({
                    "error": "Competition not found."
                }), 404

            db.execute("""
                DELETE FROM competitions
                WHERE id = ?
            """, (
                competition_id,
            ))

        return jsonify({
            "success": True,
            "message": "Competition deleted successfully."
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/settings",
    methods=["POST"]
)
def admin_update_setting():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided."
        }), 400

    setting = data.get("setting")
    value = data.get("value")

    allowed_settings = {
        "competition_blur",
        "competition_blur_days"
    }

    if setting not in allowed_settings:
        return jsonify({
            "error": "Unknown setting."
        }), 400

    try:
        with get_db() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            db.execute("""
                INSERT INTO settings (
                    key,
                    value
                )
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
            """, (
                setting,
                str(value)
            ))

        return jsonify({
            "success": True,
            "message": "Setting updated successfully."
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/games/clear",
    methods=["DELETE"]
)
def admin_clear_games():
    try:
        with get_db() as db:
            db.execute("""
                DELETE FROM games
            """)

        return jsonify({
            "success": True,
            "message": "All recorded games have been deleted."
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route(
    "/admin/api/database/reset",
    methods=["POST"]
)
def admin_reset_database():
    try:
        with get_db() as db:
            db.execute("""
                DELETE FROM game_player_values
            """)

            db.execute("""
                DELETE FROM game_players
            """)

            db.execute("""
                DELETE FROM games
            """)

            db.execute("""
                DELETE FROM competition_goals
            """)

            db.execute("""
                DELETE FROM competitions
            """)

            db.execute("""
                DELETE FROM game_fields
            """)

            db.execute("""
                DELETE FROM game_list
            """)

            db.execute("""
                DELETE FROM settings
            """)

        return jsonify({
            "success": True,
            "message": "Database reset successfully."
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/pin", methods=["GET", "POST"])
def pin():
    profile_id = request.args.get("profile")

    if profile_id not in profiles:
        return "Profile not found", 404

    profile = profiles[profile_id]
    error = None

    if request.method == "POST":
        entered_pin = request.form.get("pin", "")

        if entered_pin == profile["pin"]:
            session["authenticated_profile"] = profile_id

            return redirect(
                url_for(
                    "profile",
                    profile_id=profile_id
                )
            )

        error = "Incorrect PIN"

    return render_template(
        "pin.html",
        profile_id=profile_id,
        profile_name=profile["name"],
        error=error
    )


@app.route("/profile/<profile_id>")
def profile(profile_id):
    if profile_id not in profiles:
        return "Profile not found", 404

    authenticated_profile = session.get(
        "authenticated_profile"
    )

    if authenticated_profile != profile_id:
        return redirect(
            url_for(
                "pin",
                profile=profile_id
            )
        )

    profile_data = profiles[profile_id]

    profile_stats = get_player_global_stats(
        profile_data["name"]
    )

    return render_template(
        "profile.html",
        profile_id=profile_id,
        profile_name=profile_data["name"],
        profile_stats=profile_stats,
        stats=get_home_stats(),
        recent_games=profile_stats["games"],
        game_stats=[],
        blur_general_stats=should_blur_general_stats()
    )


@app.route("/add-game")
def add_game():
    return render_template("add-game.html")


@app.route("/logout")
def logout():
    session.pop(
        "authenticated_profile",
        None
    )

    return redirect(
        url_for("index")
    )


@app.route("/up")
def up():
    try:
        commit = subprocess.check_output(
            [
                "git",
                "rev-parse",
                "--short",
                "HEAD"
            ],
            cwd="/root/braggingrights"
        ).decode().strip()

    except:
        commit = "unknown"

    return jsonify({
        "status": "online",
        "service": "Bragging Rights, Owned by Jacob Navaratne",
        "version": commit,
        "last_updated": datetime.datetime.now(
            datetime.UTC
        ).isoformat(),
        "environment": "production"
    })


@app.route("/updates.xml")
def updates():
    fg = FeedGenerator()

    fg.id(
        "https://braggingrights.mini-jacob.hackclub.app"
    )

    fg.title(
        "Bragging Rights Deployments"
    )

    fg.link(
        href="https://braggingrights.mini-jacob.hackclub.app/updates.xml"
    )

    fg.description(
        "Automatic Bragging Rights deployment updates"
    )

    try:
        with open(
            "/root/braggingrights/deployments.json"
        ) as f:
            deployments = json.load(f)

        for deployment in deployments:
            entry = fg.add_entry()

            entry.id(
                deployment["commit"]
            )

            entry.title(
                f"Deployment {deployment['commit']}"
            )

            entry.description(
                deployment["message"]
            )

            entry.pubDate(
                deployment["time"]
            )

    except Exception as e:
        entry = fg.add_entry()

        entry.id("error")

        entry.title(
            "RSS Error"
        )

        entry.description(
            str(e)
        )

    return Response(
        fg.rss_str(),
        mimetype="application/rss+xml"
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=7834,
        host="0.0.0.0"
    )