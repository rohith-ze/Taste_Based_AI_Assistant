# couple_agent.py

import os
from dotenv import load_dotenv
from collections import Counter
from emby_utils import get_user_id, get_watched_movies, get_qloo_recommendations
from gemini_utils import explain_recommendations

load_dotenv()

EMBY_SERVER = os.getenv("EMBY_SERVER")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
USER_1 = os.getenv("EMBY_USER")
USER_2 = os.getenv("EMBY_USER_2")
USER_LOCATION = os.getenv("USER_LOCATION", "India")

def fetch_couple_watched_movies():
    """Fetch watched movies for both users."""
    user1_id = get_user_id(EMBY_SERVER, EMBY_API_KEY, USER_1)
    user2_id = get_user_id(EMBY_SERVER, EMBY_API_KEY, USER_2)

    if not user1_id or not user2_id:
        return {"error": "Failed to fetch user IDs from Emby."}

    user1_movies = get_watched_movies(EMBY_SERVER, EMBY_API_KEY, user1_id)
    user2_movies = get_watched_movies(EMBY_SERVER, EMBY_API_KEY, user2_id)

    return {
        "user1": user1_movies,
        "user2": user2_movies
    }

def recommend_couple_movies():
    """Recommend movies for couples based on shared genres using Qloo."""
    data = fetch_couple_watched_movies()
    if "error" in data:
        return data["error"]

    genres = []
    for user_movies in [data["user1"], data["user2"]]:
        for m in user_movies:
            genres.extend(m.get("Genres", []))

    if not genres:
        return ["No genres found for either user."]

    # Find top 1 shared genre
    top_genre = Counter(genres).most_common(1)[0][0].lower().replace(" ", "_")
    genre_urn = f"urn:tag:genre:media:{top_genre}"

    print(f"[❤️] Shared top genre: {genre_urn}")

    recommendations = get_qloo_recommendations(
        genre_urn=genre_urn,
        year_min=2020,
        location_query=USER_LOCATION
    )

    if not recommendations:
        return ["No suitable recommendations found from Qloo."]

    return [
        f"* **{movie['name']}** ([Image URL]({movie['image_url']}))" if movie.get('image_url') else f"* **{movie['name']}**"
        for movie in recommendations
    ]

def summarize_couple_taste():
    """Summarize shared taste using Gemini."""
    data = fetch_couple_watched_movies()
    if "error" in data:
        return data["error"]

    watched_titles = [m['Name'] for m in data["user1"][:3]] + [m['Name'] for m in data["user2"][:3]]
    recommendations = recommend_couple_movies()
    rec_titles = [r.split("**")[1] if "**" in r else r for r in recommendations[:5]]

    return explain_recommendations(watched_titles, rec_titles)
