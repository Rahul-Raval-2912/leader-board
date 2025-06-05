import json
import datetime

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Player, Score
from .serializers import PlayerSerializer, ScoreSerializer

current_time = datetime.datetime.now()

# ViewSets for Django Rest Framework API
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all().order_by('-points')
    serializer_class = ScoreSerializer

# HTML Views
def leaderboard_view(request):
    top_scores = Score.objects.select_related('player').order_by('-points')[:10]
    return render(request, 'leaderboard/leaderboard.html', {'top_scores': top_scores})


def home(request):
    return render(request, 'home.html', {'year': current_time})

def contact_view(request):
    if request.method == "POST":
        return redirect('contact')
    return render(request, 'contact.html')

def register_player(request):
    return render(request, 'register.html')

# API Views
@csrf_exempt
def api_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")

            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)

            if Player.objects.filter(name=name).exists():
                return JsonResponse({"error": "Player already registered"}, status=409)

            Player.objects.create(name=name, score=0)
            return JsonResponse({"message": f"{name} successfully registered."}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

@csrf_exempt
def add_score(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('player_email')
            new_score = int(request.POST.get('score_value'))

            if not email or new_score is None:
                return render(request, 'home.html', {'message': 'Missing email or score.'})

            player = Player.objects.filter(email=email).first()
            if not player:
                return render(request, 'home.html', {'message': 'Player not found.'})

            existing_scores = Score.objects.filter(player=player)
            if existing_scores.exists():
                best_score = max(score.score for score in existing_scores)
                if new_score > best_score:
                    Score.objects.create(player=player, score=new_score, timestamp=datetime.datetime.now())
                    message = f"✅ Score updated! Previous best was {best_score}."
                else:
                    message = f"⚠️ New score ({new_score}) is not better than your best score ({best_score})."
            else:
                Score.objects.create(player=player, score=new_score, timestamp=datetime.datetime.now())
                message = "✅ Score added for the first time!"

            return render(request, 'home.html', {'message': message})

        except Exception as e:
            return render(request, 'home.html', {'message': str(e)})

    return render(request, 'home.html', {'message': 'Only POST method allowed'})

@csrf_exempt
def api_home(request):
    if request.method == "GET":
        players = list(Player.objects.values("name", "score"))
        return JsonResponse(players, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            score = data.get("score")

            if not name or score is None:
                return JsonResponse({"error": "Missing 'name' or 'score'"}, status=400)

            player, created = Player.objects.get_or_create(name=name)
            player.score = score
            player.save()

            msg = "registered" if created else "updated"
            return JsonResponse({"message": f"Player '{name}' score {msg}."}, status=201 if created else 200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Method not allowed. Use GET or POST."}, status=405)


@csrf_exempt
def register_or_update_player(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')

            if not email or not name:
                return JsonResponse({'success': False, 'error': 'Name and email required'}, status=400)

            player, created = Player.objects.update_or_create(
                email=email,
                defaults={'name': name}
            )

            return JsonResponse({
                'success': True,
                'message': 'Player registered' if created else 'Player updated'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@csrf_exempt
def main_api_view(request):
    return redirect('home')
