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
        'api_key': api_key,
        
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()  # Raise an exception for bad status codes
        data = res.json()
        with open("get_watched_movies.json",'w')as f:
            json.dump(data,f)
        if "html" in res.headers.get("Content-Type", ""):
            print("[ERROR] Emby returned HTML instead of JSON. Check server URL or API key.")
            print("[DEBUG] Response:", res.text[:200])
            return []

        movies = data.get('Items', [])
        if not movies:
            print("[INFO] No watched movies found in Emby.")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Emby API request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        print(f"[DEBUG] Raw response: {res.content[:200]}")
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
            
            # Extract name and image URL
            movies_with_images = []
            for e in entities:
                name = e.get("name")
                image_url = e.get("properties", {}).get("image", {}).get("url")
                if name:
                    movies_with_images.append({"name": name, "image_url": image_url})
            
            return movies_with_images
        else:
            print("[❌] Qloo Insights API failed:", res.status_code)
            print(res.text)
            return []
    except Exception as e:
        print("[❌] Exception in Qloo insights:", e)
        return []


import datetime

# Fetch trending movies from Emby
def get_trending_movies(emby_server, api_key):
    url = f"{emby_server}/Items/Trending"
    params = {
        'IncludeItemTypes': 'Movie',
        'Limit': 20,
        'api_key': api_key
    }

    try:
        res = requests.get(url, params=params)
        data = res.json().get('Items', [])
        return [{
            'Name': m.get('Name'),
            'Id': m.get('Id'),
            'Year': m.get('ProductionYear'),
            'Genres': m.get('Genres', []),
        } for m in data]
    except Exception as e:
        print("[❌] Error fetching trending movies:", e)
        return []

# Fetch recently released movies (within last X months)
def get_recent_movies(emby_server, api_key, months=3):
    today = datetime.date.today()
    from_date = today - datetime.timedelta(days=30 * months)
    from_str = from_date.isoformat()

    url = f"{emby_server}/Items"
    params = {
        'IncludeItemTypes': 'Movie',
        'SortBy': 'DateCreated',
        'SortOrder': 'Descending',
        'Fields': 'Genres',
        'Limit': 20,
        'api_key': api_key,
        'StartIndex': 0,
        'MinPremiereDate': from_str
    }

    try:
        res = requests.get(url, params=params)
        data = res.json().get('Items', [])
        return [{
            'Name': m.get('Name'),
            'Id': m.get('Id'),
            'Year': m.get('ProductionYear'),
            'Genres': m.get('Genres', [])
        } for m in data]
    except Exception as e:
        print("[❌] Error fetching recent movies:", e)
        return []

