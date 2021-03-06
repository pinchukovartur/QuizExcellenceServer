from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from quiz_word.models import QuizWordPrestige
import json


def clear_empty(request):
    delatable_objects = QuizWordPrestige.objects.filter(prestige=0)[:1000]
    for m in delatable_objects:
        m.delete()

    return HttpResponse("ok")

def save(request):
    game_state_id = request.GET["game_state_id"]
    prestige = request.GET["prestige"]
    name = request.GET["name"]

    try:
        pr = QuizWordPrestige.objects.get(pk=game_state_id)
        pr.prestige = prestige
        pr.name = name
        pr.save()
    except ObjectDoesNotExist:
        QuizWordPrestige.objects.create(game_state_id=game_state_id, prestige=prestige, name=name)

    return HttpResponse("ok")

def get_leader_board(request):
    result = dict()

    game_state_id = request.GET["game_state_id"]
    user_name = request.GET["user_name"]

    if not game_state_id or not user_name:
        return HttpResponse("error")

    current_prestige, current_num, result["current"] = _get_current_prestige(game_state_id, user_name)
    result["top"] = _get_top(5)
    result["max"] = _get_max(2, current_prestige, current_num)
    result["min"] = _get_min(2, current_prestige, current_num)
    return HttpResponse(json.dumps(result))


def _get_top(top_count):
    # create top 5 prestige data
    top_prestige = QuizWordPrestige.objects.order_by('-prestige', "-updated_at")[:top_count]
    num = 1
    top_prestige_list = list()
    #print("TOP")
    for pr in top_prestige:
        #print(num, pr.game_state_id, pr.created_at)
        top_prestige_list.append({"number": num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        num = num + 1
    return top_prestige_list


def _get_current_prestige(game_state_id, user_name):
    # create current user data
    try:
        current_prestige = QuizWordPrestige.objects.get(pk=game_state_id)
    except ObjectDoesNotExist:
        current_prestige = QuizWordPrestige.objects.create(game_state_id=game_state_id, prestige=0, name=user_name)

    count_user_max_prestige = QuizWordPrestige.objects.filter(prestige__gt=current_prestige.prestige).count()
    count_user_quelas_prestige = QuizWordPrestige.objects.filter(prestige=current_prestige.prestige,
                                                         created_at__gt=current_prestige.created_at).count()

    current_num = count_user_quelas_prestige + count_user_max_prestige + 1

    result = {"number": current_num, "prestige": current_prestige.prestige, "name": current_prestige.name,
              "id": current_prestige.game_state_id}
    #print("Current")
    #print(current_num, current_prestige.game_state_id, current_prestige.created_at)
    return current_prestige, current_num, result


def _get_max(max_count, current_prestige, current_num):
    # create max 2 prestige
    max_list = list()
    max_num = current_num - 1

    max_prestige = QuizWordPrestige.objects.filter(prestige=current_prestige.prestige, created_at__gt=current_prestige.created_at).order_by("updated_at")[:max_count]
    #print("MAX")
    for pr in max_prestige:
        #print(max_num, pr.game_state_id, pr.created_at)
        max_list.append({"number": max_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        max_num = max_num - 1

    if len(max_list) < max_count:
        max_prestige = QuizWordPrestige.objects.filter(prestige__gt=current_prestige.prestige).order_by("prestige", "updated_at")[:max_count - len(max_list)]
        for pr in max_prestige:
            #print(max_num, pr.game_state_id, pr.created_at)
            max_list.append({"number": max_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
            max_num = max_num - 1

    return max_list


def _get_min(min_count, current_prestige, current_num):
    # create min prestige
    min_list = list()
    min_num = current_num + 1

    min_prestige = QuizWordPrestige.objects.filter(prestige=current_prestige.prestige,
                                           created_at__lt=current_prestige.created_at).order_by("-updated_at")[
                   :min_count]
    #print("min")
    for pr in min_prestige:
        #print(min_num, pr.game_state_id, pr.created_at, pr.prestige)
        min_list.append({"number": min_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        min_num = min_num + 1

    if len(min_list) < min_num:
        min_prestige = QuizWordPrestige.objects.filter(prestige__lt=current_prestige.prestige).order_by("-prestige", "-updated_at")[
                       :min_count - len(min_list)]
        for pr in min_prestige:
            #print(min_num, pr.game_state_id, pr.created_at, pr.prestige)
            min_list.append({"number": min_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
            min_num = min_num + 1

    return min_list

