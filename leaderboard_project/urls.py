from django.contrib import admin
from django.urls import path, include
from . import views 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('leaderboard.urls')),  # Replace with your actual app name
]