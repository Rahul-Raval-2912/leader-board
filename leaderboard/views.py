import json
from django.http import JsonResponse
from rest_framework import viewsets
from django.shortcuts import redirect, render
from .models import Player, Score
from .serializers import PlayerSerializer, ScoreSerializer
import datetime
from django.views.decorators.csrf import csrf_exempt
from .serializers import ScoreSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status



current_time = datetime.datetime.now()

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all().order_by('-points')
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
def api_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")

            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)

            # check if already exists
            if Player.objects.filter(name=name).exists():
                return JsonResponse({"error": "Player already registered"}, status=409)

            Player.objects.create(name=name, score=0)
            return JsonResponse({"message": f"{name} successfully registered."}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    else:
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)


@csrf_exempt
def register_or_update_player(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            score = data.get("score")

            if not name or score is None:
                return JsonResponse({"error": "Both 'name' and 'score' are required"}, status=400)

            player, created = Player.objects.get_or_create(name=name)
            player.score = score
            player.save()

            return JsonResponse({
                "message": "Player registered" if created else "Player score updated",
                "name": player.name,
                "score": player.score
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)
    
    
def serialize_players():
    return list(Player.objects.values("name", "score"))

@csrf_exempt
def api_home(request):
    if request.method == "GET":
        # Return all players
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

            if created:
                return JsonResponse({"message": f"Player '{name}' registered with score {score}."}, status=201)
            else:
                return JsonResponse({"message": f"Player '{name}' score updated to {score}."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    else:
        return JsonResponse({"error": "Method not allowed. Use GET or POST."}, status=405)
    
@api_view(['POST'])
def add_score(request):
    serializer = ScoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)