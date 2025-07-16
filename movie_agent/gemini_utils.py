# gemini_utils.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini with API key from .env file
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file.")
genai.configure(api_key=api_key)

# Initialize the Gemini 2.0 Flash model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")  # Correct model name

def explain_recommendations(watched_titles):
    if not watched_titles:
        return "[ERROR] No watched titles provided."

    prompt = (
        f"I have watched these movies: {', '.join(watched_titles[:5])}.\n"
        "Can you explain my movie taste based on these, and recommend 5 more?"
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
