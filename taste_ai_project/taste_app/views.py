import random
from django.shortcuts import render
from .movie_tools import fetch_movies_for_view
from .emby_utils import get_trending_movies, get_popular_movies, get_user_id
import os

def get_base_context():
    """Gets base context data for templates."""
    emby_server = os.getenv("EMBY_SERVER")
    api_key = os.getenv("EMBY_API_KEY")
    username = os.getenv("EMBY_USER")
    user_id = get_user_id(emby_server, api_key, username)
    return emby_server, api_key, user_id

def enrich_movie_data(movies, emby_server, api_key):
    """Adds image URLs to movie data."""
    for movie in movies:
        if movie.get("Id"):
            movie["image_url"] = f"{emby_server}/Items/{movie['Id']}/Images/Primary?api_key={api_key}"
    return movies

def index(request):
    """Home page view."""
    emby_server, api_key, user_id = get_base_context()
    trending = get_trending_movies(emby_server, api_key, user_id)
    featured_movie = random.choice(trending) if trending else None
    
    context = {
        "featured_movie": featured_movie,
        "trending_movies": trending[:10],
        "recommended_movies": enrich_movie_data(fetch_movies_for_view()[:10], emby_server, api_key),
    }
    return render(request, "index.html", context)

def movies_view(request):
    """Movies page view."""
    emby_server, api_key, user_id = get_base_context()
    context = {
        "trending_movies": get_trending_movies(emby_server, api_key, user_id),
        "popular_movies": get_popular_movies(emby_server, api_key),
        "recommended_movies": enrich_movie_data(fetch_movies_for_view(), emby_server, api_key),
    }
    return render(request, "movies.html", context)

def music_view(request):
    """Music page view."""
    music_data = [
        {"name": f"Album {i}", "artist": f"Artist {chr(64+i)}", "image_url": "https://via.placeholder.com/300x450"}
        for i in range(1, 16)
    ]
    context = {"music": music_data}
    return render(request, "music.html", context)

from movie_tools import fetch_trending_movies, fetch_recent_movies

def trending_movies(request):
    movies = fetch_trending_movies({})
    return render(request, 'trending.html', {'movies': movies})

def recent_movies(request):
    movies = fetch_recent_movies({})
    return render(request, 'recent.html', {'movies': movies})
