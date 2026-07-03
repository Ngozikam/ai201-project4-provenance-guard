from flask import Flask, request, jsonify
import uuid

from groq_classifier import classify_text

from audit_logger import (
    create_log_entry,
    write_log,
    get_log
)

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Provenance Guard API"
    })


@app.route("/submit", methods=["POST"])
def submit():

    data = request.get_json()

    text = data.get("text")
    creator_id = data.get("creator_id")

    content_id = str(uuid.uuid4())

    signal_result = classify_text(text)

    confidence = 0.5

    label = "We're not sure who wrote this."

    log_entry = create_log_entry(
        content_id=content_id,
        creator_id=creator_id,
        attribution=signal_result["attribution"],
        confidence=confidence,
        llm_score=signal_result["llm_score"]
    )

    write_log(log_entry)

    return jsonify({
        "content_id": content_id,
        "attribution": signal_result["attribution"],
        "confidence": confidence,
        "label": label
    })


@app.route("/log", methods=["GET"])
def log():

    return jsonify({
        "entries": get_log()
    })


if __name__ == "__main__":
    app.run(debug=True)