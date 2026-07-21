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
    get_active_competitions
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

    game_types = get_all_games()

    today = datetime.date.today().isoformat()

    active_competitions = get_active_competitions(
        today
    )

    competitions = [
        {
            "id": competition["id"],
            "name": competition["name"],
            "start_date": competition["start_date"],
            "end_date": competition["end_date"],
            "active": True
        }
        for competition in active_competitions
    ]

    return render_template(
        "admin.html",
        stats=stats,
        game_types=game_types,
        competitions=competitions,
        profiles=profiles
    )


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

        else:

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