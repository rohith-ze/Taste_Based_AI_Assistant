# taste_api.py
import requests

def get_taste_recommendations(movie_titles, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "movies": movie_titles,
        "limit": 10
    }

    try:
        res = requests.post("https://api.qloo.com/movies/recommend", json=data, headers=headers)
        if res.status_code == 200:
            return res.json().get("recommendations", [])
        else:
            print("[ERROR] Qloo API failed:", res.status_code)
            print("[DEBUG] Response:", res.text[:200])
            return []
    except Exception as e:
        print("[ERROR] Qloo API error:", str(e))
        return []
