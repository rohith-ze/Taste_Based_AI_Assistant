from django.shortcuts import render
from django.http import JsonResponse
from .movie_tools import fetch_watched_movies, recommend_movies
from .emby_utils import get_emby_play_url  # You’ll define this
#rom music_agent import get_music_recommendations  # optional
import os

def index(request): return render(request, 'index.html')
def movies(request): return render(request, 'movies.html')
def music(request): return render(request, 'music.html')

def api_watched(request): 
    return JsonResponse(fetch_watched_movies(), safe=False)

def api_recommended(request):
    return JsonResponse([{'name': r, 'id': None} for r in recommend_movies()], safe=False)

def api_play_url(request, item_id):
    url = get_emby_play_url(item_id)  # You need to implement this
    return JsonResponse({'playUrl': url})

def api_music_recommend(request):
    return JsonResponse(get_music_recommendations(), safe=False)

from django.shortcuts import render
from .movie_tools import fetch_watched_movies, recommend_movies

from django.shortcuts import render
from .movie_tools import fetch_movies_for_view, get_recommendations_for_view
import os

def movies(request):
    watched = fetch_movies_for_view()
    recommended = get_recommendations_for_view()

    emby_server = os.getenv("EMBY_SERVER")
    api_key = os.getenv("EMBY_API_KEY")
    for movie in watched:
        if movie.get("Id"):
            movie["image_url"] = f"{emby_server}/Items/{movie['Id']}/Images/Primary?api_key={api_key}"

    return render(request, "movies.html", {
        "watched_movies": watched,
        "recommended_movies": recommended,
    })
