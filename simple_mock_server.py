#!/usr/bin/env python3
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    return jsonify({
        "output_text": "navigate to object",
        "output_len": 18
    })

@app.route("/generate", methods=["POST"])
def generate():
    return chat()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=10000, debug=False)
