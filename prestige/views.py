from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from metrics.track import mark_active
from prestige.models import Prestige

from django.db import models

import json


def clear_all_empty(request):
    """Удаление игроков с престижем не выше порога.

    Запрос удаляет данные безвозвратно, поэтому требует secret_key —
    тот же, что у state_update:

        /prestige_clear_empty/?secret_key=...&prestige=0&count=1000
    """
    if request.GET.get("secret_key") != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    prestige = request.GET["prestige"]
    count = request.GET["count"]
    delatable_objects = Prestige.objects.filter(prestige__lte=int(prestige))[:int(count)]
    # Сколько строк реально попало под условие — считаем до удаления,
    # после него запрос вернул бы уже пустой результат.
    doomed = list(delatable_objects.values_list("pk", flat=True))
    Prestige.objects.filter(pk__in=doomed).delete()
    return HttpResponse("ok - " + str(len(doomed)))


def save_avatar(request):
    """Обновляет только иконку игрока: /save_avatar/?...

    Отдельно от save намеренно: тот отмечает день активности, и вызов
    при каждом открытии рейтинга сделал бы «активным» любого, кто
    просто заглянул в таблицу, — retention бы поехал.

    Запись не создаём: если игрока ещё нет, обновлять нечего, а
    создание пустого Prestige исказило бы конверсию.
    """
    game_state_id = request.GET.get("game_state_id", "")
    avatar = _requested_avatar(request)

    fields = {}
    if avatar is not None:
        fields["avatar"] = avatar

    if not game_state_id or not fields:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    updated = Prestige.objects.filter(pk=game_state_id).update(**fields)

    return HttpResponse(json.dumps({"ok": True, "updated": updated}))


def _row(number, prestige):
    """Одна строка лидерборда. Собирается только здесь, чтобы новые поля
    не приходилось добавлять в каждый сборщик по отдельности."""
    return {"number": number, "prestige": prestige.prestige, "name": prestige.name,
            "id": prestige.game_state_id, "avatar": prestige.avatar}


def _requested_avatar(request):
    """Номер иконки из запроса. Старые версии клиента его не присылают —
    для них возвращаем None, чтобы не затирать уже сохранённое значение."""
    raw = request.GET.get("avatar")
    if raw is None or raw == "":
        return None

    try:
        return int(raw)
    except ValueError:
        return None


def save(request):
    game_state_id = request.GET["game_state_id"]
    prestige = request.GET["prestige"]
    name = request.GET["name"]
    avatar = _requested_avatar(request)

    try:
        pr = Prestige.objects.get(pk=game_state_id)
        pr.prestige = prestige
        pr.name = name
        if avatar is not None:
            pr.avatar = avatar
        pr.save()
    except ObjectDoesNotExist:
        pr = Prestige.objects.create(game_state_id=game_state_id, prestige=prestige, name=name,
                                     avatar=-1 if avatar is None else avatar)

    # Клиент дёргает save только при первом прохождении темы, поэтому
    # здесь же отмечаем день активности — иначе retention не посчитать:
    # Prestige хранит лишь последний updated_at, истории дней в нём нет.
    # mark_active гасит свои ошибки: метрика не должна мешать сохранению.
    mark_active(game_state_id, prestige, pr.created_at)

    return HttpResponse("ok")


def get_leader_board(request):
    result = dict()

    game_state_id = request.GET["game_state_id"]
    user_name = request.GET["user_name"]

    if not game_state_id or not user_name:
        return HttpResponse("error")

    current_prestige, current_num, result["current"] = _get_current_prestige(game_state_id, user_name)
    result["max"] = _get_max(2, current_prestige, current_num)
    result["min"] = _get_min(2, current_prestige, current_num)

    # Топ добираем до полной таблицы: у лидера соседей сверху нет, и
    # с фиксированными пятью строками он видел вдвое короче список,
    # чем игрок из середины.
    top_count = 5 + (2 - len(result["max"])) + (2 - len(result["min"]))
    result["top"] = _get_top(top_count)
    return HttpResponse(json.dumps(result))


def _scored():
    """Игроки, прошедшие хотя бы одну тему.

    Нули в таблицу не попадают: раньше запись заводилась при первом же
    открытии рейтинга, и половина базы — это зашедшие, но не игравшие.
    Свой нулевой игрок всё равно видит себя — последней строкой.
    """
    return Prestige.objects.filter(prestige__gt=0)


