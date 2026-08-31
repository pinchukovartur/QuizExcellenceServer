import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from answer_counter.models import AnswerCounter


def _get_current_quest(quest_hash):
    """Строка счётчика для записи — создаём, если её ещё нет."""
    try:
        current_quest = AnswerCounter.objects.get(pk=quest_hash)
    except ObjectDoesNotExist:
        current_quest = AnswerCounter.objects.create(quest_hash=quest_hash)
    return current_quest


def save(request):
    quest_hash = request.GET["quest_hash"]
    quest = _get_current_quest(quest_hash)

    key = request.GET["index"]
    if key == "0":
        quest.first_answer += 1
    elif key == "1":
        quest.second_answer += 1
    elif key == "2":
        quest.third_answer += 1
    elif key == "3":
        quest.four_answer += 1
    else:
        return HttpResponse(json.dumps({"error": "key not found"}))

    quest.save()
    return HttpResponse(json.dumps({"ok": "complete add"}))


def get_counter(request):
    # Чтение не создаёт строку: раньше каждый показанный вопрос оставлял
    # в базе пустую запись, и таблица росла без единого ответа.
    quest_hash = request.GET["quest_hash"]
    quest = AnswerCounter.objects.filter(pk=quest_hash).first()

    if quest is None:
        return HttpResponse(json.dumps({1: 0, 2: 0, 3: 0, 4: 0}))

    return HttpResponse(json.dumps({1: quest.first_answer, 2: quest.second_answer,
                                    3: quest.third_answer, 4: quest.four_answer}))


def clear(request):
    """Полная очистка таблицы ответов.

    Хеш вопроса считается из его текста, поэтому после правки вопросов
    старые строки остаются в базе навсегда. Здесь сносится всё — счётчики
    наберутся заново, восстановить их нельзя, поэтому нужен secret_key:

        /answer_counter_clear/?secret_key=...&confirm=1
    """
    if request.GET.get("secret_key") != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    total = AnswerCounter.objects.count()

    # Без confirm только показываем размер: слишком легко снести таблицу,
    # открыв старую ссылку из истории браузера.
    if request.GET.get("confirm") != "1":
        return HttpResponse(json.dumps({"total": total,
                                        "hint": "add confirm=1 to delete"}))

    AnswerCounter.objects.all().delete()
    return HttpResponse(json.dumps({"ok": "cleared", "deleted": total}))
