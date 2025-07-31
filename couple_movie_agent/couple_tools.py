from langchain.tools import tool
from couple_emby_utils import get_user_id, get_watched_movies
from couple_qloo_utils import get_qloo_recommendations
from couple_gemini_utils import explain_recommendations
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
EMBY_SERVER = os.getenv("EMBY_SERVER")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
USER_NAME_1 = os.getenv("EMBY_USER")
USER_NAME_2 = os.getenv("EMBY_USER_2")

watched_cache = []

def _fetch_joint_movies():
    if not EMBY_SERVER or not EMBY_API_KEY or not USER_NAME_1 or not USER_NAME_2:
        return []

    user_id_1 = get_user_id(EMBY_SERVER, EMBY_API_KEY, USER_NAME_1)
    user_id_2 = get_user_id(EMBY_SERVER, EMBY_API_KEY, USER_NAME_2)

    if not user_id_1 or not user_id_2:
        return []

    watched_1 = get_watched_movies(EMBY_SERVER, EMBY_API_KEY, user_id_1)
    watched_2 = get_watched_movies(EMBY_SERVER, EMBY_API_KEY, user_id_2)

    return watched_1 + watched_2

def _get_top_genre(movies):
    genres = []
    for m in movies:
        genres.extend(m.get("Genres", []))
    if not genres:
        return "urn:tag:genre:media:drama"
    top_genre = Counter(genres).most_common(1)[0][0].lower().replace(" ", "_")
    return f"urn:tag:genre:media:{top_genre}"

@tool
def fetch_joint_watched_movies(input) -> list:
    """Fetch combined watched movies of both users"""
    global watched_cache
    watched_cache = _fetch_joint_movies()
    return [{"Name": m["Name"], "Genres": m.get("Genres", [])} for m in watched_cache]

@tool
def recommend_couple_movies(input) -> list:
    """Recommend movies for the couple based on shared watched history"""
    global watched_cache
    if not watched_cache:
        watched_cache = _fetch_joint_movies()

    genre_urn = _get_top_genre(watched_cache)

    qloo_results = get_qloo_recommendations(genre_urn=genre_urn)
    formatted = []
    for movie in qloo_results:
        name = movie.get("name")
        image = movie.get("image_url")
        if image:
            formatted.append(f"* **{name}** ([Image]({image}))")
        else:
            formatted.append(f"* **{name}**")
    return formatted

@tool
def summarize_couple_taste(input) -> str:
    """Summarize shared movie taste of the couple"""
    global watched_cache
    if not watched_cache:
        watched_cache = _fetch_joint_movies()
    watched_titles = [m["Name"] for m in watched_cache]
    recommended_titles = [m.get("name") for m in get_qloo_recommendations()]
    return explain_recommendations(watched_titles[:5], recommended_titles[:5])
