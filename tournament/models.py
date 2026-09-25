from django.db import models
from django.utils import timezone


class Season(models.Model):
    """Запуск события: сроки задаются руками в админке.

    Сезон общий для всех: начинается и заканчивается у всех в одно
    время, чтобы событие можно было анонсировать. Комнаты только делят
    участников, своих сроков у них нет.

    Автоматически сезоны больше не создаются. Нет заведённого запуска
    или все закончились — турнира нет, и окно честно говорит, что
    следующий будет позже. Событие, которое идёт всегда, перестаёт
    быть событием.
    """

    #: Название запуска: «Весенняя олимпиада», «Зимний кубок».
    #:
    #: Уходит в игру и показывается на кнопке события, так что это
    #: текст для игрока, а не пометка для админки. Пусто — игра
    #: подставит своё слово.
    title = models.CharField(max_length=100, default="", blank=True)

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField()

    #: За сколько дней до конца закрывается вход.
    #:
    #: Попасть в событие, где остался день, значит заведомо проиграть,
    #: и новичок решит, что турниры не для него. Но правильное окно
    #: зависит от длины запуска: двухнедельному нужно два дня, а
    #: трёхдневному спринту хватит нескольких часов.
    #:
    #: Ноль — вход открыт до самого конца.
    closed_before_end_days = models.IntegerField(default=2)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        name = self.title or f"запуск {self.pk}"
        return f"{name}: {self.started_at:%d.%m} — {self.finished_at:%d.%m}"


class Room(models.Model):
    """Комната на 15 игроков внутри сезона.

    Счётчик участников держим полем, а не считаем запросом: регистрация
    ищет свободную комнату на каждый вход, и подсчёт по связанной
    таблице на каждый такой запрос быстро стал бы самым дорогим местом.
    """

    season = models.ForeignKey(Season, on_delete=models.CASCADE,
                               related_name="rooms")
    players_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"room {self.pk} ({self.players_count})"


class Member(models.Model):
    """Игрок в комнате и его очки за сезон.

    Очки отдельные от престижа: престиж накопительный, и тот, кто
    играет месяц, занимал бы первое место в каждом событии. Здесь счёт
    начинается с нуля у всех.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                            related_name="members")
    game_state_id = models.CharField(max_length=60)
    name = models.CharField(max_length=200, default="")
    avatar = models.IntegerField(default=-1)
    score = models.IntegerField(default=0)

    #: Место, за которое игрок забрал награду. 0 — не забирал.
    #:
    #: Награду начисляет клиент по итоговой таблице, но отметку он
    #: присылает сюда: иначе не видно, кто получил приз, а игрок,
    #: переустановивший игру, мог бы забрать его второй раз.
    rewarded_place = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Один игрок — одна комната в сезоне. Уникальность на уровне
        # базы, а не проверкой в коде: два запроса подряд с плохой
        # связью иначе создали бы две записи.
        unique_together = ("room", "game_state_id")
        indexes = [models.Index(fields=["game_state_id"])]

    def __str__(self):
        return f"{self.name}: {self.score}"
