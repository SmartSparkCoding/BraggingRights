from flask import Flask, app, render_template, jsonify 
import subprocess 
import datetime

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('home.html')

@app.route("/up")
def up():
        try:
            commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd="/root/braggingrights").decode().strip()
            return jsonify({"commit": commit})
        
        except:
            commit = "unknown"
        
        return jsonify({
              "status": "online",
              "service": "Bragging Rights, Owned by Jacob Navaratne",
              "version": commit,
              "last_updated": datetime.datetime.now(datetime.UTC).isoformat(),
              "environment": "production"
        })

if __name__ == '__main__':
    app.run(debug=True, port=7834, host="0.0.0.0")