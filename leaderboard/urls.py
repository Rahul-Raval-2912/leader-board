from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, ScoreViewSet, contact_view, leaderboard_view
from . import views

router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'scores', ScoreViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_player, name='register'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('contact/', views.contact_view, name='contact'),
    path("api/", views.api_home, name="api"),
    path('api/register/', views.register_or_update_player, name='api-register'),
    path('add-score/', views.add_score, name='add_score'),
]
