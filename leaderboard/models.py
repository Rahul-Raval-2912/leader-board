from django.db import models


    
class Player(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField(default=0)