def _get_top(top_count):
    # Нулевой престиж в таблицу не берём: это либо следы прежнего
    # поведения, когда запись заводилась при заходе в рейтинг, либо
    # игрок, не прошедший ни одной темы. Показывать чужие нули незачем —
    # свой игрок видит только себя последним.
    top_prestige = _scored().order_by('-prestige', "-updated_at")[:top_count]
    num = 1
    top_prestige_list = list()
    #print("TOP")
    for pr in top_prestige:
        #print(num, pr.game_state_id, pr.created_at)
        top_prestige_list.append(_row(num, pr))
        num = num + 1
    return top_prestige_list


def _get_current_prestige(game_state_id, user_name):
    # create current user data
    is_new = False
    try:
        current_prestige = Prestige.objects.get(pk=game_state_id)
    except ObjectDoesNotExist:
        # Запись не создаём: игрок мог просто заглянуть в таблицу, не
        # пройдя ни одной темы. Прежде такой заход клал в базу строку
        # с нулём — отсюда мёртвые записи, а метрика активности
        # считала зашедшего игравшим. Строка собирается в памяти:
        # себя игрок видит, в базу это не попадает.
        is_new = True
        current_prestige = Prestige(game_state_id=game_state_id, prestige=0, name=user_name,
                                    created_at=timezone.now())

    count_user_max_prestige = _scored().filter(prestige__gt=current_prestige.prestige).count()
    if is_new:
        # Ещё не играл — встаёт сразу за последним, у кого есть хотя бы
        # очко. Нули в таблице выше него не поднимаются: это следы
        # прежнего поведения, когда запись заводилась при одном заходе
        # в рейтинг, а не за игру.
        count_user_quelas_prestige = 0
    else:
        count_user_quelas_prestige = _scored().filter(prestige=current_prestige.prestige,
                                                      created_at__gt=current_prestige.created_at).count()

    current_num = count_user_quelas_prestige + count_user_max_prestige + 1

    result = _row(current_num, current_prestige)
    #print("Current")
    #print(current_num, current_prestige.game_state_id, current_prestige.created_at)
    return current_prestige, current_num, result


def _get_max(max_count, current_prestige, current_num):
    # create max 2 prestige
    max_list = list()
    max_num = current_num - 1

    max_prestige = _scored().filter(prestige=current_prestige.prestige,
                                    created_at__gt=current_prestige.created_at).order_by("updated_at")[:max_count]
    #print("MAX")
    for pr in max_prestige:
        #print(max_num, pr.game_state_id, pr.created_at)
        max_list.append(_row(max_num, pr))
        max_num = max_num - 1

    if len(max_list) < max_count:
        max_prestige = _scored().filter(prestige__gt=current_prestige.prestige).order_by("prestige", "updated_at")[:max_count - len(max_list)]
        for pr in max_prestige:
            #print(max_num, pr.game_state_id, pr.created_at)
            max_list.append(_row(max_num, pr))
            max_num = max_num - 1

    return max_list


def _get_min(min_count, current_prestige, current_num):
    # create min prestige
    min_list = list()
    min_num = current_num + 1

    min_prestige = _scored().filter(prestige=current_prestige.prestige,
                                    created_at__lt=current_prestige.created_at).order_by("-updated_at")[
                   :min_count]
    #print("min")
    for pr in min_prestige:
        #print(min_num, pr.game_state_id, pr.created_at, pr.prestige)
        min_list.append(_row(min_num, pr))
        min_num = min_num + 1

    # Сравниваем с нужным количеством, а не с позицией в таблице:
    # min_num — это номер строки, и у игрока из середины он всегда
    # больше len(min_list), поэтому добор срабатывал вхолостую.
    if len(min_list) < min_count:
        min_prestige = _scored().filter(prestige__lt=current_prestige.prestige).order_by("-prestige", "-updated_at")[
                       :min_count - len(min_list)]
        for pr in min_prestige:
            #print(min_num, pr.game_state_id, pr.created_at, pr.prestige)
            min_list.append(_row(min_num, pr))
            min_num = min_num + 1

    return min_list
