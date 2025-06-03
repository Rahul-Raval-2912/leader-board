from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(default="test@example.com")  

    def __str__(self):
        return self.name

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player.name} - {self.points}"

