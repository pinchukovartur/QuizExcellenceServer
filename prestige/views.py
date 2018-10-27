from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from prestige.models import Prestige

import json


def save(request):
    game_state_id = request.GET["game_state_id"]
    prestige = request.GET["prestige"]
    name = request.GET["name"]

    Prestige.objects.create(game_state_id=game_state_id, prestige=prestige, name=name)

    return HttpResponse("ok")


def get_leader_board(request):
    result = dict()

    game_state_id = request.GET["game_state_id"]
    user_name = request.GET["user_name"]

    if not game_state_id or not user_name:
        return HttpResponse("error")

    # create current user data
    try:
        current_prestige = Prestige.objects.get(pk=game_state_id)
    except ObjectDoesNotExist:
        current_prestige = Prestige.objects.create(game_state_id=game_state_id, prestige=0, name=user_name)
    current_num = Prestige.objects.filter(prestige__gte=current_prestige.prestige).order_by("-updated_at").count()
    result["current"] = {"number": current_num, "prestige": current_prestige.prestige, "name": current_prestige.name,
                         "id": current_prestige.game_state_id}

    # create top 5 prestige data
    top_prestige = Prestige.objects.order_by('-prestige')[:5]
    num = 1
    top_prestige_list = list()
    for pr in top_prestige:
        top_prestige_list.append({"number": num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        num = num + 1
    result["top"] = top_prestige_list

    # create min 2 prestige
    min_prestige = Prestige.objects.filter(prestige__lt=current_prestige.prestige).order_by('-prestige').order_by(
        "-updated_at")[:2]
    min_list = list()
    min_num = current_num + 1
    for pr in reversed(min_prestige):
        min_list.append({"number": min_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        min_num = min_num + 1
    result["min"] = min_list

    # create max 2 prestige
    max_prestige = Prestige.objects.filter(prestige__gt=current_prestige.prestige).order_by('prestige').order_by(
        "-updated_at")[:2]
    max_list = list()
    max_num = current_num - 1
    for pr in max_prestige:
        max_list.append({"number": max_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        max_num = max_num - 1
    result["max"] = max_list

    return HttpResponse(json.dumps(result))
