import json
import os


from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def classify_text(text):
    """
    First detection signal for Provenance Guard.

    Sends submitted text to Groq and returns a structured
    assessment with an attribution result and LLM score.
    """

    prompt = f"""
You are an AI-content attribution assistant.

Analyze the text below and decide whether it is more likely human-written,
AI-generated, or uncertain.

Return ONLY valid JSON with these fields:
- attribution: one of "likely_human", "likely_ai", or "uncertain"
- llm_score: a number between 0.0 and 1.0, where 0.0 means strongly human-written and 1.0 means strongly AI-generated
- reasoning: one short sentence explaining the decision

Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    '''
    content = response.choices[0].message.content

    
    print("\n========== RAW GROQ RESPONSE ==========\n")
    print(content)
    print("\n=======================================\n")

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "attribution": "uncertain",
            "llm_score": 0.5,
            "reasoning": "The model response could not be parsed as JSON."
        }

    return result
'''
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content.strip()

    # Remove Markdown code fences if present
    if content.startswith("```json"):
        content = content.replace("```json", "", 1)

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        result = {
            "attribution": "uncertain",
            "llm_score": 0.5,
            "reasoning": "The model response could not be parsed as JSON."
        }

    return result

if __name__ == "__main__":
    sample_text = (
        "The sun dipped below the horizon, painting the sky in hues of amber "
        "and rose. I sat on the porch, coffee in hand, watching the neighborhood "
        "slowly go quiet."
    )

    result = classify_text(sample_text)
    print(json.dumps(result, indent=4))