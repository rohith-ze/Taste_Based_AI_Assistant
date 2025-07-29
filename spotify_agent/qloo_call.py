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
from pydantic import BaseModel, Field

class Track(TypedDict):
    track_name: str
    artists: List[str]

class TrackRequest(TypedDict):
    tracks: List[Track]

class ArtistNames(BaseModel):
    names: List[str] = Field(description="List of artist names")

class EntityIds(BaseModel):
    entity_ids: List[str] = Field(description="List of entity IDs")

@tool
def get_entity_id(tracks: TrackRequest):
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


@tool(args_schema=ArtistNames)
def get_artist_entity_id(names:list):
    """Gets the entity ID for the specified artists."""
    headers={'x-api-key':QLOO_API_KEY}
    artist_id =[]
    for name in names:
        query={'query':name,
               'types':"urn:entity:artist",
               'sort_by':'match'}
        response= requests.get(
            url=BASE_URL_1,
            headers=headers,
            params=query
        )
        data = response.json()
        if data and 'results' in data:
            for result in data['results']:
               
                if result.get('name', '').lower() == name.lower():
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
                    break 
    with open("artist_entity_id_.json",'w') as f:
        json.dump(artist_id,f)
    return artist_id

@tool(args_schema=EntityIds)
def get_insights(entity_ids: list):
    """Gets insights from Qloo API using a list of entity IDs."""
    headers = {"x-api-key": QLOO_API_KEY}
    
    params = {
        "filter.type": "urn:entity:artist",
        "signal.interests.entities": ",".join(entity_ids),
    }
    
    try:
        response = requests.get("https://hackathon.api.qloo.com/v2/insights", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        with open("insights.json",'w')as f:
            json.dump(data,f) 
        
        # Extract relevant information from the insights data
        insights_summary = {
            "recommended_artists": [],
            "recommended_genres": [],
            "recommended_themes": []
        }

        recommended_artists_str = ""
        if "results" in data and "entities" in data["results"]:
            for entity in data["results"]["entities"]:
                artist_name = entity.get("name")
                image_url = entity.get("properties", {}).get("image", {}).get("url")
                if artist_name and image_url:
                    recommended_artists_str += f"* **{artist_name}** ([Image URL]({image_url}))\n"

        recommended_genres_str = ""
        if "results" in data and "tags" in data["results"]:
            genres = [tag.get("name") for tag in data["results"]["tags"] if tag.get("type") == "urn:tag:genre"]
            if genres:
                recommended_genres_str = "* " + "\n* ".join(genres)

        recommended_themes_str = ""
        if "results" in data and "tags" in data["results"]:
            themes = [tag.get("name") for tag in data["results"]["tags"] if tag.get("type") == "urn:tag:theme"]
            if themes:
                recommended_themes_str = "* " + "\n* ".join(themes)

        # Format the final output string
        output_str = ""
        if recommended_artists_str:
            output_str += f"**Recommended Artists:**\n{recommended_artists_str}\n"
        
        if recommended_genres_str:
            output_str += f"**Recommended Genres:**\n{recommended_genres_str}\n"
        else:
            output_str += "**Recommended Genres:**\nNo genres were recommended\n"
            
        if recommended_themes_str:
            output_str += f"**Recommended Themes:**\n{recommended_themes_str}"

        return output_str if output_str else "No recommendations found."
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Test case for get_artist_entity_id
    artist_names = ["Taylor Swift", "Ed Sheeran"]
    artist_info_list = get_artist_entity_id({"names": artist_names})
    print("---- Artist Info ----")
    print(json.dumps(artist_info_list, indent=2))

    if artist_info_list:
        entity_ids = [artist.get('entity_id') for artist in artist_info_list if artist.get('entity_id')]
        
        if entity_ids:
            print("\n---- Entity IDs ----")
            print(entity_ids)
            
            print("\n---- Insights ----")
            insights_result = get_insights({"entity_ids": entity_ids})
            print(json.dumps(insights_result, indent=2))
        else:
            print("\nCould not find entity IDs to fetch insights.")
