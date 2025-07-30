import os
from dotenv import load_dotenv
import requests
import json
from langchain_core.tools import tool
import pydantic_core
from auth import get_access_token


TOKEN = get_access_token()

load_dotenv()


@tool
def get_playlist():
    """Fetches the user's playlists from Spotify and parses them."""
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'items' not in data:
        return []

    parsed_playlists = []
    for item in data['items']:
        playlist_name = item.get('name')
        playlist_id = item.get('id')
        playlist_uri = item.get('uri')

        parsed_playlists.append({
            "playlist_name": playlist_name,
            "playlist_id": playlist_id,
        })
    return json.dumps(parsed_playlists, indent=2)


# In data_gathering.py, modify all tools to return proper JSON:

@tool
def get_last_played():
    """Fetches the user's recently played tracks with detailed information."""
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=10"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'items' not in data:
        return json.dumps({"tracks": []})  # Return empty but valid JSON

    tracks = []
    for item in data['items']:
        track = item.get('track', {})
        if not track:
            continue

        tracks.append({
            "track_name": track.get('name', "Unknown"),
            "artists": [artist['name'] for artist in track.get('artists', [])],
            "album_name": track.get('album', {}).get('name', "Unknown"),
            "release_date": track.get('album', {}).get('release_date', "Unknown")
        })

    return json.dumps({"tracks": tracks}, ensure_ascii=False)  # Proper JSON string

@tool
def get_song_list(playlist_ID:str) :
    """Fetches the songs from a specific playlist with detailed information."""
    url = f"https://api.spotify.com/v1/playlists/{playlist_ID}/tracks"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'items' not in data:
        return []

    parsed_tracks = []
    for item in data['items']:
        track = item.get('track', {})
        if not track:
            continue

        track_name = track.get('name')
        artists = [artist['name'] for artist in track.get('artists', [])]
        album_name = track.get('album', {}).get('name')
        release_date = track.get('album', {}).get('release_date')
        track_uri = track.get('uri')

        parsed_tracks.append({
            "track_name": track_name,
            "artists": artists,
            "album_name": album_name,
            "release_date": release_date,
        })
    return json.dumps(parsed_tracks, indent=2)


@tool
def get_liked_songs():
    """Fetches the user's liked songs from Spotify with detailed information."""
    url = "https://api.spotify.com/v1/me/tracks?limit=50"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'items' not in data:
        return []

    parsed_tracks = []
    for item in data['items']:
        track = item.get('track', {})
        if not track:
            continue

        track_name = track.get('name')
        artists = [artist['name'] for artist in track.get('artists', [])]
        album_name = track.get('album', {}).get('name')
        release_date = track.get('album', {}).get('release_date')
        track_uri = track.get('uri')

        parsed_tracks.append({
            "track_name": track_name,
            "artists": artists,
            "album_name": album_name,
            "release_date": release_date,
        })
    return json.dumps(parsed_tracks, indent=2)


@tool
def get_liked_song_names():
    """Fetches the user's liked songs from Spotify and returns only the song names."""
    url = "https://api.spotify.com/v1/me/tracks?limit=50"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if 'items' not in data:
        return []

    track_names = []
    for item in data['items']:
        track = item.get('track', {})
        if not track:
            continue
        track_names.append(track.get('name'))
    return json.dumps(track_names, indent=2)

if __name__ == "__main__":
    print("-----song----list-----")
    print(get_song_list("0qYVoEVgiCjbnWEDZ72WsH"))