from flask import Flask, request, jsonify
import uuid

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

    return jsonify({
        "content_id": str(uuid.uuid4()),
        "attribution": "uncertain",
        "confidence": 0.5,
        "label": "We're not sure who wrote this."
    })


if __name__ == "__main__":
    app.run(debug=True)