from django.db import models

from state.models import States


class Profile(models.Model):
    """Карточка игрока для чужих глаз.

    Отдельная таблица, а не поле в Prestige: карточка нужна рейтингу,
    турниру, друзьям и тому, что появится дальше. Живи она в рейтинге,
    остальным пришлось бы ходить за ней в чужое приложение.

    От States отличается тем, что там лежит сохранёнка целиком —
    мегабайты на активного игрока. Здесь только то, что показывается
    другим, и читается это одним запросом.
    """

    #: Связь со стейтом один к одному: профиль есть только у того, кто
    #: играет, и уходит вместе с ним. Ключ тот же game_state_id, так
    #: что искать профиль по идентификатору игрока можно напрямую.
    state = models.OneToOneField(
        States,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
        db_column="game_state_id",
    )

    #: Что показывать в карточке: пройдено тем, достижений, серия дней
    #: и что там ещё захочется.
    #:
    #: JSON строкой, а не полями: набор данных будет меняться, и
    #: заводить миграцию под каждую новую строчку — лишнее. Сюда же
    #: ляжет всё будущее, чего мы пока не придумали.
    data = models.TextField(default="", blank=True)

    #: Числовой код, по которому игрока находят друзья.
    #:
    #: Выдаётся один раз и закрепляется навсегда: порядковый номер в
    #: таблице для этого не годится — он съедет, как только кто-то
    #: удалит прогресс, и старый код приведёт к чужому человеку.
    #:
    #: Пусто — код ещё не выдан. Именно NULL, а не ноль: уникальность
    #: держит база, а нулей у неё было бы столько же, сколько игроков
    #: без кода, и второй такой уже не сохранился бы.
    code = models.IntegerField(null=True, blank=True, unique=True,
                               db_index=True)

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def game_state_id(self):
        return self.state_id

    def __str__(self):
        return self.state_id


class Friendship(models.Model):
    """Кто у кого в друзьях.

    Связь односторонняя: строка «А добавил Б» не делает А другом у Б.
    Так проще и честнее для детской игры — подтверждать заявки ребёнок
    не станет, а добавивший видит успехи того, за кем следит.

    Взаимность видна по наличию обратной строки, и при желании её
    можно показать значком.
    """

    #: Кто добавил
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                              related_name="friends")

    #: Кого добавили
    friend = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               related_name="friend_of")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Одна пара — одна строка. Уникальность на уровне базы, а не
        # проверкой в коде: два запроса подряд с плохой связью иначе
        # завели бы дубль.
        unique_together = ("owner", "friend")
        indexes = [models.Index(fields=["owner", "created_at"])]

    def __str__(self):
        return "%s -> %s" % (self.owner_id, self.friend_id)
