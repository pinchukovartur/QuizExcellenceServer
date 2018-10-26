from django.http import HttpResponse
from prestige.models import Prestige


def save(request):
    game_state_id = request.GET["game_state_id"]
    prestige = request.GET["prestige"]
    name = request.GET["name"]

    Prestige.objects.create(game_state_id=game_state_id, prestige=prestige, name=name)

    return HttpResponse("ok")


def get_leader_board(request):
    game_state_id = request.GET["game_state_id"]

    result = dict()

    top_prestigeis = Prestige.objects.order_by('-prestige')[:5]
    num = 1
    top_prestigeis_list = list()
    for pr in top_prestigeis:
        top_prestigeis_list.append({"number": num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        num = num + 1
    result["top"] = top_prestigeis_list

    current_prestige = Prestige.objects.get(pk=game_state_id)
    current_num = Prestige.objects.filter(prestige__gte=current_prestige.prestige).order_by("-updated_at").count()
    result["current"] = {"number": current_num, "prestige": current_prestige.prestige, "name": current_prestige.name,
                         "id": current_prestige.game_state_id}

    min_prestigeis = Prestige.objects.filter(prestige__lt=current_prestige.prestige).order_by('-prestige').order_by("-updated_at")[:2]
    min_list = list()
    min_num = current_num + 1
    for pr in reversed(min_prestigeis):
        min_list.append({"number": min_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        min_num = min_num + 1
    result["min"] = min_list

    max_prestigeis = Prestige.objects.filter(prestige__gt=current_prestige.prestige).order_by('prestige').order_by("-updated_at")[:2]
    max_list = list()
    max_num = current_num - 1
    for pr in max_prestigeis:
        max_list.append({"number": max_num, "prestige": pr.prestige, "name": pr.name, "id": pr.game_state_id})
        max_num = max_num - 1
    result["max"] = max_list

    return HttpResponse(json.dumps(result))
