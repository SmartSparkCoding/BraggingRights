from flask import Flask, request
import subprocess
import hmac
import hashlib

app = Flask(__name__)

SECRET = b"very-secret-i-dont-care-if-you-see-this"


@app.route("/github", methods=["POST"])
def github():

    signature = request.headers.get("X-Hub-Signature-256")

    if signature:
        expected = "sha256=" + hmac.new(
            SECRET,
            request.data,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return "Invalid signature", 403

    print("GitHub push received")

    subprocess.Popen(
        ["/root/braggingrights/deploy.sh"]
    )

    return "Deploy started", 200


app.run(
    host="0.0.0.0",
    port=9000
)