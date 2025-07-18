import folium
import json
from folium.plugins import HeatMap
from langchain_core.tools import tool

@tool
def generate_map(latitude:int,longitude:int):
    """Generate a Visual Heat map based on the data from Qloo api"""
    with open("heatmaps.json") as f:
        data = json.load(f)
    location=[latitude,longitude]
    heatmaps_entries = data['results']['heatmap']

    heat_data = [
        (
            entry['location']['latitude'],
            entry['location']['longitude'],
            entry['query']['affinity'] * entry['query']['popularity']

        ) for entry in heatmaps_entries
    ]

    m = folium.Map(location=location, zoom_start=7)

    HeatMap(heat_data).add_to(m)

    m.save("heatmap.html")