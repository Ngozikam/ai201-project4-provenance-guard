from flask import Flask, request, jsonify
import uuid

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from groq_classifier import classify_text

from audit_logger import (
    create_log_entry,
    create_appeal_entry,
    write_log,
    get_log
)

from stylometric_analyzer import analyze_stylometry

from confidence_scorer import (
    calculate_confidence,
    classify_confidence,
    generate_label
)

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Provenance Guard API"
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():

    data = request.get_json()

    text = data.get("text")
    creator_id = data.get("creator_id")

    content_id = str(uuid.uuid4())

    # First detection signal (Groq LLM)
    signal_result = classify_text(text)

    # Second detection signal (Stylometric Analysis)
    stylometric_result = analyze_stylometry(text)

    # Combined confidence score
    confidence = calculate_confidence(
        signal_result["llm_score"],
        stylometric_result["stylometric_score"]
    )

    # Final classification
    classification = classify_confidence(confidence)

    # Transparency label
    label = generate_label(classification)

    # Create audit log entry
    log_entry = create_log_entry(
        content_id=content_id,
        creator_id=creator_id,
        attribution=classification,
        confidence=confidence,
        llm_score=signal_result["llm_score"],
        stylometric_score=stylometric_result["stylometric_score"]
    )

    # Write audit log
    write_log(log_entry)

    # Return API response
    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": classification,
        "confidence": confidence,
        "label": label,
        "llm_score": signal_result["llm_score"],
        "stylometric_score": stylometric_result["stylometric_score"]
    })


@app.route("/appeal", methods=["POST"])
def appeal():

    data = request.get_json()

    content_id = data.get("content_id")
    creator_reasoning = data.get("creator_reasoning")

    appeal_entry = create_appeal_entry(
        content_id=content_id,
        creator_reasoning=creator_reasoning
    )

    write_log(appeal_entry)

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal received and logged for review."
    })


@app.route("/log", methods=["GET"])
def log():

    return jsonify({
        "entries": get_log()
    })


if __name__ == "__main__":
    app.run(debug=True)