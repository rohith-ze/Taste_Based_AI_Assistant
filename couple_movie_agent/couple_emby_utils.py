import requests
import json

def get_user_id(server, api_key, username):
    try:
        res = requests.get(f"{server}/Users", params={'api_key': api_key})
        users = res.json()
        for user in users:
            if user['Name'].lower() == username.lower():
                return user['Id']
    except Exception as e:
        print("[❌] USER_ID fetch failed:", e)
    return None

def get_watched_movies(server, api_key, user_id):
    try:
        url = f"{server}/Users/{user_id}/Items"
        params = {
            'IncludeItemTypes': 'Movie',
            'Recursive': 'true',
            'SortBy': 'DatePlayed',
            'Filters': 'IsPlayed',
            'Fields': 'Genres',
            'api_key': api_key
        }
        res = requests.get(url, params=params)
        data = res.json().get("Items", [])
        return [{
            "Name": m.get("Name"),
            "Genres": m.get("Genres", []),
            "Id": m.get("Id"),
            "Year": m.get("ProductionYear")
        } for m in data]
    except Exception as e:
        print("[❌] Error fetching watched movies:", e)
        return []
