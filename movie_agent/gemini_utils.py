# gemini_utils.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file.")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-lite")

def explain_recommendations(watched_titles, recommended_titles):
    if not watched_titles or not recommended_titles:
        return "[ERROR] Both watched and recommended movie lists are required."

    prompt = (
        f"I have watched these movies: {', '.join(watched_titles[:5])}.\n"
        f"And these movies were recommended to me: {', '.join(recommended_titles[:5])}.\n"
        "Based on this, analyze my movie taste and explain why these recommendations are a good fit."
    )

    try:
        response = model.generate_content(prompt)
        if hasattr(response, "text"):
            return response.text.strip()
        elif hasattr(response, "candidates"):
            return response.candidates[0].text.strip()
        else:
            return "[ERROR] Unexpected Gemini response format."
    except Exception as e:
        return f"[ERROR] Gemini response failed: {e}"
