"""Отметка активности игрока. Вызывается из prestige.views.save."""

from django.utils import timezone

from metrics.models import ActivityDay


def mark_active(game_state_id, prestige, created_at=None):
    """Отмечает, что игрок сегодня закрыл тему.

    Вызывается из сохранения престижа, поэтому обязана быть
    безопасной: сбой метрики не должен мешать игроку сохранить
    прогресс. Любое исключение гасится — данные метрик менее
    важны, чем работающая игра.

    prestige == 0 не отмечаем: такие вызовы приходят и от
    лидерборда (prestige.views._get_current_prestige создаёт
    запись при открытии рейтинга), а это не активность.
    """
    try:
        value = int(prestige)
    except (TypeError, ValueError):
        return

    if value <= 0:
        return

    today = timezone.localdate()
    # За первый день считаем день создания записи в Prestige, а если
    # его нет под рукой — сегодняшний: игрок, впервые попавший сюда,
    # своей когортой и открывается.
    first = created_at.date() if created_at else today

    try:
        row, made = ActivityDay.objects.get_or_create(
            game_state_id=game_state_id, day=today,
            defaults={'prestige': value, 'first_day': first})
        # Престиж за день растёт: держим максимум, а не первое
        # значение — иначе не видно, сколько тем закрыто за день.
        if not made and value > row.prestige:
            row.prestige = value
            row.save(update_fields=['prestige'])
    except Exception:
        pass
