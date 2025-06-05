from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Removed default as previously recommended
    score = models.IntegerField(default=0)  # Keep this for api_home compatibility

    def __str__(self):
        return self.name

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')  # Use 'scores' to avoid conflict
    points = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.name} - {self.points}"