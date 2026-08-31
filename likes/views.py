import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from likes.models import Likes


def _get_current_quest(quest_hash):
    """Строка оценок для записи — создаём, если её ещё нет."""
    try:
        current_quest = Likes.objects.get(pk=quest_hash)
    except ObjectDoesNotExist:
        current_quest = Likes.objects.create(quest_hash=quest_hash)
    return current_quest


def save(request):
    quest_hash = request.GET["quest_hash"]
    quest = _get_current_quest(quest_hash)

    key = request.GET["type"]
    clear_old = request.GET["clear_old"]
    print(clear_old)
    if key == "like":
        quest.likes += 1
        if clear_old == "True":
            quest.dislikes -= 1
    elif key == "dislike":
        quest.dislikes += 1
        if clear_old == "True":
            quest.likes -= 1
    else:
        return HttpResponse(json.dumps({"error": "key not found"}))

    quest.save()
    return HttpResponse(json.dumps({"ok": "complete add"}))


def get_counter(request):
    # Чтение не создаёт строку: раньше каждый показанный вопрос оставлял
    # в базе пустую запись, и таблица росла без единой оценки.
    quest_hash = request.GET["quest_hash"]
    quest = Likes.objects.filter(pk=quest_hash).first()

    if quest is None:
        return HttpResponse(json.dumps({"likes": 0, "dislikes": 0}))

    return HttpResponse(json.dumps({"likes": quest.likes, "dislikes": quest.dislikes}))


def clear(request):
    """Полная очистка таблицы оценок.

    Хеш вопроса считается из его текста, поэтому после правки вопросов
    старые строки остаются в базе навсегда. Здесь сносится всё — счётчики
    наберутся заново, восстановить их нельзя, поэтому нужен secret_key:

        /likes_clear/?secret_key=...&confirm=1
    """
    if request.GET.get("secret_key") != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    total = Likes.objects.count()

    # Без confirm только показываем размер: слишком легко снести таблицу,
    # открыв старую ссылку из истории браузера.
    if request.GET.get("confirm") != "1":
        return HttpResponse(json.dumps({"total": total,
                                        "hint": "add confirm=1 to delete"}))

    Likes.objects.all().delete()
    return HttpResponse(json.dumps({"ok": "cleared", "deleted": total}))
