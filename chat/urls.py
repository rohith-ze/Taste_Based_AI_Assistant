from django.urls import path
from . import views

urlpatterns = [
    path('v1/song', views.spotify_agent_view, name='spotify_agent_view'),
    path('v1/movie', views.movie_agent_view, name='movie_agent_view'),
]