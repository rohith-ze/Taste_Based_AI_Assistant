import requests
import json
from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

QLOO_API_KEY = os.getenv('QLOO_API_KEY')
BASE_URL ="https://hackathon.api.qloo.com/v2/insights/"
BASE_URL_1 ="https://hackathon.api.qloo.com/search"

from typing import TypedDict, List

class Track(TypedDict):
    track_name: str
    artists: List[str]

class TrackRequest(TypedDict):
    tracks: List[Track]

@tool
def get_qloo_recommendations(tracks: TrackRequest):
    """
    Fetches music recommendations from Qloo based on artist names from a list of Spotify tracks.
    Expects a TrackRequest object containing a list of tracks.
    """

    headers = {"x-api-key": QLOO_API_KEY}
    try:
        track_list = tracks.get('tracks', [])
        artist_tags = []
        for track in track_list:
            artist_tags.extend(track.get("artists", []))

        # Clean, deduplicate, and URL-safe format
        unique_tags = list(set(artist_tags))
        tag_string = ",".join(unique_tags)

        params = {
            "filter.type": "urn:tag",
            "filter.tag.types": "urn:tag:keyword:music",
            "filter.tags": tag_string,
        }

        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code != 200:
            return response.json()

        return response.json()

    except Exception as e:
        return {"error": str(e)}


@tool
def get_artist_entity_id(names:list):
    """Gets the entity ID for all the artist"""
    headers={'x-api-key':QLOO_API_KEY}
    artist_id =[]
    for name in names:
        query={'query':name,
               'types':"urn:entity:artist",
               'filter.popularity':"0.9",
               'operator.filter.tags':'union',
               'page':"1",
               'sort_by':'popularity',
               'filter.tags':''}
        response= requests.get(
            url=BASE_URL_1,
            headers=headers,
            params=query
        )
        data = response.json()
        if data and 'results' in data:
            for result in data['results']:
                artist_info = {
                    'name': result.get('name'),
                    'entity_id': result.get('entity_id'),
                    'image_url': result.get('properties', {}).get('image', {}).get('url'),
                    'genres': [],
                    'audiences': [],
                    'styles': [],
                    'characteristics': [],
                    'influences': [],
                    'influenced_by_artists': [],
                    'instruments': [],
                    'themes': [],
                    'subgenres': []
                }
                if 'tags' in result:
                    for tag in result['tags']:
                        if tag.get('type') == 'urn:tag:genre':
                            artist_info['genres'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:audience:qloo':
                            artist_info['audiences'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:style:qloo':
                            artist_info['styles'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:characteristic:qloo':
                            artist_info['characteristics'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:influence:qloo':
                            artist_info['influences'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:influenced_by:qloo':
                            artist_info['influenced_by_artists'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:instrument:qloo':
                            artist_info['instruments'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:theme:qloo':
                            artist_info['themes'].append(tag.get('name'))
                        elif tag.get('type') == 'urn:tag:subgenre:qloo':
                            artist_info['subgenres'].append(tag.get('name'))
                artist_id.append(artist_info)
    with open("artist_entity_id_.json",'w') as f:
        json.dump(artist_id,f)

if __name__ == "__main__":
    # Test case for get_artist_entity_id
    artist_names = ["Taylor Swift", "Ed Sheeran"]
    result = get_artist_entity_id({"names": artist_names})
    print(result)