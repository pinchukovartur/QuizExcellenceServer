from django.db import models
from django.utils import timezone


class Prestige(models.Model):
    game_state_id = models.CharField(primary_key=True, max_length=60)
    name = models.CharField(max_length=200)
    prestige = models.IntegerField()
    # Номер иконки игрока в наборе приложения, -1 — иконка не выбрана.
    # Старые записи остаются с -1, клиент рисует им заглушку.
    avatar = models.IntegerField(default=-1)
    # Ссылка на аватарку из аккаунта игровых сервисов. Пусто — игрок
    # не входил или картинки нет, клиент рисует иконку из набора.
    avatar_url = models.CharField(max_length=500, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.game_state_id
