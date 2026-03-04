from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests, os, glob

app = Flask(__name__)
CORS(app, origins="*")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

@app.route("/", methods=["GET"])
def home():
    # Try to find any HTML file
    files = glob.glob("/app/*.html")
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html")
    return jsonify({"error": "no html found", "files": os.listdir("/app")})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": CLAUDE_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-6", "max_tokens": 1024, "system": data.get("system",""), "messages": data.get("messages",[])},
            timeout=30
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
