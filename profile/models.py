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

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def game_state_id(self):
        return self.state_id

    def __str__(self):
        return self.state_id
