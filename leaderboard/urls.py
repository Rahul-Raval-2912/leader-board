from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, ScoreViewSet, contact_view, leaderboard_view, home, register_player, main_api_view, register_or_update_player, add_score, api_home, api_leaderboard

router = DefaultRouter()
router.register(r'api/players', PlayerViewSet)
router.register(r'api/scores', ScoreViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_player, name='register'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('contact/', contact_view, name='contact'),
    path('add/', add_score, name='add_score'),
    path('api/', main_api_view, name='api'),
    path('api/register/', register_or_update_player, name='api-register'),
    path('api/leaderboard/', api_leaderboard, name='api_leaderboard'),
    path('api/players/', api_home, name='api_home'),
    path('', include(router.urls)),  # API routes
]