import json

from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone

from metrics.models import ActivityDay
from prestige.models import Prestige

# За сколько дней строим сводку. Больше месяца смотреть смысла нет:
# когорты старше уже не показательны, а запрос тяжелеет.
WINDOW = 30

# Дни, по которым считаем возврат. D1 — вернулся на следующий день,
# D7 — через неделю.
CHECKPOINTS = (1, 3, 7, 14, 30)


def _cohorts(today):
    """{день первого прохождения: {смещение: сколько игроков}}."""
    rows = (ActivityDay.objects
            .filter(first_day__gte=today - timezone.timedelta(days=WINDOW))
            .values('first_day', 'day')
            .annotate(players=Count('game_state_id', distinct=True)))

    data = {}
    for r in rows:
        offset = (r['day'] - r['first_day']).days
        data.setdefault(r['first_day'], {})[offset] = r['players']
    return data


def summary(request):
    """Сводка удержания: /metrics/?secret_key=...

    Отдаёт JSON — по когортам видно, сколько игроков вернулось на
    следующий день, через неделю и так далее. Плюс конверсия
    «завёл запись → прошёл первую тему»: записи в Prestige создаёт
    и открытие лидерборда, поэтому нулевые считаются отдельно.
    """
    if request.GET.get("secret_key") != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    today = timezone.localdate()
    since = today - timezone.timedelta(days=WINDOW)
    cohorts = _cohorts(today)

    result = []
    for first_day in sorted(cohorts, reverse=True):
        by_offset = cohorts[first_day]
        size = by_offset.get(0, 0)
        if not size:
            continue

        age = (today - first_day).days
        row = {"day": first_day.isoformat(), "players": size}
        for point in CHECKPOINTS:
            # Когорта младше контрольной точки — данных ещё нет,
            # и ноль тут читался бы как «никто не вернулся».
            if age < point:
                row["d%d" % point] = None
            else:
                back = by_offset.get(point, 0)
                row["d%d" % point] = round(back * 100.0 / size, 1)
        result.append(row)

    # Сколько записей завелось и сколько из них с прогрессом.
    fresh = Prestige.objects.filter(created_at__date__gte=since)
    total = fresh.count()
    played = fresh.filter(prestige__gt=0).count()

    return HttpResponse(json.dumps({
        "today": today.isoformat(),
        "window_days": WINDOW,
        "records": total,
        "played_first_topic": played,
        "conversion_percent": round(played * 100.0 / total, 1) if total else 0,
        "cohorts": result,
    }, ensure_ascii=False, indent=2), content_type="application/json")
