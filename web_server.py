"""
web_server.py — Serves the 'hacked system' simulation as a web page.

Run this, then use ngrok to get a public link:
    python web_server.py
    ngrok http 5000

Send the ngrok link to any device — the simulation runs in the browser.
"""

import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="web", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("web", "index.html")

if __name__ == "__main__":
    print("=" * 60)
    print("  DARKDREEM — Web Simulation Server")
    print("  Local:  http://localhost:5000")
    print("  To share: run 'ngrok http 5000' in another terminal")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
