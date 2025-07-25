# main.py
import os
from dotenv import load_dotenv
from emby_utils import (
    get_user_id,
    get_watched_movies,
    get_qloo_recommendations
)
from gemini_utils import explain_recommendations  # Optional
load_dotenv()

EMBY_API_KEY = os.getenv("EMBY_API_KEY")
EMBY_SERVER = os.getenv("EMBY_SERVER")
USER_NAME = os.getenv("USER_NAME")

def main():
    print("🔑 Fetching Emby User ID...")
    user_id = get_user_id(EMBY_SERVER, EMBY_API_KEY, USER_NAME)
    if not user_id:
        print("❌ Could not get Emby USER_ID.")
        return 

    print("📺 Fetching watched movies from Emby...")
    watched = get_watched_movies(EMBY_SERVER, EMBY_API_KEY, user_id)

    if not watched:
        print("❌ No watched movies found.")
        return

    watched_titles = [movie['Name'] for movie in watched]
    print("\n🎬 Recently Watched Movies:")
    for title in watched_titles[:5]:
        print(" -", title)

    print("\n🔍 Getting Taste-based Recommendations using Qloo Insights...")
    all_genres = [genre for movie in watched for genre in movie.get('Genres', [])]
    if all_genres:
        most_common_genre = max(set(all_genres), key=all_genres.count)
        genre_urn = f"urn:tag:genre:media:{most_common_genre.lower()}"
    else:
        # Default genre if no watched movies have genres
        most_common_genre = 'comedy'
        genre_urn = f"urn:tag:genre:media:{most_common_genre.lower()}"

    if recommended:
        print("\n📽️ Recommended Movies:")
        for r in recommended[:5]:
            print(" -", r)
    else:
        print("❌ No recommendations received from Qloo.")

    print("\n🧠 Generating Taste Summary using Gemini...")
    summary = explain_recommendations(watched_titles)
    print("\n📜 Taste Summary:\n", summary)

if __name__ == "__main__":
    main()
