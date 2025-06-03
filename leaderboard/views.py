import json
from django.http import JsonResponse
from rest_framework import viewsets
from django.shortcuts import redirect, render
from .models import Player, Score
from .serializers import PlayerSerializer, ScoreSerializer
import datetime
from django.views.decorators.csrf import csrf_exempt

current_time = datetime.datetime.now()

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all().order_by('-score')
    serializer_class = ScoreSerializer

def leaderboard_view(request):
    top_players = Player.objects.order_by('-score')[:10]
    context = {'top_players': top_players}
    return render(request, 'leaderboard/leaderboard.html', context)

def home(request):
    return render(request, 'home.html', {'year': current_time})


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        message = request.POST.get('message')
        # Save or handle data here (optional)
        return redirect('contact')  # redirect to same page or a 'thank you' page

    return render(request, 'contact.html') 

def api_endpoint(request):
    data = list(Player.objects.values('name', 'score').order_by('-score'))
    return JsonResponse(data, safe=False)

def register_player(request):
    return render(request, 'register.html')

@csrf_exempt
def register_player(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            score = data.get('score')

            if not name or score is None:
                return JsonResponse({'error': 'Missing name or score'}, status=400)

            # Find or create player
            player, created = Player.objects.get_or_create(name=name)
            player.score = score
            player.date = datetime.timezone.now()
            player.save()

            if created:
                return JsonResponse({'message': f'New player "{name}" registered.', 'status': 'created'}, status=201)
            else:
                return JsonResponse({'message': f'Score updated for "{name}".', 'status': 'updated'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Optional: show HTML form if visited via browser (not needed for API users)
    return render(request, 'register.html')



@csrf_exempt
def register_or_update_player(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            score = data.get("score")

            if not name or score is None:
                return JsonResponse({"error": "Name and score are required."}, status=400)

            # Check if player already exists
            player, created = Player.objects.get_or_create(name=name)

            if not created:
                # Update score if already exists
                player.score = score
                player.save()
                return JsonResponse({"message": f"Score updated for {name}", "score": score})

            else:
                # New player registered
                player.score = score
                player.save()
                return JsonResponse({"message": f"New player {name} registered", "score": score})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == "GET":
        return JsonResponse({
            "note": "Use POST method to register or update score",
            "example": {
                "name": "Rahul Raval",
                "score": 100
            }
        })

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
def serialize_players():
    return list(Player.objects.values("name", "score"))

@csrf_exempt
def api_home(request):
    if request.method == "GET":
        # You can return a list of players
        players = list(Player.objects.values("name", "score"))
        return JsonResponse(players, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            score = data.get("score")

            if not name or score is None:
                return JsonResponse({"error": "Missing 'name' or 'score'"}, status=400)

            try:
                player = Player.objects.get(name=name)
                player.score = score
                player.save()
                return JsonResponse({"message": f"Score updated for {name}."})
            except Player.DoesNotExist:
                return JsonResponse({"error": f"Player '{name}' not found. Please register first."}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    else:
        return JsonResponse({"error": "Method not allowed. Use GET or POST."}, status=405)