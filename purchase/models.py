from django.db import models


class Purchase(models.Model):
    """Подтверждённая покупка.

    Токен уникален: Google выдаёт его один раз на платёж, и повторный
    запрос с тем же токеном означает либо потерянный ответ, либо
    попытку получить товар дважды. И то и другое решается одинаково —
    отдаём прежний результат, второй раз не начисляем.
    """

    token = models.CharField(primary_key=True, max_length=512)
    game_state_id = models.CharField(max_length=60)
    product_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["game_state_id"])]

    def __str__(self):
        return f"{self.product_id} / {self.game_state_id}"
