from flask import Flask, app, render_template, jsonify, Response
import json
from feedgen.feed import FeedGenerator
import subprocess 
import datetime

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('home.html')

@app.route("/up")
def up():
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd="/root/braggingrights"
        ).decode().strip()
    except:
        commit = "unknown"

    return jsonify({
        "status": "online",
        "service": "Bragging Rights, Owned by Jacob Navaratne",
        "version": commit,
        "last_updated": datetime.datetime.now(datetime.UTC).isoformat(),
        "environment": "production"
    })

@app.route("/updates.xml")
def updates():
    fg = FeedGenerator()

    fg.id("https://braggingrights.mini-jacob.hackclub.app")
    fg.title("Bragging Rights Deployments")
    fg.link(
        href="https://braggingrights.mini-jacob.hackclub.app/updates.xml"
    )
    fg.description("Automatic Bragging Rights deployment updates")

    try:
        with open("/root/braggingrights/deployments.json") as f:
            deployments = json.load(f)

        for deployment in deployments:
            entry = fg.add_entry()

            entry.id(deployment["commit"])
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
        entry.title("RSS Error")
        entry.description(str(e))

    return Response(
        fg.rss_str(),
        mimetype="application/rss+xml"
    )

if __name__ == '__main__':
    app.run(debug=True, port=7834, host="0.0.0.0")