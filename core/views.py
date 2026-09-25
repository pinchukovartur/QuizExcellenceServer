from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from prestige.models import Prestige

import json


def index(request):
    """Короткая сводка по престижам за сегодня.

    updated_at обновляется при каждом сохранении (auto_now), так что
    записи с сегодняшней датой — это игроки, заходившие сегодня.

    Время в базе хранится в UTC, а день считаем по TIME_ZONE проекта,
    поэтому границы суток берём через localdate/make_aware, а не по utcnow.
    """
    today = timezone.localdate()
    start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time()))

    updated_today = Prestige.objects.filter(updated_at__gte=start).count()
    created_today = Prestige.objects.filter(created_at__gte=start).count()

    return HttpResponse(json.dumps({
        "ok": True,
        "date": today.isoformat(),
        "updated_today": updated_today,
        "new_today": created_today,
        "total": Prestige.objects.count(),
    }), content_type="application/json")


def privacy(request):
    """Политика конфиденциальности.

    Нужна магазинам: и Google Play, и AppGallery требуют ссылку на
    живую страницу, иначе приложение не отправить на проверку. Держим
    её у себя, а не на стороннем хостинге: ссылка в карточке магазина
    не должна протухнуть.
    """
    return render(request, "privacy.html", {
        "updated": "25 сентября 2026 года",
        "email": "artur.pinchukou@redbarkgames.com",
    })


def server_time(request):
    """Текущее время сервера: GET /server_time/.

    Нужно всему, что раздаёт награды по календарю. Часы на устройстве
    переводятся, и по ним ежедневный бонус забирался бы сколько
    угодно раз подряд.

    Секретный ключ не спрашиваем: время не тайна, а лишняя проверка
    только мешала бы позвать его на старте игры.
    """
    now = timezone.localtime()

    return HttpResponse(json.dumps({
        "ok": True,
        "now": now.isoformat(),
        # День числом yyyymmdd — клиент сравнивает календарные дни, и
        # разбирать дату ради этого ему незачем
        "day": now.year * 10000 + now.month * 100 + now.day,
    }))
