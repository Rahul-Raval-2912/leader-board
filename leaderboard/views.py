import json
import datetime
from django.contrib import messages
from django.contrib.auth.models import User
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
    leaderboard_data = [
        {'rank': index, 'name': score.player.name, 'points': score.points}
        for index, score in enumerate(top_scores, start=1)
    ]
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard_data})

def home(request):
    return render(request, 'home.html', {'year': current_time})

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        message = request.POST.get('message')
        if name and message:
            messages.success(request, 'Message sent successfully!')
        else:
            messages.error(request, 'Please provide both name and message.')
        return redirect('contact')
    return render(request, 'contact.html')

def register_player(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')
        user = User.objects.create_user(username=username, email=email, password=password1)
        Player.objects.create(name=username, email=email)
        messages.success(request, 'Player registered successfully!')
        return redirect('home')
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
            Player.objects.create(name=name, email=f"{name.lower().replace(' ', '')}@example.com")
            messages.success(request, f"{name} successfully registered.")
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
                messages.error(request, 'Missing email or score.')
                return render(request, 'add_score.html')
            player = Player.objects.filter(email=email).first()
            if not player:
                messages.error(request, 'Player not found.')
                return render(request, 'add_score.html')
            existing_scores = Score.objects.filter(player=player)
            if existing_scores.exists():
                best_score = max(score.points for score in existing_scores)
                if new_score > best_score:
                    Score.objects.create(player=player, points=new_score)
                    messages.success(request, f"✅ Score updated! Previous best was {best_score}.")
                else:
                    messages.warning(request, f"⚠️ New score ({new_score}) is not better than your best ({best_score}).")
            else:
                Score.objects.create(player=player, points=new_score)
                messages.success(request, "✅ Score added for the first time!")
            return render(request, 'add_score.html')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'add_score.html')
    return render(request, 'add_score.html')

@csrf_exempt
def api_home(request):
    if request.method == "GET":
        players = list(Player.objects.values("name", "email"))
        return JsonResponse(players, safe=False)
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            score = data.get("score")
            if not name or score is None:
                return JsonResponse({"error": "Missing 'name' or 'score'"}, status=400)
            player, created = Player.objects.get_or_create(
                name=name,
                defaults={'email': f"{name.lower().replace(' ', '')}@example.com"}
            )
            Score.objects.create(player=player, points=score)
            msg = "registered and score added" if created else "score added"
            messages.success(request, f"Player '{name}' {msg}.")
            return JsonResponse({"message": f"Player '{name}' {msg}."}, status=201 if created else 200)
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
            messages.success(request, 'Player registered' if created else 'Player updated')
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

@api_view(['GET'])
def api_leaderboard(request):
    scores = Score.objects.select_related('player').order_by('-points')[:10]
    result = [
        {"player_name": score.player.name, "points": score.points}
        for score in scores
    ]
    return Response(result)