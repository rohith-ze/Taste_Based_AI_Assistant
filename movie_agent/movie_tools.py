# movie_tools.py
import os
from typing import List
from langchain.tools import tool
from emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations
from gemini_utils import explain_recommendations
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

EMBY_SERVER = os.getenv("EMBY_SERVER")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
USER_NAME = os.getenv("USER_NAME")

# Store movies globally for reuse
watched_cache = []
recommended_cache = []

def _fetch_movies():
    user_id = get_user_id(EMBY_SERVER, EMBY_API_KEY, USER_NAME)
    if not user_id:
        print("[ERROR] Could not fetch user ID.")
        return []

    movies = get_watched_movies(EMBY_SERVER, EMBY_API_KEY, user_id)
    return movies

def _get_top_genre(movies: List[dict]) -> str:
    genre_list = []
    for movie in movies:
        genres = movie.get("Genres", [])
        if isinstance(genres, list):
            genre_list.extend(genres)

    if not genre_list:
        print("[❌] No genres found in Emby data.")
        return "urn:tag:genre:media:drama"  # Fallback genre

    top_genre = Counter(genre_list).most_common(1)[0][0].lower().replace(" ", "_")
    return f"urn:tag:genre:media:{top_genre}"

@tool
def fetch_watched_movies() -> List[dict]:
    """Fetch the recently watched movies from Emby."""
    global watched_cache
    watched_cache = _fetch_movies()
    return [{"Name": m["Name"], "Genres": m["Genres"]} for m in watched_cache]

@tool
def recommend_movies() -> List[str]:
    """Recommend new movies based on watched history using Qloo."""
    global watched_cache, recommended_cache
    if not watched_cache:
        watched_cache = _fetch_movies()

    genre_urn = _get_top_genre(watched_cache)
    print(f"[🎯] Using top genre: {genre_urn}")

    recommended_cache = get_qloo_recommendations(genre_urn=genre_urn, year_min=2020)
    return recommended_cache

@tool
def summarize_movie_taste() -> str:
    """Summarize the user's movie taste and assess recommendation fit."""
    global watched_cache, recommended_cache
    if not watched_cache:
        watched_cache = _fetch_movies()

    watched_titles = [m['Name'] for m in watched_cache]
    return explain_recommendations(watched_titles, recommended_cache)
