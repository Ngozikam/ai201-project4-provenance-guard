import json
import os
from datetime import datetime

LOG_FILE = "logs/audit_log.json"


def get_log():
    """Return all audit log entries."""

    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as file:
        return json.load(file)


def write_log(entry):
    """Append a new entry to the audit log."""

    entries = get_log()
    entries.append(entry)

    with open(LOG_FILE, "w") as file:
        json.dump(entries, file, indent=4)


def create_log_entry(
        content_id,
        creator_id,
        attribution,
        confidence,
        llm_score):

    return {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "status": "classified"
    }