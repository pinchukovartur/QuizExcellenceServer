from django.db import models


class TutorialStep(models.Model):
    """Пройденный шаг обучения.

    Нужна, чтобы видеть, где новый игрок отваливается: первый шаг —
    сам запуск игры, дальше шаги обучения по порядку. Разница между
    соседними шагами и есть воронка первого сеанса.

    Одна строка на игрока и шаг: шаг проходится один раз, а повторная
    отправка того же шага (клиент повторяет неудачные) не должна
    плодить дубли — за это отвечает unique_together.
    """

    game_state_id = models.CharField(max_length=60, db_index=True)

    # Строковый id шага, а не число: он приходит с клиента как есть
    # (см. TutorialStepId в lib/state/tutorial_state.dart) и переживает
    # переименование значений в коде.
    step = models.CharField(max_length=40, db_index=True)

    # Когда шаг пройден по времени сервера. Клиентскому времени
    # доверять нельзя: часы на устройстве бывают сбиты.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game_state_id', 'step')
        # Имя задаём явно — см. feedback/models.py
        indexes = [models.Index(fields=['step', 'created_at'],
                                name='tutorial_tu_step_idx')]

    def __str__(self):
        return '%s %s' % (self.game_state_id, self.step)
