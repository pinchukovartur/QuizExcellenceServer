import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render

from answer_counter.models import AnswerCounter


def _get_current_quest(quest_hash):
    # create current quest data
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
    quest_hash = request.GET["quest_hash"]
    quest = _get_current_quest(quest_hash)
    return HttpResponse(json.dumps({1: quest.first_answer, 2: quest.second_answer,
                                    3: quest.third_answer, 4: quest.four_answer}))
