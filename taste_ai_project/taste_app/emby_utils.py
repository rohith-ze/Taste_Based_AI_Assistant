# emby_utils.py
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Fetch Emby user ID by name
def get_user_id(emby_server, api_key, username):
    url = f"{emby_server}/Users"
    try:
        res = requests.get(url, params={'api_key': api_key})
        data = json.loads(res.content.decode("utf-8-sig"))

        if not isinstance(data, list):
            print("[ERROR] Emby response is not a list.")
            print("[DEBUG] Response:", data)
            return None

        for user in data:
            name = user.get("Name")
            if name and name.lower() == username.lower():
                print(f"[✅] Found user '{name}' with ID: {user.get('Id')}")
                return user.get("Id")

        print(f"[❌] USER_NAME '{username}' not found in Emby Users list.")
        return None

    except Exception as e:
        print("[❌] Exception while fetching USER_ID:", e)
        print("[DEBUG] URL tried:", url)
        return None

# Fetch watched movies from Emby
def get_watched_movies(emby_server, api_key, user_id):
    url = f"{emby_server}/Users/{user_id}/Items"
    params = {
        'IncludeItemTypes': 'Movie',
        'Recursive': 'true',
        'SortBy': 'DatePlayed',
        'Filters': 'IsPlayed',
        'Fields': 'Genres,GenreItems,Tags',
        'api_key': api_key
    }

    try:
        res = requests.get(url, params=params)
        if "html" in res.headers.get("Content-Type", ""):
            print("[ERROR] Emby returned HTML instead of JSON. Check server URL or API key.")
            print("[DEBUG] Response:", res.text[:200])
            return []

        if res.status_code != 200:
            print("[ERROR] Emby API failed:", res.status_code)
            print("[DEBUG] URL:", res.url)
            print("[DEBUG] Response:", res.text[:200])
            return []

        data = json.loads(res.content.decode('utf-8-sig'))
        movies = data.get('Items', [])
    except json.JSONDecodeError as e:
        print("[ERROR] Failed to parse JSON:", e)
        print("[DEBUG] Raw response:", res.content[:200])
        return []

    return [{
        'Name': m.get('Name'),
        'Id': m.get('Id'),
        'Year': m.get('ProductionYear'),
        'Genres': (
            m.get('Genres') or
            [g['Name'] for g in m.get('GenreItems', []) if 'Name' in g] or
            m.get('Tags', [])
        ),
        'People': m.get('People', [])
    } for m in movies]


# Use Qloo Insights API for movie recommendations
# emby_utils.py (updated function only)

# emby_utils.py (only updated function shown)
def get_qloo_recommendations(genre_urn=None, year_min=2022, location_query=None):
    url = "https://hackathon.api.qloo.com/v2/insights"
    headers = {
        "x-api-key": os.getenv("QLOO_API_KEY")
    }

    params = {
        "filter.type": "urn:entity:movie",
        "filter.release_year.min": year_min
    }

    if genre_urn:
        params["filter.tags"] = genre_urn
    if location_query:
        params["signal.location.query"] = location_query

    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            results = res.json().get("results", {})
            entities = results.get("entities", [])
            return [e.get("name") for e in entities if e.get("name")]
        else:
            print("[❌] Qloo Insights API failed:", res.status_code)
            print(res.text)
            return []
    except Exception as e:
        print("[❌] Exception in Qloo insights:", e)
        return []

def get_emby_play_url(movie_id: str) -> str:
    """
    Construct a playable Emby URL for a given movie item ID.
    Assumes EMBY_SERVER and API_KEY are set in .env
    """
    import os
    from urllib.parse import urlencode

    emby_server = os.getenv("EMBY_SERVER")
    api_key = os.getenv("EMBY_API_KEY")

    if not emby_server or not api_key:
        return ""

    params = urlencode({'api_key': api_key})
    return f"{emby_server}/web/index.html#!/item?id={movie_id}&{params}"

