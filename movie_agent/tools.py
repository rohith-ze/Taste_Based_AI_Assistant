# tools.py
from langchain.tools import tool
from emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations
from gemini_utils import explain_recommendations
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def fetch_watched_movies() -> list:
    """Fetch recently watched movie titles from the user's Emby server."""
    emby_api_key = os.getenv("EMBY_API_KEY")
    emby_server = os.getenv("EMBY_SERVER")
    user_name = os.getenv("USER_NAME")

    user_id = get_user_id(emby_server, emby_api_key, user_name)
    if not user_id:
        return ["[ERROR] Could not fetch Emby user ID."]

    movies = get_watched_movies(emby_server, emby_api_key, user_id)
    titles = [m["Name"] for m in movies if m.get("Name")]
    return titles or ["[ERROR] No watched movies found."]


@tool
def qloo_recommend_movies(genre: str = "urn:tag:genre:media:comedy", year_min: int = 2022) -> list:
    """Get movie recommendations based on taste using Qloo's Insights API."""
    return get_qloo_recommendations(genre_urn=genre, year_min=year_min)


@tool
def gemini_taste_summary(titles: list) -> str:
    """Explain movie taste based on a list of watched movie titles using Gemini."""
    return explain_recommendations(titles)
