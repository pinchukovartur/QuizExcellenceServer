from django.db import models
from django.utils import timezone


class Prestige(models.Model):
    game_state_id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=200)
    prestige = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.game_state_id
