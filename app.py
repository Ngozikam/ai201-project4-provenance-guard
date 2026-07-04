from flask import Flask, request, jsonify
import uuid

from groq_classifier import classify_text

from audit_logger import (
    create_log_entry,
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


@app.route("/log", methods=["GET"])
def log():

    return jsonify({
        "entries": get_log()
    })


if __name__ == "__main__":
    app.run(debug=True)