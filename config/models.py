from django.core.cache import cache
from django.db import models


class Setting(models.Model):
    """Игровая настройка, которую можно менять без деплоя.

    Здесь живут величины, которые захочется подкрутить по метрикам:
    размер комнаты турнира, сколько мест награждается, предел списка
    друзей. Технические константы — формат кода игрока, коды ответов
    Google — сюда не попадают: их правка задним числом ломает уже
    выданное.

    Значение строкой, а тип задаёт тот, кто читает: настроек немного,
    и отдельные колонки под число, флаг и текст усложнили бы таблицу
    ради пары процентов удобства.
    """

    #: Ключ вида "tournament.room_size" — по нему настройка и читается
    key = models.CharField(primary_key=True, max_length=100)

    value = models.CharField(max_length=500)

    #: Зачем она нужна. Заполняется кодом при первом чтении, чтобы в
    #: админке было видно, на что влияет строка.
    note = models.CharField(max_length=300, default="", blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return "%s = %s" % (self.key, self.value)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Настройку читают на каждый запрос, поэтому она кэшируется.
        # Правка в админке должна применяться сразу, а не через пять
        # минут, когда кэш сам протухнет.
        cache.delete(_cache_key(self.pk))


def _cache_key(key):
    return "setting:%s" % key


#: Насколько держим значение в памяти. Настройки меняются редко, а
#: читаются постоянно: без кэша каждый запрос к турниру ходил бы в
#: базу за размером комнаты.
CACHE_SECONDS = 300


def get_int(key, default, note=""):
    """Число из настроек. Нет записи — заводим её со значением по
    умолчанию, чтобы настройка появилась в админке сама."""
    raw = _raw(key, default, note)
    try:
        return int(raw)
    except (TypeError, ValueError):
        # Кто-то вписал в админке текст вместо числа: работаем по
        # умолчанию, а не падаем на каждом запросе
        return default


def _raw(key, default, note):
    cached = cache.get(_cache_key(key))
    if cached is not None:
        return cached

    setting, _ = Setting.objects.get_or_create(
        pk=key,
        defaults={"value": str(default), "note": note},
    )

    # Описание могло появиться позже самой настройки
    if note and setting.note != note:
        Setting.objects.filter(pk=key).update(note=note)

    cache.set(_cache_key(key), setting.value, CACHE_SECONDS)
    return setting.value
