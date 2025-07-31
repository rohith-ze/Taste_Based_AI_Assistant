import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")

def explain_recommendations(watched_titles, recommended_titles):
    if not watched_titles or not recommended_titles:
        return "No watched or recommended titles provided."

    prompt = (
        f"User 1 and User 2 watched: {', '.join(watched_titles[:5])}.\n"
        f"Recommended movies: {', '.join(recommended_titles[:5])}.\n"
        "Explain why these suggestions match their shared preferences."
    )
    try:
        res = model.generate_content(prompt)
        return getattr(res, "text", "[❌] Gemini error")
    except Exception as e:
        return f"[ERROR] Gemini failed: {e}"
