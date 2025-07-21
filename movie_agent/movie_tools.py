# movie_tools.py
import os
from dotenv import load_dotenv
from langchain.tools import tool
from emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations
from gemini_utils import explain_recommendations

load_dotenv()

@tool
def fetch_watched_movies():
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
def recommend_movies(genre: str) -> list:
    """Get Qloo taste-based movie recommendations for a specific genre."""
    try:
        genre_urn = f"urn:tag:genre:media:{genre.lower()}"
        return get_qloo_recommendations(genre_urn=genre_urn, year_min=2022)
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

        # Extract genres and find the most common one
        all_genres = [genre for m in watched for genre in m.get('Genres', [])]
        if all_genres:
            most_common_genre = max(set(all_genres), key=all_genres.count)
            genre_urn = f"urn:tag:genre:media:{most_common_genre.lower()}"
        else:
            # Default genre if no watched movies have genres
            most_common_genre = 'comedy'
            genre_urn = f"urn:tag:genre:media:{most_common_genre.lower()}"


        recommended = get_qloo_recommendations(genre_urn=genre_urn)
        return explain_recommendations(watched_titles, recommended)
    except Exception as e:
        return f"[ERROR] Summary generation failed: {e}"
