# movie_tools.py
import os
from typing import List
from langchain.tools import tool
from .emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations, get_trending_movies, get_recent_movies, get_movie_details
from .gemini_utils import explain_recommendations
from dotenv import load_dotenv
from collections import Counter

script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path="/home/rohith/github/Taste_Based_AI_Assistant-2/movie_agent/.env")

EMBY_SERVER = os.getenv("EMBY_SERVER")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
USER_NAME = os.getenv("EMBY_USER")
USER_LOCATION = os.getenv("USER_LOCATION", "India")  # loaded from .env

# Cache
watched_cache = []
recommended_cache = []

def _fetch_movies():
    if not all([EMBY_SERVER, EMBY_API_KEY, USER_NAME]):
        return {"error": "EMBY_SERVER, EMBY_API_KEY, and USER_NAME must be set in the .env file."}
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
    if isinstance(watched_cache, dict) and 'error' in watched_cache:
        return watched_cache
    return [{"Name": m["Name"], "Genres": m["Genres"]} for m in watched_cache]

@tool
def recommend_movies(genre: str = None, language: str = None) -> List[str]:
    """
    Recommend movies using Qloo, then enrich with genre data from Emby.
    Can be filtered by genre (e.g., "comedy", "drama") and language (e.g., "english", "french").
    If no genre or language is specified, it provides general recommendations based on taste and location.
    """
    global watched_cache, recommended_cache
    if not watched_cache:
        watched_cache = _fetch_movies()

    qloo_recs = []
    # If a specific genre or language is requested, only fetch based on that.
    if genre or language:
        genre_urn = f"urn:tag:genre:media:{genre.lower().replace(' ', '_')}" if genre else None
        print(f"[🎯] Fetching specific recommendations. Genre: {genre_urn}, Language: {language}")
        qloo_recs = get_qloo_recommendations(
            genre_urn=genre_urn,
            year_min=2020,
            language=language
        )
    # Otherwise, get general recommendations.
    else:
        genre_urn = _get_top_genre(watched_cache)
        location = USER_LOCATION
        print(f"[🎯] Fetching general recommendations. Top Genre: {genre_urn}, Location: {location}")
        
        # Step 1: Fetch taste-based recommendations
        taste_based = get_qloo_recommendations(
            genre_urn=genre_urn,
            year_min=2020
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
            if isinstance(movie, dict) and 'name' in movie:
                movie_name = movie['name']
                if movie_name not in seen:
                    seen.add(movie_name)
                    merged.append(movie)
        qloo_recs = merged

    # Enrich with genre data from Emby
    enriched_recs = []
    for movie in qloo_recs:
        details = get_movie_details(EMBY_SERVER, EMBY_API_KEY, movie['name'])
        movie['genres'] = details.get('Genres', [])
        enriched_recs.append(movie)

    recommended_cache = enriched_recs
    
    # Format the output
    formatted_recommendations = []
    for movie in enriched_recs:
        movie_name = movie.get('name')
        image_url = movie.get('image_url')
        genres = ", ".join(movie.get('genres', []))
        if image_url:
            formatted_recommendations.append(f"* **{movie_name}** ([Image URL]({image_url})) (Genres: {genres})")
        else:
            formatted_recommendations.append(f"* **{movie_name}** (Genres: {genres})")
            
    return formatted_recommendations

@tool
def summarize_movie_taste() -> str:
    """Summarize the user's movie taste and assess recommendation fit."""
    global watched_cache, recommended_cache
    if not watched_cache:
        watched_cache = _fetch_movies()
    if isinstance(watched_cache, dict) and 'error' in watched_cache:
        return watched_cache['error']

    watched_titles = [m['Name'] for m in watched_cache]
    recommended_titles = [m['name'] for m in recommended_cache]
    return explain_recommendations(watched_titles, recommended_titles)

@tool
def fetch_trending_movies() -> List[dict]:
    """Fetch trending (most watched) movies from Emby."""
    return get_trending_movies(EMBY_SERVER, EMBY_API_KEY)

@tool
def fetch_recent_movies() -> List[dict]:
    """Fetch recently released movies from Emby."""
    return get_recent_movies(EMBY_SERVER, EMBY_API_KEY)
