from django.db import models

from prestige.models import Prestige


class States(models.Model):
    game_state_id = models.CharField(primary_key=True, max_length=60)
    device_id = models.CharField(max_length=60, default="")
    name = models.CharField(max_length=200)
    state_data = models.TextField()

    prestige = models.OneToOneField(Prestige, on_delete=models.CASCADE, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
