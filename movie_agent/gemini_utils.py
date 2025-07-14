# gemini_utils.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Make sure this key is in .env

def explain_recommendations(watched_titles):
    prompt = (
        f"I have watched these movies: {', '.join(watched_titles[:5])}.\n"
        "Can you explain my movie taste based on these, and recommend 5 more?"
    )

    try:
        model = genai.GenerativeModel("gemini-pro")  # ✅ FIXED model name
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[ERROR] Gemini response failed: {e}"
