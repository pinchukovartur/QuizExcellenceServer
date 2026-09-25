from django.db import models

from prestige.models import Prestige


class States(models.Model):
    game_state_id = models.CharField(primary_key=True, max_length=60)
    device_id = models.CharField(max_length=60, default="")

    #: Откуда игрок: "google", "huawei", "ios". Сервер общий для всех
    #: магазинов, и без этого поля нельзя ни посчитать аудиторию
    #: AppGallery, ни понять, где случился баг.
    #:
    #: По умолчанию google: до выхода в AppGallery других установок не
    #: было, и записи, сделанные до появления поля, — это Google Play.
    #: Клиент старой версии платформу не шлёт, и она останется такой.
    platform = models.CharField(max_length=20, default="google", blank=True)
    name = models.CharField(max_length=200)
    state_data = models.TextField()

    prestige = models.OneToOneField(Prestige, on_delete=models.CASCADE, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
