from django.db import models


class TutorialStep(models.Model):
    """Счётчик игроков, дошедших до шага обучения.

    Одна строка на шаг, а не на пару «игрок и шаг»: отчёт показывает
    только число дошедших, а хранение каждого игрока раздувало базу —
    девять строк на человека и рост без предела.

    Двойного учёта не будет: клиент помнит отправленные шаги и второй
    раз их не шлёт (см. ServerTutorialController). Совсем точным
    счётчик от этого не становится — переустановка игры посчитает
    игрока заново, — но воронку это не искажает: так ведут себя все
    шаги одинаково.
    """

    #: Строковый id шага, а не число: он приходит с клиента как есть
    #: (см. TutorialStepId в lib/state/tutorial_state.dart) и переживает
    #: переименование значений в коде.
    step = models.CharField(primary_key=True, max_length=40)

    players = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s: %s' % (self.step, self.players)
