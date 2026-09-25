from django.db import models


class Feedback(models.Model):
    """Сообщение от игрока: об ошибке в вопросе или низкая оценка.

    Раньше и то и другое уходило только в аналитику: посмотреть
    глазами было можно, а разобрать скриптом или ответить игроку —
    нет. Здесь текст лежит целиком и с контекстом.
    """

    # Откуда пришло: разбирать эти два потока нужно по-разному —
    # ошибка правится в вопросе, а оценка говорит об игре в целом.
    KIND_ERROR = 'error'
    KIND_RATE = 'rate'
    KINDS = ((KIND_ERROR, 'Ошибка в вопросе'), (KIND_RATE, 'Оценка игры'))

    game_state_id = models.CharField(max_length=60, db_index=True)
    kind = models.CharField(max_length=16, choices=KINDS, db_index=True)
    text = models.TextField()

    # Контекст ошибки: по хешу вопроса его можно найти в ассетах, а
    # предмет сужает поиск. У оценки пусто — она не про вопрос.
    question_hash = models.CharField(max_length=64, default='', blank=True)
    subject_id = models.CharField(max_length=40, default='', blank=True)

    # Оценка 1–5 у kind=rate, 0 у сообщений об ошибке
    rating = models.IntegerField(default=0)

    # Версия приложения: без неё непонятно, исправлено ли уже
    version = models.CharField(max_length=20, default='', blank=True)

    # Разобрано ли сообщение. Скрипт мониторинга смотрит только новые,
    # а разобранные не удаляются — по ним видно историю правок.
    is_done = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        # Имя задаём явно: без него Django считает его от хеша
        # полей и при каждой проверке предлагает переименовать
        # индекс, заведённый первой миграцией
        indexes = [models.Index(fields=['is_done', 'created_at'],
                                name='feedback_fe_done_idx')]

    def __str__(self):
        return '%s %s' % (self.kind, self.text[:40])
