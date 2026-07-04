import re
import statistics


def split_sentences(text):
    sentences = re.split(r"[.!?]+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def tokenize_words(text):
    return re.findall(r"\b\w+\b", text.lower())


def analyze_stylometry(text):
    sentences = split_sentences(text)
    words = tokenize_words(text)

    if not words or not sentences:
        return {
            "stylometric_score": 0.5,
            "sentence_length_variance": 0,
            "type_token_ratio": 0,
            "punctuation_density": 0,
            "average_sentence_length": 0
        }

    sentence_lengths = [
        len(tokenize_words(sentence)) for sentence in sentences
    ]

    if len(sentence_lengths) > 1:
        sentence_length_variance = statistics.variance(sentence_lengths)
    else:
        sentence_length_variance = 0

    unique_words = set(words)
    type_token_ratio = len(unique_words) / len(words)

    punctuation_count = len(re.findall(r"[.,!?;:]", text))
    punctuation_density = punctuation_count / len(words)

    average_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

    uniform_sentence_score = max(0, 1 - min(sentence_length_variance / 25, 1))
    vocabulary_score = max(0, 1 - type_token_ratio)
    punctuation_score = min(punctuation_density * 5, 1)

    stylometric_score = round(
        (0.40 * uniform_sentence_score)
        + (0.40 * vocabulary_score)
        + (0.20 * punctuation_score),
        2
    )

    return {
        "stylometric_score": stylometric_score,
        "sentence_length_variance": round(sentence_length_variance, 2),
        "type_token_ratio": round(type_token_ratio, 2),
        "punctuation_density": round(punctuation_density, 2),
        "average_sentence_length": round(average_sentence_length, 2)
    }


if __name__ == "__main__":
    
    sample_text = (
    "Hello."
)
    

    print(analyze_stylometry(sample_text))