def get_trending_movies(emby_server, api_key, user_id):
    """
    Fetches recently added movies from Emby to serve as "trending" content.
    """
    url = f"{emby_server}/Users/{user_id}/Items/Latest"
    params = {
        'IncludeItemTypes': 'Movie',
        'api_key': api_key,
        'Fields': 'Genres,CommunityRating',
        'Limit': 20
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()  # Raise an exception for bad status codes
        data = res.json()
        return [{
            'name': item.get('Name'),
            'Id': item.get('Id'),
            'image_url': f"{emby_server}/Items/{item.get('Id')}/Images/Primary?api_key={api_key}",
            'genres': item.get('Genres', []),
            'rating': round(item.get('CommunityRating', 0), 1)
        } for item in data]
    except requests.exceptions.RequestException as e:
        print(f"[❌] Exception while fetching trending movies: {e}")
        return []

def get_popular_movies(emby_server, api_key):
    """
    Fetches popular movies from Emby based on play count.
    """
    url = f"{emby_server}/Items"
    params = {
        'IncludeItemTypes': 'Movie',
        'Recursive': 'true',
        'SortBy': 'PlayCount',
        'SortOrder': 'Descending',
        'Limit': 20,
        'Fields': 'Genres,CommunityRating',
        'api_key': api_key
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json().get('Items', [])
        return [{
            'name': item.get('Name'),
            'Id': item.get('Id'),
            'image_url': f"{emby_server}/Items/{item.get('Id')}/Images/Primary?api_key={api_key}",
            'genres': item.get('Genres', []),
            'rating': round(item.get('CommunityRating', 0), 1)
        } for item in data]
    except requests.exceptions.RequestException as e:
        print(f"[❌] Exception while fetching popular movies: {e}")
        return []

def get_continue_watching(emby_server, api_key, user_id):
    """Fetches items that are in progress for the user."""
    url = f"{emby_server}/Users/{user_id}/Items/Resume"
    params = {
        'Limit': 10,
        'Fields': 'Genres,CommunityRating',
        'api_key': api_key
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json().get('Items', [])
        return [{
            'name': item.get('Name'),
            'Id': item.get('Id'),
            'image_url': f"{emby_server}/Items/{item.get('Id')}/Images/Primary?api_key={api_key}",
            'genres': item.get('Genres', []),
            'rating': round(item.get('CommunityRating', 0), 1)
        } for item in data]
    except requests.exceptions.RequestException as e:
        print(f"[❌] Exception while fetching continue watching items: {e}")
        return []

def get_emby_stream_url(movie_id: str) -> str:
    """
    Constructs a direct, embeddable stream URL for a given movie ID.
    """
    emby_server = os.getenv("EMBY_SERVER")
    api_key = os.getenv("EMBY_API_KEY")
    if not emby_server or not api_key:
        return ""
    return f"{emby_server}/Videos/{movie_id}/stream?api_key={api_key}&static=true"

def get_continue_watching(emby_server, api_key, user_id):
    """Fetches items that are in progress for the user."""
    url = f"{emby_server}/Users/{user_id}/Items/Resume"
    params = {
        'Limit': 10,
        'Fields': 'Genres',
        'api_key': api_key
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json().get('Items', [])
        return [{
            'name': item.get('Name'),
            'Id': item.get('Id'),
            'image_url': f"{emby_server}/Items/{item.get('Id')}/Images/Primary?api_key={api_key}",
            'genres': item.get('Genres', [])
        } for item in data]
    except requests.exceptions.RequestException as e:
        print(f"[❌] Exception while fetching continue watching items: {e}")
        return []

def get_latest_music(emby_server, api_key):
    """Fetches the latest music albums."""
    url = f"{emby_server}/Items/Latest"
    params = {
        'IncludeItemTypes': 'MusicAlbum',
        'Limit': 10,
        'api_key': api_key
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        return [{
            'name': item.get('Name'),
            'Id': item.get('Id'),
            'artist': item.get('AlbumArtist'),
            'image_url': f"{emby_server}/Items/{item.get('Id')}/Images/Primary?api_key={api_key}"
        } for item in data]
    except requests.exceptions.RequestException as e:
        print(f"[❌] Exception while fetching latest music: {e}")
        return []
