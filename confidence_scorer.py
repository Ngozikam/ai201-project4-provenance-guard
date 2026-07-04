def calculate_confidence(llm_score, stylometric_score):
    return round((0.70 * llm_score) + (0.30 * stylometric_score), 2)


def classify_confidence(confidence):
    if confidence >= 0.85:
        return "likely_ai"
    elif confidence <= 0.59:
        return "likely_human"
    else:
        return "uncertain"


def generate_label(classification):
    if classification == "likely_ai":
        return "This content appears likely to have been generated using artificial intelligence. This assessment was produced automatically and may not always be correct."

    if classification == "likely_human":
        return "This content appears likely to have been written by a human author. This assessment was produced automatically and may not always be correct."

    return "The system could not confidently determine whether this content was written by a human or generated using artificial intelligence. Additional review may be required."