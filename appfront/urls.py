"""
URL configuration for appfront project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from appfront import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.gemini_index, name='gemini_index'),
    path('chat/', include('chat.urls')),
    path('movie_agent_chat/', views.movie_agent_chat, name='movie_agent_chat'),
    path('api/movie_agent_chat/', views.movie_agent_api, name='movie_agent_api'),
    path('spotify_agent_chat/', views.spotify_agent_chat, name='spotify_agent_chat'),
    path('api/spotify_agent_chat/', views.spotify_agent_api, name='spotify_agent_api'),
    path('couple_movie_agent_chat/', views.couple_movie_agent_chat, name='couple_movie_agent_chat'),
    path('api/couple_movie_agent_chat/', views.couple_movie_agent_api, name='couple_movie_agent_api'),
]
