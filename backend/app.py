"""
ASTraCore++ — Flask API for code analysis and similarity comparison.

Run from the backend directory: python app.py
Serves the frontend so open http://127.0.0.1:5000 in a browser.
"""

import os

from flask import Flask, jsonify, request, send_from_directory

from analyzer import analyze
from lexer import tokenize
from similarity import combined_similarity_percent
from utils import normalize_tokens, preprocess

# Project root: parent of backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__)


def _tokens_to_json(tokens):
    return [(t, v) for t, v in tokens]


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/script.js")
def script_js():
    return send_from_directory(FRONTEND_DIR, "script.js", mimetype="application/javascript")


@app.route("/analyze", methods=["POST"])
def analyze_code():
    """
    Accept JSON: { "code": "..." }
    Returns: { "tokens": [...], "warnings": [...] }
    """
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str):
        return jsonify({"error": "invalid payload"}), 400

    cleaned = preprocess(code)
    tokens = tokenize(cleaned)
    warnings = analyze(tokens)

    return jsonify(
        {
            "tokens": _tokens_to_json(tokens),
            "warnings": warnings,
        }
    )


@app.route("/compare", methods=["POST"])
def compare_codes():
    """
    Accept JSON: { "code1": "...", "code2": "..." }
    Returns: { "similarity_percent": 0-100 }
    """
    data = request.get_json(silent=True) or {}
    code1 = data.get("code1", "")
    code2 = data.get("code2", "")
    if not isinstance(code1, str) or not isinstance(code2, str):
        return jsonify({"error": "invalid payload"}), 400

    t1 = normalize_tokens(tokenize(preprocess(code1)))
    t2 = normalize_tokens(tokenize(preprocess(code2)))
    pct = combined_similarity_percent(t1, t2)

    return jsonify({"similarity_percent": pct})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
