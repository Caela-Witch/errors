from datetime import datetime, UTC
from collections import defaultdict
from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
import http.client

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def format_iso_interval(td):
    seconds = int(td.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = ["P"]
    if days:
        parts.append(f"{days}D")
    if any([hours, minutes, seconds]):
        parts.append("T")
        if hours:
            parts.append(f"{hours}H")
        if minutes:
            parts.append(f"{minutes}M")
        if seconds:
            parts.append(f"{seconds}S")

    return "".join(parts) if len(parts) > 1 else "P0D"

server_stats = {
    "started": datetime.now(UTC),
    "endpoints": {
        "error": 0,
        "status": 0,
        "about": 0
    },
    "codes": defaultdict(int)
}

#@app.before_request
#def force_https():
#    if request.url.startswith("http://"):
#        return redirect(request.url.replace("http://", "https://"), code=301)

def handle_options():
    response = jsonify({"message": "CORS preflight successful"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response, 200

def handle_error(code):
    if not (100 <= code <= 599):
        code = 400

    server_stats['codes'][code] += 1
    message = http.client.responses.get(code, "Unknown Error")
    response = jsonify({"error": message})
    response.status_code = code
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/error", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def error():
    if request.method == "OPTIONS":
        return handle_options()

    server_stats["endpoints"]["error"] += 1

    if request.method == "GET":
        code = request.args.get("code", default=400, type=int)
    else:
        data = request.get_json(silent=True) or {}
        code = data.get("code", 400)

    return handle_error(code)

@app.route("/status", methods=["GET"])
def status():
    server_stats["endpoints"]["status"] += 1
    return jsonify({
        "status": "ok",
        "started": server_stats["started"].isoformat(),
        "now": datetime.now(UTC).isoformat(),
        "uptime": format_iso_interval(datetime.now(UTC) - server_stats["started"]),
        "endpoints": server_stats['endpoints'],
        "codes": dict(server_stats['codes'])
    }), 201

@app.route("/index.html", methods=["GET"])
@app.route("/about.html", methods=["GET"])
@app.route("/", methods=["GET"])
def about():
    server_stats["endpoints"]["about"] += 1
    return render_template('about.html')

