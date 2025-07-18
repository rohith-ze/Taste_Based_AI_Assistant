# movie_tools.py
import os
from dotenv import load_dotenv
from langchain.tools import tool
from emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations
from gemini_utils import explain_recommendations

load_dotenv()

@tool
def fetch_watched_movies() -> list:
    """Fetch recently watched movies from Emby."""
    try:
        emby_server = os.getenv("EMBY_SERVER")
        api_key = os.getenv("EMBY_API_KEY")
        username = os.getenv("USER_NAME")
        user_id = get_user_id(emby_server, api_key, username)
        if not user_id:
            raise ValueError("Failed to get user ID")
        watched = get_watched_movies(emby_server, api_key, user_id)
        return [{"Name": m["Name"], "Genres": m.get("Genres", [])} for m in watched]
    except Exception as e:
        print("[ERROR] Failed to fetch watched movies:", e)
        return []

@tool
def recommend_movies() -> list:
    """Get Qloo taste-based movie recommendations."""
    try:
        # Hardcoded genre can be updated to dynamic genre extraction logic later
        return get_qloo_recommendations(genre_urn="urn:tag:genre:media:comedy", year_min=2022)
    except Exception as e:
        print("[ERROR] Failed to fetch Qloo recommendations:", e)
        return []

@tool
def summarize_movie_taste() -> str:
    """Summarize the user's movie taste and assess Qloo recommendations."""
    try:
        emby_server = os.getenv("EMBY_SERVER")
        api_key = os.getenv("EMBY_API_KEY")
        username = os.getenv("USER_NAME")
        user_id = get_user_id(emby_server, api_key, username)
        if not user_id:
            return "[ERROR] Could not get user ID"

        watched = get_watched_movies(emby_server, api_key, user_id)
        watched_titles = [m['Name'] for m in watched][:5]
        recommended = get_qloo_recommendations()
        return explain_recommendations(watched_titles, recommended)
    except Exception as e:
        return f"[ERROR] Summary generation failed: {e}"
