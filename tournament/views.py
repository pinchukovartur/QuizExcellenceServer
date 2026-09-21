import json
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from tournament.models import Member, Room, Season

# Сколько игроков помещается в комнату
ROOM_SIZE = 15

# Сколько длится сезон
SEASON_DAYS = 14

# За сколько до конца закрываем вход: попасть в событие, где остался
# день, — значит заведомо проиграть, и новичок решит, что турниры не
# для него.
CLOSED_BEFORE_END = timedelta(days=2)


def _forbidden(request):
    key = request.POST.get("secret_key") or request.GET.get("secret_key", "")
    return key != settings.API_SECRET_KEY


def _actual_season():
    """Текущий сезон. Закончился или его нет — заводим следующий.

    Расписание не храним: сезон начинается тогда, когда в игру зашёл
    первый игрок после конца предыдущего. Для события на две недели
    этого достаточно, а планировщика на хостинге нет.
    """
    now = timezone.now()
    season = Season.objects.filter(finished_at__gt=now).order_by("-pk").first()
    if season is not None:
        return season

    return Season.objects.create(
        started_at=now,
        finished_at=now + timedelta(days=SEASON_DAYS),
    )


def _open_for_join(season):
    """Можно ли ещё войти: за два дня до конца вход закрыт."""
    return timezone.now() + CLOSED_BEFORE_END <= season.finished_at


def _season_json(season, room=None):
    data = {
        "season_id": season.pk,
        "started_at": season.started_at.isoformat(),
        "finished_at": season.finished_at.isoformat(),
        "room_size": ROOM_SIZE,
    }
    if room is not None:
        data["room_id"] = room.pk

    return data


@csrf_exempt
def join(request):
    """Регистрирует игрока: POST на /tournament_join/.

    Ищет комнату с местом, свободной нет — создаёт свою. Игрок, уже
    состоящий в комнате этого сезона, получает её же: повторный вход
    после переустановки не должен плодить записи и обнулять счёт.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    game_state_id = request.POST.get("game_state_id", "")
    if not game_state_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    season = _actual_season()

    existing = Member.objects.filter(
        room__season=season, game_state_id=game_state_id
    ).first()
    if existing is not None:
        return HttpResponse(json.dumps({
            "ok": True,
            **_season_json(season, existing.room),
        }))

    # Вход закрыт — сезон доигрывают те, кто успел
    if not _open_for_join(season):
        return HttpResponse(json.dumps({
            "ok": False,
            "closed": True,
            **_season_json(season),
        }))

    name = request.POST.get("name", "")[:200]
    try:
        avatar = int(request.POST.get("avatar", "-1"))
    except ValueError:
        avatar = -1

    for _ in range(3):
        room = (Room.objects
                .filter(season=season, players_count__lt=ROOM_SIZE)
                .order_by("-players_count", "pk")
                .first())
        if room is None:
            room = Room.objects.create(season=season)

        try:
            with transaction.atomic():
                Member.objects.create(
                    room=room,
                    game_state_id=game_state_id,
                    name=name,
                    avatar=avatar,
                )
                # Счётчик поднимаем запросом к базе, а не в питоне:
                # два игрока, зашедших одновременно, иначе записали бы
                # одно и то же значение и комната переполнилась бы.
                Room.objects.filter(pk=room.pk).update(
                    players_count=F("players_count") + 1
                )
        except IntegrityError:
            # Кто-то занял место между выбором и вставкой — пробуем ещё
            continue

        return HttpResponse(json.dumps({
            "ok": True,
            **_season_json(season, room),
        }))

    return HttpResponse(json.dumps({"error": "no room"}), status=503)


@csrf_exempt
def add_score(request):
    """Добавляет очки: POST на /tournament_score/.

    Присылается прибавка, а не итог: игра могла не достучаться до
    сервера в прошлый раз, и итог с устройства затёр бы то, что уже
    засчитано.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    game_state_id = request.POST.get("game_state_id", "")
    try:
        delta = int(request.POST.get("delta", "0"))
    except ValueError:
        delta = 0

    if not game_state_id or delta <= 0:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    season = _actual_season()
    member = Member.objects.filter(
        room__season=season, game_state_id=game_state_id
    ).first()
    if member is None:
        return HttpResponse(json.dumps({"ok": False, "not_joined": True}))

    Member.objects.filter(pk=member.pk).update(score=F("score") + delta)
    member.refresh_from_db()

    return HttpResponse(json.dumps({"ok": True, "score": member.score}))


def board(request):
    """Таблица комнаты: /tournament_board/?game_state_id=...

    Отдаёт всех участников комнаты с местами. Пятнадцать строк —
    столько же, сколько в комнате, поэтому страницы не нужны.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    game_state_id = request.GET.get("game_state_id", "")
    if not game_state_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    season = _actual_season()
    member = Member.objects.filter(
        room__season=season, game_state_id=game_state_id
    ).first()
    if member is None:
        return HttpResponse(json.dumps({
            "ok": False,
            "not_joined": True,
            "open": _open_for_join(season),
            **_season_json(season),
        }))

    rows = (Member.objects
            .filter(room=member.room)
            .order_by("-score", "updated_at"))

    items = []
    for number, row in enumerate(rows, start=1):
        items.append({
            "number": number,
            "game_state_id": row.game_state_id,
            "name": row.name,
            "avatar": row.avatar,
            "score": row.score,
        })

    return HttpResponse(json.dumps({
        "ok": True,
        "items": items,
        **_season_json(season, member.room),
    }, ensure_ascii=False), content_type="application/json")


def status(request):
    """Состояние события: /tournament_status/

    Нужен экрану до регистрации: показать, сколько осталось и можно ли
    ещё войти, не заводя игрока в комнату.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    season = _actual_season()

    return HttpResponse(json.dumps({
        "ok": True,
        "open": _open_for_join(season),
        **_season_json(season),
    }))
