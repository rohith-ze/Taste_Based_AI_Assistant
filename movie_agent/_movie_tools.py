# movie_tools.py
import os
from typing import List
from langchain.tools import tool
from .emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations, get_trending_movies, get_recent_movies
from .gemini_utils import explain_recommendations
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

EMBY_SERVER = os.getenv("EMBY_SERVER")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
USER_NAME = os.getenv("USER_NAME")
USER_LOCATION = os.getenv("USER_LOCATION", "India")  # loaded from .env

# Cache
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
        return "urn:tag:genre:media:drama"  # fallback genre

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
    """Recommend movies using Qloo based on both watched history and user location."""
    global watched_cache, recommended_cache
    if not watched_cache:
        watched_cache = _fetch_movies()

    genre_urn = _get_top_genre(watched_cache)
    location = USER_LOCATION
    print(f"[🎯] Fetching recommendations by genre: {genre_urn} and location: {location}")

    # Step 1: Fetch taste-based recommendations
    taste_based = get_qloo_recommendations(
        genre_urn=genre_urn,
        year_min=2020,
        location_query=None  # no location here
    )

    # Step 2: Fetch location-based recommendations
    location_based = get_qloo_recommendations(
        genre_urn=None,
        year_min=2020,
        location_query=location
    )

    # Step 3: Merge while preserving order & deduplication
    seen = set()
    merged = []
    for movie in taste_based + location_based:
        if movie not in seen:
            seen.add(movie)
            merged.append(movie)

    recommended_cache = merged
    return merged

@tool
def summarize_movie_taste() -> str:
    """Summarize the user's movie taste and assess recommendation fit."""
    global watched_cache, recommended_cache
    if not watched_cache:
        watched_cache = _fetch_movies()

    watched_titles = [m['Name'] for m in watched_cache]
    return explain_recommendations(watched_titles, recommended_cache)

@tool
def fetch_trending_movies() -> List[dict]:
    """Fetch trending (most watched) movies from Emby."""
    return get_trending_movies(EMBY_SERVER, EMBY_API_KEY)

@tool
def fetch_recent_movies() -> List[dict]:
    """Fetch recently released movies from Emby."""
    return get_recent_movies(EMBY_SERVER, EMBY_API_KEY)
