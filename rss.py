from feedgen.feed import FeedGenerator
import json

@app.route("/updates.xml")
def updates():
    fg = FeedGenerator()

    fg.id("https://braggingrights.mini-jacob.hackclub.app")
    fg.title("Bragging Rights Deployments")
    fg.link(
        href="https://braggingrights.mini-jacob.hackclub.app/updates.xml"
    )

    with open("deployments.json") as f:
        deployments = json.load(f)
    
    for deploy in deployments:
        entry = fg.add_entry()
        entry.id(deploy["commit"])
        entry.title(
            f"Deployment {deploy['commit']}"
        )
        entry.description(
            deploy["message"]
        )
        entry.pubDate(
            deploy["time"]
        )

    return fg.rss_str(), 200, {
        "Content-Type": "application/rss+xml"
    }