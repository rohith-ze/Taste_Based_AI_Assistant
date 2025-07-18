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

@tool
def qloo_taste_analysis(tracks_json: str):
    """
    Analyzes music taste using artist names from a list of Spotify tracks.
    Expects a JSON string that is either:
    - a list of tracks (recommended)
    - OR a dict with a "tracks" key
    """

    headers = {"x-api-key": QLOO_API_KEY}
    try:
        data = json.loads(tracks_json)

        # Accept both list of tracks or {"tracks": [...]}
        if isinstance(data, dict) and "tracks" in data:
            track_list = data["tracks"]
        elif isinstance(data, list):
            track_list = data
        else:
            return {"error": "Invalid track format"}

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
    

from typing import TypedDict, List

class Track(TypedDict):
    track_name: str
    artists: List[str]

class TrackRequest(TypedDict):
    tracks: List[Track]


@tool
def generate_heatmap_from_tracks(tracks: TrackRequest, location: str = "NYC"):


    """
    Analyzes tracks and generates a brand heatmap using inferred genres.
    Handles various LLM response formats and validates genres.
    """
    # Allowed Qloo music genres
    ALLOWED_GENRES = {
        "cinematic", "ambient", "pop", "rock", 
        "folk", "edm", "hip_hop", "blues"
    }
    
    # Step 1: LLM genre analysis
    analysis_prompt = """Analyze these music tracks and suggest exactly 2-3 music genres 
    from this list: cinematic, ambient, pop, rock, folk, edm, hip_hop, blues
    
    Example response: "pop, rock"
    
    Tracks:
    {tracks}
    
    Respond ONLY with comma-separated genres:"""

    
    tracks_data = tracks 
  ##with open("raw.json") as f:
       ## json.dump(tracks_json,f)
   ## print(f"Raw_json",tracks_json)"""
    track_list = "\n".join([
        f"- {t.get('track_name', '?')} by {', '.join(t.get('artists', []))}"
        for t in tracks_data.get('tracks', [])
    ])
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
    llm_response = llm.invoke(analysis_prompt.format(tracks=track_list)).content
    
    # Step 2: Robust genre parsing
    def parse_genres(response):
        # Clean and split the response
        cleaned = response.lower().replace(" ", "").strip(" .,;")
        potential_genres = [g.strip() for g in cleaned.split(",") if g.strip()]
        
        # Validate against allowed genres
        valid_genres = []
        for genre in potential_genres:
            # Handle slight variations
            if genre in ALLOWED_GENRES:
                valid_genres.append(genre)
            elif genre == "hiphop":
                valid_genres.append("hip_hop")
            elif genre == "electronic":
                valid_genres.append("edm")
        
        # Ensure we have 1-3 valid genres
        if not valid_genres:
            return ["cinematic", "ambient"]  # Default fallback
        return valid_genres[:3]
    
    genres = parse_genres(llm_response)
    
    # Step 3: Generate heatmap
    headers = {"x-api-key": QLOO_API_KEY}
    tags = [f"urn:tag:genre:music:{g}" for g in genres]
    
    params = {
        "filter.type": "urn:heatmap",
        "signal.interests.tags": ",".join(tags),
        "filter.entity.types": "urn:entity:brand",
        "filter.location.query": location
    }
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    data = response.json()
    with open("heatmaps.json",'w') as f:
        json.dump(data,f)
    return {
        "llm_response": llm_response,
        "parsed_genres": genres,
        "qloo_tags": tags,
        "heatmap_data": response.json()
    }


"""if __name__ == "__main__":
    qloo_call("")"""