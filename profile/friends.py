"""Друзья: поиск по коду, добавление и список.

Найти игрока можно только по коду, который он сам назвал. Поиска по
имени нет намеренно: игра детская, и возможность перебрать чужие имена
здесь опаснее, чем неудобство продиктовать шесть цифр.
"""

import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from prestige.models import Prestige
from profile.models import Friendship, Profile
from profile.views import _issue_code

#: Сколько друзей можно держать. Ограничение не техническое: список
#: сверх этого перестаёт быть списком друзей.
MAX_FRIENDS = 100


def _forbidden(request):
    key = request.POST.get("secret_key") or request.GET.get("secret_key")
    return key != settings.API_SECRET_KEY


def _profile_of(game_state_id):
    return Profile.objects.filter(pk=game_state_id).first()


def _card(profile):
    """Строка друга: то, что видно в списке.

    Имя и престиж берём из рейтинга — отдельно их в профиле не держим,
    чтобы не расходились.
    """
    prestige = Prestige.objects.filter(pk=profile.state_id).first()

    return {
        "id": profile.state_id,
        "code": profile.code or 0,
        "name": prestige.name if prestige else "",
        "prestige": prestige.prestige if prestige else 0,
        "avatar": prestige.avatar if prestige else -1,
    }


@csrf_exempt
def my_code(request):
    """Свой код: POST /friend_code/

    Выдаётся при первом запросе и больше не меняется. POST, а не GET,
    потому что первый вызов создаёт код.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    game_state_id = request.POST.get("game_state_id", "")
    profile = _profile_of(game_state_id)
    if profile is None:
        return HttpResponse(json.dumps({"error": "no profile"}), status=404)

    return HttpResponse(json.dumps({"ok": True, "code": _issue_code(profile)}))


def find(request):
    """Игрок по коду: GET /friend_find/?code=123456

    Отдаём то же, что видно в списке друзей: этого хватает, чтобы
    узнать человека и решить, добавлять ли его.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    raw = request.GET.get("code", "")
    if not raw.isdigit():
        return HttpResponse(json.dumps({"ok": True, "found": False}))

    profile = Profile.objects.filter(code=int(raw)).first()
    if profile is None:
        return HttpResponse(json.dumps({"ok": True, "found": False}))

    return HttpResponse(json.dumps({
        "ok": True,
        "found": True,
        "player": _card(profile),
    }))


@csrf_exempt
def add(request):
    """Добавляет друга: POST /friend_add/

    Подтверждения не спрашиваем: ребёнок не станет ждать, пока друг
    примет заявку, а показываем мы только то, что и так видно в
    рейтинге.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    owner = _profile_of(request.POST.get("game_state_id", ""))
    if owner is None:
        return HttpResponse(json.dumps({"error": "no profile"}), status=404)

    raw = request.POST.get("code", "")
    if not raw.isdigit():
        return HttpResponse(json.dumps({"ok": True, "found": False}))

    friend = Profile.objects.filter(code=int(raw)).first()
    if friend is None:
        return HttpResponse(json.dumps({"ok": True, "found": False}))

    if friend.state_id == owner.state_id:
        return HttpResponse(json.dumps({"ok": False, "self": True}))

    if owner.friends.count() >= MAX_FRIENDS:
        return HttpResponse(json.dumps({"ok": False, "full": True}))

    # Уже в друзьях — не ошибка: игрок мог нажать дважды
    Friendship.objects.get_or_create(owner=owner, friend=friend)

    return HttpResponse(json.dumps({
        "ok": True,
        "found": True,
        "player": _card(friend),
    }))


@csrf_exempt
def remove(request):
    """Убирает друга: POST /friend_remove/"""
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    owner_id = request.POST.get("game_state_id", "")
    friend_id = request.POST.get("friend_id", "")

    if not owner_id or not friend_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    removed, _ = Friendship.objects.filter(
        owner_id=owner_id, friend_id=friend_id).delete()

    return HttpResponse(json.dumps({"ok": True, "removed": removed}))


def friend_list(request):
    """Список друзей: GET /friend_list/?game_state_id=...

    Отдаём с престижем и именем, чтобы рядом с каждым сразу было
    видно, как у него дела, — карточка открывается тапом, как в
    рейтинге.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    owner_id = request.GET.get("game_state_id", "")
    if not owner_id:
        return HttpResponse(json.dumps({"ok": True, "items": []}))

    links = (Friendship.objects
             .filter(owner_id=owner_id)
             .select_related("friend")
             .order_by("-created_at")[:MAX_FRIENDS])

    items = [_card(link.friend) for link in links]
    # Сильнейшие сверху: список друзей читается как маленький рейтинг
    items.sort(key=lambda row: row["prestige"], reverse=True)

    return HttpResponse(json.dumps({"ok": True, "items": items}))
