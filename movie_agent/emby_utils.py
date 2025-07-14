# emby_utils.py
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

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

def get_watched_movies(emby_server, api_key, user_id):
    url = f"{emby_server}/Users/{user_id}/Items"
    params = {
        'IncludeItemTypes': 'Movie',
        'Recursive': 'true',
        'SortBy': 'DatePlayed',
        'Filters': 'IsPlayed',
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
        'Genres': m.get('Genres', []),
        'People': m.get('People', [])
    } for m in movies]

# Qloo integration
def get_qloo_recommendations(movie_titles):
    QLOO_API_URL = "https://hackathon.api.qloo.com/recommendations" 

    headers = {
        "x-api-key": os.getenv("QLOO_API_KEY"),
        "Content-Type": "application/json"
    }

    params = {
        "type": "movie",
        "items": ",".join(movie_titles),  # Qloo expects items as comma-separated string
        "limit": 5
    }

    response = requests.get(QLOO_API_URL, headers=headers, params=params) 

    if response.status_code == 200:
        return response.json().get("recommendations", [])
    else:
        print("[ERROR] Qloo API failed:", response.status_code)
        print("[DEBUG] Response:", response.text)
        return []
