from django.http import HttpResponse
from prestige.models import Prestige


def save(request):
    game_state_id = request.GET["game_state_id"]
    prestige = request.GET["prestige"]
    name = request.GET["name"]

    Prestige.objects.create(game_state_id=game_state_id, prestige=prestige, name=name)

    return HttpResponse("ok")
