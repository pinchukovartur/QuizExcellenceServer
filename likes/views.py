import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render

from likes.models import Likes


def _get_current_quest(quest_hash):
    # create current quest data
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
    quest_hash = request.GET["quest_hash"]
    quest = _get_current_quest(quest_hash)
    return HttpResponse(json.dumps({"likes": quest.likes, "dislikes": quest.dislikes}))


