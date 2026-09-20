import logging
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Get key from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in the .env file.")

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GOOGLE_API_KEY)


def get_diet_insights(food_data: list) -> list:
    insights = []

    # 1. DATA PREP: Minimal serialization to save input tokens.
    summary = ", ".join([f"{f['food_name']} ({f['calories']} kcal)" for f in food_data])

    # 2. EXPERT PROMPT (English): Use of ROLE, FEW-SHOT, and CoT to guide reasoning.
    prompt = f"""
    ROLE: Professional dietitian analyzing food intake.
    CONSTRAINTS: Plain text ONLY. No Markdown (*). No line breaks. Max 20 words. to analyze if the user's diet is healthy or unhealthy.
    FEW-SHOT: Apple: 50 kcal, Chicken Salad: 300 kcal -> Apple is low-calorie, Chicken Salad is high-calorie.
    INPUT: {summary}
    REASONING: Compare top vs bottom.
    OUTPUT:"""

    # 3. TECHNICAL PARAMS: Temperature 0.1 ensures deterministic responses free from "hallucinations."
    config = types.GenerateContentConfig(temperature=0.1, top_p=0.95)

    try:
        raw_models = client.models.list()
        # Dynamic filter: searches for models that support text and ignores catalog prefixes.
        candidate_names = [
            m.name.replace("models/", "")
            for m in raw_models
            if any(x in m.name.lower() for x in ["flash", "gemma", "pro", "nano"])
        ]
        # In ai_coach.py, limit the list after the filter.
        candidate_names = [
            m for m in candidate_names if m in ["gemini-2.5-flash", "gemma-3-4b-it"]
        ]
        logger.info(f"Scanning {len(candidate_names)} models...")
    except Exception as e:
        logger.error(f"Catalog Error: {e}")
        return [{"error": "Inaccessible"}]

    # 4. EXECUTION LOOP: Full scan with throttling to avoid 429 (Rate Limit) errors.
    for model_id in candidate_names:
        try:
            logger.info(f"Testing: {model_id}")
            response = client.models.generate_content(
                model=model_id, contents=prompt, config=config
            )

            if response.text:
                # Sanitization via software: remove asterisks and line breaks that the AI might generate.
                clean = response.text.replace("*", "").replace("\n", " ").strip()
                insights.append({"model": model_id, "comment": clean})

            # Sleep required outside the try block to ensure the interval is maintained even in case of errors.
            time.sleep(1.0)
        except Exception:
            continue

    return insights
