import os
import requests

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
        entities = res.json().get("results", {}).get("entities", [])
        return [
            {"name": e.get("name"), "image_url": e.get("properties", {}).get("image", {}).get("url")}
            for e in entities if e.get("name")
        ]
    except Exception as e:
        print("[❌] Qloo API Error:", e)
        return []
