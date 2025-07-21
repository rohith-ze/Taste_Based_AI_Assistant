from django.contrib import admin
from django.urls import path
from taste_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('movies/', views.movies_view, name='movies'),
    path('music/', views.music_view, name='music'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)