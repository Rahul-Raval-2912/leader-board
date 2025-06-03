from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    points = models.IntegerField()