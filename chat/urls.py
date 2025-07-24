from django.urls import path
from . import views

urlpatterns = [
    path('spotify/', views.spotify_agent_view, name='spotify_agent_view'),
    path('movie/', views.movie_agent_view, name='movie_agent_view'),
]