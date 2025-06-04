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
    top_players = Player.objects.order_by('-score')[:10]
    return render(request, 'leaderboard/leaderboard.html', {'top_players': top_players})

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
            data = json.loads(request.body)
            player_name = data.get('player_name')
            new_score = int(data.get('score'))

            if not player_name or new_score is None:
                return JsonResponse({'error': 'Missing player_name or score'}, status=400)

            player = Player.objects.filter(name=player_name).first()
            if not player:
                return JsonResponse({'error': 'Player not found'}, status=404)

            score_obj, created = Score.objects.get_or_create(player=player)
            if created or new_score > score_obj.points:
                score_obj.points = new_score
                score_obj.save()
                return JsonResponse({'message': 'Score added/updated successfully'})
            else:
                return JsonResponse({'message': 'Score not updated (lower than existing)'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

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
    message = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_score':
            email = request.POST.get('player_email')
            new_score = int(request.POST.get('score_value'))

            try:
                player = Player.objects.get(email=email)
                existing_scores = Score.objects.filter(player=player)

                if existing_scores.exists():
                    best_score = max(score.score for score in existing_scores)

                    if new_score > best_score:
                        Score.objects.create(player=player, score=new_score, timestamp=timezone.now())
                        message = f"✅ Score updated! Previous best was {best_score}."
                    else:
                        message = f"⚠️ New score ({new_score}) is not better than your best score ({best_score})."
                else:
                    Score.objects.create(player=player, score=new_score, timestamp=timezone.now())
                    message = "✅ Score added for the first time!"

            except Player.DoesNotExist:
                message = "❌ Player with this email not found."

    return render(request, 'home.html', {'message': message})